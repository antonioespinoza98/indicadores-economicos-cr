# -------------------------------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: Página inicial de Streamlit
# -------------------------------------------------------------------------------------

# -- Importamos las dependencias
import streamlit as st

# -- Cuerpo de la aplicación --

# Subtítulo corto
st.subheader("Consulta indicadores del BCCR y la lista oficial de salarios mínimos del MTSS")

# Intro general
st.markdown("""
Bienvenido/a a esta aplicación.  
Aquí puedes explorar, visualizar y descargar datos económicos oficiales de Costa Rica de forma sencilla e interactiva.
""")

st.markdown("---")
st.header("¿Qué puedes hacer en esta aplicación?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Indicadores BCCR")
    st.markdown("""
- Consultar indicadores económicos del **Banco Central de Costa Rica (BCCR)**.  
- Ver sus series históricas en gráficos interactivos.  
- Cambiar el indicador y el período de análisis.  
- Descargar los datos para trabajarlos en Excel, R, Python, etc.
    """)

with col2:
    st.markdown("### 💼 Salarios mínimos MTSS")
    st.markdown("""
- Revisar la lista oficial de **salarios mínimos** del **MTSS**.  
- Filtrar y ordenar por tipo de empleo o código.  
- Descargar la tabla completa en formato CSV.  
    """)

st.markdown("---")

# Instrucción general de cómo usar la app
st.header("Cómo empezar")

st.markdown("""
1. Usa el menú lateral para ir a la sección **Indicadores**.  
2. Selecciona un indicador del BCCR en la lista desplegable.  
3. Explora el gráfico y, si lo necesitas, descarga los datos.  
4. Si te interesa la parte laboral, entra a **Lista de salarios - MTSS** dentro de *Indicadores* para ver la tabla de salarios mínimos.  
5. En la sección **Sobre la aplicación** encontrarás más detalles sobre el objetivo, fuentes de datos y alcances del proyecto.
""")

st.markdown("---")

# Nota final
st.info(
    "Los datos provienen de fuentes oficiales (BCCR y MTSS). "
    "Esta aplicación es solo una herramienta de consulta y no reemplaza la información publicada por las instituciones."
)