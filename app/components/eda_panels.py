"""Paneles interactivos del análisis exploratorio (PCA, correlaciones, atípicos, deriva, sensores).

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: panel_pca(datos), panel_correlaciones(datos), panel_calidad(datos),
    panel_deriva_sensores(datos), panel_seleccion_sensores(datos).

Cada función pinta un bloque completo (controles + gráficos + una nota que explica cómo leerlo)
con los datos que recibe, así que se puede llamar dentro de cualquier pestaña:

    from components.eda_panels import panel_pca
    with st.tabs(["PCA"])[0]:
        panel_pca(filtrados)

Los cálculos viven en src/exploratory_analysis.py y los gráficos en src/eda_plots.py; aquí solo
hay interfaz. Los resultados pesados llevan @st.cache_data para no repetirse en cada clic.
Los textos de las notas se escriben a partir de los números calculados, no a mano.
"""
import streamlit as st

from components import theme as t
from components.datos import CARACTERISTICAS, N_CARACTERISTICAS, N_SENSORES, columna, nombre_legible
from components.ui import grafico, nota
from src import eda_plots as ep
from src import exploratory_analysis as ea

ETIQUETAS_COLOR = {"Gas": "gas_name", "Lote": "batch", "Concentración": "concentration"}


# --- Cálculos con caché (la clave de la caché es el contenido de las tablas y los parámetros) ---
@st.cache_data(show_spinner="Calculando el PCA...")
def _pca(datos, transformar_log, lotes_ajuste, n_componentes):
    return ea.pca_proyeccion(datos, n_componentes, transformar_log=transformar_log,
                             lotes_ajuste=list(lotes_ajuste))


@st.cache_data(show_spinner=False)
def _varianza(datos, transformar_log):
    return ea.varianza_explicada(datos, 20, transformar_log=transformar_log)


@st.cache_data(show_spinner="Buscando valores atípicos...")
def _outliers(datos, factor, por_gas):
    return ea.resumen_outliers(datos, factor=factor, por_gas=por_gas)


@st.cache_data(show_spinner="Calculando correlaciones...")
def _redundancia(datos, caracteristica, metodo):
    return ea.redundancia_sensores(datos, caracteristica, metodo)


@st.cache_data(show_spinner="Calculando correlaciones...")
def _correlacion_features(datos, metodo):
    return ea.matriz_correlacion(datos, metodo=metodo)


@st.cache_data(show_spinner="Calculando la importancia de los sensores...")
def _importancia(datos, metodo, lotes):
    return ea.importancia_sensores(datos, metodo, lotes=list(lotes))


@st.cache_data(show_spinner="Calculando la importancia lote a lote...")
def _importancia_lotes(datos, metodo):
    return ea.importancia_por_lote(datos, metodo)


def _gases_presentes(datos):
    return [g for g in ea.ORDEN_GASES if g in set(datos["gas_name"])]


