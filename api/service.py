"""Servicio BentoML (esqueleto, sin modelo).

Responsable: Persona 4 (Ane).
Funciones públicas: SmartNoseAPI.predict(features).
Uso: bentoml serve api.service:SmartNoseAPI
"""
import bentoml


@bentoml.service
class SmartNoseAPI:
    @bentoml.api
    def predict(self, features: list[float]) -> dict:
        # Pendiente: validar las 128 features, cargar el pipeline (joblib) y predecir
        return {"error": "Todavía no hay modelo disponible"}
