"""Gráficos interactivos (Plotly) del análisis exploratorio, reutilizables en Streamlit.

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: fig_mediciones_por_gas, fig_gas_por_lote, fig_concentracion,
    fig_histograma, fig_correlacion, fig_outliers_por_columna, fig_outliers_por_lote,
    fig_outliers_vs_concentracion, fig_pca, fig_varianza, fig_pca_centroides, fig_deriva_pca,
    fig_deriva_sensor, fig_importancia, fig_importancia_por_lote.

Cada función recibe una tabla (casi siempre la que devuelve src/exploratory_analysis.py) y
devuelve una figura de Plotly. No usa Streamlit: en la app se muestra con
components.ui.grafico(fig) y en el notebook con fig.show().
Los colores de los gases son los mismos que app/components/theme.py.
"""
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.exploratory_analysis import ORDEN_GASES, resumen_lotes
from src.preprocessing import CARACTERISTICAS, log_firmada

COLORES_GAS = {
    "Etanol": "#FF6FA8",
    "Etileno": "#B58CFF",
    "Amoníaco": "#4FC9F0",
    "Acetaldehído": "#FF8A4C",
    "Acetona": "#B6F06A",
    "Tolueno": "#FFD45C",
}
CIAN = "#4FC9F0"
NARANJA = "#FF8A4C"
ESCALA_CIAN = [[0.0, "#161B27"], [0.5, "#1F6F8F"], [1.0, CIAN]]
ESCALA_DIVERGENTE = [[0.0, NARANJA], [0.5, "#2A3142"], [1.0, CIAN]]
ESCALA_LOTES = ["#1F6F8F", CIAN, "#EFEBE3"]

_COLOR_GAS = dict(color_discrete_map=COLORES_GAS, category_orders={"gas_name": ORDEN_GASES})


def fig_mediciones_por_gas(tabla):
    """Barras horizontales con el nº de mediciones de cada gas. tabla = mediciones_por_gas(datos)."""
    fig = px.bar(tabla, x="mediciones", y="gas_name", color="gas_name", orientation="h",
                 text="mediciones", title="Mediciones por gas", **_COLOR_GAS)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(showlegend=False, yaxis_title=None, xaxis_title="Nº de mediciones")
    return fig


def fig_gas_por_lote(datos, porcentaje=False):
    """Barras apiladas: de qué gases se compone cada lote (el orden de los lotes es el del tiempo)."""
    cuentas = resumen_lotes(datos).drop(columns="total")
    largo = cuentas.reset_index().melt(id_vars="batch", var_name="gas_name", value_name="mediciones")
    if porcentaje:
        totales = largo.groupby("batch")["mediciones"].transform("sum")
        largo["mediciones"] = largo["mediciones"] / totales * 100
    fig = px.bar(largo, x="batch", y="mediciones", color="gas_name",
                 title="Composición de cada lote (orden temporal)", **_COLOR_GAS)
    fig.update_layout(barmode="stack", legend_title=None,
                      xaxis=dict(title="Lote", tickmode="linear", dtick=1),
                      yaxis_title="% del lote" if porcentaje else "Nº de mediciones")
    return fig


def fig_concentracion(datos):
    """Cajas de la concentración (ppmv) de cada gas, en escala logarítmica."""
    fig = px.box(datos, x="gas_name", y="concentration", color="gas_name", log_y=True,
                 points=False, title="Concentración por gas (escala log)", **_COLOR_GAS)
    fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="ppmv")
    return fig


def fig_histograma(datos, columna, transformar_log=False, nbins=60):
    """Histograma de una feature, coloreado por gas. Con transformar_log=True usa sign(x)*log(1+|x|)."""
    tabla = datos[[columna, "gas_name"]].copy()
    if transformar_log:
        tabla[columna] = log_firmada(tabla[columna].to_numpy())
    titulo = f"{columna}: distribución" + (" (log firmada)" if transformar_log else " (valores originales)")
    fig = px.histogram(tabla, x=columna, color="gas_name", nbins=nbins, barmode="overlay",
                       opacity=0.65, title=titulo, **_COLOR_GAS)
    fig.update_layout(legend_title=None, yaxis_title="Nº de mediciones")
    return fig


def fig_correlacion(matriz, titulo="Correlación", mostrar_valores=False):
    """Mapa de calor de una matriz de correlación (de -1 a 1)."""
    fig = px.imshow(matriz, zmin=-1, zmax=1, color_continuous_scale=ESCALA_DIVERGENTE,
                    aspect="auto", title=titulo, text_auto=".2f" if mostrar_valores else False)
    fig.update_layout(coloraxis_colorbar=dict(title="r"))
    return fig


def fig_outliers_por_columna(por_columna):
    """Mapa de calor del % de valores atípicos: sensores en filas y las 8 características en columnas."""
    tabla = por_columna.pivot(index="sensor", columns="caracteristica", values="porcentaje")
    tabla.index = [f"S{s:02d}" for s in tabla.index]
    tabla.columns = [CARACTERISTICAS[c] for c in tabla.columns]
    fig = px.imshow(tabla, color_continuous_scale=ESCALA_CIAN, aspect="auto",
                    title="% de valores atípicos por sensor y característica")
    fig.update_layout(coloraxis_colorbar=dict(title="%"))
    return fig


def fig_outliers_por_lote(medias):
    """Barras con el % medio de features atípicas de cada lote. medias = outliers_por_grupo(..., "batch")."""
    tabla = medias.rename("porcentaje").reset_index()
    tabla.columns = ["batch", "porcentaje"]
    fig = px.bar(tabla, x="batch", y="porcentaje", title="Valores atípicos por lote")
    fig.update_traces(marker_color=NARANJA)
    fig.update_layout(xaxis=dict(title="Lote", tickmode="linear", dtick=1),
                      yaxis_title="% de features atípicas (media)")
    return fig