# ---------------------------------------------------------------------------
def panel_pca(datos):
    """PCA coloreado por gas, lote o concentración, con control de con qué lotes se ajusta."""
    lotes = sorted(int(b) for b in datos["batch"].unique())
    if len(datos) < 10:
        st.warning("Hay muy pocas mediciones con estos filtros para calcular un PCA.")
        return

    c1, c2, c3 = st.columns([3, 2, 4], gap="large", vertical_alignment="bottom")
    with c1:
        color = st.segmented_control("Color", list(ETIQUETAS_COLOR), default="Gas", key="eda_pca_color") or "Gas"
    with c2:
        usar_log = st.toggle("Transformación log", value=True, key="eda_pca_log",
                             help="Aplica sign(x)·log(1+|x|) antes de escalar. Sin ella, unos pocos valores "
                                  "enormes dominan los primeros componentes.")
    with c3:
        if len(lotes) > 1:
            ultimo = st.select_slider("Ajustar el PCA con los lotes hasta el…", options=lotes, value=lotes[-1],
                                      key="eda_pca_lotes",
                                      help="Si eliges un lote anterior al último, el PCA solo 'aprende' de los lotes "
                                           "iniciales y los posteriores se proyectan sobre él (así se ve la deriva).")
        else:
            ultimo = lotes[-1]
    lotes_ajuste = tuple(b for b in lotes if b <= ultimo)

    n_comp = min(5, len(datos) - 1)
    coords, info = _pca(datos, usar_log, lotes_ajuste, n_comp)
    componentes = [f"PC{i}" for i in range(1, n_comp + 1)]

    c4, c5, _ = st.columns([1, 1, 4], gap="large")
    with c4:
        eje_x = st.selectbox("Eje X", componentes, index=0, key="eda_pca_x")
    with c5:
        eje_y = st.selectbox("Eje Y", componentes, index=min(1, n_comp - 1), key="eda_pca_y")

    fig = ep.fig_pca(coords, ETIQUETAS_COLOR[color], eje_x, eje_y, info)
    grafico(fig, alto=540)

    v = info["varianza_explicada"]
    texto = (f"Los dos primeros componentes resumen el <b>{(v[0] + v[1]):.0%}</b> de la información de las 128 "
             f"variables ({v[0]:.0%} el primero y {v[1]:.0%} el segundo). Cada punto es una medición. ")
    if color == "Gas":
        texto += "Si cada gas forma su propio grupo, las 128 variables bastan para distinguirlos. "
    elif color == "Lote":
        texto += "Si los colores de los lotes se desplazan o se separan, la respuesta de los sensores ha cambiado con el tiempo. "
    else:
        texto += "Si el color cambia de forma ordenada a lo largo de la nube, la concentración también mueve los puntos. "
    if len(lotes_ajuste) < len(lotes):
        texto += (f"El PCA se ha ajustado solo con los lotes {lotes_ajuste[0]}-{lotes_ajuste[-1]}: "
                  "los lotes posteriores aparecen fuera de donde 'aprendió', lo que apunta a <b>deriva</b>.")
    else:
        texto += "El PCA se ha ajustado con todos los lotes filtrados."
    nota(texto)

    izquierda, derecha = st.columns(2, gap="large")
    with izquierda:
        grafico(ep.fig_varianza(_varianza(datos, usar_log)), alto=360)
    with derecha:
        grafico(ep.fig_pca_centroides(coords, eje_x, eje_y), alto=360)

    if len(lotes) > 1:
        tabla = ea.deriva_pca(coords)
        if not tabla.empty:
            grafico(ep.fig_deriva_pca(tabla), alto=360)
            peor = tabla.loc[tabla["distancia"].idxmax()]
            nota(f"La mayor distancia respecto al lote {lotes[0]} es la de <b>{peor['gas_name']}</b> en el lote "
                 f"<b>{int(peor['batch'])}</b> ({peor['distancia']:.1f} unidades del PCA). Ojo: esta distancia "
                 "mezcla deriva real con cambios de concentración y de mezcla de gases entre lotes; "
                 "para separarlos, filtra un rango estrecho de concentración en la barra lateral.",
                 titulo="Cuidado al interpretarlo", color=t.NARANJA)


