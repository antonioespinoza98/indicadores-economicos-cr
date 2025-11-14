# ----------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones complejas y/o específicas
# ----------------------------------------------------------------

import streamlit as st
import polars as pl 
from sqlalchemy import create_engine
from sample.utils import logger
import os
from dotenv import load_dotenv
import base64

get_logger = logger("Helpers", "helpers.log")
class database_conn:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv("SQL_URL")
        self.engine = create_engine(
            url=self.url
        )
        self.alchemy_conn = self.engine.connect()

    @st.cache_data
    def load_indicadores(_self):
        # Only get the names you need, distinct and ordered
        q = """
            SELECT *
            FROM mart_sch.mrt_cuenta_ind
            ORDER BY indicador ASC;
        """
        # Convert directly to a Python list for the selectbox
        return pl.read_database(
            query=q,
            connection=_self.alchemy_conn).to_series()

    @st.cache_data
    def load_indicador_data(_self, raw_value: str):
        # raw_value example: "912 - Importaciones de servicios"

        # split into code and name
        code, name = raw_value.split(" - ", 1)

        # escape name
        name_safe = name.replace("'", "''")

        q = f"""
            SELECT *
            FROM curado_sch.mrt_indicadores_disp
            WHERE "Código de indicador" = '{code}'
            AND "Nombre de indicador" = '{name_safe}'
            ORDER BY "Fecha de emisión" DESC;
        """

        data = pl.read_database(
            query=q,
            connection=_self.alchemy_conn
        )
        return data


