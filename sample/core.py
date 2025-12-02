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
from sample.helpers import PostgreSQLconn
from datetime import datetime
from uuid import uuid4
import json
import time

get_logger = logger("Core", "core.log")

class BccrRateLimitError(RuntimeError):
    """Se lanzó cuando se agotaron los reintentos por errores 429."""
    pass

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
    SESSION = requests.Session()

    BASE_URL: str | None = None
    TOKEN: str | None = None
    CONF_LOADED: bool = False

    def __init__(
            self,
            api_name: str,
            indicador: str,
            fecha_inicio: str,
            fecha_final: str,  
            conf_path: Optional[os.PathLike[str] | str] = None, 
            timeout: float = 20.0,
            session: Optional[requests.Session] = None,
        ) -> None:

        self.api_name = api_name
        self.timeout = timeout
        self.indicador = indicador
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.conn= PostgreSQLconn()
        self.engine=self.conn.create_conn()

        # Shared HTTP session
        self.session = session or BccrAPI.SESSION

        # ============= CONFIG CARGA UNA SOLA VEZ ===================
        if not hasattr(BccrAPI, "CONF_LOADED") or not BccrAPI.CONF_LOADED:

            config = configparser.ConfigParser(interpolation=None)

            # Path resolution
            if conf_path is None:
                conf_path = Path(__file__).resolve().parent / "conf.ini"
            else:
                conf_path = Path(conf_path)

            if not conf_path.exists():
                get_logger.error("No se encontró el archivo de configuración en %s", conf_path)
                raise RuntimeError(f"conf.ini no encontrado en {conf_path}")

            if not config.read(conf_path, encoding="utf-8"):
                raise RuntimeError(f"No se pudo leer el archivo de configuración: {conf_path}")

            if not config.has_section(api_name):
                raise KeyError(f"[{api_name}] no existe en {conf_path}")

            # Check missing keys
            missing = [k for k in self.KEYS if not config.has_option(api_name, k)]
            if missing:
                raise KeyError(f"Faltan claves {missing} en la sección [{api_name}] de {conf_path}")

            # Store credentials globally (cached)
            BccrAPI.BASE_URL = config.get(api_name, "url")
            BccrAPI.TOKEN = config.get(api_name, "token")
            BccrAPI.CONF_LOADED = True

            get_logger.info(
                "Credenciales cargadas con éxito desde %s (sección [%s])",
                conf_path, api_name
            )
        # =============================================================

        # Now assign reused values
        self.base_url = BccrAPI.BASE_URL
        self._token = BccrAPI.TOKEN

        # ========== DATE & ENDPOINT PROCESSING ==========
        self.fecha_inicio = datetime.strptime(self.fecha_inicio, '%d/%m/%Y').date()
        self.fecha_final = datetime.strptime(self.fecha_final, '%d/%m/%Y').date()

        self.mes_inicio = self.fecha_inicio.strftime("%m")
        self.dia_inicio = self.fecha_inicio.strftime("%d")
        self.mes_final = self.fecha_final.strftime("%m")
        self.dia_final = self.fecha_final.strftime("%d")

        self.default_endpoint = (
            f"SDDE/api/Bccr.GE.SDDE.Publico.Indicadores.API/indicadoresEconomicos/"
            f"{self.indicador}/series?fechaInicio={self.fecha_inicio.year}%2F{self.mes_inicio}%2F{self.dia_inicio}"
            f"&fechaFin={self.fecha_final.year}%2F{self.mes_final}%2F{self.dia_final}&idioma=es"
        )

        # Headers reuse the cached token
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

    def _request_with_backoff(
        self,
        url,
        params=None,
        timeout=None,
        max_retries: int = 3,         # menos reintentos
        base_delay: float = 20.0,     # esperas más largas
    ):
        to = self.timeout if timeout is None else timeout
        last_status = None

        for attempt in range(1, max_retries + 1):
            try:
                resp = self.session.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=to,
                )

                # --- Manejo específico de 429
                if resp.status_code == 429:
                    last_status = 429

                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait = float(retry_after)
                        except ValueError:
                            wait = base_delay
                    else:
                        wait = base_delay

                    get_logger.warning(
                        "429 Too Many Requests al llamar %s. Intento %s/%s. "
                        "Esperando %.1f segundos antes de reintentar.",
                        url, attempt, max_retries, wait,
                    )
                    time.sleep(wait)
                    continue  # intenta de nuevo

                # Si no es 429, deja que raise_for_status maneje otros errores HTTP
                resp.raise_for_status()
                return resp

            except requests.Timeout as e:
                get_logger.error("Timeout al llamar %s: %s", url, e)
                if attempt == max_retries:
                    raise
                wait = base_delay
                get_logger.warning(
                    "Reintentando tras timeout. Intento %s/%s. Esperando %.1f segundos.",
                    attempt, max_retries, wait,
                )
                time.sleep(wait)

            except requests.RequestException as e:
                get_logger.error("Error de red al llamar %s: %s", url, e)
                # Para otros errores de red, no tiene sentido reintentar infinito
                raise

        # Si salimos del bucle porque se agotaron los reintentos:
        if last_status == 429:
            raise BccrRateLimitError(f"Máximo de reintentos alcanzado para {url}")
        else:
            raise RuntimeError(f"Máximo de reintentos alcanzado para {url}")


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
        ep = endpoint or self.default_endpoint
        url = urljoin(self.base_url, ep)
        to = self.timeout if timeout is None else timeout

        get_logger.debug("GET %s params=%s", url, params)

        # Ahora toda la lógica de reintentos / 429 / timeout vive en _request_with_backoff
        response = self._request_with_backoff(url=url, params=params, timeout=to)

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

            get_logger.debug(
                "Respuesta JSON recibida correctamente. data=%s",
                json.dumps(data, ensure_ascii=False)
            )

            # Validaciones defensivas del contrato
            if not isinstance(data, dict):
                raise TypeError(f"Respuesta inesperada (no es dict): {type(data)}")

            if "datos" not in data:
                raise KeyError("La respuesta JSON no contiene la clave 'datos'")

            datos = data.get("datos")
            if not isinstance(datos, list):
                raise TypeError(f"'datos' no es una lista: {type(datos)}")

            # ---- Caso sin datos
            if len(datos) == 0:
                mensaje = data.get("mensaje") or "No existen datos para las fechas suministradas."
                get_logger.info("Sin datos para el rango solicitado: %s", mensaje)

                empty_df = pl.DataFrame(
                    schema={
                        "fecha": pl.Date,
                        "valorDatoPorPeriodo": pl.Float64,
                        "codigo_indicador": pl.Utf8,
                        "nombre_indicador": pl.Utf8,
                        "ingestion_run_id": pl.Utf8,
                    }
                )
                return empty_df  # no escribe a DB

            # ---- Hay datos: construimos indicador y series
            indicador = datos[0]
            series = indicador.get("series", [])
            if not isinstance(series, list):
                raise TypeError(f"'series' no es una lista: {type(series)}")

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
                    connection=self.engine,
                    if_table_exists='append'
                    # engine='sqlalchemy'
                )
                get_logger.info("Escritura completada: %d filas en indicador_crudo", df.height)
            else:
                get_logger.info("DataFrame vacío tras normalización; no se escribe a DB.")

            return df

        # ---- Rama XLSX (por si el endpoint entrega Excel en vez de JSON)
        if ctype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            get_logger.warning("Contenido XLSX recibido; se intentará parsear el Excel.")
            try:
                df_xlsx = pl.read_excel(
                    source=BytesIO(response.content),
                    read_options={"header_row": 0}
                )
            except Exception as e:
                get_logger.error("No se pudo leer XLSX: %s", e)
                raise

            return df_xlsx

        # ---- Cualquier otro Content-Type es inesperado
        get_logger.error("Se esperaba JSON o XLSX y llegó: %s", ctype)
        raise ValueError(f"Contenido no soportado: {ctype}")

    def read_as_dataframe(
        self,
        endpoint: Optional[str] = None,
        params: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> pl.DataFrame:

        ep = endpoint or self.default_endpoint
        url = urljoin(self.base_url, ep)
        to = self.timeout if timeout is None else timeout

        get_logger.debug("GET %s params=%s", url, params)

        # ---- Use backoff retry wrapper
        response = self._request_with_backoff(url=url, params=params, timeout=to)

        # ---- Normalize content type
        ctype = (response.headers.get("Content-Type", "") or "").lower().split(";")[0].strip()
        get_logger.debug("Content-Type recibido: %s", ctype)

        # ---- JSON response branch
        if ctype == "application/json" or ctype.endswith("+json"):
            try:
                data = response.json()
            except ValueError as e:
                get_logger.error("No se pudo parsear JSON desde %s: %s", url, e)
                raise

            get_logger.debug("Respuesta JSON recibida correctamente. data=%s",
                            json.dumps(data, ensure_ascii=False))

            if not isinstance(data, dict):
                raise TypeError(f"Respuesta inesperada (no es dict): {type(data)}")

            if "datos" not in data:
                raise KeyError("La respuesta JSON no contiene la clave 'datos'")

            datos = data.get("datos")
            if not isinstance(datos, list):
                raise TypeError(f"'datos' no es una lista: {type(datos)}")

            # ---- No data condition
            if len(datos) == 0:
                mensaje = data.get("mensaje") or "No existen datos para las fechas suministradas."
                get_logger.info("Sin datos para el rango solicitado: %s", mensaje)

                return pl.DataFrame(
                    schema={
                        "fecha": pl.Date,
                        "valorDatoPorPeriodo": pl.Float64,
                        "codigo_indicador": pl.Utf8,
                        "nombre_indicador": pl.Utf8,
                    }
                )

            # ---- Build standard DataFrame
            indicador = datos[0]
            series = indicador.get("series", [])

            df = (
                pl.DataFrame(series, schema=["fecha", "valorDatoPorPeriodo"])
                .with_columns([
                    pl.lit(indicador.get("codigoIndicador")).alias("codigo_indicador"),
                    pl.lit(indicador.get("nombreIndicador")).alias("nombre_indicador"),
                    pl.col("fecha").str.strptime(pl.Date, strict=False),
                    pl.col("valorDatoPorPeriodo").cast(pl.Float64),
                ])
            )

            return df

        # ---- XLSX fallback
        if ctype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            get_logger.warning("Contenido XLSX recibido; intentando parsear Excel.")

            try:
                return pl.read_excel(BytesIO(response.content))
            except Exception as e:
                get_logger.error("No se pudo leer XLSX: %s", e)
                raise

        # ---- Unexpected format
        get_logger.error("Se esperaba JSON o XLSX y llegó: %s", ctype)
        raise ValueError(f"Contenido no soportado: {ctype}")