# ---------------------------------------------------------------------------
def panel_correlaciones(datos):
    """Correlación entre sensores y búsqueda de sensores redundantes."""
    if len(datos) < 10:
        st.warning("Hay muy pocas mediciones con estos filtros para calcular correlaciones.")
        return

    c1, c2, c3 = st.columns([3, 2, 3], gap="large", vertical_alignment="bottom")
    with c1:
        opciones = ["Todas (promedio)"] + [CARACTERISTICAS[c] for c in range(1, N_CARACTERISTICAS + 1)]
        elegida = st.selectbox("Característica con la que se comparan los sensores", opciones, key="eda_corr_car")
        caracteristica = None if elegida == opciones[0] else opciones.index(elegida)
    with c2:
        metodo = st.segmented_control("Método", ["Spearman", "Pearson"], default="Spearman", key="eda_corr_met") or "Spearman"
    with c3:
        umbral = st.slider("Umbral de redundancia (|r| ≥)", 0.80, 0.999, 0.95, 0.005, key="eda_corr_umbral")

    matriz = _redundancia(datos, caracteristica, metodo.lower())
    grafico(ep.fig_correlacion(matriz, "Correlación entre sensores", mostrar_valores=True), alto=560)

    pares = ea.pares_redundantes(matriz, umbral)
    grupos = ea.grupos_redundantes(matriz, umbral)
    if grupos:
        listado = "; ".join("{" + ", ".join(g) + "}" for g in grupos)
        sensores_grupo = sum(len(g) for g in grupos)
        nota(f"Con |r| ≥ {umbral} hay <b>{len(pares)}</b> pares redundantes. Los sensores se agrupan así: {listado}. "
             f"De cada grupo bastaría un sensor, así que {sensores_grupo} sensores podrían resumirse en "
             f"{len(grupos)}: quedarían <b>{N_SENSORES - sensores_grupo + len(grupos)}</b> de {N_SENSORES}. "
             "Esto es una pista, no una decisión: hay que comprobar con los modelos que no se pierde precisión.")
        st.dataframe(pares.rename(columns={"a": "Sensor A", "b": "Sensor B", "correlacion": "Correlación"}),
                     hide_index=True)
    else:
        nota(f"Con |r| ≥ {umbral} no hay sensores redundantes: cada uno aporta información distinta. "
             "Prueba a bajar el umbral.")

    with st.expander("Correlación entre las 128 variables (puede tardar unos segundos)"):
        if st.toggle("Calcular el mapa de 128 × 128", value=False, key="eda_corr_128"):
            grafico(ep.fig_correlacion(_correlacion_features(datos, metodo.lower()),
                                       "Correlación entre las 128 variables"), alto=640)
            st.caption("Las variables van en el orden del contrato: de 8 en 8 son un sensor (feature_1..8 = S01).")


