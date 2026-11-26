"""Colores, fuentes y plantilla de gráficos de SmartNose.

Responsable: Persona 3 (Iria).
Todo sale de la presentación del Grupo 15. Si quieres cambiar un color,
cámbialo SOLO aquí y se actualiza en toda la app.
"""
import plotly.graph_objects as go
import plotly.io as pio

FONDO = "#0B0D13"
FONDO_PANEL = "#10141E"
TARJETA = "#161B27"
BORDE = "#262C3A"
REJILLA = "#232937"
TEXTO = "#EFEBE3"
TEXTO_SUAVE = "#AEB6C6"
TEXTO_APAGADO = "#6B7385"
CIAN = "#4FC9F0"
NARANJA = "#FF8A4C"
VERDE = "#B6F06A"

FUENTE = "DM Sans, Helvetica, Arial, sans-serif"

COLORES_GAS = {
    "Etanol": "#FF6FA8",
    "Etileno": "#B58CFF",
    "Amoníaco": "#4FC9F0",
    "Acetaldehído": "#FF8A4C",
    "Acetona": "#B6F06A",
    "Tolueno": "#FFD45C",
}
ORDEN_GASES = list(COLORES_GAS.keys())

ESCALA_CIAN = [[0.0, TARJETA], [0.5, "#1F6F8F"], [1.0, CIAN]]
ESCALA_DIVERGENTE = [[0.0, NARANJA], [0.5, TARJETA], [1.0, CIAN]]


def registrar_plantilla_plotly():
    """Crea la plantilla "smartnose" de Plotly y la deja como predeterminada.

    Así cada gráfico sale ya con fondo transparente, la fuente DM Sans y
    la rejilla discreta, sin repetir esa configuración en cada página.
    """
    eje = dict(
        automargin=True,
        gridcolor=REJILLA,
        zerolinecolor=BORDE,
        linecolor=BORDE,
        tickfont=dict(color=TEXTO_SUAVE, size=12),
        title=dict(font=dict(color=TEXTO_SUAVE, size=13)),
    )
    plantilla = go.layout.Template(
        layout=dict(
            font=dict(family=FUENTE, color=TEXTO, size=13),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=list(COLORES_GAS.values()),
            xaxis=eje,
            yaxis=eje,
            legend=dict(font=dict(color=TEXTO_SUAVE), bgcolor="rgba(0,0,0,0)", itemsizing="constant"),
            hoverlabel=dict(bgcolor=TARJETA, bordercolor=BORDE,
                            font=dict(family=FUENTE, color=TEXTO)),
            margin=dict(l=10, r=10, t=30, b=10),
            title=dict(font=dict(size=15, color=TEXTO)),
        )
    )
    pio.templates["smartnose"] = plantilla
    pio.templates.default = "smartnose"
