-- Creación de la tabla de fct
-- cuando se utiliza el reference es porque ese key es un foreign key que en la tabla referenciada es el primary key
-- esto permite juntar los queries de forma mas rapida y eficiente. 
create table if not exists curado_sch.fct_indicador(
	fact_id bigserial primary key, -- Aseguramos el primary key
	indicador_key bigint not null references curado_sch.dim_indicador(indicador_key),
	date_key integer not null references curado_sch.dim_fecha(date_key),
	valorind numeric(20,8),
	source_key bigint references curado_sch.dim_fuente(source_key),
	last_run_key integer not null references curado_sch.dim_run(run_key),
	row_loaded_at timestamptz not null default now(),
	constraint uq_fact_indicador_day unique(indicador_key, date_key)
);

create index if not exists ix_fact_indicator_date on curado_sch.fct_indicador(indicador_key, date_key);
create index if not exists ix_fact_date on curado_sch.fct_indicador(date_key);