# ---------------------------------------------------------------------------
def panel_calidad(datos):
    """Calidad de los datos, distribución de una variable y valores atípicos (sin eliminar nada)."""
    calidad = ea.calidad_datos(datos)
    ausentes = calidad["gases_ausentes"]
    detalle_ausentes = "; ".join(f"{g}: lotes {', '.join(map(str, l))}" for g, l in ausentes.items()) or "ninguno"
    texto = (f"<b>{calidad['n_nulos']}</b> valores nulos, <b>{calidad['n_duplicadas']}</b> filas duplicadas y "
             f"<b>{len(calidad['columnas_constantes'])}</b> variables constantes. Gases ausentes en algún lote: {detalle_ausentes}. "
             "Que no haya nulos ni duplicados <b>no</b> significa que los datos estén listos: "
             "la variación entre lotes es justo el fenómeno que queremos estudiar.")
    nota(texto, titulo="Calidad de los datos")

    st.markdown("**Distribución de una variable**")
    c1, c2, c3 = st.columns([2, 3, 2], gap="large", vertical_alignment="bottom")
    with c1:
        sensor = st.selectbox("Sensor", list(range(1, N_SENSORES + 1)), format_func=lambda s: f"S{s:02d}", key="eda_dist_sensor")
    with c2:
        car = st.selectbox("Característica", list(CARACTERISTICAS), format_func=lambda c: CARACTERISTICAS[c], key="eda_dist_car")
    with c3:
        log = st.toggle("Log firmada", value=False, key="eda_dist_log",
                        help="sign(x)·log(1+|x|): acerca los valores extremos al resto.")
    nombre = columna(sensor, car)
    grafico(ep.fig_histograma(datos, nombre, log), alto=380)
    asimetria = float(datos[nombre].skew())
    nota(f"La asimetría de {nombre_legible(nombre)} es <b>{asimetria:.2f}</b> "
         "(0 = simétrica; valores grandes = unos pocos valores muy altos). "
         "Activa la transformación log y compara: si la forma se acerca a una campana, el log ayuda al escalado.")

    st.markdown("**Valores atípicos (outliers)**")
    c4, c5 = st.columns([3, 3], gap="large", vertical_alignment="bottom")
    with c4:
        regla = st.segmented_control("Dónde se calculan los cuartiles", ["Todos los gases", "Dentro de cada gas"],
                                     default="Todos los gases", key="eda_out_regla") or "Todos los gases"
    with c5:
        factor = st.slider("Factor del IQR (más alto = menos atípicos)", 1.0, 5.0, 1.5, 0.5, key="eda_out_factor")
    por_columna, por_fila = _outliers(datos, factor, regla == "Dentro de cada gas")

    izquierda, derecha = st.columns(2, gap="large")
    with izquierda:
        grafico(ep.fig_outliers_por_columna(por_columna), alto=420)
    with derecha:
        grafico(ep.fig_outliers_por_lote(ea.outliers_por_grupo(por_fila, datos, "batch")), alto=420)
    grafico(ep.fig_outliers_vs_concentracion(por_fila, datos), alto=420)

    con_atipicos = float((por_fila > 0).mean() * 100)
    r = por_fila.corr(datos["concentration"], method="spearman")
    if r >= 0.4:
        lectura = ("Los atípicos <b>crecen con la concentración</b>: son respuestas fuertes de verdad, no errores. "
                   "Borrarlos quitaría justo las mediciones de más gas.")
    elif r > 0.1:
        lectura = "Hay una relación moderada con la concentración, así que parte de los atípicos son respuestas fuertes y no errores."
    else:
        lectura = "No hay una relación clara con la concentración."
    nota(f"El <b>{con_atipicos:.0f}%</b> de las mediciones tiene al menos una variable atípica. "
         f"Correlación (Spearman) entre el % de variables atípicas y la concentración: <b>{r:.2f}</b>. {lectura} "
         "Por eso no se elimina ninguna fila: se detectan y se tratan con la transformación log y el escalado.",
         titulo="Cómo leerlo", color=t.NARANJA)


# ---------------------------------------------------------------------------
def panel_deriva_sensores(datos):
    """Qué sensores cambian su respuesta con el tiempo, para un gas concreto."""
    gases = _gases_presentes(datos)
    lotes = sorted(int(b) for b in datos["batch"].unique())
    if not gases or len(lotes) < 2:
        st.info("Necesitas al menos dos lotes en los filtros para comparar la respuesta en el tiempo.")
        return

    c1, c2, c3 = st.columns([2, 3, 2], gap="large", vertical_alignment="bottom")
    with c1:
        gas = st.selectbox("Gas", gases, key="eda_der_gas")
    with c2:
        car = st.selectbox("Característica", list(CARACTERISTICAS), format_func=lambda c: CARACTERISTICAS[c], key="eda_der_car")
    with c3:
        referencia = st.selectbox("Lote de referencia", lotes, key="eda_der_ref")

    sub = datos[datos["gas_name"] == gas]
    conc_lo, conc_hi = float(sub["concentration"].min()), float(sub["concentration"].max())
    if conc_lo < conc_hi:
        rango = st.slider("Comparar solo mediciones con concentración entre (ppmv)", conc_lo, conc_hi,
                          (conc_lo, conc_hi), key="eda_der_rango",
                          help="Una concentración mayor también sube la respuesta. Un rango estrecho compara de forma más justa.")
    else:
        rango = (conc_lo, conc_hi)

    try:
        matriz = ea.deriva_por_sensor(datos, gas, car, referencia, rango)
    except ValueError as error:
        st.info(f"No se puede calcular con esta selección: {error}")
        return
    grafico(ep.fig_deriva_sensor(matriz, f"{gas} · {CARACTERISTICAS[car]}: cambio respecto al lote {referencia}"), alto=520)

    valores = matriz.drop(columns=referencia, errors="ignore").abs()
    if valores.notna().to_numpy().any():
        sensor_max = valores.max(axis=1).idxmax()
        lote_max = valores.loc[sensor_max].idxmax()
        cambio = float(matriz.loc[sensor_max, lote_max])
        veces = 2 ** abs(cambio)
        sentido = "más alta" if cambio > 0 else "más baja"
        nota(f"El mayor cambio es el de <b>{sensor_max}</b> en el lote <b>{lote_max}</b>: su respuesta es "
             f"unas <b>{veces:.1f} veces {sentido}</b> que en el lote {referencia}. "
             "<b>0</b> = igual que la referencia; <b>+1</b> = el doble; <b>−1</b> = la mitad. "
             "Si un sensor cambia mucho y otro casi nada, la deriva no afecta por igual a todo el array.")
    else:
        nota("Con esta selección solo hay datos del lote de referencia: amplía los filtros para ver otros lotes.")


