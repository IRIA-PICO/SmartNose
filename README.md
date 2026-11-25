# SmartNose AI Lab

Proyecto final de Analítica de Datos para la Industria. Entrega: **19 de diciembre de 2026**.

**Pregunta central:** ¿podemos detectar cuándo una nariz electrónica pierde fiabilidad por deriva temporal y comprobar si reentrenar el modelo recupera el rendimiento?

Flujo previsto: notebook + funciones de `src/` → Streamlit → API BentoML local (por HTTP).

**Estado:** estructura inicial y carga de datos. Todavía no hay modelos, gráficas ni predicciones.

## Ejecución
Todos los comandos se lanzan desde la raíz del proyecto, con Python 3.12.

1. Instalar (PowerShell):

       py -3.12 -m venv .venv
       .venv\Scripts\Activate.ps1
       pip install -r requirements.txt

   En macOS/Linux: `python3.12 -m venv .venv` y `source .venv/bin/activate`.

2. Descargar los datos: `python scripts/download_data.py`
3. Preparar la tabla limpia: `python -m src.data_loader`
4. API (terminal 1): `bentoml serve api.service:SmartNoseAPI` → http://localhost:3000
   Si el puerto 3000 está ocupado (por ejemplo, por Grafana), añade `--port 3123` y cambia `API_URL` en `src/contracts.py` solo en tu equipo, sin subir el cambio.
5. App (terminal 2): `streamlit run app/Home.py`
6. Tests: `python -m pytest`

Más información sobre el dataset en [data/README.md](data/README.md). **Hay una duda abierta sobre los nombres de los códigos de gas.**

## Reparto

| Persona | Parte | Archivos | Rama |
|---|---|---|---|
| 1. Lucía Barañano | Datos y EDA | `data_loader.py`, `preprocessing.py`, `exploratory_analysis.py`, notebook | `feature/data` |
| 2. Lucía Díez | Modelos y deriva | `training.py`, `evaluation.py`, `drift_analysis.py`, modelos, notebook | `feature/models` |
| 3. Iria | Streamlit | `Home.py`, páginas 1, 2 y 3 | `feature/dashboard` |
| 4. Ane | BentoML e integración | `api/service.py`, `api_client.py`, página 4, tests, README | `feature/api` |

- Iria no implementa algoritmos y Ane no reentrena: ambas usan lo que prepara la Persona 2.
- Una sola persona integra el notebook (pendiente de decidir quién), para no tener conflictos en el `.ipynb`. Las demás ponen el código en `src/` y le pasan las celdas.

## Contrato técnico
Definido en [src/contracts.py](src/contracts.py). Si cambia, se avisa a todo el equipo.

- **Tabla limpia** (`data/processed/gas_drift.parquet`): `batch` (1-10), `gas` (1-6), `gas_name`, `concentration`, `feature_1` ... `feature_128`.
- **Constantes:** `FEATURE_COLUMNS` (orden fijo), `GAS_NAMES`, `N_FEATURES=128`, rutas y `RANDOM_STATE`.
- **Entrenamiento:** `entrenar(datos, config)` recibe la tabla y un dict; devuelve un `Pipeline` de scikit-learn completo (escalado + modelo) y un dict de métricas.
- **Métricas:** `{accuracy, macro_f1, f1_por_gas, matriz_confusion, n_train, n_test, train_batches, test_batches}`.
- **Deriva:** `evolucion_por_lote(datos, config)` devuelve una tabla con `estrategia`, `lote`, `accuracy`, `macro_f1`.
- **API:** entrada, lista de 128 floats en el orden de `FEATURE_COLUMNS`. Salida: `{gas, gas_name, probabilidades, aviso_fuera_de_rango}` (`probabilidades` solo si el modelo las ofrece). Usa el mismo pipeline guardado con joblib, sin reescalar a mano.

## Git
No se trabaja directamente en `main` (la única excepción es el commit inicial con la estructura).

**Una vez**, quien hizo el commit inicial lo sube: `git push -u origin main`. Después, conviene proteger `main` en GitHub (*Settings → Branches*: exigir pull request).

Cada persona crea su rama (ejemplo con la de datos; las otras son `feature/models`, `feature/dashboard` y `feature/api`):

    git clone https://github.com/IRIA-PICO/SmartNose.git
    cd SmartNose
    git switch -c feature/data
    git push -u origin feature/data

Trabajo diario:

    git add <archivos>
    git commit -m "Describe el cambio"
    git push

Para integrar: abrir un **pull request** de la rama hacia `main`, que otra persona lo revise y entonces hacer *merge*. Para traer los cambios de `main` a tu rama:

    git fetch origin
    git merge origin/main

Antes de un pull request: `python -m pytest`. En el notebook, un solo editor.

**Entrega:** con todo en `main` y antes de que acabe el 19 de diciembre:

    git switch main
    git pull
    git tag -a v1.0-final -m "Entrega final"
    git push origin v1.0-final

**No se hacen commits después del 19 de diciembre.**

## Notas para más adelante (todavía sin implementar)
- Escalar solo con datos de entrenamiento y dentro del `Pipeline`, para no filtrar información del futuro.
- Respetar el orden temporal: nada de `train_test_split` aleatorio global; entrenar con lotes anteriores y evaluar en posteriores. Lo mismo al ajustar parámetros.
- Usar macro-F1 y métricas por gas, no solo accuracy, por el desbalance y los gases ausentes. Decidir cómo calcular macro-F1 en los lotes sin tolueno (3, 4 y 5) y usar el mismo criterio en todo el proyecto.
- No eliminar outliers a ciegas: pueden ser la propia deriva.
- Distinguir la deriva real de los cambios en la mezcla de gases y concentraciones entre lotes.
- Semillas fijas, versiones fijadas, rutas relativas y caché en Streamlit.
- Colab: comprobar que las versiones de `requirements.txt` se instalan allí (puede pedir reiniciar el entorno).

## Experimentos previstos
- **E1:** comparar regresión logística, Random Forest y SVM.
- **E2:** entrenar con lotes antiguos y medir la caída en los posteriores.
- **E3:** modelo fijo frente a modelo reentrenado periódicamente.
- **Ampliación:** indicador de cambio de distribución.
- **Extras si sobra tiempo:** reducir de 16 a 12/8/4 sensores y regresión de concentración.

## Pantallas de Streamlit
1. **Sensor Explorer:** explorar las medidas.
2. **Drift Monitor:** evolución por lote.
3. **Model Lab:** elegir algoritmo y parámetros, entrenar y comparar.
4. **Live Prediction:** elegir una medición o subir un CSV, enviarla a la API y mostrar el gas predicho.
