"""Test de humo de src/eda_plots.py: cada función debe devolver una figura de Plotly.

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: ninguna (tests de pytest). Se salta si Plotly no está instalado.
"""
import pytest

go = pytest.importorskip("plotly.graph_objects")

from src import eda_plots as ep
from src import exploratory_analysis as ea


def test_todas_las_figuras(datos_sinteticos):
    d = datos_sinteticos
    por_columna, por_fila = ea.resumen_outliers(d)
    coords, info = ea.pca_proyeccion(d, 3)
    figuras = [
        ep.fig_mediciones_por_gas(ea.mediciones_por_gas(d)),
        ep.fig_gas_por_lote(d), ep.fig_gas_por_lote(d, porcentaje=True),
        ep.fig_concentracion(d),
        ep.fig_histograma(d, "feature_1"), ep.fig_histograma(d, "feature_1", transformar_log=True),
        ep.fig_correlacion(ea.redundancia_sensores(d), mostrar_valores=True),
        ep.fig_outliers_por_columna(por_columna),
        ep.fig_outliers_por_lote(ea.outliers_por_grupo(por_fila, d, "batch")),
        ep.fig_outliers_vs_concentracion(por_fila, d),
        ep.fig_pca(coords, "gas_name", info=info), ep.fig_pca(coords, "batch", "PC2", "PC3", info),
        ep.fig_pca(coords, "concentration"),
        ep.fig_varianza(ea.varianza_explicada(d, 10)),
        ep.fig_pca_centroides(coords), ep.fig_deriva_pca(ea.deriva_pca(coords)),
        ep.fig_deriva_sensor(ea.deriva_por_sensor(d, "Acetona", 1)),
        ep.fig_importancia(ea.importancia_sensores(d)),
        ep.fig_importancia_por_lote(ea.importancia_por_lote(d)),
    ]
    for figura in figuras:
        assert isinstance(figura, go.Figure)
