"""Piezas de interfaz reutilizables de SmartNose (cabeceras, tarjetas, notas...).

Responsable: Persona 3 (Iria).

Idea general: cada función devuelve o pinta un trozo de HTML con clases CSS
("sn-tarjeta", "sn-kpi"...). El aspecto de esas clases se define UNA vez en
ESTILO_CSS, así todas las páginas se ven iguales.

Uso típico al principio de cada página:

    from components.ui import configurar_pagina, cabecera
    configurar_pagina("Sensor Explorer", "🔬")
    cabecera("01 · Exploración", "Sensor Explorer", "Texto de introducción")
"""
from pathlib import Path

import streamlit as st

from components import theme as t

CARPETA_ASSETS = Path(__file__).resolve().parents[1] / "assets"

ESTILO_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700;9..40,800&display=swap');

:root {{
  --sn-fondo: {t.FONDO};
  --sn-tarjeta: {t.TARJETA};
  --sn-borde: {t.BORDE};
  --sn-texto: {t.TEXTO};
  --sn-suave: {t.TEXTO_SUAVE};
  --sn-apagado: {t.TEXTO_APAGADO};
  --sn-cian: {t.CIAN};
  --sn-naranja: {t.NARANJA};
  --sn-verde: {t.VERDE};
}}

/* Fondo con "estrellas" de colores, como en las diapositivas */
[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(1.5px 1.5px at 8% 12%, rgba(79,201,240,.55), transparent 60%),
    radial-gradient(1.5px 1.5px at 22% 78%, rgba(255,111,168,.45), transparent 60%),
    radial-gradient(1.5px 1.5px at 37% 34%, rgba(255,212,92,.40), transparent 60%),
    radial-gradient(1.5px 1.5px at 58% 8%, rgba(181,140,255,.45), transparent 60%),
    radial-gradient(1.5px 1.5px at 71% 63%, rgba(182,240,106,.40), transparent 60%),
    radial-gradient(1.5px 1.5px at 86% 22%, rgba(255,138,76,.45), transparent 60%),
    radial-gradient(1.5px 1.5px at 93% 88%, rgba(79,201,240,.40), transparent 60%),
    radial-gradient(1.5px 1.5px at 48% 92%, rgba(239,235,227,.30), transparent 60%),
    radial-gradient(900px 500px at 85% -10%, rgba(79,201,240,.07), transparent 70%),
    var(--sn-fondo);
  background-attachment: fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"] {{ padding-top: 2.2rem; max-width: 1320px; }}

/* Barra lateral */
[data-testid="stSidebar"] {{ border-right: 1px solid var(--sn-borde); }}
[data-testid="stSidebarNav"] a span {{ font-weight: 500; }}

/* Títulos con la tipografía de la presentación */
h1, h2, h3 {{ letter-spacing: -0.02em; font-weight: 800 !important; }}

/* ---- Cabecera de página: "SMARTNOSE ........ 01 · DATASET" ---- */
.sn-barra {{
  display: flex; justify-content: space-between; align-items: center;
  font-size: .72rem; font-weight: 700; letter-spacing: .28em;
  text-transform: uppercase; color: var(--sn-texto); margin-bottom: 1.2rem;
}}
.sn-barra .sn-seccion {{ color: var(--sn-cian); }}
.sn-titulo {{
  font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.05;
  letter-spacing: -0.03em; color: var(--sn-texto); margin: 0 0 .5rem 0;
}}
.sn-titulo em {{ font-style: normal; color: var(--sn-naranja); }}
.sn-subtitulo {{ color: var(--sn-suave); font-size: 1.05rem; max-width: 60ch; margin: 0; }}

/* ---- Portada (Home) ---- */
.sn-eyebrow {{
  font-size: .72rem; font-weight: 700; letter-spacing: .28em;
  text-transform: uppercase; color: var(--sn-cian);
}}
.sn-hero {{
  font-size: clamp(3.4rem, 9vw, 6.8rem); font-weight: 800; line-height: .92;
  letter-spacing: -0.045em; color: var(--sn-texto); margin: .6rem 0 1rem 0;
}}
.sn-hero span {{ color: var(--sn-cian); }}
.sn-pregunta {{ font-size: 1.35rem; color: var(--sn-texto); max-width: 28ch; line-height: 1.35; }}

/* ---- Títulos de sección ---- */
.sn-h2 {{
  display: flex; align-items: baseline; gap: .8rem;
  font-size: 1.35rem; font-weight: 800; color: var(--sn-texto);
  margin: 2.2rem 0 .9rem 0; letter-spacing: -0.02em;
}}
.sn-h2 .sn-num {{ font-size: .75rem; letter-spacing: .2em; color: var(--sn-cian); font-weight: 700; }}

/* ---- Tarjetas genéricas ---- */
.sn-tarjeta {{
  background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,0)), var(--sn-tarjeta);
  border: 1px solid var(--sn-borde); border-radius: 14px;
  padding: 1.1rem 1.2rem; height: 100%;
}}

