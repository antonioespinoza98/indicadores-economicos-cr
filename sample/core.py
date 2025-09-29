# -------------------------------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones importantes que no tienen depedencias de proyecto
# -------------------------------------------------------------------------------------

import configparser
import requests
import os
from dotenv import load_dotenv
import polars
from sample.utils import TOKEN
class BccrAPI:
    """
    Clase que se encarga de la captura de datos económicos del Banco Central de Costa Rica (BCCR).

    ...

    Atributos
    ----------
    API : str
        Nombre de la API a utilizar

    Métodos
    ----------
    BccrAPI("BCCR").get()
        Extrae la tabla de indicadores económicos 
    """
    def __init__(self, API):
        """
        Parámetros
        ----------
        API : str
            Nombre de la API a utilizar
        """
        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + '/conf.ini')
        self.url = config.get(API, 'url')
        self.endpoint = config.get(API, 'endpoint')
        self.header = {"authorization": f"Bearer {TOKEN}",
                        "Content-Type": "application/json",
                          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                          }

    def get(self):
        """
        Envía una solicitud GET

        Raises
        ----------
        Error: 401
            Si la conexión con el API no pudo ser establecida. 
        """
        response = requests.get(self.url + self.endpoint, headers= self.header)
        if response.status_code == 200:
            print("Funcioné!")
        else: 
            print(f"Error: {response.status_code}")