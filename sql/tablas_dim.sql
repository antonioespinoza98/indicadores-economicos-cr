-- Creacion de tablas dimensionales

create schema if not exists curado_sch;

create table curado_sch.dim_fecha(
	date_key integer primary key,
	fecha date not null unique
); 

create table curado_sch.dim_indicador(
	indicador_key bigserial primary key,
	codigo_indicador text not null,
	nombre_indicador text,
	descripcion_indicador text,
	indicador text,
	periodicidad text,
	cuadro text,
	titulocuadro text,
	valid_from date not null,
	valid_to date,
	is_current boolean not null default true,
	watermark text,
	hashdiff bytea,
	constraint uq__dim_indicator_version
	unique(codigo_indicador, valid_from)
);

create index if not exists ix_dim_indicator_codigo on curado_sch.dim_indicador(codigo_indicador);
create index if not exists ix_dim_indicator_current on curado_sch.dim_indicador(codigo_indicador, is_current);

create table curado_sch.dim_fuente(
	source_key bigserial primary key,
	fuente_datos text not null unique
);

create table curado_sch.dim_run(
	run_key bigserial primary key,
	ingestion_run_id uuid not null unique,
	extraccion_en timestamptz not null
);
