import streamlit as st
import polars as pl
import plotly.express as px
st.set_page_config(layout="wide")


# --- CONEXION CON LA BASE DE DATOS ---
conn = st.connection("postgresql", type="sql")



q= 'SELECT * FROM curado_sch.mrt_cuenta_ind;'
q1= 'SELECT * FROM curado_sch.mrt_indicadores_disp;'


mrt_indicadores_disp= conn.query(q, ttl='10m')
mrt_cuenta_ind= conn.query(q1, ttl='10m')

mrt_indicadores_disp = pl.DataFrame(mrt_indicadores_disp)
mrt_cuenta_ind=pl.DataFrame(mrt_cuenta_ind)
# ---
st.title("Indicadores Económicos")

select_box=st.selectbox(
    "Seleccione una tabla para visualizar",
    options=mrt_indicadores_disp
)

st.header("Indicadores utilizados")
st.subheader("Descripción de los indicadores utilizados")
with st.container(border=True):
    tabla_desc = (
        mrt_cuenta_ind.filter(pl.col("Nombre de indicador") == select_box).sort("Fecha de emisión", descending=True)
    )
    st.header("Gráficos")
    st.header("valor del indicador")
    fig = px.line(
        tabla_desc,
        x= "Fecha de emisión",
        y="Valor de Indicador"
    )

    st.plotly_chart(fig)



    st.subheader("Descargue los datos")
    st.dataframe(tabla_desc)



st.header("Balance de la cuenta corriente: Suma de los indicadores por trimestre")

# with st.container(border=True):
#     st.dataframe(BalanzaDePagosTrim)

st.header("balance de la cuenta corriente: Sumo Anual para el año 2016")

# with st.container(border=True):
#     st.dataframe(mart_balanza)
