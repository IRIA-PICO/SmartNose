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

URL = ("https://archive.ics.uci.edu/static/public/270/"
       "gas+sensor+array+drift+dataset+at+different+concentrations.zip")
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
CHECKSUMS = ROOT / "data" / "checksums.txt"


def main():
    print(f"Descargando {URL}")
    with urllib.request.urlopen(URL, timeout=120) as respuesta:
        archivo_zip = zipfile.ZipFile(io.BytesIO(respuesta.read()))

    nombres = [f"batch{i}.dat" for i in range(1, 11)]
    contenidos = {nombre: archivo_zip.read(nombre) for nombre in nombres}
    # Hacemos el hash de los .dat (no del zip), que es lo que realmente usamos
    lineas = [f"{hashlib.sha256(contenidos[n]).hexdigest()}  {n}" for n in nombres]

    # Si ya hay hashes guardados, comparamos y no los sobrescribimos
    if CHECKSUMS.exists():
        if CHECKSUMS.read_text().split() != " ".join(lineas).split():
            raise SystemExit("ERROR: los hashes no coinciden con data/checksums.txt")
        print("Hashes correctos")
    else:
        CHECKSUMS.write_text("\n".join(lineas) + "\n", newline="\n")
        print(f"Hashes guardados en {CHECKSUMS}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for nombre, contenido in contenidos.items():
        (RAW_DIR / nombre).write_bytes(contenido)
    print(f"10 archivos guardados en {RAW_DIR}")


if __name__ == "__main__":
    main()
