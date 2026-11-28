"""Métricas en el formato común.

Responsable: Persona 2 (Lucía Díez).
Funciones públicas: calcular_metricas(y_real, y_pred).
"""
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from src.contracts import GAS_NAMES


def calcular_metricas(y_real, y_pred):
    """Devuelve accuracy, macro_f1, f1_por_gas y matriz_confusion.

    El macro-F1 se calcula solo con los gases que aparecen en y_real. Así un gas
    que no está en el lote (el tolueno en los lotes 3, 4 y 5) no cuenta como un
    cero. Si el modelo lo predice por error, baja igualmente el recall del gas
    real. Al comparar lotes, no todos promedian el mismo número de gases.

    f1_por_gas es un dict {codigo_gas: f1} solo con los gases presentes.
    matriz_confusion es siempre de 6x6 (filas = real, columnas = predicho),
    con los códigos del 1 al 6. La fila de un gas ausente queda a ceros.

    n_train, n_test, train_batches y test_batches los añade entrenar().
    """
    accuracy = accuracy_score(y_real, y_pred)

    gases_presentes = np.unique(y_real).tolist() #solo los gases que estan en los datos reales

    valores_f1 = f1_score(y_real, y_pred, labels=gases_presentes,
                          average=None, zero_division=0) #average=None para sacar un f1 por gas

    f1_por_gas = {}
    for posicion in range(len(gases_presentes)): #cada f1 con el codigo de su gas
        gas = gases_presentes[posicion]
        f1_por_gas[gas] = float(valores_f1[posicion])

    macro_f1 = valores_f1.mean() #todos los gases pesan igual

    todos_los_gases = sorted(GAS_NAMES)
    matriz = confusion_matrix(y_real, y_pred, labels=todos_los_gases) #con los 6 gases siempre sale 6x6

    metricas = {
        "accuracy": float(accuracy), #tipos normales de python
        "macro_f1": float(macro_f1),
        "f1_por_gas": f1_por_gas,
        "matriz_confusion": matriz.tolist(),
    }
    return metricas
