-- Primero nos aseguramos que estamos en la base de datos correcta
select current_database();

-- Creamos un schema para los datos crudos que llegan del API
create schema if not exists bccr_sch;

create table if not exists bccr_sch.indicador_crudo (
  crudo_id            bigserial primary key, 
  fuente_datos        text not null default 'api_bccr',
  ingestion_run_id    uuid not null,
  extraccion_en       timestamptz not null default now(),
  codigo_indicador    text not null,
  nombre_indicador    text,
  fecha               date not null,
  "valorDatoPorPeriodo"    numeric(20,8)
);


-- permite los merges y upserts para el fact table (filtrar por fechas y codigo de indicador)
create index if not exists ix_indicador_raw_code_fecha
	on bccr_sch.indicador_crudo (codigo_indicador, fecha);


-- lo mismo pero para el tiempo de llegada a la base, util para ver las ingestas por fecha

create index if not exists ix_indicador_raw_arrival
	on bccr_sch.indicador_crudo (ingestion_run_id);


-- CREAMOS la tabla de catalogo para luego crear las dimensiones y las facts

create table if not exists bccr_sch.catalogo (
  codigo        text primary key, 
  nombre        text,
  descripcion   text,
  indicador     text, 
  periodicidad  text,
  cuadro        bigint,
  titulocuadro  text,
  fecha_inicio  date,
  fecha_final   date,
  watermark     text,
  constraint chk_catalog_fechas -- para matener integridad de los datos, creamos un constraint para revisar los datos que ingresan
    check (
      fecha_final is null
      or fecha_inicio is null
      or fecha_final >= fecha_inicio -- Esto nos asegura que la fecha de inicio nunca es mayor que la fecha final (incongruencia)
    )
);


-- Al igual que en la tabla de indicadores, creamos indexes que nos permiten crear queries mas eficientes

create index if not exists ix_catalogo_codigo on bccr_sch.catalogo(codigo);
create index if not exists ix_catalogo_fecha_inicio on bccr_sch.catalogo(fecha_inicio);
create index if not exists ix_catalogo_fecha_final on bccr_sch.catalogo(fecha_final);

-- Una vez que los datos estan arriba, cambiamos la definicion de la tabla de indicadores para poder crear un Foreign Key que nos permitirá posteriormente crear las tablas de
-- dimensiones y facts

alter table bccr_sch.indicador_crudo
	add constraint fk_indicador_crudo_catalogo
	foreign key (codigo_indicador)
	references bccr_sch.catalogo(codigo)
	not valid;

-- hacemos una verificacion de los los keys

alter table bccr_sch.indicador_crudo
	validate constraint fk_indicador_crudo_catalogo;


















