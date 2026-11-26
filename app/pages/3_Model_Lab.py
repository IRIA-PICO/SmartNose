"""Model Lab (provisional, con el estilo de SmartNose).

Responsable: Persona 3 (Iria).
Funciones públicas: ninguna (es una página de Streamlit).
Cuando esté lista la parte de la que depende, se sustituye pagina_en_construccion()
por el contenido real; configurar_pagina() y cabecera() se mantienen.
"""
from components.ui import configurar_pagina, pagina_en_construccion

configurar_pagina("Model Lab")

pagina_en_construccion(
    seccion="03-Modelos",
    titulo="Laboratorio de <em>Modelo</em>",
    subtitulo="Elige un algoritmo, ajusta sus parámetros, entrena y compara métricas.",
    planes=['Selector de algoritmo: regresión logística, Random Forest y SVM.', 'Parámetros ajustables y elección de lotes de entrenamiento y de prueba.', 'Métricas (accuracy, macro-F1, F1 por gas) y matriz de confusión.', 'Tabla para comparar los experimentos de la sesión.'],
    responsable="src/training.py → entrenar() (Lucía Díez)",
)
