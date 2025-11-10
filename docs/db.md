# Guía de la base de datos

## 

AGREGAR ACA QUE SON PRIMARY Y FOREIGN KEYS


## Esquema crudo

Cuando los datos se extraen por primera vez, estos son actualizados en la base de datos de `PostgreSQL`, que está almacenada en el servidor oficial de la CEPAL. 
En este esquema existen dos tablas; la primera tabla `indicador_crudo` donde se almacenan los valores de los indicadores en conjunto con otros metadatos que permiten un control granular de las extracciones de datos que se realizan. 

En este caso, la fecha que conecta a ambas tablan indican que la columna `foreign key` en una tabla es la columna `primary key` en la otra tabla. En este caso, la tabla `catalogo` contiene la columna `codigo` que contiene al código del indicador, mientras que para `indicador_crudo` esta columna le pertenece a `codigo_indicador`. 
El objetivo de crear esta linealidad es que permite unir ambas tablas de una manera sencilla y rápida. Esto forma parte de la estrategia de modelaje de bases de datos, que a su vez, facilitan la eficiencia cuando la base de datos se escala. 

![crudo_db.bccr_sch](./img/crudo_db%20-%20bccr_sch.png)

### Definición de las tablas

```sql
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
```

```sql
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
      or fecha_final >= fecha_inicio
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
```


## Esquema curado

El esquema `curado_sch` tiene una capa de complejidad extra debido a que en esta sección se crea una lineadad que permite conectar los procesos descriptivos del negocio en las tablas dimensionales `dim` y las tablas `facts` son hechos cuantificables. 
Estos siguen la misma lógica, las tablas dimensionales están conectadas a la tabla de hechos por medio de una llave que permite en la lógica de negocio, cruzar las tablas por medio de transformaciones que muestran los distintos procesos. 


![crudo_db.curado_sch](./img/crudo_db%20-%20curado_sch.png)


