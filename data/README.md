# Datos

**Responsable:** Persona 1 (Lucía Barañano).

## Origen
- UCI, id 270: *Gas Sensor Array Drift Dataset at Different Concentrations* (**no** la versión sin concentraciones).
- Página: https://archive.ics.uci.edu/dataset/270/gas+sensor+array+drift+dataset+at+different+concentrations
- Descarga exacta: https://archive.ics.uci.edu/static/public/270/gas+sensor+array+drift+dataset+at+different+concentrations.zip
- DOI: 10.24432/C5MK6M. La página indica licencia CC BY 4.0, pero su descripción habla además de uso solo para investigación (excluye el comercial).
- Versión usada: no hemos visto número de versión en la página. Consultada el 25/11/2026; los `.dat` del zip tienen fecha 23/10/2013. La versión queda identificada por los SHA-256 de `checksums.txt`.

## Cómo obtenerlos
Desde la raíz del proyecto:

    python scripts/download_data.py     # descarga en data/raw/ y comprueba hashes
    python -m src.data_loader           # crea data/processed/gas_drift.parquet

`data/raw/` y `data/processed/` no se suben a git. `checksums.txt` sí.

## Formato
Cada línea: `gas;concentración 1:valor 2:valor ... 128:valor` (16 sensores x 8 características). Concentración en ppmv.

## Comprobado con los archivos reales (25/11/2026)
- 10 archivos, 13.910 filas, todas con las 128 features en orden.
- Sin líneas duplicadas, tampoco mirando solo las features.
- El código de gas 6 (Tolueno) no aparece en los lotes 3, 4 y 5.
- En el lote 2 el código 6 tiene solo 5 mediciones.

Mediciones por lote (las columnas 1-6 son los códigos de gas de los archivos):

| Lote | 1 | 2 | 3 | 4 | 5 | 6 | Total |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 98 | 83 | 30 | 70 | 74 | 445 |
| 2 | 164 | 334 | 100 | 109 | 532 | 5 | 1244 |
| 3 | 365 | 490 | 216 | 240 | 275 | 0 | 1586 |
| 4 | 64 | 43 | 12 | 30 | 12 | 0 | 161 |
| 5 | 28 | 40 | 20 | 46 | 63 | 0 | 197 |
| 6 | 514 | 574 | 110 | 29 | 606 | 467 | 2300 |
| 7 | 649 | 662 | 360 | 744 | 630 | 568 | 3613 |
| 8 | 30 | 30 | 40 | 33 | 143 | 18 | 294 |
| 9 | 61 | 55 | 100 | 75 | 78 | 101 | 470 |
| 10 | 600 | 600 | 600 | 600 | 600 | 600 | 3600 |

## Nombre de cada código de gas (duda resuelta, pendiente de confirmar por el equipo)
El texto de la página de UCI dice: 1 Etanol, 2 Etileno, 3 Amoníaco, 4 Acetaldehído, 5 Acetona, 6 Tolueno.
Pero las **tablas de recuentos por gas y lote** de UCI y de *Data in Brief* (Fonollosa et al., 2015) no cuadran con esa
codificación. Si se comparan gas a gas con los archivos, las cifras solo coinciden así:

| Código | Según el texto de UCI (antes en `GAS_NAMES`) | Según los recuentos publicados (ahora en `GAS_NAMES`) |
|---|---|---|
| 1 | Etanol | **Acetona** |
| 2 | Etileno | **Acetaldehído** |
| 3 | Amoníaco | **Etanol** |
| 4 | Acetaldehído | **Etileno** |
| 5 | Acetona | **Amoníaco** |
| 6 | Tolueno | Tolueno |

Ejemplo (lote 1): las tablas publicadas dan Etanol 83, Etileno 30, Amoníaco 70, Acetaldehído 98, Acetona 90 y Tolueno 74.
En `batch1.dat` los códigos 1 a 6 tienen 90, 98, 83, 30, 70 y 74 mediciones. Con la codificación nueva los recuentos
coinciden en todos los lotes comprobados (1, 2, 3, 6 y 10); con la del texto de UCI no coincide ninguno. Un artículo que
usa este dataset (arXiv 1505.06405, tabla I) enumera las columnas en el mismo orden: Acetona, Acetaldehído,
Etanol, Etileno, Amoníaco, Tolueno. La comprobación se puede repetir en el apartado 1.2 del notebook y en
`tests/test_exploratory.py`.

**Qué cambia:** solo los nombres (`GAS_NAMES` en `src/contracts.py`). Los modelos trabajan con el código. Hay que
regenerar el parquet (`python -m src.data_loader`) para que `gas_name` salga con los nombres nuevos.
**Pendiente:** confirmarlo con la tabla del artículo original (Vergara et al., 2012) o con la profesora, y avisar al equipo
(`contracts.py` es de la Persona 2). Si se decidiera volver a la codificación anterior, basta con restaurar ese diccionario.
Los rangos de concentración tampoco los resuelven: los observados por código (mín-máx, ppmv) son 1: 2,5-600; 2: 2,5-300;
3: 2,5-1000; 4: 2,5-300; 5: 10-1000; 6: 1-230 y no coinciden del todo con los que publica UCI.
