"""Test básico de la carga de datos.

Responsable: Persona 4 (Ane), con la Persona 1.
Funciones públicas: ninguna (tests de pytest).
"""
import pytest

from src.contracts import FEATURE_COLUMNS, RAW_DIR
from src.data_loader import cargar_todos


def test_dataset_completo():
    primer_lote = RAW_DIR / "batch1.dat"
    if not primer_lote.exists():
        pytest.skip("Faltan los datos en data/raw")

    datos = cargar_todos(salida=None)

    assert len(datos) == 13910

    assert len(FEATURE_COLUMNS) == 128
    features = datos[FEATURE_COLUMNS]
    nulos_por_columna = features.isna().sum()
    assert nulos_por_columna.sum() == 0

    assert datos["batch"].nunique() == 10
    assert datos["batch"].min() == 1
    assert datos["batch"].max() == 10