/* ---- KPI: línea de color arriba + número grande (diapositiva 2) ---- */
.sn-kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }}
.sn-kpi {{ border-top: 2px solid var(--kpi-color, var(--sn-cian)); padding-top: .9rem; }}
.sn-kpi .valor {{ font-size: 2.6rem; font-weight: 800; line-height: 1; color: var(--sn-texto); letter-spacing: -0.03em; }}
.sn-kpi .etiqueta {{ color: var(--sn-suave); font-size: .85rem; margin-top: .45rem; }}
.sn-kpi .detalle {{ color: var(--sn-apagado); font-size: .75rem; margin-top: .15rem; }}

/* ---- Pasos "cómo funciona" ---- */
.sn-pasos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; }}
.sn-paso .num {{ color: var(--sn-cian); font-weight: 700; font-size: .8rem; letter-spacing: .15em; }}
.sn-paso .nombre {{ color: var(--sn-texto); font-weight: 700; font-size: 1.05rem; margin: .35rem 0 .3rem 0; }}
.sn-paso .texto {{ color: var(--sn-suave); font-size: .9rem; line-height: 1.45; }}

/* ---- Tarjetas de módulo con su estado ---- */
.sn-modulo .cabeza {{ display: flex; flex-direction: column; align-items: flex-start; gap: .55rem; }}
.sn-modulo .nombre {{ font-weight: 700; font-size: 1.1rem; color: var(--sn-texto); }}
.sn-modulo {{ min-height: 205px; }}
.sn-modulo .texto {{ color: var(--sn-suave); font-size: .88rem; margin: .5rem 0 .6rem 0; line-height: 1.45; }}
.sn-modulo .quien {{ color: var(--sn-apagado); font-size: .75rem; }}
.sn-estado {{
  display: inline-flex; align-items: center; gap: .4rem; white-space: nowrap;
  font-size: .72rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  padding: .22rem .6rem; border-radius: 999px; border: 1px solid currentColor;
}}
.sn-estado::before {{
  content: ""; width: 7px; height: 7px; border-radius: 50%;
  background: currentColor; box-shadow: 0 0 8px currentColor;
}}
.sn-estado.ok {{ color: var(--sn-verde); }}
.sn-estado.dev {{ color: var(--sn-cian); }}
.sn-estado.pend {{ color: var(--sn-naranja); }}

/* ---- Chips de gases con punto brillante ---- */
.sn-chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.sn-chip {{
  display: inline-flex; align-items: center; gap: .45rem; font-size: .85rem;
  padding: .3rem .75rem; border-radius: 999px; border: 1px solid var(--sn-borde);
  color: var(--sn-texto); background: rgba(255,255,255,.02);
}}
.sn-chip i {{ width: 9px; height: 9px; border-radius: 50%; background: var(--c); box-shadow: 0 0 10px var(--c); }}

/* ---- Notas de interpretación ---- */
.sn-nota {{
  border-left: 3px solid var(--nota-color, var(--sn-cian));
  background: rgba(79,201,240,.05); border-radius: 0 10px 10px 0;
  padding: .75rem 1rem; color: var(--sn-suave); font-size: .92rem; line-height: 1.5;
  margin: .4rem 0 1rem 0;
}}
.sn-nota b {{ color: var(--sn-texto); }}
.sn-nota .tit {{ display: block; font-size: .68rem; font-weight: 700; letter-spacing: .2em;
  text-transform: uppercase; color: var(--nota-color, var(--sn-cian)); margin-bottom: .25rem; }}

/* ---- Etiqueta pequeña tipo "FILTROS" en la barra lateral ---- */
.sn-etiqueta {{ font-size: .7rem; font-weight: 700; letter-spacing: .24em;
  text-transform: uppercase; color: var(--sn-cian); margin: .4rem 0 .2rem 0; }}

/* Pestañas (st.tabs) con subrayado cian, como la navegación de las diapositivas */
/* (el color del subrayado sale de primaryColor en .streamlit/config.toml) */
[data-testid="stTab"] p {{ font-weight: 600; font-size: .95rem; }}

/* Contenedores con borde (st.container(border=True)) como tarjetas */
[data-testid="stVerticalBlockBorderWrapper"] {{ background: rgba(22,27,39,.55); border-radius: 14px; }}

