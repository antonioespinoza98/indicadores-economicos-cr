# -------------------------------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: Segunda página del Streamlit, indicadores
# -------------------------------------------------------------------------------------

# -- Primero se importan las dependencias
import streamlit as st 
import plotly.express as px
from sample.helpers import database_conn # -- Traemos esta clase que establece la conexión con la base de datos
import polars as pl
# --

# -- Cuerpo del código

#-- CONEXION BASE DE DATOS
conn = database_conn()

# Creamos dos tabs para cada uno de los indicadores
tab1, tab2 = st.tabs(["Indicadores - BCCR","Lista de Salarios - MTSS"])

with tab1:

    # -- Creamos un recuadro sobre la información que se presenta
    with st.container(border=True):
        # -- agregamos dos columnas, una para agregar el texto desc, y la otra para colocar la imagen del BCCR
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            Consulta indicadores oficiales del Banco Central de Costa Rica y analiza sus series históricas con visualizaciones interactivas para apoyar investigación y toma de decisiones.
                """)
        with col2:
            st.image("./docs/img/bccr.svg")

    # Cargamos la lista indicadores
    indicadores = conn.load_indicadores()

    st.header("Indicadores")
    # Creamos un select box para el input del usuario
    select_box = st.selectbox(
        "Seleccione un indicador para comenzar",
        options=indicadores,
    )
    # -- Filtramos la base de datos de acuerdo a la selección, esta forma es más sencilla
    # -- Ya que traer la tabla completa en un query no es muy eficiente

    mrt_indicadores_disp = conn.load_indicador_data(select_box)

    with st.container(border=True):
        tabla_desc = mrt_indicadores_disp.sort("Fecha de emisión", descending=True)

        # -- Algunas transformaciones utilizando la libreria de Polars
        result = (
            tabla_desc.select(
                pl.col("Nombre de indicador").first().alias("indicador"),
                pl.col("Fecha de emisión").min().alias("min_date"),
                pl.col("Fecha de emisión").max().alias("max_date"),
                pl.col("Periodicidad").first().alias("periodicidad")
                )
                ).to_dicts()[0]
        # -- Título dinámico del gráfico
        st.subheader(
            f"{result['indicador']}: Serie {result['periodicidad']} {result['min_date'].strftime('%d/%m/%Y')} — {result['max_date'].strftime('%d/%m/%Y')}"
        )
        st.markdown("Unidad de medida: Colón Costarricense")
        fig = px.line(
            tabla_desc.to_pandas(),
            x="Fecha de emisión",
            y="Valor de Indicador",
            markers=True
        )
        # Presentamos el grafico
        st.plotly_chart(fig, width='stretch')


    # Sección para la descarga de los datos
    st.subheader("Descargue los datos")
    with st.container(border=True):
        st.markdown("""
        Esta tabla muestra los metadatos correspondientes al indicador seleccionado. Puede descargarla haciendo clic en “Download as CSV” en la esquina superior derecha.
        """)
        st.dataframe(tabla_desc)

with tab2:
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown( """
                        En esta sección se presenta la lista oficial de salarios mínimos definidos por el Ministerio de Trabajo y Seguridad Social (MTSS). 
                        La información está organizada por tipo de empleo, su código correspondiente y el monto salarial asignado según la normativa vigente.
        """ )
        with col2:
            st.image("./docs/img/MTSS_logo.png")

        # Un menu desplegable que permite ver los detalles de la tabla de la lista de salarios
        with st.expander("Ver siglas y salarios mínimos"):
            st.markdown("""
            **TONC**  - Trabajador en Ocupación No Calificada - ₡12 236,95  
            **TOSC**  - Trabajador en Ocupación Semicalificada - ₡13 306,79  
            **TOC**   - Trabajador en Ocupación Calificada - ₡13 767,45  
            **TOE**   - Trabajador en Ocupación Especializada - ₡15 983,96  
            **TES**   - Trabajador de Especialización Superior - ₡24 805,47  
            **TONCG** - Trabajador en Ocupación No Calificada (Genérico) - ₡376 953,70  
            **TOSCG** - Trabajador en Ocupación Semicalificada (Genérico) - ₡399 203,69  
            **TOCG**  - Trabajador en Ocupación Calificada (Genérico) - ₡432 323,05  
            **TOEG**  - Trabajador en Ocupación Especializada (Genérico) - ₡476 086,67  
            **TMED**  - Técnico Medio en Educación Diversificada - ₡484 568,18  
            **TeDS**  - Técnico de Educación Superior - ₡533 802,13  
            **DES**   - Diplomado de Educación Superior - ₡576 094,24  
            **Bach.** - Bachiller Universitario - ₡704 864,91  
            **Lic.**  - Licenciado Universitario - ₡784 139,53  

            *Salario mínimo mensual.
            """)

    st.subheader("Descargue los datos")

    with st.container(border=True):
        
        lista_salarios = conn.load_lista_salarios()
        
        st.markdown("""
            Esta tabla muestra los metadatos correspondientes a la lista de salarios. Puede descargarla haciendo clic en “Download as CSV” en la esquina superior derecha.
            """)
        
        st.dataframe(lista_salarios) 