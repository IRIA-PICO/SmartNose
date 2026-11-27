"""Datos de mentira con la misma estructura que la tabla limpia, para probar sin descargar nada.

Responsable: Persona 1 (Lucía Barañano).
"""
import numpy as np
import pandas as pd
import pytest

from src.contracts import FEATURE_COLUMNS, GAS_NAMES


@pytest.fixture
def datos_sinteticos():
    """3 lotes x 3 gases x 40 mediciones, 128 features. El sensor 2 es casi una copia del sensor 1."""
    generador = np.random.default_rng(0)
    filas = []
    for lote in (1, 2, 3):
        for gas in (1, 2, 3):
            n = 40
            centro = gas * 2.0 + lote * 0.3  # cada gas tiene su "huella" y el tiempo la desplaza un poco
            X = generador.normal(centro, 1.0, size=(n, 128))
            concentracion = generador.choice([10.0, 50.0, 100.0], size=n)
            tabla = pd.DataFrame(X, columns=FEATURE_COLUMNS)
            tabla.insert(0, "concentration", concentracion)
            tabla.insert(0, "gas_name", GAS_NAMES[gas])
            tabla.insert(0, "gas", gas)
            tabla.insert(0, "batch", lote)
            filas.append(tabla)
    datos = pd.concat(filas, ignore_index=True)
    # El sensor 2 (feature_9..16) copia al sensor 1 (feature_1..8) con un poco de ruido
    for i in range(8):
        datos[f"feature_{9 + i}"] = datos[f"feature_{1 + i}"] + generador.normal(0, 0.05, len(datos))
    return datos
