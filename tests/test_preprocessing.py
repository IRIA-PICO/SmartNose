"""Tests de src/preprocessing.py (usan datos sintéticos: no necesitan descargar nada).

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: ninguna (tests de pytest).
"""
import joblib
import numpy as np
import pytest

from src.contracts import FEATURE_COLUMNS
from src import preprocessing as pp


def test_columna_y_su_inversa():
    assert pp.columna(1, 1) == "feature_1"
    assert pp.columna(2, 1) == "feature_9"
    assert pp.columna(16, 8) == "feature_128"
    assert pp.sensor_y_caracteristica("feature_9") == (2, 1)
    assert pp.nombre_legible("feature_9") == "S02 · ΔR estacionario"
    with pytest.raises(ValueError):
        pp.columna(17, 1)


def test_columnas_de_sensores_mantiene_el_orden_del_contrato():
    assert pp.columnas_de_sensores([3, 1], [2, 1]) == ["feature_1", "feature_2", "feature_17", "feature_18"]
    assert pp.columnas_de_sensores() == FEATURE_COLUMNS


def test_separar_xy_no_modifica_la_tabla(datos_sinteticos):
    copia = datos_sinteticos.copy()
    X, y = pp.separar_xy(datos_sinteticos)
    assert list(X.columns) == FEATURE_COLUMNS
    assert len(X) == len(y) == len(datos_sinteticos)
    X.iloc[0, 0] = 999
    assert datos_sinteticos.equals(copia)


def test_separar_xy_con_columnas_elegidas(datos_sinteticos):
    X, _ = pp.separar_xy(datos_sinteticos, ["feature_9", "feature_1"])
    assert list(X.columns) == ["feature_1", "feature_9"]
    with pytest.raises(ValueError):
        pp.separar_xy(datos_sinteticos, ["batch"])


def test_dividir_por_lotes(datos_sinteticos):
    train, test = pp.dividir_por_lotes(datos_sinteticos, [1, 2], [3])
    assert set(train["batch"]) == {1, 2}
    assert set(test["batch"]) == {3}
    assert len(train) + len(test) == len(datos_sinteticos)


def test_dividir_por_lotes_detecta_fuga_temporal(datos_sinteticos):
    with pytest.raises(ValueError, match="Fuga temporal"):
        pp.dividir_por_lotes(datos_sinteticos, [3], [1, 2])
    train, test = pp.dividir_por_lotes(datos_sinteticos, [3], [1, 2], permitir_futuro=True)
    assert len(train) > 0 and len(test) > 0


def test_dividir_por_lotes_rechaza_repetidos_y_lotes_que_no_existen(datos_sinteticos):
    with pytest.raises(ValueError):
        pp.dividir_por_lotes(datos_sinteticos, [1, 2], [2, 3])
    with pytest.raises(ValueError):
        pp.dividir_por_lotes(datos_sinteticos, [1], [9])


def test_log_firmada_mantiene_signo_y_comprime():
    X = np.array([-1000.0, -1.0, 0.0, 1.0, 1000.0])
    Y = pp.log_firmada(X)
    assert list(np.sign(Y)) == [-1, -1, 0, 1, 1]
    assert abs(Y[-1]) < 10  # 1000 pasa a ~6,9
    assert Y[2] == 0


def test_preprocesador_se_ajusta_solo_con_train(datos_sinteticos):
    train, test = pp.dividir_por_lotes(datos_sinteticos, [1], [3])
    preproceso = pp.crear_preprocesador().fit(train[FEATURE_COLUMNS])
    Z_train = preproceso.transform(train[FEATURE_COLUMNS])
    Z_test = preproceso.transform(test[FEATURE_COLUMNS])
    assert Z_train.shape[1] == Z_test.shape[1] == 128
    # En train la media es 0 por construcción; en test no (si no, se habría ajustado con test)
    assert abs(Z_train.mean()) < 1e-6
    assert abs(Z_test.mean()) > 0.05


def test_preprocesador_se_puede_guardar_con_joblib(datos_sinteticos, tmp_path):
    preproceso = pp.crear_preprocesador().fit(datos_sinteticos[FEATURE_COLUMNS])
    ruta = tmp_path / "preproceso.joblib"
    joblib.dump(preproceso, ruta)
    recargado = joblib.load(ruta)
    esperado = preproceso.transform(datos_sinteticos[FEATURE_COLUMNS].head(5))
    assert np.allclose(recargado.transform(datos_sinteticos[FEATURE_COLUMNS].head(5)), esperado)


def test_preprocesador_sin_log(datos_sinteticos):
    preproceso = pp.crear_preprocesador(transformar_log=False)
    assert [nombre for nombre, _ in preproceso.steps] == ["escalado"]
