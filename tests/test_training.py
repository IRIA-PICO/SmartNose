"""Tests de src/training.py (usan datos sintéticos: no necesitan descargar nada).

Responsable: Persona 2 (Lucía Díez).
Funciones públicas: ninguna (tests de pytest).
"""
import pytest

from src.contracts import FEATURE_COLUMNS, METRIC_KEYS
from src.training import cargar_modelo, entrenar, guardar_modelo


def crear_config(modelo):
    config = {"modelo": modelo, "params": {}, "lotes_train": [1, 2], "lotes_test": [3]}
    return config


def test_entrenar_devuelve_pipeline_y_metricas(datos_sinteticos):
    for nombre in ["logreg", "rf", "svm"]: #se prueban los tres modelos
        pipeline, metricas = entrenar(datos_sinteticos, crear_config(nombre))

        assert sorted(metricas) == sorted(METRIC_KEYS)
        assert metricas["n_train"] == 240
        assert metricas["n_test"] == 120
        assert metricas["train_batches"] == [1, 2]
        assert metricas["test_batches"] == [3]

        assert list(pipeline.named_steps) == ["preproceso", "modelo"] #el pipeline recibe las 128 features sin escalar
        assert pipeline.n_features_in_ == 128
        predicciones = pipeline.predict(datos_sinteticos[FEATURE_COLUMNS].head(5))
        assert len(predicciones) == 5


def test_el_escalado_solo_aprende_de_train(datos_sinteticos):
    pipeline, _ = entrenar(datos_sinteticos, crear_config("logreg"))
    escalado = pipeline.named_steps["preproceso"].named_steps["escalado"]
    assert escalado.n_samples_seen_ == 240


def test_se_aplican_los_parametros(datos_sinteticos):
    config = crear_config("rf")
    config["params"] = {"n_estimators": 7}
    pipeline, _ = entrenar(datos_sinteticos, config)
    assert len(pipeline.named_steps["modelo"].estimators_) == 7


def test_entrenar_rechaza_un_modelo_desconocido(datos_sinteticos):
    with pytest.raises(ValueError, match="Modelo desconocido"):
        entrenar(datos_sinteticos, crear_config("otro"))


def test_entrenar_rechaza_entrenar_con_el_futuro(datos_sinteticos):
    config = crear_config("logreg")
    config["lotes_train"] = [3]
    config["lotes_test"] = [1]
    with pytest.raises(ValueError, match="Fuga temporal"):
        entrenar(datos_sinteticos, config)


def test_guardar_y_cargar_modelo(datos_sinteticos, tmp_path):
    pipeline, _ = entrenar(datos_sinteticos, crear_config("rf"))
    ruta = tmp_path / "carpeta_nueva" / "modelo.joblib" #ruta temporal para no pisar el modelo real
    guardar_modelo(pipeline, ruta)
    recargado = cargar_modelo(ruta)

    X = datos_sinteticos[FEATURE_COLUMNS]
    assert list(recargado.predict(X)) == list(pipeline.predict(X))
