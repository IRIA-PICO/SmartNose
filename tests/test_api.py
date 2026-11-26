"""Test mínimo de la API (solo comprueba que el servicio se importa).

Responsable: Persona 4 (Ane).
Funciones públicas: ninguna (tests de pytest).
"""


def test_servicio_se_importa():
    from api.service import SmartNoseAPI

    assert SmartNoseAPI is not None
