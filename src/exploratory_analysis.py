"""Análisis exploratorio reutilizable: lo usan el notebook y las pestañas de Streamlit.

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas:
  Distribuciones y calidad:
    resumen_lotes(datos), mediciones_por_gas(datos), resumen_concentraciones(datos),
    gases_ausentes_por_lote(datos), calidad_datos(datos), estadisticas_descriptivas(datos)
  Valores atípicos (solo se detectan, nunca se borran):
    resumen_outliers(datos), outliers_por_grupo(por_fila, datos, por)
  Correlaciones y redundancia entre sensores:
    matriz_correlacion(datos), redundancia_sensores(datos), pares_redundantes(matriz),
    grupos_redundantes(matriz)
  PCA y deriva:
    pca_proyeccion(datos), varianza_explicada(datos), deriva_pca(coords),
    deriva_por_sensor(datos, gas)
  Relevancia de sensores:
    importancia_features(datos), importancia_sensores(datos), importancia_por_lote(datos)

Todas devuelven DataFrames, Series o diccionarios (no dibujan nada: los gráficos están en
src/eda_plots.py). Ninguna modifica la tabla que reciben.
"""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif

from src.contracts import FEATURE_COLUMNS, GAS_NAMES, RANDOM_STATE
from src.preprocessing import (N_CARACTERISTICAS, N_SENSORES, columna, crear_preprocesador,
                               log_firmada, sensor_y_caracteristica)

# Nombres de los gases en el orden de sus códigos (1 a 6)
ORDEN_GASES = [GAS_NAMES[codigo] for codigo in sorted(GAS_NAMES)]


def _etiqueta_sensor(sensor):
    return f"S{sensor:02d}"


# ---------------------------------------------------------------------------
# Distribuciones y calidad de los datos
# ---------------------------------------------------------------------------
def resumen_lotes(datos):
    """Tabla de mediciones por lote (filas) y gas (columnas), con una columna "total"."""
    tabla = pd.crosstab(datos["batch"], datos["gas_name"])
    # Los gases se ordenan por código y se añaden con 0 los que no aparecen en ningún lote
    tabla = tabla.reindex(columns=ORDEN_GASES, fill_value=0)
    tabla["total"] = tabla.sum(axis=1)
    return tabla


def mediciones_por_gas(datos):
    """Nº y porcentaje de mediciones de cada gas (en el orden de los códigos)."""
    conteo = datos["gas_name"].value_counts().reindex(ORDEN_GASES, fill_value=0)
    tabla = conteo.rename("mediciones").reset_index()
    tabla.columns = ["gas_name", "mediciones"]
    total = tabla["mediciones"].sum()
    tabla["porcentaje"] = (tabla["mediciones"] / total * 100) if total else 0.0
    return tabla


def resumen_concentraciones(datos):
    """Por gas: nº de mediciones, nº de niveles de concentración distintos y mínimo/mediana/máximo (ppmv)."""
    grupos = datos.groupby("gas_name")["concentration"]
    tabla = pd.DataFrame({
        "mediciones": grupos.size(),
        "niveles_distintos": grupos.nunique(),
        "minimo": grupos.min(),
        "mediana": grupos.median(),
        "maximo": grupos.max(),
    })
    return tabla.reindex([g for g in ORDEN_GASES if g in tabla.index])


def gases_ausentes_por_lote(datos):
    """Diccionario {gas: [lotes en los que no aparece]}, solo con los gases que faltan en algún lote."""
    tabla = resumen_lotes(datos).drop(columns="total")
    ausentes = {}
    for gas in tabla.columns:
        lotes = [int(lote) for lote in tabla.index[tabla[gas] == 0]]
        if lotes:
            ausentes[gas] = lotes
    return ausentes


