import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la Interfaz
st.set_page_config(page_title="Algoritmo Pro - Mi Cartera", layout="wide")
st.title("🛡️ Sistema de Gestión de Cartera en Tiempo Real")

# 2. Definición del Algoritmo (Pesos Objetivo)
OBJETIVOS = {
    "Rama 1 (VTI - Núcleo)": 0.35,
    "Rama 2 (Tecnología/Crecimiento)": 0.25,
    "Rama 3 (Oro/Refugio)": 0.15,
    "Rama 4 (Bonos/Estabilidad)": 0.15,
    "Rama 5 (Consumo/REITs)": 0.10
}

# Clasificación de tus activos reales
activos_usuario = {
    "Rama 1 (VTI - Núcleo)": ["VTI"],
    "Rama 2 (Tecnología/Crecimiento)": ["NVDA", "TSM", "GOOGL", "AAPL", "MU", "AVGO", "IONQ", "APP", "COIN", "CLS"],
    "Rama 3 (Oro/Refugio)": ["GLD"], 
    "Rama 4 (Bonos/Estabilidad)": ["BND"],
    "Rama 5 (Consumo/REITs)": ["KOF", "PEP", "COKE", "PG", "V", "BLK", "NU", "BA"]
}

# 3. Sidebar: Entrada de cantidades
st.sidebar.header("📥 Tus Acciones Actuales")
cantidades = {}
for rama, tickers in activos_usuario.items():
    with st.sidebar.expander(f"Editar {rama}"):
        for t in tickers:
            # Valores por defecto basados en tus capturas para facilitarte el llenado
            default_val = 0.0
            if t == "VTI": default_val = 9.49
            if t == "NVDA": default_val = 13.76
            if t == "TSM": default_val = 4.95
            
            cantidades[t] = st.number_input(f"Cant. {t}", min_value=0.0, value=default_val, step=0.01, key=t)

# 4. Botón Principal
if st.button("🔄 ACTUALIZAR PRECIOS EN VIVO"):
    with st.spinner("Conectando con la bolsa de valores..."):
        total_cartera = 0
        datos_por_accion = []
        resumen_ramas = {rama: 0.0 for rama in OBJETIVOS.keys()}
        
        for rama, tickers in activos_usuario.items():
            for t in tickers:
                if cantidades[t] > 0:
                    try:
                        ticker_data = yf.Ticker(t)
                        # Obtenemos precio actual
                        precio_actual = ticker_data.fast_info['lastPrice']
                        valor_posicion = precio_actual * cantidades[t]
                        
                        resumen_ramas[rama] += valor_posicion
                        total_cartera += valor_posicion
                        
                        datos_por_accion.append({
                            "Ticker": t,
                            "Precio Actual": f"${precio_actual:,.22f}",
                            "Valor Total": valor_posicion,
                            "Rama": rama
                        })
                    except:
                        st.error(f"Error cargando {t}")

    # 5. Visualización de Resultados
    st.metric("VALOR TOTAL DE TU CARTERA (USD)", f"${total_cartera:,.2f}")
    
    # Tabla Comparativa de Ramas
    st.subheader("📊 Análisis de Rebalanceo")
    analisis_data = []
    for rama in OBJETIVOS.keys():
        actual = resumen_ramas[rama]
        porc_actual = (actual / total_cartera) if total_cartera > 0 else 0
        objetivo_usd = total_cartera * OBJETIVOS[rama]
        diff = objetivo_usd - actual
        
        analisis_data.append({
            "Rama": rama,
            "Actual (%)": f"{porc_actual*100:.1f}%",
            "Objetivo (%)": f"{OBJETIVOS[rama]*100:.0f}%",
            "Diferencia (USD)": f"{'+' if diff > 0 else ''}${diff:,.22f}",
            "Estado": "Bajo Peso (Comprar)" if diff > 0 else "Sobre Peso (Vender)"
        })
    st.table(pd.DataFrame(analisis_data))

    # Detalle por Acción
    with st.expander("🔍 Ver detalle por acción individual"):
        st.dataframe(pd.DataFrame(datos_por_accion), use_container_width=True)

# 6. Gráfico Histórico al final
st.divider()
st.subheader("📈 Monitor de Tendencia")
ticker_sel = st.selectbox("Selecciona una acción para ver su gráfico mensual", 
                         ["NVDA", "VTI", "TSM", "AAPL", "GOOGL", "KOF", "COIN"])
if ticker_sel:
    hist = yf.Ticker(ticker_sel).history(period="1mo")
    st.line_chart(hist.Close)