# ---------------------------------------------------------------------------
def panel_seleccion_sensores(datos):
    """Qué sensores distinguen mejor los gases, calculado solo con los lotes de entrenamiento elegidos."""
    lotes = sorted(int(b) for b in datos["batch"].unique())
    if datos["gas_name"].nunique() < 2 or not lotes:
        st.info("Hacen falta al menos dos gases en los filtros para calcular la importancia de los sensores.")
        return

    c1, c2 = st.columns([2, 4], gap="large", vertical_alignment="bottom")
    with c1:
        metodo = st.segmented_control("Método", ["ANOVA", "Random Forest"], default="ANOVA", key="eda_imp_met") or "ANOVA"
    with c2:
        entrenamiento = st.multiselect("Lotes de entrenamiento (solo con ellos se calcula el ranking)", lotes,
                                       default=lotes[:min(3, len(lotes))], key="eda_imp_lotes",
                                       help="Para no filtrar información del futuro, el ranking debe usar solo lotes anteriores a los de prueba.")
    if not entrenamiento:
        st.info("Elige al menos un lote de entrenamiento.")
        return
    clave = "anova" if metodo == "ANOVA" else "random_forest"
    sub = datos[datos["batch"].isin(entrenamiento)]
    if sub["gas_name"].nunique() < 2:
        st.info("Con esos lotes solo hay un gas: elige otros lotes.")
        return

    ranking = _importancia(datos, clave, tuple(entrenamiento))
    grafico(ep.fig_importancia(ranking, f"Importancia de cada sensor ({metodo}, lotes {', '.join(map(str, entrenamiento))})"), alto=380)

    n = st.slider("¿Con cuántos sensores te quedarías?", 1, N_SENSORES, 8, key="eda_imp_n")
    mejores = ranking.sort_values("puntuacion", ascending=False).head(n)
    st.write("Elegidos: " + ", ".join(mejores["etiqueta"]))
    nota(f"Con los lotes {', '.join(map(str, entrenamiento))}, los {n} sensores más útiles según {metodo} son "
         f"{', '.join(mejores['etiqueta'])}. Es una puntuación <b>univariante</b> (mira cada sensor por separado), "
         "así que dos sensores redundantes pueden salir los dos arriba: contrasta este ranking con la pestaña de redundancia. "
         "Y calcula el ranking solo con lotes de entrenamiento.")

    st.markdown("**¿Cambia el ranking con el tiempo?**")
    grafico(ep.fig_importancia_por_lote(_importancia_lotes(datos, clave)), alto=480)
    nota("Cada columna es un lote y se normaliza para que 1 sea el mejor sensor de ese lote. Si los colores cambian de "
         "izquierda a derecha, el sensor 'mejor' <b>depende del momento</b>: una selección hecha con lotes antiguos "
         "puede dejar de ser la mejor, otra consecuencia de la deriva.",
         titulo="Cómo leerlo", color=t.NARANJA)
