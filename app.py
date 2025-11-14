import streamlit as st
import plotly.express as px
from sample.helpers import database_conn

st.set_page_config(layout="wide")


#-- CONEXION BASE DE DATOS
conn = database_conn()


indicadores = conn.load_indicadores()

select_box = st.selectbox(
    "Seleccione una tabla para visualizar",
    options=indicadores,
)

mrt_indicadores_disp = conn.load_indicador_data(select_box)

st.header("Indicadores utilizados")
st.subheader("Descripción de los indicadores utilizados")

with st.container(border=True):
    # Already sorted in SQL, but sort again if you want to be extra sure
    tabla_desc = mrt_indicadores_disp.sort("Fecha de emisión", descending=True)

    st.header("Gráficos")
    st.subheader("Valor del indicador")

    # Plotly is happier with pandas:
    fig = px.line(
        tabla_desc.to_pandas(),
        x="Fecha de emisión",
        y="Valor de Indicador",
        title=select_box,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Descargue los datos")
    st.dataframe(tabla_desc)
