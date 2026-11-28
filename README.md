# SmartNose AI Lab

Proyecto final de Analítica de Datos para la Industria. Entrega: **19 de diciembre de 2026**.

**Pregunta central:** ¿podemos detectar cuándo una nariz electrónica pierde fiabilidad por deriva temporal y comprobar si reentrenar el modelo recupera el rendimiento?

Flujo previsto: notebook + funciones de `src/` → Streamlit → API BentoML local (por HTTP).

**Estado:** carga de datos, análisis exploratorio (PCA, correlaciones, atípicos, deriva por sensor, importancia de sensores) y preprocesado listos; el análisis está en el notebook y en cinco pestañas nuevas de *Sensor Explorer*. Todavía no hay modelos ni predicciones.

## Primera vez: crear el entorno
Necesitas Git y **Python 3.12**. El entorno se llama `nose`. Cada una crea el suyo: la carpeta no se sube a git.

En la terminal (PowerShell):

    git clone https://github.com/IRIA-PICO/SmartNose.git
    cd SmartNose
    py -3.12 -m venv nose
    nose\Scripts\Activate.ps1
    pip install -r requirements.txt

- Si ya tienes el repositorio clonado, sáltate `git clone` y entra en la carpeta.
- En macOS/Linux: `python3.12 -m venv nose` y `source nose/bin/activate`.
- La instalación puede tardar varios minutos. Cuando el entorno está activado, aparece `(nose)` al principio de la línea.
- Si PowerShell no deja activarlo, ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` y vuelve a activarlo (solo afecta a esa terminal).
- En VS Code: `Ctrl+Shift+P` → **Python: Select Interpreter** → el de la carpeta `nose`.
- Si la carpeta del proyecto está en OneDrive y la instalación da errores de rutas o archivos bloqueados, clona el proyecto fuera de OneDrive.

**Cada vez que abras una terminal nueva**, activa el entorno con `nose\Scripts\Activate.ps1`. Si cambia `requirements.txt`, repite `pip install -r requirements.txt`.

## Ejecución
Todos los comandos se lanzan desde la raíz del proyecto, con el entorno `nose` activado.

1. Comprueba que has creado el entorno (apartado anterior).
2. Descargar los datos: `python scripts/download_data.py`
3. Preparar la tabla limpia: `python -m src.data_loader`
4. API (terminal 1): `bentoml serve api.service:SmartNoseAPI` → http://localhost:3000
   Si el puerto 3000 está ocupado (por ejemplo, por Grafana), añade `--port 3123` y cambia `API_URL` en `src/contracts.py` solo en tu equipo, sin subir el cambio.
5. App (terminal 2): `streamlit run app/Home.py`
6. Tests: `python -m pytest` (los de datos reales se saltan si no has descargado `data/raw`; el de gráficos, si no tienes Plotly)

Más información sobre el dataset en [data/README.md](data/README.md). **Los nombres de los códigos de gas se han corregido y el equipo lo ha confirmado (ver ese archivo).**

## Reparto

| Persona | Parte | Archivos |
|---|---|---|
| 1. Lucía Barañano | Datos y EDA | `data_loader.py`, `preprocessing.py`, `exploratory_analysis.py`, `eda_plots.py`, `app/components/eda_panels.py`, notebook (secciones 0-3) |
| 2. Lucía Díez | Modelos y deriva | `training.py`, `evaluation.py`, `drift_analysis.py`, modelos, notebook |
| 3. Iria | Streamlit | `Home.py`, páginas 1, 2 y 3 |
| 4. Ane | BentoML e integración | `api/service.py`, `api_client.py`, página 4, tests, README |

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
**Trabajamos todas directamente en `main`, sin ramas ni pull requests.** Para que no haya conflictos, cada persona edita solo sus archivos (tabla de Reparto) y hace `git pull` antes de empezar y antes de subir.

Una vez, para tener el proyecto:

    git clone https://github.com/IRIA-PICO/SmartNose.git
    cd SmartNose

Trabajo diario (en `main`):

    git pull
    git add <archivos>
    git commit -m "Describe el cambio"
    git pull
    git push

- Si `git push` dice que ha sido rechazado, es que alguien ha subido antes: haz `git pull` y vuelve a hacer `git push`.
- Sube cambios pequeños y a menudo, y no subas código que rompa los tests: antes de subir, `python -m pytest`.
- Si hace falta tocar un archivo que es de otra persona (por ejemplo `src/contracts.py`), avísala antes.
- Si `git pull` avisa de un conflicto, no lo resuelvas a ciegas: pregunta a quien editó ese archivo.
- En el notebook, un solo editor a la vez. Las demás ponen el código en `src/` y le pasan las celdas.
- En Colab, el notebook usa `RAMA = "main"`. Los cambios hechos solo en Colab no se suben a GitHub.

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

## Análisis exploratorio y preprocesado (Persona 1)
Los cálculos devuelven tablas y no dibujan; los usan el notebook y la app:

| Módulo | Qué hace |
|---|---|
| `src/preprocessing.py` | `separar_xy`, `dividir_por_lotes` (avisa si se entrena con el futuro), `crear_preprocesador` (log firmada + `StandardScaler`, primer bloque del Pipeline), `seleccionar_sensores`, nombres de sensores y características |
| `src/exploratory_analysis.py` | recuentos por gas/lote/concentración, calidad, estadísticas, atípicos (solo se detectan), correlación y redundancia entre sensores, PCA, deriva por PCA y por sensor, importancia de sensores (ANOVA o Random Forest, por lotes) |
| `src/eda_plots.py` | gráficos de Plotly para esas tablas (sin Streamlit) |
| `app/components/eda_panels.py` | cinco paneles de Streamlit (`panel_pca`, `panel_correlaciones`, `panel_calidad`, `panel_deriva_sensores`, `panel_seleccion_sensores`) que se llaman desde *Sensor Explorer* con la tabla ya filtrada |

Para usar `crear_preprocesador` en el entrenamiento: `Pipeline([("preproceso", crear_preprocesador()), ("modelo", ...)])`.
