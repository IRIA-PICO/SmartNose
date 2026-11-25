"""Cliente HTTP para la API BentoML local (pendiente).

Responsable: Persona 4 (Ane).
Funciones públicas: predecir(features, url).
"""
from src.contracts import API_URL


def predecir(features, url=API_URL):
    """Envía 128 floats a la API y devuelve un dict con contracts.API_OUTPUT_KEYS."""
    raise NotImplementedError("Pendiente")
