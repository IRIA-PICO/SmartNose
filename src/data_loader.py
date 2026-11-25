"""Carga de los 10 lotes originales y creación de la tabla limpia.

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: cargar_lote(ruta), cargar_todos().
Uso: python -m src.data_loader
"""
from pathlib import Path

import pandas as pd

from src.contracts import (CLEAN_DATA_PATH, FEATURE_COLUMNS, GAS_NAMES, N_BATCHES,
                           N_FEATURES, RAW_DIR, TABLE_COLUMNS)


def cargar_lote(ruta):
    """Lee un archivo batchN.dat y devuelve una tabla con las columnas del contrato."""
    ruta = Path(ruta)
    batch = int(ruta.stem.replace("batch", ""))  # "batch7" -> 7
    filas = []
    for linea in ruta.read_text().splitlines():
        if not linea.strip():
            continue
        # Formato: "gas;concentración 1:valor 2:valor ... 128:valor"
        cabecera, *pares = linea.split()
        gas, concentracion = cabecera.split(";")
        # Comprobamos que están las 128 features y en orden
        indices = [int(par.split(":")[0]) for par in pares]
        if indices != list(range(1, N_FEATURES + 1)):
            raise ValueError(f"{ruta.name}: hay una fila sin las {N_FEATURES} features en orden")
        valores = [float(par.split(":")[1]) for par in pares]
        filas.append([batch, int(gas), GAS_NAMES[int(gas)], float(concentracion)] + valores)
    return pd.DataFrame(filas, columns=TABLE_COLUMNS)


def cargar_todos(carpeta=RAW_DIR, salida=CLEAN_DATA_PATH):
    """Une los 10 lotes, muestra las comprobaciones básicas y guarda un parquet."""
    lotes = [cargar_lote(Path(carpeta) / f"batch{i}.dat") for i in range(1, N_BATCHES + 1)]
    datos = pd.concat(lotes, ignore_index=True)

    # Solo informamos: no borramos ni modificamos ninguna fila
    print(f"Filas: {len(datos)} | Features por fila: {len(FEATURE_COLUMNS)}")
    print(f"Valores nulos: {datos.isna().sum().sum()}")
    print(f"Filas duplicadas: {datos.duplicated().sum()}")
    print(f"Duplicadas mirando solo las features: {datos.duplicated(subset=FEATURE_COLUMNS).sum()}")
    print("Mediciones por lote y gas:")
    print(pd.crosstab(datos["batch"], datos["gas"]).to_string())

    if salida is not None:  # con salida=None no se escribe nada (lo usa el test)
        Path(salida).parent.mkdir(parents=True, exist_ok=True)
        datos.to_parquet(salida, index=False)
        print(f"Guardado en {salida}")
    return datos


if __name__ == "__main__":
    cargar_todos()
