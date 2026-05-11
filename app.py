import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la Interfaz
st.set_page_config(page_title="Algoritmo Pro - Mi Cartera", layout="wide")
st.title("🛡️ Sistema de Gestión de Cartera Inteligente")

# 2. Definición del Algoritmo (Pesos Objetivo)
OBJETIVOS = {
    "Rama 1 (VTI - Núcleo)": 0.35,
    "Rama 2 (Tecnología/Crecimiento)": 0.25,
    "Rama 3 (Oro/Refugio)": 0.15,
    "Rama 4 (Bonos/Estabilidad)": 0.15,
    "Rama 5 (Consumo/REITs)": 0.10
}

# 3. BASE DE DATOS DE TUS ACCIONES ACTUALES (Aquí se mantienen tus cantidades)
# Puedes editar estos números directamente en el código cuando tus posiciones cambien mucho
posiciones_iniciales = {
    "VTI": 9.497, "NVDA": 13.766, "TSM": 4.952, "CLS": 3.075, 
    "KOF": 10.012, "IONQ": 19.735, "GOOGL": 1.660, "AAPL": 1.556, 
    "BA": 1.458, "PEP": 2.212, "MU": 0.382, "V": 0.812, 
    "APP": 0.548, "COKE": 1.152, "GTY": 5.0, "BLK": 0.127, 
    "PG": 0.605, "COIN": 0.410, "AVGO": 0.175, "NU": 5.0,
    "GLD": 0.0, "BND": 0.0  # Estas empiezan en 0 para que el algoritmo te diga cuánto comprar
}

# Clasificación por Ramas
ramas_map = {
    "Rama 1 (VTI - Núcleo)": ["VTI"],
    "Rama 2 (Tecnología/Crecimiento)": ["NVDA", "TSM", "CLS", "IONQ", "GOOGL", "AAPL", "MU", "APP", "COIN", "AVGO"],
    "Rama 3 (Oro/Refugio)": ["GLD"], 
    "Rama 4 (Bonos/Estabilidad)": ["BND"],
    "Rama 5 (Consumo/REITs)": ["KOF", "BA", "PEP", "V", "COKE", "GTY", "BLK", "PG", "NU"]
}

# 4. Sidebar: Interfaz para ajustar cantidades manualmente
st.sidebar.header("⚙️ Ajustar Cantidades Actuales")
cantidades_finales = {}

for rama, tickers in ramas_map.items():
    with st.sidebar.expander(f"Configurar {rama}"):
        for t in tickers:
            # El valor por defecto se toma de 'posiciones_iniciales'
            valor_base = posiciones_iniciales.get(t, 0.0)
            cantidades_finales[t] = st.number_input(
                f"Acciones de {t}", 
                min_value=0.0, 
                value=float(valor_base), 
                step=0.001, 
                key=f"input_{t}"
            )

# 5. Ejecución del Algoritmo
if st.button("🚀 CALCULAR REBALANCEO EN TIEMPO REAL"):
    with st.spinner("Consultando precios de mercado..."):
        total_cartera = 0
        datos_acciones = []
        valores_por_rama = {rama: 0.0 for rama in OBJETIVOS.keys()}
        
        for rama, tickers in ramas_map.items():
            for t in tickers:
                cant = cantidades_finales[t]
                if t in ["GLD", "BND"] and cant == 0:
                    continue # No procesar si aún no compramos de estas
                
                try:
                    tick = yf.Ticker(t)
                    precio = tick.fast_info['lastPrice']
                    valor_pos = precio * cant
                    
                    valores_por_rama[rama] += valor_pos
                    total_cartera += valor_pos
                    
                    datos_acciones.append({
                        "Ticker": t,
                        "Precio": f"${precio:,.2f}",
                        "Mi Valor": valor_pos,
                        "Rama": rama
                    })
                except:
                    pass

    # 6. Mostrar métricas principales
    st.metric("VALOR TOTAL DEL PORTAFOLIO", f"${total_cartera:,.2f} USD")

    # Tabla de Decisiones
    st.subheader("📋 Plan de Acción para Progresar")
    analisis = []
    for rama, peso_obj in OBJETIVOS.items():
        v_actual = valores_por_rama[rama]
        p_actual = (v_actual / total_cartera) if total_cartera > 0 else 0
        v_objetivo = total_cartera * peso_obj
        dif = v_objetivo - v_actual
        
        analisis.append({
            "Rama": rama,
            "Distribución Actual": f"{p_actual*100:.1f}%",
            "Meta": f"{peso_obj*100:.0f}%",
            "Ajuste Necesario (USD)": f"{'+' if dif > 0 else ''}${dif:,.2f}",
            "Instrucción": "🟢 COMPRAR" if dif > 0 else "🔴 VENDER / COSECHAR"
        })
    
    st.table(pd.DataFrame(analisis))

    # Detalle Individual
    with st.expander("Ver desglose por acción individual"):
        df_ind = pd.DataFrame(datos_acciones)
        if not df_ind.empty:
            st.dataframe(df_ind.sort_values(by="Mi Valor", ascending=False), use_container_width=True)

st.info("Nota: Las cantidades se mantienen grabadas en el código. Si haces una compra grande, actualiza el número en la barra lateral.")
