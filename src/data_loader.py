"""Carga de los 10 lotes originales y creación de la tabla limpia.

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: cargar_lote(ruta), cargar_todos().
Uso: python -m src.data_loader
"""
from pathlib import Path

import pandas as pd

from src.contracts import CLEAN_DATA_PATH, FEATURE_COLUMNS, GAS_NAMES
from src.contracts import N_BATCHES, N_FEATURES, RAW_DIR, TABLE_COLUMNS


def cargar_lote(ruta):
    """Lee un archivo batchN.dat y devuelve una tabla con las columnas del contrato."""
    ruta = Path(ruta)

    # Sacamos el número de lote del nombre del archivo: "batch7" -> 7
    nombre_archivo = ruta.stem
    texto_lote = nombre_archivo.replace("batch", "")
    batch = int(texto_lote)

    filas = []
    texto = ruta.read_text()
    lineas = texto.splitlines()

    for linea in lineas:
        # Saltamos las líneas vacías
        if linea.strip() == "":
            continue

        # Cada línea es: "gas;concentración 1:valor 2:valor ... 128:valor"
        # Separamos por los espacios
        partes = linea.split()
        cabecera = partes[0]  # "gas;concentración"
        pares = partes[1:]    # el resto: "número:valor"

        # Separamos el gas y la concentración
        trozos_cabecera = cabecera.split(";")
        gas = int(trozos_cabecera[0])
        concentracion = float(trozos_cabecera[1])

        # Comprobamos que hay 128 features
        if len(pares) != N_FEATURES:
            raise ValueError(f"{ruta.name}: hay una fila sin {N_FEATURES} features")

        # Guardamos los valores, comprobando que vienen en orden
        valores = []
        numero_esperado = 1
        for par in pares:
            trozos = par.split(":")
            numero = int(trozos[0])
            valor = float(trozos[1])

            if numero != numero_esperado:
                raise ValueError(f"{ruta.name}: hay una fila con las features desordenadas")

            valores.append(valor)
            numero_esperado = numero_esperado + 1

        # Montamos la fila completa
        nombre_gas = GAS_NAMES[gas]
        fila = [batch, gas, nombre_gas, concentracion] + valores
        filas.append(fila)

    tabla = pd.DataFrame(filas, columns=TABLE_COLUMNS)
    return tabla


def cargar_todos(carpeta=RAW_DIR, salida=CLEAN_DATA_PATH):
    """Une los 10 lotes, muestra las comprobaciones básicas y guarda un parquet."""
    carpeta = Path(carpeta)

    # Leemos los lotes del 1 al 10, uno a uno
    lotes = []
    for numero_lote in range(1, N_BATCHES + 1):
        ruta = carpeta / f"batch{numero_lote}.dat"
        lote = cargar_lote(ruta)
        lotes.append(lote)

    # Los juntamos en una sola tabla
    datos = pd.concat(lotes, ignore_index=True)

    # Comprobaciones: solo informamos, no borramos ni modificamos ninguna fila
    total_filas = len(datos)
    total_features = len(FEATURE_COLUMNS)

    nulos_por_columna = datos.isna().sum()
    total_nulos = nulos_por_columna.sum()

    filas_repetidas = datos.duplicated()
    total_duplicadas = filas_repetidas.sum()

    features_repetidas = datos.duplicated(subset=FEATURE_COLUMNS)
    total_features_repetidas = features_repetidas.sum()

    mediciones = pd.crosstab(datos["batch"], datos["gas"]) #crea una tabla que cuenta cuantas mediciiones hay de cada gas en cada lote

    print(f"Filas: {total_filas} | Features por fila: {total_features}")
    print(f"Valores nulos: {total_nulos}")
    print(f"Filas duplicadas: {total_duplicadas}")
    print(f"Duplicadas mirando solo las features: {total_features_repetidas}")
    print("Mediciones por lote y gas:")
    print(mediciones.to_string())

    # Con salida=None no se guarda nada (lo usa el test)
    if salida is not None:
        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        datos.to_parquet(salida, index=False)
        print(f"Guardado en {salida}")

    return datos


if __name__ == "__main__":
    cargar_todos()