def calidad_datos(datos):
    """Comprobaciones básicas en un diccionario. Solo informa: no borra ni cambia nada."""
    X = datos[FEATURE_COLUMNS]
    tamanos = datos["batch"].value_counts()
    return {
        "n_filas": int(len(datos)),
        "n_features": len(FEATURE_COLUMNS),
        "n_lotes": int(datos["batch"].nunique()),
        "n_nulos": int(datos.isna().sum().sum()),
        "n_infinitos": int(np.isinf(X.to_numpy(dtype=float)).sum()),
        "n_duplicadas": int(datos.duplicated().sum()),
        "n_duplicadas_solo_features": int(datos.duplicated(subset=FEATURE_COLUMNS).sum()),
        "columnas_constantes": [c for c in FEATURE_COLUMNS if X[c].nunique() <= 1],
        "lote_mas_pequeno": (int(tamanos.idxmin()), int(tamanos.min())),
        "lote_mas_grande": (int(tamanos.idxmax()), int(tamanos.max())),
        "gases_ausentes": gases_ausentes_por_lote(datos),
    }


def estadisticas_descriptivas(datos, columnas=None):
    """Estadísticas de cada feature: media, desviación, cuartiles, asimetría, curtosis y % de negativos.

    La asimetría (skew) mide cuánto se alarga la cola: 0 es simétrica y valores grandes
    indican unos pocos valores muy altos. Es la señal de que conviene transformar (log).
    """
    columnas = list(columnas) if columnas is not None else FEATURE_COLUMNS
    X = datos[columnas]
    tabla = pd.DataFrame({
        "media": X.mean(),
        "desviacion": X.std(),
        "minimo": X.min(),
        "q25": X.quantile(0.25),
        "mediana": X.median(),
        "q75": X.quantile(0.75),
        "maximo": X.max(),
        "asimetria": X.skew(),
        "curtosis": X.kurt(),
        "negativos_pct": (X < 0).mean() * 100,
    })
    tabla.insert(0, "caracteristica", [sensor_y_caracteristica(c)[1] for c in columnas])
    tabla.insert(0, "sensor", [sensor_y_caracteristica(c)[0] for c in columnas])
    return tabla


# ---------------------------------------------------------------------------
# Valores atípicos (outliers): se detectan y se miden, NO se eliminan
# ---------------------------------------------------------------------------
def resumen_outliers(datos, factor=1.5, por_gas=False, columnas=None):
    """Marca los valores atípicos con la regla del rango intercuartílico (IQR).

    Un valor es atípico si está por debajo de Q1 - factor*IQR o por encima de Q3 + factor*IQR.
    Con por_gas=True los cuartiles se calculan dentro de cada gas (así no se marca como
    "raro" algo que solo es normal para ese gas).

    Devuelve (por_columna, por_fila):
      - por_columna: tabla con n_atipicos y porcentaje de cada feature
      - por_fila: Series con el % de features atípicas de cada medición (índice = el de datos)
    """
    columnas = list(columnas) if columnas is not None else FEATURE_COLUMNS
    valores = datos[columnas].to_numpy(dtype=float)
    marcas = np.zeros(valores.shape, dtype=bool)

    if por_gas:
        grupos = [np.flatnonzero((datos["gas"] == g).to_numpy()) for g in datos["gas"].unique()]
    else:
        grupos = [np.arange(len(datos))]
    for posiciones in grupos:
        sub = valores[posiciones]
        q1, q3 = np.percentile(sub, [25, 75], axis=0)
        iqr = q3 - q1
        marcas[posiciones] = (sub < q1 - factor * iqr) | (sub > q3 + factor * iqr)

    por_columna = pd.DataFrame({
        "n_atipicos": marcas.sum(axis=0),
        "porcentaje": marcas.mean(axis=0) * 100,
    }, index=columnas)
    por_columna.insert(0, "caracteristica", [sensor_y_caracteristica(c)[1] for c in columnas])
    por_columna.insert(0, "sensor", [sensor_y_caracteristica(c)[0] for c in columnas])
    por_fila = pd.Series(marcas.mean(axis=1) * 100, index=datos.index, name="pct_features_atipicas")
    return por_columna, por_fila


def outliers_por_grupo(por_fila, datos, por="batch"):
    """% medio de features atípicas por lote ("batch"), gas ("gas_name") o concentración."""
    return por_fila.groupby(datos[por]).mean()


