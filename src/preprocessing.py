"""Preparación de la tabla limpia: columnas, división por lotes y preprocesado.

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: separar_xy(datos), columna(sensor, caracteristica),
    columnas_de_sensor(sensor), columnas_de_sensores(sensores, caracteristicas),
    nombre_legible(columna), dividir_por_lotes(datos, lotes_train, lotes_test),
    log_firmada(X), crear_preprocesador(transformar_log).

Idea clave: aquí NO se elimina ninguna fila. Solo se ofrecen herramientas para
separar X e y, elegir columnas, dividir por tiempo y escalar sin filtrar información
del futuro. El preprocesador se pensó para ser el primer paso del Pipeline que entrena
la Persona 2 (así la API aplica exactamente lo mismo que el entrenamiento).
"""
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.contracts import FEATURE_COLUMNS, N_FEATURES

# Las 128 features son 16 sensores x 8 características, ordenadas por sensor:
# feature_1..8 son del sensor 1, feature_9..16 del sensor 2, etc. (ver data/README.md)
CARACTERISTICAS = {
    1: "ΔR estacionario",
    2: "ΔR normalizado",
    3: "Subida EMA α=0,001",
    4: "Subida EMA α=0,01",
    5: "Subida EMA α=0,1",
    6: "Bajada EMA α=0,001",
    7: "Bajada EMA α=0,01",
    8: "Bajada EMA α=0,1",
}
N_CARACTERISTICAS = len(CARACTERISTICAS)
N_SENSORES = N_FEATURES // N_CARACTERISTICAS


def columna(sensor, caracteristica):
    """Nombre de la columna de un sensor (1-16) y una característica (1-8).

    columna(2, 1) -> "feature_9"
    """
    if not 1 <= sensor <= N_SENSORES:
        raise ValueError(f"El sensor debe estar entre 1 y {N_SENSORES}, no {sensor}")
    if not 1 <= caracteristica <= N_CARACTERISTICAS:
        raise ValueError(f"La característica debe estar entre 1 y {N_CARACTERISTICAS}, no {caracteristica}")
    numero = (sensor - 1) * N_CARACTERISTICAS + caracteristica
    return f"feature_{numero}"


def columnas_de_sensor(sensor):
    """Las 8 columnas de un sensor, en orden."""
    return [columna(sensor, c) for c in range(1, N_CARACTERISTICAS + 1)]


def columnas_de_sensores(sensores=None, caracteristicas=None):
    """Columnas de varios sensores y/o varias características, en el orden del contrato.

    sensores=None -> los 16. caracteristicas=None -> las 8.
    Ejemplo: columnas_de_sensores([1, 3], [1, 2]) -> feature_1, feature_2, feature_17, feature_18
    """
    if sensores is None:
        sensores = range(1, N_SENSORES + 1)
    if caracteristicas is None:
        caracteristicas = range(1, N_CARACTERISTICAS + 1)
    pedidas = {columna(s, c) for s in sensores for c in caracteristicas}
    # Devolvemos siempre en el orden de FEATURE_COLUMNS (el de la tabla y la API)
    return [col for col in FEATURE_COLUMNS if col in pedidas]


def sensor_y_caracteristica(nombre_columna):
    """Inversa de columna(): "feature_9" -> (2, 1)."""
    numero = int(nombre_columna.split("_")[1])
    sensor = (numero - 1) // N_CARACTERISTICAS + 1
    caracteristica = (numero - 1) % N_CARACTERISTICAS + 1
    return sensor, caracteristica


def nombre_legible(nombre_columna):
    """"feature_9" -> "S02 · ΔR estacionario". Otras columnas se devuelven igual."""
    if not nombre_columna.startswith("feature_"):
        return nombre_columna
    sensor, caracteristica = sensor_y_caracteristica(nombre_columna)
    return f"S{sensor:02d} · {CARACTERISTICAS[caracteristica]}"


