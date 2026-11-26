"""Contrato técnico compartido: constantes y formatos que usamos todas.

Responsable: Persona 2 (Lucía Díez). Cualquier cambio se avisa al equipo y va por pull request.
Funciones públicas: ninguna (solo constantes).
"""
from pathlib import Path

# --- Rutas (relativas a la raíz del proyecto) ---
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
CLEAN_DATA_PATH = PROCESSED_DIR / "gas_drift.parquet"
MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "smartnose_pipeline.joblib"  # el que sirve la API

RANDOM_STATE = 42
API_URL = "http://localhost:3000"

# --- Datos ---
N_BATCHES = 10
N_FEATURES = 128
# El orden es fijo: es el mismo en la tabla, en el entrenamiento y en la API
FEATURE_COLUMNS = []
for numero in range(1, N_FEATURES + 1):
    FEATURE_COLUMNS.append(f"feature_{numero}")  # feature_1 ... feature_128

TABLE_COLUMNS = ["batch", "gas", "gas_name", "concentration"] + FEATURE_COLUMNS
# Codificación según el texto de UCI. OJO: ver la duda abierta en data/README.md
GAS_NAMES = {1: "Etanol", 2: "Etileno", 3: "Amoníaco",
             4: "Acetaldehído", 5: "Acetona", 6: "Tolueno"}

# --- Formato común de métricas (claves del dict) ---
# f1_por_gas: {codigo_gas: f1}
# matriz_confusion: lista de listas (filas = real, columnas = predicho), códigos de menor a mayor
# n_train, n_test: número de filas; train_batches, test_batches: listas de lotes
METRIC_KEYS = ["accuracy", "macro_f1", "f1_por_gas", "matriz_confusion",
               "n_train", "n_test", "train_batches", "test_batches"]

# --- Tabla de deriva: una fila por (estrategia, lote) ---
DRIFT_COLUMNS = ["estrategia", "lote", "accuracy", "macro_f1"]

# --- API ---
# Entrada: lista de N_FEATURES floats en el orden de FEATURE_COLUMNS
# Salida: dict con estas claves (probabilidades = None si el modelo no las ofrece)
API_OUTPUT_KEYS = ["gas", "gas_name", "probabilidades", "aviso_fuera_de_rango"]
