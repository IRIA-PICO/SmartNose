"""Tests de src/evaluation.py (usan datos sintéticos: no necesitan descargar nada).

Responsable: Persona 2 (Lucía Díez).
Funciones públicas: ninguna (tests de pytest).
"""
import pandas as pd
import pytest

from src.evaluation import calcular_metricas


def test_prediccion_perfecta_sin_tolueno():
    y_real = [1, 2, 3, 4, 5]
    metricas = calcular_metricas(y_real, y_real)

    assert metricas["accuracy"] == 1.0
    assert metricas["macro_f1"] == 1.0 #el tolueno no esta y no baja la nota
    assert list(metricas["f1_por_gas"]) == [1, 2, 3, 4, 5]


def test_predecir_un_gas_ausente_penaliza_al_gas_real():
    y_real = pd.Series([1, 1, 2, 2])
    y_pred = [1, 6, 2, 2] #una muestra del gas 1 sale como tolueno, que no esta
    metricas = calcular_metricas(y_real, y_pred)

    assert metricas["accuracy"] == 0.75
    assert metricas["f1_por_gas"] == {1: pytest.approx(2 / 3), 2: 1.0} #a mano: el gas 1 tiene precision 1 y recall 0.5
    assert metricas["macro_f1"] == pytest.approx((2 / 3 + 1) / 2)


def test_matriz_confusion_siempre_6x6():
    metricas = calcular_metricas([1, 1, 2, 2], [1, 6, 2, 2])
    matriz = metricas["matriz_confusion"]

    assert len(matriz) == 6
    for fila in matriz:
        assert len(fila) == 6

    assert matriz[0] == [1, 0, 0, 0, 0, 1] #gas 1: un acierto y uno como tolueno
    assert matriz[1] == [0, 2, 0, 0, 0, 0] #gas 2: los dos bien
    assert matriz[5] == [0, 0, 0, 0, 0, 0] #no hay tolueno real
