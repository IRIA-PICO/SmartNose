"""Tests de src/drift_analysis.py (usan datos sintéticos: no necesitan descargar nada).

Responsable: Persona 2 (Lucía Díez).
Funciones públicas: ninguna (tests de pytest).
"""
import pytest

from src.contracts import DRIFT_COLUMNS, FEATURE_COLUMNS
from src.drift_analysis import evolucion_por_lote
from src.training import entrenar


def crear_config():
    config = {"modelo": "rf", "params": {}, "lotes_train": [1], "lotes_test": [2, 3]}
    return config


def sacar_accuracy(tabla, estrategia, lote):
    filtro = (tabla["estrategia"] == estrategia) & (tabla["lote"] == lote)
    return tabla.loc[filtro, "accuracy"].iloc[0]


def test_formato_de_la_tabla(datos_sinteticos):
    config = crear_config()
    tabla = evolucion_por_lote(datos_sinteticos, config)

    assert list(tabla.columns) == DRIFT_COLUMNS
    assert list(tabla["estrategia"]) == ["fijo", "fijo", "reentrenado", "reentrenado"]
    assert list(tabla["lote"]) == [2, 3, 2, 3]
    assert config == crear_config() #el config no se modifica


def test_el_fijo_coincide_con_entrenar(datos_sinteticos):
    tabla = evolucion_por_lote(datos_sinteticos, crear_config())
    config = crear_config()
    config["lotes_test"] = [3]
    _, metricas = entrenar(datos_sinteticos, config)

    assert sacar_accuracy(tabla, "fijo", 3) == metricas["accuracy"]


def test_reentrenar_recupera_cuando_los_datos_cambian(datos_sinteticos):
    datos = datos_sinteticos.copy()
    filtro = datos["batch"] >= 2
    datos.loc[filtro, FEATURE_COLUMNS] = datos.loc[filtro, FEATURE_COLUMNS] + 20 #deriva grande desde el lote 2
    tabla = evolucion_por_lote(datos, crear_config())

    #en el lote 2 las dos estrategias han entrenado con lo mismo
    assert sacar_accuracy(tabla, "fijo", 2) == sacar_accuracy(tabla, "reentrenado", 2)
    #en el lote 3 el reentrenado ya ha visto el lote 2
    assert sacar_accuracy(tabla, "fijo", 3) < 0.5
    assert sacar_accuracy(tabla, "reentrenado", 3) > 0.9


def test_rechaza_evaluar_en_el_pasado(datos_sinteticos):
    config = crear_config()
    config["lotes_train"] = [3]
    config["lotes_test"] = [2]
    with pytest.raises(ValueError, match="Fuga temporal"):
        evolucion_por_lote(datos_sinteticos, config)
