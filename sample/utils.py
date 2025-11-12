# ----------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones simples o/y genéricas
# ----------------------------------------------------------------

# Función para realizar logs
import logging

def logger(filename: str, log_file: str) -> logging.Logger:
    
    logger = logging.getLogger(filename)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler =logging.FileHandler(log_file, encoding= 'utf-8')
        file_handler.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger