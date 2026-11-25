"""Test básico de la carga de datos.

Responsable: Persona 4 (Ane), con la Persona 1.
Funciones públicas: ninguna (tests de pytest).
"""
import pytest

from src.contracts import FEATURE_COLUMNS, RAW_DIR
from src.data_loader import cargar_todos


@pytest.mark.skipif(not (RAW_DIR / "batch1.dat").exists(), reason="Faltan los datos en data/raw")
def test_dataset_completo():
    datos = cargar_todos(salida=None)
    assert len(datos) == 13910
    assert len(FEATURE_COLUMNS) == 128
    assert datos[FEATURE_COLUMNS].notna().all().all()
    assert sorted(datos["batch"].unique()) == list(range(1, 11))
