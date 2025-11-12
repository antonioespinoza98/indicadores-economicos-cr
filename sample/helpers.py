# ----------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones complejas y/o específicas
# ----------------------------------------------------------------

import streamlit as st
import polars as pl 

# -- CLASE PARA CREAR CONEXION Y LUEGO TRAER LAS TABLAS DE LOS QUERIES
# PARAMETROS DE LA CLASE TIENEN QUE SER 

class postgresqlConn:
    """
    Clase que se encarga de crear la conexión con la base de datos y ejecutar los queries suministrados.
    
    ...

    Atributos
    ----------

    
    Métodos
    ----------

    postgresqlConn.query()
        Ejecuta el query suministrado
    """

    def __init__(self):
        self.conn = st.connection("postgresql",type="sql")

    def _read_sql(self, sql_path: str) -> str:
        """Lee el archivo SQL y retorna su contenido como texto"""    