def fig_outliers_vs_concentracion(por_fila, datos):
    """Dispersión: concentración frente al % de features atípicas de cada medición."""
    tabla = datos[["concentration", "gas_name"]].copy()
    tabla["pct_atipicas"] = por_fila.to_numpy()
    fig = px.scatter(tabla, x="concentration", y="pct_atipicas", color="gas_name", opacity=0.5,
                     log_x=True, render_mode="webgl",
                     title="¿Los atípicos son concentraciones altas?", **_COLOR_GAS)
    fig.update_layout(legend_title=None, xaxis_title="Concentración (ppmv, log)",
                      yaxis_title="% de features atípicas")
    return fig


def fig_pca(coords, color_por="gas_name", x="PC1", y="PC2", info=None):
    """Nube de puntos del PCA. color_por: "gas_name", "batch" o "concentration".

    Si pasas info (la que devuelve pca_proyeccion), los ejes muestran el % de varianza explicada.
    """
    opciones = dict(opacity=0.6, render_mode="webgl",
                    hover_data={"gas_name": True, "batch": True, "concentration": True})
    if color_por == "gas_name":
        fig = px.scatter(coords, x=x, y=y, color="gas_name", **_COLOR_GAS, **opciones)
    elif color_por == "concentration":
        fig = px.scatter(coords, x=x, y=y, color="concentration", color_continuous_scale=ESCALA_LOTES,
                         **opciones)
    else:
        fig = px.scatter(coords, x=x, y=y, color="batch", color_continuous_scale=ESCALA_LOTES, **opciones)
    fig.update_traces(marker=dict(size=5))
    titulo_x, titulo_y = x, y
    if info is not None:
        varianza = info["varianza_explicada"]
        titulo_x = f"{x} ({varianza[int(x[2:]) - 1]:.0%} de la varianza)"
        titulo_y = f"{y} ({varianza[int(y[2:]) - 1]:.0%} de la varianza)"
    fig.update_layout(legend_title=None, xaxis_title=titulo_x, yaxis_title=titulo_y)
    return fig


def fig_varianza(tabla):
    """Gráfico de codo: varianza de cada componente (barras) y acumulada (línea). tabla = varianza_explicada(datos)."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=tabla["componente"], y=tabla["varianza"] * 100, name="Por componente",
                         marker_color=CIAN))
    fig.add_trace(go.Scatter(x=tabla["componente"], y=tabla["acumulada"] * 100, name="Acumulada",
                             mode="lines+markers", line=dict(color=NARANJA)))
    fig.update_layout(title="Varianza explicada por el PCA", xaxis_title="Componente",
                      yaxis_title="% de la varianza", legend_title=None)
    return fig


def fig_pca_centroides(coords, x="PC1", y="PC2"):
    """Trayectoria del centro de cada gas a lo largo de los lotes (el número es el lote)."""
    centros = coords.groupby(["gas_name", "batch"])[[x, y]].mean().reset_index()
    centros = centros.sort_values(["gas_name", "batch"])
    fig = px.line(centros, x=x, y=y, color="gas_name", markers=True, text="batch",
                  title="Recorrido del centro de cada gas por lotes", **_COLOR_GAS)
    fig.update_traces(textposition="top center")
    fig.update_layout(legend_title=None)
    return fig


def fig_deriva_pca(tabla):
    """Distancia del centro de cada gas al de su lote de referencia. tabla = deriva_pca(coords)."""
    fig = px.line(tabla, x="batch", y="distancia", color="gas_name", markers=True,
                  title="Desplazamiento de cada gas respecto al lote de referencia", **_COLOR_GAS)
    fig.update_layout(legend_title=None, xaxis=dict(title="Lote", tickmode="linear", dtick=1),
                      yaxis_title="Distancia en el PCA")
    return fig


def fig_deriva_sensor(matriz, titulo="Cambio de la respuesta de cada sensor"):
    """Mapa de calor de deriva_por_sensor(): +1 = el doble que en la referencia, -1 = la mitad."""
    limite = float(np.nanmax(np.abs(matriz.to_numpy()))) if matriz.size else 1.0
    limite = min(max(limite, 1.0), 3.0)
    fig = px.imshow(matriz, zmin=-limite, zmax=limite, color_continuous_scale=ESCALA_DIVERGENTE,
                    aspect="auto", title=titulo)
    fig.update_layout(coloraxis_colorbar=dict(title="log2"))
    fig.update_xaxes(type="category")
    return fig


def fig_importancia(tabla, titulo="Importancia de cada sensor"):
    """Barras con la puntuación de cada sensor. tabla = importancia_sensores(...)."""
    fig = px.bar(tabla, x="etiqueta", y="puntuacion_relativa", title=titulo)
    fig.update_traces(marker_color=CIAN)
    fig.update_layout(xaxis_title=None, yaxis_title="Importancia relativa (1 = el mejor)")
    return fig


def fig_importancia_por_lote(matriz):
    """Mapa de calor de importancia_por_lote(): ¿el ranking de sensores cambia con el tiempo?"""
    fig = px.imshow(matriz, zmin=0, zmax=1, color_continuous_scale=ESCALA_CIAN, aspect="auto",
                    title="Importancia relativa de cada sensor en cada lote")
    fig.update_layout(coloraxis_colorbar=dict(title="relativa"))
    fig.update_xaxes(type="category")
    return fig
