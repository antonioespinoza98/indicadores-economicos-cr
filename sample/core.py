# -------------------------------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: funciones importantes que no tienen depedencias de proyecto
# -------------------------------------------------------------------------------------

import configparser
import requests
import os
from io import BytesIO
from sample.utils import logger
from pathlib import Path
from urllib.parse import urljoin
from typing import Any, Dict, Optional
import polars as pl
from datetime import datetime
from uuid import uuid4
import json
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

    KEYS = ("url", "token")

    def __init__(
            self,
            api_name: str,
            # Prueba de parametros
            indicador: str,
            fecha_inicio: str,
            fecha_final: str,  
            #-----------------------
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
        # ---- PARAMETROS NUEVOS
        self.indicador = indicador
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        # -----------------------
        self.session = session or requests.Session()

        # Cargar conf.ini
        config = configparser.ConfigParser(interpolation=None)
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
        # self.default_endpoint = config.get(api_name, "endpoint")
        # TRANSFORMACION DE LA FECHA ----------
        self.fecha_inicio= datetime.strptime(self.fecha_inicio, '%d/%m/%Y').date()
        self.fecha_final= datetime.strptime(self.fecha_final, '%d/%m/%Y').date()

        self.mes_inicio=self.fecha_inicio.strftime("%m")
        self.dia_inicio=self.fecha_inicio.strftime("%d")

        self.mes_final=self.fecha_final.strftime("%m")
        self.dia_final=self.fecha_final.strftime("%d")
        # -------------------------------------
        self.default_endpoint = f"SDDE/api/Bccr.GE.SDDE.Publico.Indicadores.API/indicadoresEconomicos/{self.indicador}/series?fechaInicio={self.fecha_inicio.year}%2F{self.mes_inicio}%2F{self.dia_inicio}&fechaFin={self.fecha_final.year}%2F{self.mes_final}%2F{self.dia_final}&idioma=es"
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
            "Accept": "application/json"

        }

        get_logger.info("Credenciales cargadas con éxito desde %s (sección [%s])", conf_path, api_name)

    def get(
            self,
            endpoint: Optional[str] = None,
            params: Optional[dict] = None,   # <- acepta dict real de requests
            timeout: Optional[float] = None
        ) -> Any:
        """
        Envía una solicitud GET y normaliza la respuesta a un DataFrame de series.
        Escribe a la DB solo si hay filas.
        """
        ep = (endpoint or self.default_endpoint)
        url = urljoin(self.base_url, ep)
        to = self.timeout if timeout is None else timeout

        get_logger.debug("GET %s params=%s", url, params)

        try:
            response = self.session.get(url, headers=self.headers, params=params, timeout=to)
            response.raise_for_status()
        except requests.Timeout as e:
            get_logger.error("Timeout al llamar %s: %s", url, e)
            raise
        except requests.RequestException as e:
            get_logger.error("Error de red al llamar %s: %s", url, e)
            raise

        # ---- Normalización del Content-Type (case-insensitive)
        ctype = (response.headers.get("Content-Type", "") or "").lower().split(";")[0].strip()
        get_logger.debug("Content-Type recibido: %s", ctype)

        # ---- Rama JSON
        if ctype == "application/json" or ctype.endswith("+json"):
            try:
                data = response.json()
            except ValueError as e:
                get_logger.error("No se pudo parsear JSON desde %s: %s", url, e)
                raise

            get_logger.debug("Respuesta JSON recibida correctamente. data=%s",
                            json.dumps(data, ensure_ascii=False))

            # Validaciones defensivas del contrato
            if not isinstance(data, dict):
                raise TypeError(f"Respuesta inesperada (no es dict): {type(data)}")

            if "datos" not in data:
                raise KeyError("La respuesta JSON no contiene la clave 'datos'")

            datos = data.get("datos")
            if not isinstance(datos, list):
                raise TypeError(f"'datos' no es una lista: {type(datos)}")

            # ---- Caso sin datos (tu log ya mostró este escenario)
            if len(datos) == 0:
                mensaje = data.get("mensaje") or "No existen datos para las fechas suministradas."
                get_logger.info("Sin datos para el rango solicitado: %s", mensaje)

                # Devuelve un DataFrame vacío con el mismo esquema esperado por tu pipeline
                empty_df = pl.DataFrame(
                    schema={
                        "fecha": pl.Date,
                        "valorDatoPorPeriodo": pl.Float64,
                        "codigo_indicador": pl.Utf8,
                        "nombre_indicador": pl.Utf8,
                        "ingestion_run_id": pl.Utf8,
                    }
                )
                return empty_df  # <- no intenta escribir a DB

            # ---- Hay datos: construimos indicador y series
            indicador = datos[0]
            series = indicador.get("series", [])
            if not isinstance(series, list):
                raise TypeError(f"'series' no es una lista: {type(series)}")

            # Validación mínima de columnas esperadas en cada serie
            # (si faltan, pl.DataFrame lanzará error; dejamos el error visible)
            df = pl.DataFrame(
                data=series,
                schema=["fecha", "valorDatoPorPeriodo"]
            ).with_columns([
                pl.lit(indicador.get("codigoIndicador")).alias("codigo_indicador"),
                pl.lit(indicador.get("nombreIndicador")).alias("nombre_indicador"),
            ])

            df = (
                df
                .with_columns([
                    pl.lit(str(uuid4())).alias("ingestion_run_id"),
                ])
                .with_columns([
                    pl.col("fecha").str.strptime(pl.Date, strict=False),
                    pl.col("valorDatoPorPeriodo").cast(pl.Float64),
                ])
            )

            # Escribimos solo si hay filas
            if df.height > 0:
                df.write_database(
                    table_name="bccr_sch.indicador_crudo",
                    connection="postgresql://mespinoza:mespinoza@127.0.0.1:5433/crudo_db",
                    if_table_exists='append',
                    engine='sqlalchemy'
                )
                get_logger.info("Escritura completada: %d filas en indicador_crudo", df.height)
            else:
                get_logger.info("DataFrame vacío tras normalización; no se escribe a DB.")

            return df  # devuelve el DF final (útil para pruebas / llamadas programáticas)

        # ---- Rama XLSX (por si el endpoint entrega Excel en vez de JSON)
        if ctype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            get_logger.warning("Contenido XLSX recibido; se intentará parsear el Excel.")
            # Nota: pl.read_excel acepta path; para bytes usamos BytesIO.
            try:
                df_xlsx = pl.read_excel(
                    source=BytesIO(response.content),
                    read_options={"header_row": 0}
                )
            except Exception as e:
                get_logger.error("No se pudo leer XLSX: %s", e)
                raise

            return df_xlsx  # lo devolvemos tal cual; si lo quieres normalizar, ajusta aquí

        # ---- Cualquier otro Content-Type es inesperado
        get_logger.error("Se esperaba JSON o XLSX y llegó: %s", ctype)
        raise ValueError(f"Contenido no soportado: {ctype}")
