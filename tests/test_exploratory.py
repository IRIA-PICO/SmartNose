"""Tests de src/exploratory_analysis.py (datos sintéticos, y algunos con los datos reales si existen).

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: ninguna (tests de pytest).
"""
import numpy as np
import pandas as pd
import pytest

from src.contracts import FEATURE_COLUMNS, RAW_DIR
from src import exploratory_analysis as ea


def test_resumen_lotes_suma_bien(datos_sinteticos):
    tabla = ea.resumen_lotes(datos_sinteticos)
    assert list(tabla.index) == [1, 2, 3]
    assert (tabla["total"] == 120).all()
    assert tabla["total"].sum() == len(datos_sinteticos)
    # Los 6 gases aparecen como columna aunque solo haya 3 en los datos
    assert tabla.shape[1] == 7


def test_gases_ausentes_y_mediciones_por_gas(datos_sinteticos):
    ausentes = ea.gases_ausentes_por_lote(datos_sinteticos)
    assert "Tolueno" in ausentes and ausentes["Tolueno"] == [1, 2, 3]
    assert "Acetona" not in ausentes
    por_gas = ea.mediciones_por_gas(datos_sinteticos)
    assert por_gas["mediciones"].sum() == len(datos_sinteticos)
    assert abs(por_gas["porcentaje"].sum() - 100) < 1e-9


def test_calidad_datos_detecta_nulos_y_duplicadas(datos_sinteticos):
    limpia = ea.calidad_datos(datos_sinteticos)
    assert limpia["n_nulos"] == 0 and limpia["n_duplicadas"] == 0
    sucia = datos_sinteticos.copy()
    sucia.loc[0, "feature_5"] = np.nan
    sucia = pd.concat([sucia, sucia.iloc[[10]]], ignore_index=True)  # una fila repetida
    resultado = ea.calidad_datos(sucia)
    assert resultado["n_nulos"] == 1
    assert resultado["n_duplicadas"] == 1


def test_estadisticas_descriptivas(datos_sinteticos):
    tabla = ea.estadisticas_descriptivas(datos_sinteticos)
    assert len(tabla) == 128
    assert {"sensor", "caracteristica", "asimetria", "negativos_pct"} <= set(tabla.columns)
    assert tabla.loc["feature_9", "sensor"] == 2


def test_outliers_se_detectan_pero_no_se_borran(datos_sinteticos):
    original = datos_sinteticos.copy()
    datos = datos_sinteticos.copy()
    datos.loc[5, "feature_3"] = 1e6  # un valor disparatado
    copia = datos.copy()
    por_columna, por_fila = ea.resumen_outliers(datos)
    assert datos.equals(copia)  # no se ha tocado nada
    assert len(datos) == len(original)
    assert por_columna.loc["feature_3", "n_atipicos"] >= 1
    assert por_fila.loc[5] > 0
    assert len(por_fila) == len(datos)
    # Dentro de cada gas también lo marca
    _, por_fila_gas = ea.resumen_outliers(datos, por_gas=True)
    assert por_fila_gas.loc[5] > 0


def test_outliers_por_grupo(datos_sinteticos):
    _, por_fila = ea.resumen_outliers(datos_sinteticos)
    medias = ea.outliers_por_grupo(por_fila, datos_sinteticos, "batch")
    assert list(medias.index) == [1, 2, 3]


def test_redundancia_encuentra_el_sensor_copiado(datos_sinteticos):
    matriz = ea.redundancia_sensores(datos_sinteticos)
    assert matriz.shape == (16, 16)
    assert matriz.loc["S01", "S02"] > 0.95
    assert np.allclose(np.diag(matriz.to_numpy()), 1)
    pares = ea.pares_redundantes(matriz, 0.95)
    assert ("S01", "S02") in set(zip(pares["a"], pares["b"]))
    grupos = ea.grupos_redundantes(matriz, 0.95)
    assert any({"S01", "S02"} <= set(g) for g in grupos)
    # Una característica concreta también funciona
    assert ea.redundancia_sensores(datos_sinteticos, 1).shape == (16, 16)


def test_matriz_correlacion_metodos(datos_sinteticos):
    assert ea.matriz_correlacion(datos_sinteticos).shape == (128, 128)
    assert ea.matriz_correlacion(datos_sinteticos, ["feature_1", "feature_9"], "pearson").shape == (2, 2)
    with pytest.raises(ValueError):
        ea.matriz_correlacion(datos_sinteticos, metodo="otro")


def test_pca_proyeccion(datos_sinteticos):
    coords, info = ea.pca_proyeccion(datos_sinteticos, 3)
    assert {"PC1", "PC2", "PC3", "batch", "gas_name", "concentration"} <= set(coords.columns)
    assert len(coords) == len(datos_sinteticos)
    assert coords.index.equals(datos_sinteticos.index)
    assert (np.diff(info["varianza_explicada"]) <= 1e-12).all()  # de mayor a menor
    assert info["varianza_acumulada"][-1] <= 1 + 1e-9
    assert info["componentes"].shape == (128, 3)


