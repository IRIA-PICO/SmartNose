"""Carga de datos para la app y nombres legibles de las 128 variables.

Responsable: Persona 3 (Iria).
No transforma los datos: solo lee el Parquet que prepara src/data_loader.py.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.contracts import CLEAN_DATA_PATH, MODEL_PATH, N_FEATURES  # noqa: E402

CARACTERISTICAS = {
    1: "ΔR estacionario",
    2: "ΔR normalizado",
    3: "Subida EMA α=0,001",
    4: "Subida EMA α=0,01",
    5: "Subida EMA α=0,1",
    6: "Bajada EMA α=0,001",
    7: "Bajada EMA α=0,01",
    8: "Bajada EMA α=0,1",
}
N_CARACTERISTICAS = len(CARACTERISTICAS)
N_SENSORES = N_FEATURES // N_CARACTERISTICAS


def columna(sensor, caracteristica):
    """Devuelve el nombre de la columna: columna(2, 1) -> "feature_9"."""
    numero = (sensor - 1) * N_CARACTERISTICAS + caracteristica
    return f"feature_{numero}"


def nombre_legible(nombre_columna):
    """Traduce una columna a texto: "feature_9" -> "S02 · ΔR estacionario".

    Las columnas que no son features (batch, concentration...) también tienen nombre.
    """
    otros = {"concentration": "Concentración (ppmv)", "batch": "Lote", "gas_name": "Gas"}
    if nombre_columna in otros:
        return otros[nombre_columna]
    numero = int(nombre_columna.split("_")[1])
    sensor = (numero - 1) // N_CARACTERISTICAS + 1
    caracteristica = (numero - 1) % N_CARACTERISTICAS + 1
    return f"S{sensor:02d} · {CARACTERISTICAS[caracteristica]}"


@st.cache_data(show_spinner="Cargando mediciones...")
def cargar_datos():
    """Lee data/processed/gas_drift.parquet una sola vez (luego usa la caché).

    Si el archivo no existe, explica cómo crearlo y detiene la página.
    """
    if not CLEAN_DATA_PATH.exists():
        st.error(
            "No encuentro `data/processed/gas_drift.parquet`. Desde la raíz del proyecto ejecuta:\n\n"
            "`python scripts/download_data.py` y después `python -m src.data_loader`."
        )
        st.stop()
    return pd.read_parquet(CLEAN_DATA_PATH)


def modelo_disponible():
    """True si ya existe el pipeline entrenado que usará la API."""
    return MODEL_PATH.exists()
