# App de Streamlit (Iria)

## Cómo arrancarla
Desde la **raíz** del proyecto, con el entorno `nose` activado:

    pip install -r requirements.txt   # la primera vez (añade plotly)
    streamlit run app/Home.py

Se abre en http://localhost:8501. Al guardar un archivo, pulsa **R** en el navegador para recargar.
Importante: si la lanzas desde otra carpeta, Streamlit no encuentra `.streamlit/config.toml` y pierde el tema.

## Cómo encajan las piezas

    .streamlit/config.toml     tema base: colores, fuente DM Sans (lo lee Streamlit solo)
    app/Home.py                portada (es la página principal)
    app/pages/N_Nombre.py      cada archivo = una página del menú lateral, en orden por N
    app/components/theme.py    colores de la presentación y plantilla de Plotly
    app/components/ui.py       CSS + piezas: cabecera(), fila_kpis(), nota(), grafico()...
    app/components/datos.py    cargar_datos() con caché y nombres de sensores ("S03 · ΔR")
    app/assets/                logo e icono

Toda página nueva empieza igual:

    from components.ui import configurar_pagina, cabecera
    configurar_pagina("Nombre")          # siempre lo primero
    cabecera("02 · Deriva", "Drift <em>Monitor</em>", "Subtítulo")

## Ideas clave de Streamlit
- El script se ejecuta **entero de arriba abajo** cada vez que tocas un filtro.
- Por eso `cargar_datos()` lleva `@st.cache_data`: el Parquet se lee una sola vez.
- Los gráficos van con `grafico(fig)` (usa `theme=None` para que Streamlit no cambie nuestros colores).
- `128 features = 16 sensores × 8 características`: `feature_1..8` son del sensor 1, `feature_9..16` del 2...
