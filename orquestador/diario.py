# -------------------------------------------------------------------------------------
#  Autor: Marco Espinoza — Consultor 
# Laboratorio de Prospectiva, Innovación e Inteligencia Artificial
# Fecha: 29-09-2025
# Descripción del archivo: Orquestador para la extracción de datos diarios
# -------------------------------------------------------------------------------------

import polars as pl
import uuid
from sample.core import BccrAPI 
from datetime import datetime
from sample.utils import logger
from sample.helpers import PostgreSQLconn
import time
from sample.core import BccrRateLimitError

get_logger=logger("orquestador","orquestador.log")

class dailyorchestrator:
    """
    Orquestador de la extracción de datos que se actualizan diario.

    ...
    Atributos
    ----------

    Métodos
    ----------

    """
    def __init__(self):
        self.conn = PostgreSQLconn()
        self.engine= self.conn.create_conn()


    def readData(self) -> pl.DataFrame:
        """
        Docstring for engine
        
        :param self: Description
        """
        # Leemos el archivo predeterminado para el query
        with open("./orquestador/sql/query.sql", "r") as f:
            query = f.read()

        # determinamos la cadencia, en este caso diaria
        cadence = "Diaria"

        # leemos el query y le damos el formato con la cadencia 
        query = query.format(CADENCE=cadence)

        # Extraemos la base de datos
        data = pl.read_database(query=query,
                                     connection=self.engine
                                     )

        return data

    def TidyJob(self):
        """
        Docstring for TidyJob
        
        :param self: Description
        """

        data = self.readData()

        # La siguiente transformación nos dice cuantos indicadores hay en lista que son diarios
        t_df = data.select(
            pl.col("codigo_indicador")
            .unique()
            .count()
            .alias("TotalIndicadores")
        )

        t = t_df.select(pl.col("TotalIndicadores")).item()
        get_logger.debug(f"En la lista existen: {t} indicadores con cadencia diaria por actualizarse.")

        ind_diarios = (
            data
            .with_columns(
                (pl.col("ultima_version") + pl.duration(days=1)).alias("fecha_inicio"), # Agregamos un dia a la fecha de inicio basado en la ultima version
                (pl.col("ultima_version") + pl.duration(weeks=12)).alias("fecha_final"), # Agregamos 12 semanas a esta misma fecha
                )
            .select(
                pl.col("codigo_indicador"),
                pl.col("fecha_inicio").dt.strftime("%d/%m/%Y"),
                pl.col("fecha_final").dt.strftime("%d/%m/%Y"),
            )
            .sort("codigo_indicador", descending=False)
            )
        
        return ind_diarios
    
    def run(self):
        """
        Docstring for run
        
        :param self: Description
        """

        data= self.TidyJob()

        # -- Proceso 2. 
        for row in data.iter_rows(named=True):
            indicador = row["codigo_indicador"]
            fecha_inicio = row["fecha_inicio"]   
            fecha_final = row["fecha_final"]     

            # print(indicador)
            # print(fecha_inicio)
            # print(fecha_final)

            try:
                # Llamada a la API
                result = BccrAPI(
                    api_name="BCCR-INDICADORES",
                    indicador=indicador,
                    fecha_inicio=fecha_inicio,
                    fecha_final=fecha_final,
                ).read_as_dataframe()

                # Aseguramos que sea un DataFrame de Polars
                df = pl.DataFrame(result)

                if df.is_empty():
                    print(f"Sin datos para {indicador}")
                    continue

                df = (
                    df.with_columns(
                        fuente_datos=pl.lit("api_bccr"),
                        ingestion_run_id=pl.lit(str(uuid.uuid4())),
                        extraccion_en=pl.lit(datetime.now()),
                        codigo_indicador=pl.lit(indicador),
                    )
                    .rename(
                        {
                            
                            "fecha": "fecha",
                            "valorDatoPorPeriodo": "valorDatoPorPeriodo",
                        }
                    )[
                        [
                            "fuente_datos",
                            "ingestion_run_id",
                            "extraccion_en",
                            "codigo_indicador",
                            "nombre_indicador",
                            "fecha",
                            "valorDatoPorPeriodo",
                        ]
                    ]
                )

                print(df)

            except BccrRateLimitError as e:
                get_logger.error("Rate limit agotado para %s: %s", indicador, e)
                time.sleep(60)
                continue

            except Exception as e:
                get_logger.error("Error con %s: %s", indicador, e)
            
            time.sleep(10)
