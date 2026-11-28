"""Sensor Explorer: exploración interactiva de las mediciones.

Responsable: Persona 3 (Iria).
Funciones públicas: ninguna (es una página de Streamlit).

Estructura de la página:
  1. Filtros en la barra lateral -> tabla "filtrados"
  2. KPIs de lo que queda tras filtrar
  3. Cuatro pestañas de Iria: mediciones por gas, gases por lote, sensores y comparador libre
  4. Cinco pestañas de la Persona 1 (Lucía Barañano), cada una es una llamada a
     components/eda_panels.py: PCA, correlación y redundancia, atípicos y calidad,
     deriva por sensor y selección de sensores
"""
import plotly.express as px
import streamlit as st

from components import theme as t
from components.datos import (CARACTERISTICAS, N_CARACTERISTICAS, N_SENSORES,
                              cargar_datos, columna, nombre_legible)
from components.eda_panels import (panel_calidad, panel_correlaciones, panel_deriva_sensores,
                                   panel_pca, panel_seleccion_sensores)
from components.ui import (cabecera, configurar_pagina, etiqueta, fila_kpis,
                           grafico, nota)

configurar_pagina("Sensor Explorer")
datos = cargar_datos()

COLOR_GAS = dict(color_discrete_map=t.COLORES_GAS,
                 category_orders={"gas_name": t.ORDEN_GASES})

with st.sidebar:
    etiqueta("Filtros")
    gases = st.pills("Gases", t.ORDEN_GASES, selection_mode="multi", default=t.ORDEN_GASES) or []
    lote_min, lote_max = st.slider("Lotes", 1, 10, (1, 10),
                                   help="Los lotes están en orden temporal: el 1 es el mes 0 y el 10 el mes 36.")
    sensores = st.pills("Sensores", list(range(1, N_SENSORES + 1)), selection_mode="multi",
                        default=list(range(1, N_SENSORES + 1)),
                        format_func=lambda s: f"S{s:02d}") or []
    caracteristica = st.selectbox("Característica del sensor", list(CARACTERISTICAS),
                                  format_func=lambda c: CARACTERISTICAS[c],
                                  help="Cada sensor da 8 valores por medición. El ΔR es el cambio "
                                       "de resistencia; las EMA resumen la subida y la bajada de la señal.")
    conc_lo, conc_hi = float(datos["concentration"].min()), float(datos["concentration"].max())
    conc_min, conc_max = st.slider("Concentración (ppmv)", conc_lo, conc_hi, (conc_lo, conc_hi), step=0.5)

filtro = (
    datos["gas_name"].isin(gases)
    & datos["batch"].between(lote_min, lote_max)
    & datos["concentration"].between(conc_min, conc_max)
)
filtrados = datos[filtro]

cabecera("01 - Exploración", "Exploración <em>De Sensor</em>",
         "Filtra las mediciones en la barra lateral y mira cómo responden los 16 sensores a cada gas.")

if filtrados.empty or not sensores:
    st.warning("Con estos filtros no queda ninguna medición (o ningún sensor). Prueba a ampliarlos.")
    st.stop()

st.html('<div style="height:1rem"></div>')
fila_kpis([
    {"valor": f"{len(filtrados):,}".replace(",", "."), "etiqueta": "mediciones filtradas",
     "detalle": f"{len(filtrados) / len(datos):.0%} del total", "color": t.CIAN},
    {"valor": filtrados["gas_name"].nunique(), "etiqueta": "gases", "color": t.COLORES_GAS["Acetona"]},
    {"valor": filtrados["batch"].nunique(), "etiqueta": "lotes", "detalle": f"del {lote_min} al {lote_max}",
     "color": t.NARANJA},
    {"valor": len(sensores), "etiqueta": "sensores", "detalle": CARACTERISTICAS[caracteristica],
     "color": t.COLORES_GAS["Etileno"]},
])
st.html('<div style="height:1.2rem"></div>')

(pestana_gas, pestana_lote, pestana_sensor, pestana_libre,
 pestana_pca, pestana_corr, pestana_calidad, pestana_deriva, pestana_seleccion) = st.tabs(
    ["Mediciones por gas", "Gases por lote", "Sensores", "Comparador libre",
     "PCA", "Correlación y redundancia", "Atípicos y calidad", "Deriva por sensor", "Selección de sensores"]
)