def test_pca_con_lotes_de_ajuste_proyecta_todos_los_lotes(datos_sinteticos):
    coords, info = ea.pca_proyeccion(datos_sinteticos, 2, lotes_ajuste=[1])
    assert info["lotes_ajuste"] == [1]
    assert len(coords) == len(datos_sinteticos)
    with pytest.raises(ValueError):
        ea.pca_proyeccion(datos_sinteticos.head(2), 2)


def test_varianza_explicada(datos_sinteticos):
    tabla = ea.varianza_explicada(datos_sinteticos, 10)
    assert len(tabla) == 10
    assert tabla["acumulada"].is_monotonic_increasing


def test_deriva_pca_crece_con_el_desplazamiento(datos_sinteticos):
    coords, _ = ea.pca_proyeccion(datos_sinteticos, 2)
    tabla = ea.deriva_pca(coords)
    referencia = tabla[tabla["batch"] == 1]
    assert (referencia["distancia"] == 0).all()
    # En los datos sintéticos cada lote desplaza 0,3 las medias: el lote 3 está más lejos que el 2
    por_lote = tabla.groupby("batch")["distancia"].mean()
    assert por_lote[3] > por_lote[2] > por_lote[1]


def test_deriva_por_sensor(datos_sinteticos):
    matriz = ea.deriva_por_sensor(datos_sinteticos, "Acetona", 1)
    assert matriz.shape == (16, 3)
    assert (matriz[1].abs() < 1e-12).all()  # el lote de referencia no cambia respecto a sí mismo
    with pytest.raises(ValueError):
        ea.deriva_por_sensor(datos_sinteticos, "Tolueno", 1)


def test_importancia_de_sensores(datos_sinteticos):
    tabla = ea.importancia_sensores(datos_sinteticos, "anova")
    assert list(tabla.index) == list(range(1, 17))
    assert tabla["puntuacion_relativa"].max() == pytest.approx(1.0)
    assert ea.importancia_features(datos_sinteticos, "anova", lotes=[1, 2]).shape == (128,)
    bosque = ea.importancia_sensores(datos_sinteticos, "random_forest")
    assert bosque["puntuacion"].sum() == pytest.approx(1.0)
    assert ea.importancia_por_lote(datos_sinteticos).shape == (16, 3)
    with pytest.raises(ValueError):
        ea.importancia_features(datos_sinteticos[datos_sinteticos["gas"] == 1])
    with pytest.raises(ValueError):
        ea.importancia_features(datos_sinteticos, "otro")


def test_importancia_es_reproducible(datos_sinteticos):
    a = ea.importancia_sensores(datos_sinteticos, "random_forest")["puntuacion"]
    b = ea.importancia_sensores(datos_sinteticos, "random_forest")["puntuacion"]
    assert np.allclose(a, b)


def test_seleccionar_sensores(datos_sinteticos):
    from src.preprocessing import seleccionar_sensores
    ranking = ea.importancia_sensores(datos_sinteticos, "anova")
    columnas = seleccionar_sensores(ranking, 4)
    assert len(columnas) == 32
    assert columnas == [c for c in FEATURE_COLUMNS if c in set(columnas)]


# --- Con los datos reales (se saltan si no están descargados en data/raw) ---
@pytest.fixture(scope="module")
def datos_reales():
    if not (RAW_DIR / "batch1.dat").exists():
        pytest.skip("Faltan los datos en data/raw")
    from src.data_loader import cargar_todos
    return cargar_todos(salida=None)


def test_datos_reales_resumen(datos_reales):
    tabla = ea.resumen_lotes(datos_reales)
    assert tabla["total"].sum() == 13910
    assert tabla.loc[10, "total"] == 3600
    assert ea.gases_ausentes_por_lote(datos_reales) == {"Tolueno": [3, 4, 5]}
    calidad = ea.calidad_datos(datos_reales)
    assert calidad["n_nulos"] == 0 and calidad["n_duplicadas"] == 0
    assert calidad["lote_mas_pequeno"] == (4, 161)


def test_datos_reales_recuentos_coinciden_con_las_tablas_publicadas(datos_reales):
    # Lote 1 según las tablas publicadas: Etanol 83, Etileno 30, Amoníaco 70, Acetaldehído 98, Acetona 90, Tolueno 74
    lote1 = ea.resumen_lotes(datos_reales).loc[1]
    esperado = {"Etanol": 83, "Etileno": 30, "Amoníaco": 70, "Acetaldehído": 98, "Acetona": 90, "Tolueno": 74}
    for gas, n in esperado.items():
        assert lote1[gas] == n
