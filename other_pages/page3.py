# -------------------------------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: Tercera página del Streamlit, información sobre la app
# -------------------------------------------------------------------------------------

# -- importamos las dependencias

import streamlit as st


# -- Cuerpo de la página
st.markdown("""
Esta aplicación ha sido diseñada para facilitar el acceso, consulta y análisis de **indicadores económicos** y **datos oficiales** publicados por instituciones públicas de Costa Rica.  
Su objetivo es ofrecer una herramienta sencilla, visual e interactiva que permita a estudiantes, investigadores, analistas, desarrolladores, periodistas y público en general explorar información económica de forma rápida y clara.
""")

st.markdown("---")
st.header("📊 ¿Qué contiene?")

st.subheader("1. Indicadores del Banco Central de Costa Rica (BCCR)")
st.markdown("""
- Consulta de indicadores económicos oficiales del **Banco Central de Costa Rica (BCCR)**.  
- Visualización de series históricas mediante gráficos interactivos.  
- Posibilidad de cambiar el indicador y el período de análisis.  
- Opción de descargar los datos para trabajarlos fuera de la aplicación.

Estos indicadores pueden incluir niveles, tasas, montos, índices y otros datos útiles para el análisis macroeconómico y financiero.
""")

st.subheader("2. Lista oficial de salarios mínimos del MTSS")
st.markdown("""
- Tabla con los **salarios mínimos oficiales** definidos por el **Ministerio de Trabajo y Seguridad Social (MTSS)**.  
- Organización por tipo de empleo, código y monto salarial asignado según la normativa vigente.  
- Opción de descarga en formato CSV para análisis, documentación o integración en otros proyectos.
""")

st.markdown("---")
st.header("🧰 Funcionalidades principales")

st.markdown("""
- Visualización interactiva de series históricas.  
- Gráficos dinámicos por indicador.  
- Tablas descargables en formato CSV.  
- Navegación simple por secciones desde la barra lateral.  
- Uso de datos provenientes de fuentes oficiales de Costa Rica.
""")

st.markdown("---")
st.header("🎯 Propósito de la herramienta")

st.markdown("""
La aplicación busca **centralizar y simplificar** el acceso a información pública relacionada con:

- Indicadores económicos nacionales.  
- Condiciones salariales mínimas oficiales.  

Con esto se apoya:

- La investigación académica.  
- La toma de decisiones basada en datos.  
- La transparencia y comprensión de la información económica.  
- El uso de datos en proyectos de ciencia de datos, visualización y desarrollo de software.
""")

st.markdown("---")
st.header("📌 Fuentes oficiales")

st.markdown("""
Los datos utilizados provienen de:

- **Banco Central de Costa Rica (BCCR)**  
- **Ministerio de Trabajo y Seguridad Social (MTSS)**  

La aplicación se limita a consultar, organizar y visualizar la información disponible públicamente en estas fuentes.
""")

st.markdown("---")
st.header("🛠️ Tecnologías utilizadas")

st.markdown("""
- **Python**  
- **PostgreSQL**  
- **Airflow**  
- Bibliotecas de análisis y visualización de datos (como *pandas* y *matplotlib/plotly*)  
- Conexión a APIs o archivos públicos oficiales para obtener los datos.
""")

st.markdown("---")
st.markdown("""
📍 **Versión:** 1.0.0  
👨‍💻 **Desarrollado por:** *Laboratorio de Prospectiva, Innovación e Inteligencia Artificial*  
📆 **Última actualización:** *10/11/2025*
""")