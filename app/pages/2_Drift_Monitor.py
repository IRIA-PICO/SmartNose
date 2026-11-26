"""Drift Monitor (provisional, con el estilo de SmartNose).

Responsable: Persona 3 (Iria).
Funciones públicas: ninguna (es una página de Streamlit).
Cuando esté lista la parte de la que depende, se sustituye pagina_en_construccion()
por el contenido real; configurar_pagina() y cabecera() se mantienen.
"""
from components.ui import configurar_pagina, pagina_en_construccion

configurar_pagina("Drift Monitor")

pagina_en_construccion(
    seccion="02 - Deriva",
    titulo="Monitor de la<em>Deriva</em>",
    subtitulo="Cómo cambia el rendimiento del modelo lote a lote, y si reentrenar lo recupera.",
    planes=['Accuracy y macro-F1 por lote para cada estrategia (modelo fijo frente a reentrenado).', 'Línea de umbral mínimo y aviso cuando el modelo cae por debajo.', 'F1 por gas para ver qué gases sufren más la deriva.', 'Notas para distinguir deriva real de cambios en la mezcla de gases.'],
    responsable="src/drift_analysis.py → evolucion_por_lote() (Lucía Díez)",
)
