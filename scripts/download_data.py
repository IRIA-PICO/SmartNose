"""Descarga los 10 .dat de UCI y guarda o comprueba sus hashes SHA-256.

Responsable: Persona 1 (Lucía Barañano).
Funciones públicas: main().
Uso: python scripts/download_data.py
"""
import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/270/gas+sensor+array+drift+dataset+at+different+concentrations.zip"
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
CHECKSUMS = ROOT / "data" / "checksums.txt"


def main():
    # Descargamos el zip y lo abrimos en memoria
    print(f"Descargando {URL}")
    respuesta = urllib.request.urlopen(URL, timeout=120)
    contenido_zip = respuesta.read()
    respuesta.close()
    archivo_zip = zipfile.ZipFile(io.BytesIO(contenido_zip))

    # Leemos los 10 .dat y calculamos el hash de cada uno
    # (hash de los .dat y no del zip, porque son lo que realmente usamos)
    contenidos = {}
    texto_hashes = ""
    for numero in range(1, 11):
        nombre = f"batch{numero}.dat"
        contenido = archivo_zip.read(nombre)
        contenidos[nombre] = contenido

        calculo = hashlib.sha256(contenido)
        codigo_hash = calculo.hexdigest()
        texto_hashes = texto_hashes + f"{codigo_hash}  {nombre}\n"

    # Si ya hay hashes guardados, comparamos y no los sobrescribimos
    if CHECKSUMS.exists():
        texto_guardado = CHECKSUMS.read_text()
        # splitlines() permite comparar aunque cambien los saltos de línea (Windows)
        if texto_guardado.splitlines() != texto_hashes.splitlines():
            raise SystemExit("ERROR: los hashes no coinciden con data/checksums.txt")
        print("Hashes correctos")
    else:
        CHECKSUMS.write_text(texto_hashes, newline="\n")
        print(f"Hashes guardados en {CHECKSUMS}")

    # Guardamos los archivos en data/raw
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for nombre in contenidos:
        ruta = RAW_DIR / nombre
        ruta.write_bytes(contenidos[nombre])
    print(f"10 archivos guardados en {RAW_DIR}")


if __name__ == "__main__":
    main()
