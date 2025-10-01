# -------------------------------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones importantes que no tienen depedencias de proyecto
# -------------------------------------------------------------------------------------

import configparser
import requests
import os
from sample.utils import logger
from pathlib import Path
from urllib.parse import urljoin
from typing import Any, Dict, Optional
import polars as pl
get_logger = logger("Core", "core.log")
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

    KEYS = ("url", "endpoint", "token")

    def __init__(
            self,
            api_name: str,
            conf_path: Optional[os.PathLike[str] | str] = None, 
            timeout: float = 20.0,
            session: Optional[requests.Session] = None,
            ) -> None:
        """
        Parámetros
        ----------
        API : str
            Nombre de la API a utilizar
        """
        self.api_name = api_name
        self.timeout = timeout
        self.session = session or requests.Session()

        # Cargar conf.ini
        config = configparser.ConfigParser()
        if conf_path is None: # Busca un archivo estándar llamado conf.ini
            conf_path = Path(__file__).resolve().parent / "conf.ini"
        else:
            # En otro caso, abre el archivo con el nombre especificado
            conf_path = Path(conf_path)
        
        if not conf_path.exists():
            # En caso de no encontrarse el archivo, devuelve un Error y lo agrega al archivo core.log
            get_logger.error("No se encontró el archivo de configuración en %s", conf_path)
            raise RuntimeError(f"conf.ini no encontrado en {conf_path}")
        
        # Se lee el archivo 
        read_files = config.read(conf_path, encoding= "utf-8")

        # Si no se lee el archivo, levanta un error de Runtime. 
        if not read_files:
            raise RuntimeError(f"No se pudo leer el archivo de configuración: {conf_path}")
        
        if not config.has_section(api_name):
            raise KeyError(f"[{api_name}] no existe en {conf_path}")

        # Validar las claves requeridas: Nos permite asegurarnos que tenga el contenido necesario para establecer la conexión
        keys_faltantes = [k for k in self.KEYS if not config.has_option(api_name, k)]
        if keys_faltantes:
            raise KeyError(f"Faltan claves {keys_faltantes} en la sección [{api_name}] de {conf_path}")
        
        # Una vez cargados, asignamos los atributos al self para poder llamarlos en las funciones

        self.base_url = config.get(api_name, "url")
        self.default_endpoint = config.get(api_name, "endpoint")
        self._token = config.get(api_name, "token")

        # Encabezados

        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),

        }

        get_logger.info("Credenciales cargadas con éxito desde %s (sección [%s])", conf_path, api_name)

    def get(
            self,
            endpoint: Optional[str] = None,
            params: Optional[str] = None,
            timeout: Optional[float] = None
            ) -> Any:
        
        """
        Envía una solicitud GET

        Raises
        ----------
        requests.HTTPError
            Si la respuesta no es 200.
        requests.RequestException
            Para errores de red/timeout
        ValueError
            Si el cuerpo no es JSON y se requiere JSON
        """
        # cargamos el endpoint manual
        ep = (endpoint or self.default_endpoint)
        # Juntamos los url con el endpoint
        url = urljoin(self.base_url, ep)
        # determinamos el timeout
        to = self.timeout if timeout is None else timeout

        get_logger.debug("GET %s params=%s", url, params)

        try:
            # hacemos la llamada mediante el GET
            response = self.session.get(url, headers= self.headers, params= params, timeout=to)
            response.raise_for_status()
        except requests.Timeout as e:
            get_logger.error("Timeout al llamar %s: %s", url, e)
            raise
        except requests.RequestException as e:
            get_logger.error("Error de red al llamar %s: %s", url, e)
            raise
        
        # Intentar json
        ctype = response.headers.get("Content-Type","")
        if "application/json" in ctype.lower():
            try:
                data = response.json()
            except ValueError as e:
                get_logger.error("No se pudo parsear JSON desde %s: %s", url, e)
                raise
            get_logger.debug("Respuesta JSON recibida correctamente.")
            return data
        get_logger.warning("Contenido no JSON recibido (%s)", ctype)
        return pl.read_excel(response.content, read_options={"header_row": 1})