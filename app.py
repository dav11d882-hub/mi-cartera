import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuración de la Interfaz
st.set_page_config(page_title="Algoritmo de Inversión Pro", layout="wide")
st.title("🛡️ Sistema de Gestión de Cartera Automática")

# 2. Definición del Algoritmo (Pesos Objetivo)
OBJETIVOS = {
    "Rama 1 (VTI - Núcleo)": 0.35,
    "Rama 2 (Tecnología/Crecimiento)": 0.25,
    "Rama 3 (Oro/Refugio)": 0.15,
    "Rama 4 (Bonos/Estabilidad)": 0.15,
    "Rama 5 (Consumo/REITs)": 0.10
}

# Mapeo de tus activos reales a las ramas
activos_usuario = {
    "Rama 1 (VTI - Núcleo)": ["VTI"],
    "Rama 2 (Tecnología/Crecimiento)": ["NVDA", "TSM", "CLS", "GOOGL", "AAPL", "MU", "AVGO", "IONQ", "APP", "COIN"],
    "Rama 3 (Oro/Refugio)": ["GLD"], 
    "Rama 4 (Bonos/Estabilidad)": ["BND"],
    "Rama 5 (Consumo/REITs)": ["KOF", "PEP", "COKE", "PG", "V", "BLK", "NU"]
}

# 3. Sidebar para entrada de datos (Cantidad de acciones que ya tienes)
st.sidebar.header("📥 Tus Tenencias Actuales")
cantidades = {}
for rama, tickers in activos_usuario.items():
    with st.sidebar.expander(f"Editar {rama}"):
        for t in tickers:
            cantidades[t] = st.number_input(f"Cantidad de {t}", min_value=0.0, value=0.0, step=0.1, key=t)

# 4. Lógica de Cálculo
if st.button("🔄 EJECUTAR ANÁLISIS DE MERCADO"):
    with st.spinner("Obteniendo precios en tiempo real..."):
        datos_actuales = {}
        total_cartera = 0
        
        # Obtener precios y calcular valor actual por rama
        resumen_ramas = {}
        for rama, tickers in activos_usuario.items():
            valor_rama = 0
            for t in tickers:
                try:
                    precio = yf.Ticker(t).fast_info['lastPrice']
                    valor_posicion = precio * cantidades[t]
                    valor_rama += valor_posicion
                except:
                    st.error(f"No se pudo obtener precio para {t}")
            
            resumen_ramas[rama] = valor_rama
            total_cartera += valor_rama

    # 5. Mostrar Resultados
    st.metric("Valor Total de tu Portafolio", f"${total_cartera:,.2f} USD")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estado Actual vs Objetivo")
        tabla_datos = []
        for rama in OBJETIVOS.keys():
            monto_actual = resumen_ramas[rama]
            porcentaje_actual = (monto_actual / total_cartera) * 100 if total_cartera > 0 else 0
            monto_objetivo = total_cartera * OBJETIVOS[rama]
            diferencia = monto_objetivo - monto_actual
            
            tabla_datos.append({
                "Rama": rama,
                "Actual ($)": round(monto_actual, 2),
                "Actual (%)": f"{porcentaje_actual:.1f}%",
                "Objetivo (%)": f"{OBJETIVOS[rama]*100:.0f}%",
                "Acción": "COMPRAR" if diferencia > 0 else "VENDER",
                "Monto Ajuste": abs(round(diferencia, 2))
            })
        
        df = pd.DataFrame(tabla_datos)
        st.table(df)

    with col2:
        st.subheader("Gráfico de Distribución")
        st.bar_chart(df.set_index('Rama')['Actual ($)'])

    st.success("💡 CONSEJO DEL ALGORITMO: Para progresar solo, vende los excedentes en rojo y compra los faltantes en verde una vez al mes.")
