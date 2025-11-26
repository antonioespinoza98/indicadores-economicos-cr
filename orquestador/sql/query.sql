with cte as (select 
	df.date_key,
	di.indicador_key,
	dr.run_key,
	dr.ingestion_run_id,
	di.codigo_indicador,
	di.nombre_indicador,
	di.titulocuadro,
	di.cuadro,
	di.descripcion_indicador, 
	di.periodicidad,
	df.fecha
from curado_sch.fct_indicador fi 
left join curado_sch.dim_fecha df 
	on fi.date_key = df.date_key
left join curado_sch.dim_run dr 
	on fi.last_run_key = dr.run_key 
left join curado_sch.dim_indicador di 
	on fi.indicador_key = di.indicador_key
where di.periodicidad = '{CADENCE}'
)select 
	distinct codigo_indicador,
	nombre_indicador,
	cuadro,
	titulocuadro,
	max(fecha) as ultima_version
from cte
group by codigo_indicador, nombre_indicador, cuadro, titulocuadro