# ---------------------------------------------------------------------------
# Correlaciones y redundancia entre sensores
# ---------------------------------------------------------------------------
def matriz_correlacion(datos, columnas=None, metodo="spearman"):
    """Matriz de correlación entre features.

    "spearman" (por defecto) compara posiciones en lugar de valores, así que los valores
    extremos le afectan mucho menos que a "pearson".
    """
    columnas = list(columnas) if columnas is not None else FEATURE_COLUMNS
    X = datos[columnas]
    if metodo == "spearman":
        return X.rank().corr(method="pearson")
    if metodo == "pearson":
        return X.corr(method="pearson")
    raise ValueError("metodo debe ser 'spearman' o 'pearson'")


def redundancia_sensores(datos, caracteristica=None, metodo="spearman"):
    """Correlación entre los 16 sensores (matriz 16x16 con etiquetas S01...S16).

    caracteristica = 1..8 compara los sensores usando solo esa característica.
    caracteristica = None promedia las 8 matrices (visión global).
    Una correlación cercana a 1 significa que dos sensores dicen casi lo mismo.
    """
    if caracteristica is None:
        caracteristicas = range(1, N_CARACTERISTICAS + 1)
    else:
        caracteristicas = [caracteristica]
    etiquetas = [_etiqueta_sensor(s) for s in range(1, N_SENSORES + 1)]
    total = np.zeros((N_SENSORES, N_SENSORES))
    for c in caracteristicas:
        columnas = [columna(s, c) for s in range(1, N_SENSORES + 1)]
        total += matriz_correlacion(datos, columnas, metodo).to_numpy()
    total /= len(list(caracteristicas))
    return pd.DataFrame(total, index=etiquetas, columns=etiquetas)


