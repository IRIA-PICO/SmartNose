# Modelos

**Responsable:** Persona 2 (Lucía Díez).

En esta carpeta se guardan con joblib los pipelines completos (preprocesado y modelo). Al guardarlo todo junto, la API
puede mandar las 128 features originales sin escalar nada a mano. Los `.joblib` no se suben a git, así que cada persona
tiene que generar el suyo.

La API usará `smartnose_pipeline.joblib` (ver `MODEL_PATH` en `src/contracts.py`).

## Cómo regenerar un modelo

Primero hace falta la tabla limpia (ver el README principal). Después, desde la raíz del proyecto y con el entorno
`nose`, se ejecuta este código en Python:

```python
import pandas as pd

from src.contracts import CLEAN_DATA_PATH
from src.training import entrenar, guardar_modelo

datos = pd.read_parquet(CLEAN_DATA_PATH)
config = {"modelo": "svm", "params": {}, "lotes_train": [1, 2, 3, 4, 5, 6, 7, 8, 9], "lotes_test": [10]}

pipeline, metricas = entrenar(datos, config)
guardar_modelo(pipeline)
```

## Modelo final

| Dato | Valor |
|---|---|
| Modelo | SVM (`SVC` con sus parámetros de partida) |
| Preprocesado | log firmada y `StandardScaler`, dentro del pipeline |
| Lotes de train | 1 a 9 (10.310 mediciones) |
| Lote de test | 10 (3.600 mediciones) |
| Semilla | `RANDOM_STATE = 42` (en `src/contracts.py`) |
| Resultado en el lote 10 | accuracy 0,693 y F1 macro 0,694 |

Se eligió el SVM porque tenía el mejor F1 macro en E1 (train con los lotes 1 a 3, test en el 4). Este modelo no ofrece
probabilidades (no tiene `predict_proba`), así que en la API ese campo debe ir como `None`.

El modelo conoce las mediciones de los lotes 1 a 9, así que acertar en ellas no sirve para evaluarlo.

## Cómo cargarlo

```python
from src.training import cargar_modelo

pipeline = cargar_modelo()
prediccion = pipeline.predict([features])  # features: lista de 128 floats en el orden de FEATURE_COLUMNS
```

- Hay que cargarlo desde un código que pueda importar `src`, porque el pipeline usa `log_firmada` de
  `src/preprocessing.py`.
- Se necesitan las mismas versiones de `requirements.txt`.
- Solo se deben cargar archivos joblib generados por el equipo.