def separar_xy(datos, columnas=None):
    """Devuelve (X, y): las features en el orden del contrato y el gas (código 1-6).

    columnas=None usa las 128 features. Con una lista (por ejemplo, de
    columnas_de_sensores) devuelve solo esas, pero siempre en el orden del contrato.
    No modifica la tabla original.
    """
    if columnas is None:
        columnas = FEATURE_COLUMNS
    else:
        desconocidas = [c for c in columnas if c not in FEATURE_COLUMNS]
        if desconocidas:
            raise ValueError(f"Columnas que no son features: {desconocidas[:3]}")
        columnas = [c for c in FEATURE_COLUMNS if c in set(columnas)]
    X = datos[columnas].copy()
    y = datos["gas"].copy()
    return X, y


def dividir_por_lotes(datos, lotes_train, lotes_test, permitir_futuro=False):
    """Separa la tabla en (train, test) usando los números de lote, nunca al azar.

    Comprueba que no haya lotes repetidos en train y test y que ningún lote de
    entrenamiento sea posterior a uno de prueba (eso sería entrenar con el futuro).
    Con permitir_futuro=True se salta solo esa segunda comprobación.
    """
    lotes_train = sorted(set(lotes_train))
    lotes_test = sorted(set(lotes_test))
    if not lotes_train or not lotes_test:
        raise ValueError("Hacen falta lotes de entrenamiento y de prueba")
    repetidos = set(lotes_train) & set(lotes_test)
    if repetidos:
        raise ValueError(f"Los lotes {sorted(repetidos)} están en train y en test")
    if not permitir_futuro and max(lotes_train) > min(lotes_test):
        raise ValueError(
            f"Fuga temporal: se entrena con el lote {max(lotes_train)} y se evalúa con el "
            f"lote {min(lotes_test)}, que es anterior. Usa permitir_futuro=True solo si es a propósito."
        )
    disponibles = set(datos["batch"].unique())
    faltan = (set(lotes_train) | set(lotes_test)) - disponibles
    if faltan:
        raise ValueError(f"No hay datos de los lotes {sorted(faltan)}")
    train = datos[datos["batch"].isin(lotes_train)].copy()
    test = datos[datos["batch"].isin(lotes_test)].copy()
    return train, test


def log_firmada(X):
    """sign(x) * log(1 + |x|): comprime los valores enormes y mantiene el signo.

    Las features tienen colas muy largas (la ΔR llega a cientos de miles mientras otras
    valen unas pocas unidades) y algunas son negativas, por eso no vale un log normal.
    Es una función definida en el módulo (no lambda) para poder guardarla con joblib.
    """
    X = np.asarray(X, dtype=float)
    return np.sign(X) * np.log1p(np.abs(X))


def crear_preprocesador(transformar_log=True):
    """Pipeline de preprocesado (sin modelo): [log firmada] + StandardScaler.

    Está pensado como primer bloque del Pipeline completo:
        Pipeline([("preproceso", crear_preprocesador()), ("modelo", ...)])
    Se ajusta solo con las filas de entrenamiento (fit) y luego se aplica a cualquier
    lote (transform), así no se filtra información del futuro. No cambia el orden ni el
    número de columnas (128 entran, 128 salen).
    """
    pasos = []
    if transformar_log:
        pasos.append(("log_firmada", FunctionTransformer(log_firmada, validate=False)))
    pasos.append(("escalado", StandardScaler()))
    return Pipeline(pasos)


def seleccionar_sensores(ranking, n_sensores):
    """Elige los n sensores mejor puntuados y devuelve sus columnas (en orden del contrato).

    ranking: tabla de exploratory_analysis.importancia_sensores() (índice = nº de sensor,
    columna "puntuacion"). Sirve para el extra de comparar 16, 12, 8 o 4 sensores.
    """
    if not 1 <= n_sensores <= N_SENSORES:
        raise ValueError(f"n_sensores debe estar entre 1 y {N_SENSORES}")
    mejores = ranking.sort_values("puntuacion", ascending=False).head(n_sensores).index
    return columnas_de_sensores(sorted(mejores))
