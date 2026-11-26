"""Portada de SmartNose: qué es, cifras clave y estado de cada módulo.

Responsable: Persona 3 (Iria).
Funciones públicas: ninguna (es una página de Streamlit).
Ejecutar desde la raíz del proyecto:  streamlit run app/Home.py
"""
import streamlit as st

from components import theme as t
from components.datos import N_SENSORES, cargar_datos, modelo_disponible
from components.ui import chips_gases, configurar_pagina, fila_kpis, nota, titulo_seccion

configurar_pagina("Home")

datos = cargar_datos()
n_mediciones = len(datos)
n_gases = datos["gas"].nunique()
n_lotes = datos["batch"].nunique()


def numero_es(n):
    """Formato español con punto de miles: 13910 -> "13.910"."""
    return f"{n:,}".replace(",", ".")


izquierda, derecha = st.columns([3, 2], gap="large", vertical_alignment="center")
with izquierda:
    st.html(
        '<div class="sn-eyebrow">E3 · Grupo 15 · Analítica de datos para la industria</div>'
        '<div class="sn-hero">Smart<br><span>Nose</span></div>'
        '<div class="sn-pregunta">¿Hasta cuándo podemos fiarnos de una nariz electrónica?</div>'
    )
with derecha:
    nota(
        "Una nariz electrónica reconoce gases con <b>16 sensores químicos</b>. Con el tiempo "
        "esos sensores <b>envejecen</b> y su señal cambia: es la <b>deriva</b>. SmartNose vigila "
        "cuándo el modelo deja de acertar y comprueba si reentrenarlo lo arregla.",
        titulo="La idea",
    )
    chips_gases()

titulo_seccion("El dataset en cifras", "01")
fila_kpis([
    {"valor": numero_es(n_mediciones), "etiqueta": "mediciones",
     "detalle": "olfateos registrados", "color": t.CIAN},
    {"valor": N_SENSORES, "etiqueta": "sensores", "detalle": "de óxido metálico · 8 variables cada uno",
     "color": t.COLORES_GAS["Etileno"]},
    {"valor": n_gases, "etiqueta": "gases", "detalle": "puros, a distintas concentraciones",
     "color": t.COLORES_GAS["Acetona"]},
    {"valor": n_lotes, "etiqueta": "lotes", "detalle": "36 meses, en orden temporal",
     "color": t.NARANJA},
])

titulo_seccion("Cómo funciona SmartNose", "02")
pasos = [
    ("01", "Llega una muestra", "Un gas entra en la cámara a una concentración conocida (ppmv)."),
    ("02", "Reaccionan 16 sensores", "La resistencia de cada sensor cambia al contacto con el gas."),
    ("03", "Se forma una huella", "Cada gas deja un patrón distinto en las 128 variables."),
    ("04", "El modelo reconoce", "Un clasificador aprende a qué gas pertenece cada huella."),
    ("05", "Vigilamos la deriva", "Medimos lote a lote si sigue acertando… o si debe avisar."),
]
tarjetas = "".join(
    f'<div class="sn-tarjeta sn-paso"><div class="num">{num}</div>'
    f'<div class="nombre">{nombre}</div><div class="texto">{texto}</div></div>'
    for num, nombre, texto in pasos
)
st.html(f'<div class="sn-pasos">{tarjetas}</div>')

titulo_seccion("Estado de los módulos", "03")

hay_modelo = modelo_disponible()
modulos = [
    {"pagina": "pages/1_Sensor_Explorer.py", "icono": "🔬", "nombre": "Sensor Explorer",
     "texto": "Filtra por gas, lote, sensor y concentración y compara variables.",
     "estado": ("Operativo", "ok"), "quien": "Iria"},
    {"pagina": "pages/2_Drift_Monitor.py", "icono": "📉", "nombre": "Drift Monitor",
     "texto": "Rendimiento del modelo lote a lote: ¿cuándo empieza a fallar?",
     "estado": ("En desarrollo", "dev"), "quien": "Iria · usa los resultados de Lucía D."},
    {"pagina": "pages/3_Model_Lab.py", "icono": "🧪", "nombre": "Model Lab",
     "texto": "Elige algoritmo y parámetros, entrena y compara métricas.",
     "estado": ("En desarrollo", "dev"), "quien": "Iria · usa src/training.py"},
    {"pagina": "pages/4_Live_Prediction.py", "icono": "⚡", "nombre": "Live Prediction",
     "texto": "Envía una medición a la API de BentoML y muestra el gas predicho.",
     "estado": ("Modelo listo", "ok") if hay_modelo else ("Esperando modelo", "pend"),
     "quien": "Ane"},
]
columnas = st.columns(len(modulos))
for columna, modulo in zip(columnas, modulos):
    texto_estado, clase_estado = modulo["estado"]
    with columna:
        st.html(
            f'<div class="sn-tarjeta sn-modulo"><div class="cabeza">'
            f'<span class="nombre">{modulo["nombre"]}</span>'
            f'<span class="sn-estado {clase_estado}">{texto_estado}</span></div>'
            f'<div class="texto">{modulo["texto"]}</div>'
            f'<div class="quien">Responsable: {modulo["quien"]}</div></div>'
        )
        st.page_link(modulo["pagina"], label=f"Abrir {modulo['nombre']}",
                     icon=modulo["icono"], width="stretch")

st.html('<div style="height:2rem"></div>')
st.caption("Datos: UCI ML Repository · Gas Sensor Array Drift Dataset (id 270) · "
           "Universidad de Deusto 2026–27")
