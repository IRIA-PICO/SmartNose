"""Entrenamiento de modelos.

Responsable: Persona 2 (Lucía Díez).
Funciones públicas: crear_modelo(nombre, params), entrenar(datos, config),
    guardar_modelo(pipeline, ruta), cargar_modelo(ruta).
"""
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from src.contracts import MODEL_PATH, RANDOM_STATE
from src.evaluation import calcular_metricas
from src.preprocessing import crear_preprocesador, dividir_por_lotes, separar_xy


def crear_modelo(nombre, params):
    """Devuelve un modelo sin entrenar: "logreg", "rf" o "svm".

    params es un dict con los parámetros que se quieran cambiar, por ejemplo
    {"n_estimators": 200}. Con {} no se cambia ninguno.
    """
    if nombre == "logreg":
        modelo = LogisticRegression(max_iter=2000, random_state=RANDOM_STATE) #mas iteraciones para que le de tiempo a converger
    elif nombre == "rf":
        modelo = RandomForestClassifier(random_state=RANDOM_STATE)
    elif nombre == "svm":
        modelo = SVC(random_state=RANDOM_STATE)
    else:
        raise ValueError(f"Modelo desconocido: {nombre}. Usa 'logreg', 'rf' o 'svm'")

    modelo.set_params(**params) #cambia los parametros del dict, si alguno no existe da error
    return modelo


def entrenar(datos, config):
    """Recibe la tabla limpia y un dict de configuración.

    config tiene estas claves:
        "modelo": "logreg", "rf" o "svm"
        "params": dict con parámetros del modelo ({} para no cambiar ninguno)
        "lotes_train": lista de lotes para entrenar
        "lotes_test": lista de lotes para evaluar (posteriores a los de train)

    Devuelve (pipeline, metricas): el Pipeline completo ya entrenado
    (preprocesado + modelo) y un dict con las claves de contracts.METRIC_KEYS.
    Si hay varios lotes de test, las métricas son de todos juntos (el macro-F1
    usa los gases que aparecen en ese conjunto).
    """
    train, test = dividir_por_lotes(datos, config["lotes_train"], config["lotes_test"]) #por lotes para no entrenar con el futuro

    X_train, y_train = separar_xy(train) #128 features y codigo del gas
    X_test, y_test = separar_xy(test)

    modelo = crear_modelo(config["modelo"], config["params"])
    pipeline = Pipeline([
        ("preproceso", crear_preprocesador()), #dentro del pipeline para que solo aprenda de train
        ("modelo", modelo),
    ])
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    metricas = calcular_metricas(y_test, y_pred)

    metricas["n_train"] = len(train) #claves del contrato que no pone calcular_metricas
    metricas["n_test"] = len(test)
    metricas["train_batches"] = sorted(train["batch"].unique().tolist())
    metricas["test_batches"] = sorted(test["batch"].unique().tolist())

    return pipeline, metricas


def guardar_modelo(pipeline, ruta=MODEL_PATH):
    """Guarda el Pipeline completo con joblib y devuelve la ruta."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True) #crea la carpeta si no existe
    joblib.dump(pipeline, ruta)
    return ruta


def cargar_modelo(ruta=MODEL_PATH):
    """Carga un Pipeline guardado. Solo se deben cargar archivos creados por el equipo."""
    pipeline = joblib.load(ruta)
    return pipeline
