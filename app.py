import streamlit as st
import polars as pl
import plotly.express as px
st.set_page_config(layout="wide")


# --- CONEXION CON LA BASE DE DATOS ---
conn = st.connection("postgresql", type="sql")

# TABLAS DIMENSIONALES Y DE HECHOS
dim_fecha_qr = conn.query('SELECT * FROM curado_sch.dim_fecha;', ttl="10m")
fct_indicador_qr = conn.query('SELECT * FROM curado_sch.fct_indicador;', ttl="10m")
mart_balanza = conn.query('SELECT * FROM mart_sch.m_balanzapagostrim;', ttl="10m")

# INDICADORES
dim_indicador_qr = conn.query('SELECT indicador_key,nombre_indicador,descripcion_indicador,periodicidad FROM curado_sch.dim_indicador;', ttl="10m")
# --- FIN --- 


# --- TRANSFORMACIONES ---
dim_fecha = pl.DataFrame(dim_fecha_qr)
fct_indicador = pl.DataFrame(fct_indicador_qr)
dim_indicador = pl.DataFrame(dim_indicador_qr)

# 2da transformacion
BalanzaDePagosTrim = fct_indicador.join(dim_fecha, how="left", on="date_key")

BalanzaDePagosTrim =(
    BalanzaDePagosTrim
    .group_by(["fecha"])
    .agg(
        pl.col("valorind").sum().alias("SumaXTrimestre")
    )
)



q1= "SELECT * FROM curado_sch.mrt_indicadores_disp"
uri = "postgresql://mespinoza:mespinoza@127.0.0.1:5433/crudo_db"

mrt_indicadores_disp= pl.read_database_uri(query=q1, uri=uri, engine='connectorx')

# ---- NUEVOS QUERIES

q= "SELECT * FROM curado_sch.mrt_cuenta_ind"
mrt_cuenta_ind= pl.read_database_uri(query=q, uri=uri, engine='connectorx').to_series()

# ---
st.title("Indicadores Económicos")

select_box=st.selectbox(
    "Seleccione una tabla para visualizar",
    options=mrt_cuenta_ind
)

st.header("Indicadores utilizados")
st.subheader("Descripción de los indicadores utilizados")
with st.container(border=True):
    tabla_desc = (
        mrt_indicadores_disp.filter(pl.col("Nombre de indicador") == select_box).sort("Fecha de emisión", descending=True)
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

with st.container(border=True):
    st.dataframe(BalanzaDePagosTrim)
    st.subheader("Código ejecutado")
    col1, col2 = st.columns(2)

    with col1:
        st.code(body= """
    BalanzaDePagosTrim = fct_indicador.join(dim_fecha, how="left", on="date_key")
    BalanzaDePagosTrim =(
        BalanzaDePagosTrim
        .group_by(["fecha"])
        .agg(
            pl.col("valorind").sum().alias("SumaXTrimestre")
        )
    )   
                """,
                language="python"
                    )
    with col2:
        st.code(body="""
    select
        d.fecha,
        sum(f.valorind) as "SumaXTrimestre"
    from curado_sch.fct_indicador as f
    left join curado_sch.dim_fecha as d
        on f.date_key = d.date_key
    group by d.fecha
    order by d.fecha;
                """,
                language="sql"
                    )

st.header("balance de la cuenta corriente: Sumo Anual para el año 2016")
with st.container(border=True):
    st.dataframe(mart_balanza)
    st.subheader("Código ejecutado")
    col3, col4 = st.columns(2)

    with col3:
        st.code(body= """
    BalanzaDePagosTrim = BalanzaDePagosTrim.with_columns(
        pl.col("fecha").dt.year().alias("Año")   
    ).group_by("Año").agg(
        pl.col("SumaXTrimestre").sum().alias("SumaAnual")
    )
                """,
                language="python"
                    )
    with col4:
        st.code(body="""
with balanza_cte as(
	select
	  d.fecha,
	  sum(f.valorind) as "SumaXTrimestre"
	from curado_sch.fct_indicador as f
	left join curado_sch.dim_fecha as d
	  on f.date_key = d.date_key
	group by d.fecha
	order by d.fecha
)
select 
	extract(year from fecha)::int as "Año",
	sum("SumaXTrimestre") as "SumaAnual"
from balanza_cte
group by "Año";
                """,
                language="sql"
                    )
