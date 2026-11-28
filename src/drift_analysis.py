"""Análisis de la deriva temporal.

Responsable: Persona 2 (Lucía Díez).
Funciones públicas: evolucion_por_lote(datos, config).
"""
import pandas as pd

from src.contracts import DRIFT_COLUMNS
from src.evaluation import calcular_metricas
from src.preprocessing import separar_xy
from src.training import entrenar


def evolucion_por_lote(datos, config):
    """Devuelve una tabla (DataFrame) con las columnas de contracts.DRIFT_COLUMNS.

    config es el mismo dict que en entrenar(). Hay una fila por estrategia y por
    cada lote de lotes_test:
        "fijo": se entrena una vez con lotes_train y se evalúa lote a lote.
        "reentrenado": antes de cada lote se vuelve a entrenar con lotes_train y
        todos los lotes intermedios anteriores a ese lote.
    El reentrenado supone que ya se conoce el gas real de los lotes anteriores.
    El macro-F1 de cada lote usa solo los gases presentes en ese lote.
    """
    lotes_train = config["lotes_train"]
    lotes_test = sorted(config["lotes_test"])
    filas = []

    pipeline_fijo, _ = entrenar(datos, config) #se entrena una sola vez

    for lote in lotes_test:
        datos_lote = datos[datos["batch"] == lote]
        X, y = separar_xy(datos_lote)
        y_pred = pipeline_fijo.predict(X)
        metricas = calcular_metricas(y, y_pred)
        fila = ["fijo", lote, metricas["accuracy"], metricas["macro_f1"]]
        filas.append(fila)

    for lote in lotes_test:
        lotes_anteriores = list(lotes_train) #copia para no cambiar el config original
        for otro_lote in sorted(datos["batch"].unique().tolist()):
            if otro_lote > max(lotes_train) and otro_lote < lote: #solo lotes anteriores al que se evalua
                lotes_anteriores.append(otro_lote)

        config_lote = {
            "modelo": config["modelo"],
            "params": config["params"],
            "lotes_train": lotes_anteriores,
            "lotes_test": [lote],
        }
        _, metricas = entrenar(datos, config_lote)
        fila = ["reentrenado", lote, metricas["accuracy"], metricas["macro_f1"]]
        filas.append(fila)

    tabla = pd.DataFrame(filas, columns=DRIFT_COLUMNS)
    return tabla
