# ----------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones simples o/y genéricas
# ----------------------------------------------------------------

# --- Exportar la variable de entorno para el API
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

