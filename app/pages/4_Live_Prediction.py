"""Live Prediction (provisional, con el estilo de SmartNose).

Responsable: Persona 4 (Ane).
Funciones públicas: ninguna (es una página de Streamlit).
Cuando esté lista la parte de la que depende, se sustituye pagina_en_construccion()
por el contenido real; configurar_pagina() y cabecera() se mantienen.
"""
from components.ui import configurar_pagina, pagina_en_construccion

configurar_pagina("Live Prediction")

pagina_en_construccion(
    seccion="04 · Predicción",
    titulo="Predicción <em>BentoML</em>",
    subtitulo="Elige una medición del dataset o sube un CSV, envíala a la API y mira el gas predicho.",
    planes=['Elegir una medición del dataset o subir un CSV con 128 valores.', 'Llamada a la API de BentoML (src/api_client.py).', 'Gas predicho, probabilidades y aviso si la medición está fuera de rango.'],
    responsable="api/service.py y src/api_client.py (Ane)",
)