with pestana_gas:
    izquierda, derecha = st.columns(2, gap="large")

    conteo = filtrados["gas_name"].value_counts().reindex(t.ORDEN_GASES).dropna().reset_index()
    conteo.columns = ["gas_name", "mediciones"]
    with izquierda:
        fig = px.bar(conteo.sort_values("mediciones"), x="mediciones", y="gas_name",
                     color="gas_name", orientation="h", text="mediciones", **COLOR_GAS,
                     title="Mediciones por gas")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, yaxis_title=None, xaxis_title="Nº de mediciones",
                          xaxis_range=[0, conteo["mediciones"].max() * 1.15])
        grafico(fig, alto=380)

    with derecha:
        fig = px.box(filtrados, x="gas_name", y="concentration", color="gas_name", **COLOR_GAS,
                     log_y=True, points=False, title="Concentración por gas (escala log)")
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="ppmv")
        grafico(fig, alto=380)

    mas = conteo.loc[conteo["mediciones"].idxmax()]
    menos = conteo.loc[conteo["mediciones"].idxmin()]
    nota(f"El gas con más mediciones es <b>{mas['gas_name']}</b> ({int(mas['mediciones'])}) y el que menos "
         f"<b>{menos['gas_name']}</b> ({int(menos['mediciones'])}). Las clases <b>no están equilibradas</b>: "
         "por eso, al evaluar los modelos, conviene mirar el macro-F1 y no solo el accuracy. "
         "La concentración va en escala logarítmica porque abarca desde 1 hasta 1.000 ppmv.")

with pestana_lote:
    modo = st.segmented_control("Mostrar", ["Recuento", "Porcentaje"], default="Recuento")
    por_lote = filtrados.groupby(["batch", "gas_name"]).size().reset_index(name="mediciones")
    if modo == "Porcentaje":
        por_lote["mediciones"] = por_lote["mediciones"] / por_lote.groupby("batch")["mediciones"].transform("sum") * 100

    fig = px.bar(por_lote, x="batch", y="mediciones", color="gas_name", **COLOR_GAS,
                 title="Composición de cada lote (orden temporal)")
    fig.update_layout(barmode="stack", bargap=0.25, legend_title=None,
                      xaxis=dict(title="Lote", tickmode="linear", dtick=1),
                      yaxis_title="% del lote" if modo == "Porcentaje" else "Nº de mediciones")
    grafico(fig, alto=430)

    tabla = filtrados.pivot_table(index="batch", columns="gas_name", values="gas", aggfunc="size", fill_value=0)
    ausencias = [f"{gas} en los lotes {', '.join(map(str, tabla.index[tabla[gas] == 0]))}"
                 for gas in tabla.columns if (tabla[gas] == 0).any()]
    totales = filtrados["batch"].value_counts()
    texto = (f"El lote más grande es el <b>{totales.idxmax()}</b> ({totales.max()} mediciones) y el más "
             f"pequeño el <b>{totales.idxmin()}</b> ({totales.min()}). ")
    if ausencias:
        texto += "Faltan gases: <b>" + "; ".join(ausencias) + "</b>. "
    texto += ("Si un lote tiene otra mezcla de gases, su rendimiento puede cambiar <b>sin que haya deriva</b>: "
              "hay que tenerlo en cuenta en el Drift Monitor.")
    nota(texto)

with pestana_sensor:
    nombre_car = CARACTERISTICAS[caracteristica]
    columnas_sensor = {f"S{s:02d}": columna(s, caracteristica) for s in sorted(sensores)}

    medianas = filtrados.groupby("gas_name")[list(columnas_sensor.values())].median()
    medianas = medianas.reindex([g for g in t.ORDEN_GASES if g in medianas.index])
    medianas.columns = list(columnas_sensor.keys())
    huella = (medianas - medianas.mean()) / medianas.std(ddof=0).replace(0, 1)

    fig = px.imshow(huella, color_continuous_scale=t.ESCALA_DIVERGENTE, zmin=-2, zmax=2, aspect="auto",
                    labels=dict(x="Sensor", y="", color="z"),
                    title=f"Huella de cada gas · {nombre_car} (mediana normalizada por sensor)")
    fig.update_traces(hovertemplate="%{y} · %{x}<br>z = %{z:.2f}<extra></extra>")
    grafico(fig, alto=360)
    nota("Cada columna es un sensor. <b>Cian</b>: ese gas da una respuesta más alta que la media de los gases; "
         "<b>naranja</b>: más baja. Si los colores cambian mucho entre filas, ese sensor <b>distingue bien</b> "
         "los gases. Como cada sensor tiene su propia escala, se normaliza columna a columna.")

    izquierda, derecha = st.columns([1, 3], gap="large", vertical_alignment="top")
    with izquierda:
        sensor_elegido = st.selectbox("Sensor a analizar", list(columnas_sensor.keys()))
        escala_log = st.toggle("Eje Y logarítmico", value=False,
                               help="Útil si hay valores extremos. Solo funciona con valores positivos.")
    col_elegida = columnas_sensor[sensor_elegido]
    if escala_log and (filtrados[col_elegida] <= 0).any():
        escala_log = False
        with izquierda:
            st.caption("Esta característica tiene valores negativos: se muestra en escala lineal.")

    with derecha:
        fig = px.box(filtrados, x="gas_name", y=col_elegida, color="gas_name", **COLOR_GAS,
                     points=False, log_y=escala_log,
                     title=f"{sensor_elegido} · {nombre_car}: respuesta por gas")
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=nombre_car)
        grafico(fig, alto=360)

    evolucion = filtrados.groupby(["batch", "gas_name"])[col_elegida].median().reset_index()
    fig = px.line(evolucion, x="batch", y=col_elegida, color="gas_name", markers=True, **COLOR_GAS,
                  title=f"{sensor_elegido} · mediana por lote (¿cambia con el tiempo?)")
    fig.update_layout(legend_title=None, xaxis=dict(title="Lote", dtick=1), yaxis_title=nombre_car)
    grafico(fig, alto=380)
    nota("Si un mismo gas da valores muy distintos según el lote, el sensor está <b>derivando</b>: "
         "el modelo aprendió una huella que ya no es la misma. Ojo: la concentración también varía entre lotes, "
         "así que filtra un rango estrecho de concentración para comparar de forma más justa.",
         titulo="Primer vistazo a la deriva", color=t.NARANJA)

