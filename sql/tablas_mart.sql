-- EJEMPLO de como ser verian las tablas mart. Que son las que ejecutan las transformaciones y permiten
-- el cruce de información

-- Creamos un schema
create schema if not exists mart_sch;

-- Creamos la tabla
create table if not exists mart_sch.m_balanzapagostrim (
	"Año" date,
	"SumaAnual" bigint
);

-- Creamos un CTE con los datos que necesitamos
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