def pares_redundantes(matriz, umbral=0.95):
    """Pares (a, b) con |correlación| >= umbral, de mayor a menor. Cada par aparece una sola vez."""
    nombres = list(matriz.index)
    valores = matriz.to_numpy()
    filas = []
    for i in range(len(nombres)):
        for j in range(i + 1, len(nombres)):
            r = valores[i, j]
            if np.isfinite(r) and abs(r) >= umbral:
                filas.append((nombres[i], nombres[j], float(r)))
    tabla = pd.DataFrame(filas, columns=["a", "b", "correlacion"])
    return tabla.reindex(tabla["correlacion"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def grupos_redundantes(matriz, umbral=0.95):
    """Agrupa los sensores (o features) enlazados por pares redundantes.

    Devuelve una lista de grupos (listas de nombres) con 2 o más elementos. De cada grupo
    bastaría con quedarse con uno si hubiera que reducir sensores.
    """
    padre = {nombre: nombre for nombre in matriz.index}

    def raiz(x):
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    for fila in pares_redundantes(matriz, umbral).itertuples():
        padre[raiz(fila.a)] = raiz(fila.b)

    grupos = {}
    for nombre in matriz.index:
        grupos.setdefault(raiz(nombre), []).append(nombre)
    return [g for g in grupos.values() if len(g) > 1]


# ---------------------------------------------------------------------------
# PCA y deriva
# ---------------------------------------------------------------------------
def pca_proyeccion(datos, n_componentes=2, columnas=None, transformar_log=True, lotes_ajuste=None):
    """Proyecta las mediciones con PCA (Análisis de Componentes Principales).

    El escalado (y el log) y el PCA se ajustan solo con las filas de los lotes en
    lotes_ajuste (por defecto, todas). Con lotes_ajuste=[1, 2] el PCA "aprende" cómo eran los
    datos al principio y luego proyecta los lotes posteriores: si la nube se desplaza, es deriva.

    Devuelve (coords, info):
      - coords: batch, gas, gas_name, concentration, PC1..PCn (mismo índice que datos)
      - info: dict con varianza_explicada, varianza_acumulada, componentes (pesos de cada
        feature en cada componente) y lotes_ajuste
    """
    columnas = list(columnas) if columnas is not None else FEATURE_COLUMNS
    n_componentes = min(n_componentes, len(columnas))
    ajuste = datos if lotes_ajuste is None else datos[datos["batch"].isin(lotes_ajuste)]
    if len(ajuste) <= n_componentes:
        raise ValueError("Hay muy pocas mediciones en los lotes elegidos para ajustar el PCA")

    preproceso = crear_preprocesador(transformar_log).fit(ajuste[columnas])
    pca = PCA(n_components=n_componentes, random_state=RANDOM_STATE)
    pca.fit(preproceso.transform(ajuste[columnas]))
    proyeccion = pca.transform(preproceso.transform(datos[columnas]))

    nombres = [f"PC{i + 1}" for i in range(n_componentes)]
    coords = datos[["batch", "gas", "gas_name", "concentration"]].copy()
    for i, nombre in enumerate(nombres):
        coords[nombre] = proyeccion[:, i]
    info = {
        "varianza_explicada": pca.explained_variance_ratio_,
        "varianza_acumulada": np.cumsum(pca.explained_variance_ratio_),
        "componentes": pd.DataFrame(pca.components_.T, index=columnas, columns=nombres),
        "lotes_ajuste": sorted(int(b) for b in ajuste["batch"].unique()),
    }
    return coords, info


def varianza_explicada(datos, n_max=20, columnas=None, transformar_log=True):
    """Tabla con la varianza explicada por cada componente y la acumulada (para el gráfico de codo)."""
    columnas = list(columnas) if columnas is not None else FEATURE_COLUMNS
    n_max = min(n_max, len(columnas), len(datos))
    preproceso = crear_preprocesador(transformar_log)
    Z = preproceso.fit_transform(datos[columnas])
    pca = PCA(n_components=n_max, random_state=RANDOM_STATE).fit(Z)
    return pd.DataFrame({
        "componente": np.arange(1, n_max + 1),
        "varianza": pca.explained_variance_ratio_,
        "acumulada": np.cumsum(pca.explained_variance_ratio_),
    })


def deriva_pca(coords, referencia=None, componentes=("PC1", "PC2")):
    """Cuánto se aleja el centro de cada gas, lote a lote, de donde estaba en el lote de referencia.

    Devuelve una tabla con gas_name, batch, distancia (en unidades del PCA) y n (nº de mediciones).
    Solo aparecen los gases que existen en el lote de referencia. Ojo: si cambian la
    concentración o la mezcla entre lotes, parte del desplazamiento no es deriva (ver notebook).
    """
    componentes = list(componentes)
    if referencia is None:
        referencia = int(coords["batch"].min())
    centros = coords.groupby(["gas_name", "batch"])[componentes].mean()
    conteos = coords.groupby(["gas_name", "batch"]).size()
    filas = []
    for gas in ORDEN_GASES:
        if (gas, referencia) not in centros.index:
            continue
        base = centros.loc[(gas, referencia)].to_numpy()
        for lote in sorted(coords.loc[coords["gas_name"] == gas, "batch"].unique()):
            centro = centros.loc[(gas, lote)].to_numpy()
            filas.append((gas, int(lote), float(np.linalg.norm(centro - base)), int(conteos[(gas, lote)])))
    return pd.DataFrame(filas, columns=["gas_name", "batch", "distancia", "n"])


def deriva_por_sensor(datos, gas, caracteristica=1, referencia=None, rango_concentracion=None):
    """Cuánto cambia la respuesta de cada sensor, lote a lote, para UN gas.

    Para cada sensor y lote se calcula la mediana de |valor| de la característica elegida y
    se compara con la del lote de referencia con log2(mediana_lote / mediana_referencia):
      0 = igual que en la referencia, +1 = el doble, -1 = la mitad.
    rango_concentracion=(min, max) compara solo mediciones de concentración parecida, porque
    una concentración mayor también sube la respuesta aunque el sensor no derive.

    Devuelve una tabla con los sensores (S01...) en filas y los lotes en columnas.
    """
    sub = datos[datos["gas_name"] == gas]
    if rango_concentracion is not None:
        sub = sub[sub["concentration"].between(*rango_concentracion)]
    if sub.empty:
        raise ValueError(f"No hay mediciones de {gas} con ese rango de concentración")
    columnas = [columna(s, caracteristica) for s in range(1, N_SENSORES + 1)]
    medianas = sub[columnas].abs().groupby(sub["batch"]).median()
    medianas.columns = [_etiqueta_sensor(s) for s in range(1, N_SENSORES + 1)]
    if referencia is None:
        referencia = int(medianas.index.min())
    if referencia not in medianas.index:
        raise ValueError(f"No hay mediciones de {gas} en el lote de referencia {referencia}")
    base = medianas.loc[referencia].replace(0, np.nan)
    cambio = np.log2(medianas / base)
    return cambio.T.rename_axis(index="sensor", columns="lote")


# ---------------------------------------------------------------------------
# Relevancia de los sensores
# ---------------------------------------------------------------------------
def importancia_features(datos, metodo="anova", lotes=None, transformar_log=True):
    """Puntuación de cada una de las 128 features para distinguir los gases.

    metodo="anova": estadístico F de ANOVA (cuánto se separan las medias de los gases frente
        a lo que varían dentro de cada gas). Rápido y fácil de explicar.
    metodo="random_forest": importancia de Random Forest (100 árboles, semilla fija).
    lotes: lista de lotes con los que calcularla. IMPORTANTE: para elegir sensores y luego
        evaluar modelos, usa solo los lotes de entrenamiento; si no, se cuela información
        del futuro en la selección.
    """
    sub = datos if lotes is None else datos[datos["batch"].isin(lotes)]
    if sub["gas"].nunique() < 2:
        raise ValueError("Hacen falta al menos 2 gases distintos para calcular la importancia")
    X = sub[FEATURE_COLUMNS].to_numpy(dtype=float)
    if transformar_log:
        X = log_firmada(X)
    y = sub["gas"].to_numpy()

    if metodo == "anova":
        puntuacion, _ = f_classif(X, y)
        puntuacion = np.nan_to_num(puntuacion, nan=0.0, posinf=0.0)
    elif metodo == "random_forest":
        bosque = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
        puntuacion = bosque.fit(X, y).feature_importances_
    else:
        raise ValueError("metodo debe ser 'anova' o 'random_forest'")
    return pd.Series(puntuacion, index=FEATURE_COLUMNS, name="puntuacion")


def importancia_sensores(datos, metodo="anova", lotes=None, transformar_log=True):
    """Puntuación de cada sensor (índice 1-16): resume las 8 features de cada uno.

    ANOVA: media de la F de sus 8 features. Random Forest: suma de sus importancias.
    Devuelve una tabla con "puntuacion", "puntuacion_relativa" (1 = el mejor sensor) y "etiqueta".
    """
    por_feature = importancia_features(datos, metodo, lotes, transformar_log)
    sensores = np.arange(len(FEATURE_COLUMNS)) // N_CARACTERISTICAS + 1
    agrupada = por_feature.groupby(sensores)
    puntuacion = agrupada.sum() if metodo == "random_forest" else agrupada.mean()
    maximo = puntuacion.max()
    tabla = pd.DataFrame({
        "puntuacion": puntuacion,
        "puntuacion_relativa": puntuacion / maximo if maximo > 0 else puntuacion,
    })
    tabla.index.name = "sensor"
    tabla["etiqueta"] = [_etiqueta_sensor(s) for s in tabla.index]
    return tabla


def importancia_por_lote(datos, metodo="anova", transformar_log=True):
    """Importancia relativa de cada sensor calculada lote a lote (sensores en filas, lotes en columnas).

    Si el ranking cambia mucho entre lotes, el "mejor sensor" depende del momento: otra
    consecuencia de la deriva y una razón para no fiarse de una selección hecha una sola vez.
    """
    columnas = {}
    for lote in sorted(datos["batch"].unique()):
        sub = datos[datos["batch"] == lote]
        if sub["gas"].nunique() < 2:
            continue
        tabla = importancia_sensores(sub, metodo, transformar_log=transformar_log)
        columnas[int(lote)] = tabla["puntuacion_relativa"]
    resultado = pd.DataFrame(columnas)
    resultado.index = [_etiqueta_sensor(s) for s in resultado.index]
    return resultado.rename_axis(index="sensor", columns="lote")
