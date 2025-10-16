# ----------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones complejas y/o específicas
# ----------------------------------------------------------------

import polars as pl
import pandera.polars as pa

data = pl.read_excel("report.xlsx", columns=[0,7,8,9])

schema = pa.DataFrameSchema({
    "codigo": pa.Column(str),
    "fecha_inicio": pa.Column(str),
    "fecha_final": pa.Column(str),
    "watermark": pa.Column(str)
})

try:
    validated_data = schema.validate(data)
    print("Validación exitosa")
except pa.errors.SchemaError as e:
    print(f"Validación fallida: {e}")