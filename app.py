import streamlit as st
import polars as pl

st.set_page_config(layout="wide")

conn = st.connection("postgresql", type="sql")

dim_fecha_qr = conn.query('SELECT * FROM curado_sch.dim_fecha;', ttl="10m")
fct_indicador_qr = conn.query('SELECT * FROM curado_sch.fct_indicador;', ttl="10m")
mart_balanza = conn.query('SELECT * FROM mart_sch.m_balanzapagostrim;', ttl="10m")
# INDICADORES
dim_indicador_qr = conn.query('SELECT indicador_key,nombre_indicador,descripcion_indicador,periodicidad FROM curado_sch.dim_indicador;', ttl="10m")



dim_fecha = pl.DataFrame(dim_fecha_qr)
fct_indicador = pl.DataFrame(fct_indicador_qr)
dim_indicador = pl.DataFrame(dim_indicador_qr)

#1era transformacion
desc_ind = dim_indicador.join(fct_indicador, how="inner", on="indicador_key")

desc_ind = desc_ind.filter(
    pl.col("nombre_indicador").is_in(["Bienes y servicios",
                                        "Ingreso primario",
                                        "Ingreso secundario"])
                                        )

# 2da transformacion
BalanzaDePagosTrim = fct_indicador.join(dim_fecha, how="left", on="date_key")

BalanzaDePagosTrim =(
    BalanzaDePagosTrim
    .group_by(["fecha"])
    .agg(
        pl.col("valorind").sum().alias("SumaXTrimestre")
    )
)




st.title("Indicadores Económicos")

st.selectbox(
    "Seleccione una tabla para visualizar",
    ("Balance de la cuenta corriente")
)

st.header("Indicadores utilizados")
st.subheader("Descripción de los indicadores utilizados")
with st.container(border=True):
    st.dataframe(desc_ind)
    st.subheader("Código ejecutado")
    col5,col6 = st.columns(2)
    with col5:
        st.code(body= """
desc_ind = dim_indicador.join(fct_indicador, how="inner", on="indicador_key")

desc_ind = desc_ind.filter(
    pl.col("nombre_indicador").is_in(["Bienes y servicios",
                                        "Ingreso primario",
                                        "Ingreso secundario"])
                                        )
""", language="python"
            )
    with col6:
        st.code(
            body= """
select
	fct.indicador_key,
	fct.valorind,
	dim.indicador_key,
	dim.nombre_indicador,
	dim.descripcion_indicador,
	dim.periodicidad
from fct_indicador fct
left join dim_indicador dim
	on fct.indicador_key = dim.indicador_key;
""", language="sql"
        )


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