/* Botones de navegación (st.page_link) */
[data-testid="stPageLink"] a {{ border: 1px solid var(--sn-borde); border-radius: 10px; }}
[data-testid="stPageLink"] a:hover {{ border-color: var(--sn-cian); }}
</style>
"""


def configurar_pagina(titulo, icono="🔬"):
    """Primera llamada de cada página: título de pestaña, ancho, logo, CSS y plantilla de gráficos."""
    st.set_page_config(
        page_title=f"{titulo} · SmartNose",
        page_icon=str(CARPETA_ASSETS / "icono.svg"),
        layout="wide",
    )
    st.logo(str(CARPETA_ASSETS / "logo.svg"), size="large",
            icon_image=str(CARPETA_ASSETS / "icono.svg"))
    st.html(ESTILO_CSS)
    t.registrar_plantilla_plotly()


def cabecera(seccion, titulo, subtitulo=""):
    """Cabecera de página: barra "SMARTNOSE · sección", título grande y subtítulo.

    En el título puedes resaltar una palabra en naranja con <em>palabra</em>.
    """
    st.html(
        f'<div class="sn-barra"><span>SmartNose</span>'
        f'<span class="sn-seccion">{seccion}</span></div>'
        f'<h1 class="sn-titulo">{titulo}</h1>'
        f'<p class="sn-subtitulo">{subtitulo}</p>'
    )


def titulo_seccion(texto, numero=""):
    """Título de un bloque dentro de la página, con un número opcional ("01")."""
    st.html(f'<div class="sn-h2"><span class="sn-num">{numero}</span>{texto}</div>')


def fila_kpis(kpis):
    """Pinta una fila de indicadores.

    kpis es una lista de diccionarios, por ejemplo:
        [{"valor": "13.910", "etiqueta": "mediciones", "detalle": "...", "color": "#4FC9F0"}]
    """
    tarjetas = ""
    for kpi in kpis:
        color = kpi.get("color", t.CIAN)
        detalle = kpi.get("detalle", "")
        tarjetas += (
            f'<div class="sn-kpi" style="--kpi-color:{color}">'
            f'<div class="valor">{kpi["valor"]}</div>'
            f'<div class="etiqueta">{kpi["etiqueta"]}</div>'
            f'<div class="detalle">{detalle}</div></div>'
        )
    st.html(f'<div class="sn-kpis">{tarjetas}</div>')


def nota(texto, titulo="Cómo leerlo", color=None):
    """Caja de interpretación debajo de un gráfico. Admite <b>negritas</b> en HTML."""
    color = color or t.CIAN
    st.html(
        f'<div class="sn-nota" style="--nota-color:{color}">'
        f'<span class="tit">{titulo}</span>{texto}</div>'
    )


def chips_gases(gases=None):
    """Fila de "chips" con el color de cada gas (sirve de leyenda)."""
    gases = gases or t.ORDEN_GASES
    chips = ""
    for gas in gases:
        chips += f'<span class="sn-chip"><i style="--c:{t.COLORES_GAS[gas]}"></i>{gas}</span>'
    st.html(f'<div class="sn-chips">{chips}</div>')


def etiqueta(texto):
    """Rótulo pequeño en mayúsculas (útil en la barra lateral)."""
    st.html(f'<div class="sn-etiqueta">{texto}</div>')


def grafico(figura, alto=None):
    """Muestra un gráfico de Plotly respetando NUESTRA plantilla.

    Importante: theme=None evita que Streamlit sustituya nuestros colores
    por los suyos.
    """
    if alto is not None:
        figura.update_layout(height=alto)
    st.plotly_chart(figura, theme=None, config={"displaylogo": False})


def pagina_en_construccion(seccion, titulo, subtitulo, planes, responsable):
    """Página provisional con estilo: explica qué tendrá y quién la prepara."""
    cabecera(seccion, titulo, subtitulo)
    st.html('<div style="height:1.2rem"></div>')
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda:
        lista = "".join(f"<li style='margin:.35rem 0'>{p}</li>" for p in planes)
        st.html(
            '<div class="sn-tarjeta sn-modulo"><div class="cabeza">'
            '<span class="nombre">Qué tendrá esta pantalla</span>'
            '<span class="sn-estado dev">En desarrollo</span></div>'
            f'<ul class="texto" style="padding-left:1.1rem">{lista}</ul>'
            f'<div class="quien">Depende de: {responsable}</div></div>'
        )
    with derecha:
        nota("Esta pantalla se conectará a las funciones de <b>src/</b> en cuanto estén "
             "listas. Mientras tanto puedes explorar los datos en <b>Sensor Explorer</b>.",
             titulo="Estado", color=t.NARANJA)
        st.page_link("pages/1_Sensor_Explorer.py", label="Ir a Sensor Explorer", icon="🔬")
        st.page_link("Home.py", label="Volver a la portada", icon="🏠")
