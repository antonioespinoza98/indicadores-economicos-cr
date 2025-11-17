-- Creamos un CTE
-- dim_fecha
with dim_date_cte as (
	select
		fecha
	from bccr_sch.indicador_crudo
)

insert into curado_sch.dim_fecha(
	date_key, fecha
)
select
	to_char(fecha, 'YYYYMMDD')::int,
	fecha
from dim_date_cte
on conflict (date_key) do nothing;

-- dim_fuente

insert into curado_sch.dim_fuente (fuente_datos)
select distinct fuente_datos
from bccr_sch.indicador_crudo
on conflict (fuente_datos) do nothing;

-- dim_run

with runs as(
	select ingestion_run_id, min(extraccion_en) as extraccion_en
	from bccr_sch.indicador_crudo
	group by ingestion_run_id 
)
insert into curado_sch.dim_run(ingestion_run_id, extraccion_en)
select ingestion_run_id, extraccion_en
from runs
on conflict (ingestion_run_id) do nothing;

-- dim_indicador

do $$
declare
 load_ts timestamptz := clock_timestamp();
begin
	create temporary table if not exists tmp_catalogo_snapshot on commit drop as 
		select
			c.codigo,
			c.nombre,
			c.descripcion,
			c.indicador,
			c.periodicidad,
			c.cuadro,
			c.titulocuadro,
			c.watermark,
			decode(md5(coalesce(c.nombre, '') ||'|'|| coalesce(c.codigo)),'hex') as hashdiff
		from bccr_sch.catalogo c;
		create index on tmp_catalogo_snapshot(codigo);
		insert into curado_sch.dim_indicador(
		codigo_indicador, nombre_indicador, descripcion_indicador, indicador,
		periodicidad, cuadro, titulocuadro, valid_from, valid_to, is_current, watermark, hashdiff
		)
		select
			s.codigo, s.nombre, s.descripcion, s.indicador, s.periodicidad, s.cuadro, s.titulocuadro,
			load_ts, null, true, s.watermark, s.hashdiff
		from tmp_catalogo_snapshot s 
		left join curado_sch.dim_indicador d 
			on d.codigo_indicador = s.codigo and d.is_current = true 
		where d.codigo_indicador is null;
		update curado_sch.dim_indicador d
		set valid_to = load_ts - interval '1 microsecond',
			is_current = false 
		from tmp_catalogo_snapshot s 
		where d.codigo_indicador = s.codigo 
			and d.is_current = true 
			and (d.hashdiff is distinct from s.hashdiff);
		insert into curado_sch.dim_indicador(
		codigo_indicador, nombre_indicador, descripcion_indicador, indicador,
		periodicidad, cuadro, titulocuadro, valid_from, valid_to, is_current, watermark, hashdiff
		)
		select
			s.codigo, s.nombre, s.descripcion, s.indicador, s.periodicidad, s.cuadro, s.titulocuadro,
			load_ts, null, true, s.watermark, s.hashdiff
		from tmp_catalogo_snapshot s 
		join curado_sch.dim_indicador d
			on d.codigo_indicador = s.codigo
			and d.valid_to = load_ts - interval '1 microsecond'
		where d.is_current = false;
end$$;

-- fct table
with ultimo_por_dia_cte as (
	select 
		ic.codigo_indicador,
		ic.fecha,
		ic."valorDatoPorPeriodo",
		ic.fuente_datos,
		ic.ingestion_run_id,
		ic.extraccion_en,
		row_number() over(
			partition by ic.codigo_indicador, ic.fecha
			order by ic.extraccion_en desc
		) as rn
	from bccr_sch.indicador_crudo ic
),
resuelto_cte as (
	select
		di.indicador_key,
		to_char(l.fecha, 'YYYYMMDD')::int date_key,
		l."valorDatoPorPeriodo" as valor_indicador,
		ds.source_key,
		dr.run_key
	from ultimo_por_dia_cte l
	join curado_sch.dim_indicador di
		on di.codigo_indicador = l.codigo_indicador and di.is_current = true 
	join curado_sch.dim_fuente ds
		on ds.fuente_datos = l.fuente_datos
	join curado_sch.dim_run dr 
		on dr.ingestion_run_id  = l.ingestion_run_id 
	where l.rn = 1
)
insert into curado_sch.fct_indicador (
	indicador_key, date_key, valorind, source_key, last_run_key
)
select indicador_key, date_key, valor_indicador, source_key, run_key
from resuelto_cte
on conflict (indicador_key, date_key) do update 
set valorind = excluded.valorind,
	last_run_key = excluded.last_run_key,
	row_loaded_at = now();

 