with pestana_libre:
    opciones = ["concentration", "batch"] + [
        columna(s, c) for s in sorted(sensores) for c in range(1, N_CARACTERISTICAS + 1)
    ]
    c1, c2, c3, c4 = st.columns([3, 3, 2, 2], vertical_alignment="bottom")
    with c1:
        eje_x = st.selectbox("Variable X", opciones, index=2, format_func=nombre_legible)
    with c2:
        indice_y = min(2 + N_CARACTERISTICAS, len(opciones) - 1)
        eje_y = st.selectbox("Variable Y", opciones, index=indice_y, format_func=nombre_legible)
    with c3:
        color_por = st.segmented_control("Color", ["Gas", "Lote"], default="Gas")
    with c4:
        log_ejes = st.toggle("Ejes logarítmicos", value=False)

    if color_por == "Lote":
        estilo_color = dict(color="batch", color_continuous_scale=["#1F6F8F", t.CIAN, t.TEXTO])
    else:
        estilo_color = dict(color="gas_name", **COLOR_GAS)

    puede_log_x = (filtrados[eje_x] > 0).all()
    puede_log_y = (filtrados[eje_y] > 0).all()

    fig = px.scatter(filtrados, x=eje_x, y=eje_y, opacity=0.55, render_mode="webgl",
                     log_x=log_ejes and puede_log_x, log_y=log_ejes and puede_log_y,
                     hover_data={"gas_name": True, "batch": True, "concentration": True},
                     labels={eje_x: nombre_legible(eje_x), eje_y: nombre_legible(eje_y),
                             "gas_name": "Gas", "batch": "Lote", "concentration": "ppmv"},
                     **estilo_color)
    fig.update_traces(marker=dict(size=5))
    fig.update_layout(legend_title=None)
    grafico(fig, alto=540)
    if log_ejes and not (puede_log_x and puede_log_y):
        st.caption("Algún eje tiene valores negativos o cero y se ha dejado en escala lineal.")

    r = filtrados[eje_x].rank().corr(filtrados[eje_y].rank())
    if abs(r) >= 0.7:
        fuerza = "fuerte"
    elif abs(r) >= 0.4:
        fuerza = "moderada"
    else:
        fuerza = "débil"
    sentido = "suben juntas" if r > 0 else "cuando una sube, la otra baja"
    nota(f"Correlación de Spearman: <b>{r:.2f}</b> (relación <b>{fuerza}</b>; {sentido}). "
         "Si dos variables están muy correlacionadas, aportan información parecida al modelo. "
         "Si los colores forman <b>grupos separados</b>, esas dos variables ya ayudan a distinguir gases. "
         "Colorea por lote para ver si los puntos se desplazan con el tiempo.")

# --- Pestañas de la Persona 1: los cálculos están en src/exploratory_analysis.py ---
with pestana_pca:
    panel_pca(filtrados)

with pestana_corr:
    panel_correlaciones(filtrados)

with pestana_calidad:
    panel_calidad(filtrados)

with pestana_deriva:
    panel_deriva_sensores(filtrados)

with pestana_seleccion:
    panel_seleccion_sensores(filtrados)

st.caption("Nota: los nombres de los gases siguen `GAS_NAMES` de src/contracts.py "
           "(codificación comprobada con los recuentos publicados, ver data/README.md).")
