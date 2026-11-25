# Modelos

**Responsable:** Persona 2 (Lucía Díez).

Aquí se guardan los pipelines completos (escalado + modelo) con joblib. Los `.joblib` no se suben a git.
La API usará `smartnose_pipeline.joblib` (ver `MODEL_PATH` en `src/contracts.py`).

Todavía no hay ningún modelo. Pendiente: documentar cómo regenerarlo (configuración, lotes de entrenamiento y semilla).
Hay que cargarlos con las mismas versiones de `requirements.txt`. Cargar solo archivos joblib generados por el equipo.
