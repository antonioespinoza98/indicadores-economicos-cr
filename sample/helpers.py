# ----------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones complejas y/o específicas
# ----------------------------------------------------------------

# Llamamos las dependencias
import streamlit as st
import polars as pl 
from sqlalchemy import create_engine
from sample.utils import logger
import os
from dotenv import load_dotenv

# Creamos una sección para los logs
get_logger = logger("Helpers", "helpers.log")

class database_conn:
    """
    Clase que se encarga de la conexión con la base de datos de PostgreSQL en el servidor de CEPAL. 
    Utiliza las librerias de Polars para manejo de DataFrames, SQLAlchemy para la conexión con la base de datos
    y streamlit para el caché.
    
    ...
    
    Atributos
    ----------
    self

    Métodos
    ----------
    conn = database_conn()
    result= conn.load_indicador_data(selectbox)
    
    """
    def __init__(self):
        load_dotenv()

        self.url = os.getenv("SQL_URL")
        self.engine = create_engine(
            url=self.url
        )
        self.alchemy_conn = self.engine.connect()
        get_logger.debug("Credenciales cargados con éxito.")

    @st.cache_data
    def load_indicadores(_self):
        # Query para traer la lista de indicadores
        q = """
            SELECT *
            FROM mart_sch.mrt_cuenta_ind
            ORDER BY indicador ASC;
        """

        # Retorna automaticamente una base de datos de tipo Polars
        # Utilizamos una conexión con SQLAlchemy para mayor fluidez para traer los queries.
        try:
            get_logger.debug("Ejecutando query solicitado...")
            data=pl.read_database(
                query=q,
                connection=_self.alchemy_conn).to_series()
            get_logger.debug("Query ejecutado correctamente.")
        except Exception as err:
            get_logger.error(f"Error inesperado: {err=} {type(err)=}")
            raise
            
        return data


    @st.cache_data
    def load_indicador_data(_self, raw_value: str):
        """
        Consulta el query solicitado y lo convierte en un DataFrame de polars.

        ...
        Atributos
        ----------
        raw_value: str
            Valor que da el `st.selectbox( )` en formato `str`.
        """


        # Al nombre lo cortamos la linea del centro para luego hacer la consulta del query
        code, name = raw_value.split(" - ", 1)
        name_safe = name.replace("'", "''")

        # Query.
        q = f"""
            SELECT *
            FROM curado_sch.mrt_indicadores_disp
            WHERE "Código de indicador" = '{code}'
            AND "Nombre de indicador" = '{name_safe}'
            ORDER BY "Fecha de emisión" DESC;
        """
        try:
            get_logger.debug("Ejecutando query solicitado...")
            data = pl.read_database(
                query=q,
                connection=_self.alchemy_conn
            )
            get_logger.debug("Query ejecutado correctamente.")
        except Exception as err:
            get_logger.error(f"Error inesperado: {err=} {type(err)=}")
            raise

        return data
    
    @st.cache_data
    def load_lista_salarios(_self):

        q = """
            SELECT *
            FROM curado_sch.lista_salarios;
        """
        try:
            get_logger.debug("Ejecutando query solicitado...")
            data=pl.read_database(
                query=q,
                connection=_self.alchemy_conn)
            get_logger.debug("Query ejecutado correctamente.")
        except Exception as err:
            get_logger.error(f"Error inesperado: {err=} {type(err)=}")
            raise
 
        
        return data

class PostgreSQLconn:
    """
    Docstring for PostgreSQLconn
    """
    def __init__(self):        
        load_dotenv()

        self.url = os.getenv("SQL_URL")
        
    def create_conn(self):
        engine = create_engine(
            url=self.url
        )
        alchemy_conn = engine.connect()
        get_logger.debug("Credenciales cargados con éxito.")

        return alchemy_conn

