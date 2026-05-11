import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la Interfaz
st.set_page_config(page_title="Algoritmo Pro - COP/USD", layout="wide")
st.title("🛡️ Sistema de Gestión de Cartera Multidivisa")

# Selector de Moneda en la barra lateral
moneda = st.sidebar.selectbox("Selecciona Moneda de Visualización", ["USD", "COP"])

# 2. Definición del Algoritmo (Pesos Objetivo)
OBJETIVOS = {
    "Rama 1 (VTI - Núcleo)": 0.35,
    "Rama 2 (Tecnología/Crecimiento)": 0.25,
    "Rama 3 (Oro/Refugio)": 0.15,
    "Rama 4 (Bonos/Estabilidad)": 0.15,
    "Rama 5 (Consumo/REITs)": 0.10
}

# 3. Cantidades Actuales (Tus datos reales)
posiciones_iniciales = {
    "VTI": 9.497, "NVDA": 13.766, "TSM": 4.952, "CLS": 3.075, 
    "KOF": 10.012, "IONQ": 19.735, "GOOGL": 1.660, "AAPL": 1.556, 
    "BA": 1.458, "PEP": 2.212, "MU": 0.382, "V": 0.812, 
    "APP": 0.548, "COKE": 1.152, "GTY": 5.0, "BLK": 0.127, 
    "PG": 0.605, "COIN": 0.410, "AVGO": 0.175, "NU": 5.0,
    "GLD": 0.0, "BND": 0.0
}

ramas_map = {
    "Rama 1 (VTI - Núcleo)": ["VTI"],
    "Rama 2 (Tecnología/Crecimiento)": ["NVDA", "TSM", "CLS", "IONQ", "GOOGL", "AAPL", "MU", "APP", "COIN", "AVGO"],
    "Rama 3 (Oro/Refugio)": ["GLD"], 
    "Rama 4 (Bonos/Estabilidad)": ["BND"],
    "Rama 5 (Consumo/REITs)": ["KOF", "BA", "PEP", "V", "COKE", "GTY", "BLK", "PG", "NU"]
}

# 4. Sidebar: Ajuste de cantidades
st.sidebar.header("⚙️ Configuración")
cantidades_finales = {}
for rama, tickers in ramas_map.items():
    with st.sidebar.expander(f"Configurar {rama}"):
        for t in tickers:
            valor_base = posiciones_iniciales.get(t, 0.0)
            cantidades_finales[t] = st.number_input(f"Acciones {t}", min_value=0.0, value=float(valor_base), step=0.001, key=f"input_{t}")

# 5. Lógica de Conversión y Ejecución
if st.button("🚀 ACTUALIZAR VALORES"):
    with st.spinner("Consultando precios y TRM..."):
        trm = 1.0
        if moneda == "COP":
            try:
                trm = yf.Ticker("COP=X").fast_info['lastPrice']
                st.sidebar.success(f"TRM Consultada: ${trm:,.2f} COP")
            except:
                trm = 3950.0
                st.sidebar.warning("Usando TRM de respaldo ($3,950)")

        total_cartera = 0
        datos_acciones = []
        valores_por_rama = {rama: 0.0 for rama in OBJETIVOS.keys()}
        
        for rama, tickers in ramas_map.items():
            for t in tickers:
                cant = cantidades_finales[t]
                if cant > 0:
                    try:
                        precio_usd = yf.Ticker(t).fast_info['lastPrice']
                        valor_pos_convertido = (precio_usd * cant) * trm
                        
                        valores_por_rama[rama] += valor_pos_convertido
                        total_cartera += valor_pos_convertido
                        
                        datos_acciones.append({
                            "Ticker": t,
                            "Precio (Local)": f"${precio_usd * trm:,.2f}",
                            "Mi Valor (Local)": valor_pos_convertido,
                            "Rama": rama
                        })
                    except: pass

    # 6. Resultados Principales
    simbolo = "$" if moneda == "USD" else "COP $"
    st.metric(f"VALOR TOTAL EN {moneda}", f"{simbolo}{total_cartera:,.2f}")

    # Tabla de Rebalanceo
    st.subheader(f"📊 Plan de Rebalanceo ({moneda})")
    analisis = []
    for rama, peso_obj in OBJETIVOS.items():
        v_actual = valores_por_rama[rama]
        p_actual = (v_actual / total_cartera) if total_cartera > 0 else 0
        v_meta = total_cartera * peso_obj
        dif = v_meta - v_actual
        
        analisis.append({
            "Rama": rama,
            "Actual (%)": f"{p_actual*100:.1f}%",
            "Meta (%)": f"{peso_obj*100:.0f}%",
            "Diferencia": f"{'+' if dif > 0 else ''}{simbolo}{dif:,.2f}",
            "Acción": "🟢 COMPRAR" if dif > 0 else "🔴 VENDER"
        })
    st.table(pd.DataFrame(analisis))

    # --- NUEVA SECCIÓN RESTAURADA: DETALLE ACCIÓN POR ACCIÓN ---
    st.divider()
    st.subheader("🔍 Detalle Acción por Acción")
    if datos_acciones:
        df_detalle = pd.DataFrame(datos_acciones)
        # Formatear la columna Mi Valor para que se vea bien en pesos o dólares
        df_detalle["Mi Valor (Local)"] = df_detalle["Mi Valor (Local)"].map(lambda x: f"{simbolo}{x:,.2f}")
        st.dataframe(df_detalle, use_container_width=True)
    else:
        st.info("No hay acciones con cantidades mayores a 0 para mostrar.")

# 7. Gráfico Histórico
st.divider()
st.subheader("📈 Monitor de Tendencia (USD)")
ticker_sel = st.selectbox("Selecciona para ver historial mensual", ["VTI", "NVDA", "TSM", "AAPL", "GOOGL", "KOF", "COIN"])
if ticker_sel:
    hist = yf.Ticker(ticker_sel).history(period="1mo")
    st.line_chart(hist.Close)
