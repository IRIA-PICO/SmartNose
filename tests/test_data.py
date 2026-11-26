"""Test básico de la carga de datos.

Responsable: Persona 4 (Ane), con la Persona 1.
Funciones públicas: ninguna (tests de pytest).
"""
import pytest

from src.contracts import FEATURE_COLUMNS, RAW_DIR
from src.data_loader import cargar_todos


def test_dataset_completo():
    # Si no se han descargado los datos, el test se salta
    primer_lote = RAW_DIR / "batch1.dat"
    if not primer_lote.exists():
        pytest.skip("Faltan los datos en data/raw")

    datos = cargar_todos(salida=None)

    # 13.910 filas
    assert len(datos) == 13910

    # 128 features sin valores vacíos
    assert len(FEATURE_COLUMNS) == 128
    features = datos[FEATURE_COLUMNS]
    nulos_por_columna = features.isna().sum()
    assert nulos_por_columna.sum() == 0

    # Los 10 lotes, del 1 al 10
    assert datos["batch"].nunique() == 10
    assert datos["batch"].min() == 1
    assert datos["batch"].max() == 10
