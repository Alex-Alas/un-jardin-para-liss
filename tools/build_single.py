#!/usr/bin/env python3
"""Empaqueta el juego en un solo archivo HTML, sin red y sin servidor.

    .venv/bin/python tools/build_single.py            # -> dist/un-jardin-para-liss.html

Lee index.html, reemplaza cada <script src> y cada <link rel=stylesheet> por su contenido, y
convierte las imágenes, la fuente y las fotos a data URI dentro de AG.ARCHIVOS_DATOS.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
SALIDA = RAIZ / "dist" / "un-jardin-para-liss.html"
MAPAS = ["casa", "pueblo", "floreria", "colina"]

RE_SCRIPT = re.compile(r'\s*<script src="([^"]+)"></script>')
RE_CSS = re.compile(r'\s*<link rel="stylesheet" href="([^"]+)"\s*/?>')


def data_uri(ruta: Path) -> str:
    tipo = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".json": "application/json",
        ".xml": "application/xml",
        ".js": "application/javascript"
    }[ruta.suffix.lower()]
    datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return f"data:{tipo};base64,{datos}"


def inventario() -> dict:
    """Recolecta el arte que existe, como data URIs, y el manifiesto que le corresponde."""
    archivos = {}
    fotos = []
    candidatos = [
        ASSETS / "atlas.png", ASSETS / "atlas.json",
        ASSETS / "font_pixel8.png", ASSETS / "font_pixel8.xml",
        ASSETS / "font_pixel16.png", ASSETS / "font_pixel16.xml"
    ]
    candidatos += [ASSETS / f"mapa_{m}.png" for m in MAPAS]
    candidatos += [ASSETS / f"mapa_{m}_frentes.png" for m in MAPAS]
    candidatos += sorted((ASSETS / "fotos").glob("*.jpg"))

    for ruta in candidatos:
        if not ruta.exists():
            continue
        relativa = str(ruta.relative_to(RAIZ))
        archivos[relativa] = data_uri(ruta)
        if ruta.parent.name == "fotos":
            fotos.append(ruta.stem.replace("recuerdo_", ""))

    fuentes = sorted({Path(r).stem.replace("font_", "") for r in archivos if "font_" in r and r.endswith(".png")})
    manifiesto = {
        "fuente": bool(fuentes),
        "fuentes": fuentes,
        "atlas": "assets/atlas.png" in archivos and "assets/atlas.json" in archivos,
        "mapas": [m for m in MAPAS if f"assets/mapa_{m}.png" in archivos],
        "frentes": [m for m in MAPAS if f"assets/mapa_{m}_frentes.png" in archivos],
        "fotos": sorted(fotos),
        "fotosPendientes": [f"r{i}" for i in range(1, 7) if f"r{i}" not in fotos]
    }
    return archivos, manifiesto


def main() -> int:
    html = (RAIZ / "index.html").read_text(encoding="utf-8")
    archivos, manifiesto = inventario()

    inyeccion = (
        "<script>window.AG = window.AG || {}; AG.ARCHIVOS_DATOS = "
        + json.dumps(archivos, ensure_ascii=False)
        + ";</script>"
    )

    def reemplazar_script(match: re.Match) -> str:
        ruta = match.group(1)
        if ruta.startswith("http"):
            return match.group(0)
        archivo = RAIZ / ruta
        if not archivo.exists():
            print(f"AVISO: falta {ruta}, se omite", file=sys.stderr)
            return ""
        if ruta.endswith("assets/manifest.js"):
            contenido = (
                "window.AG = window.AG || {};\n"
                f"AG.MANIFIESTO = {json.dumps(manifiesto, ensure_ascii=False)};\n"
            )
        else:
            contenido = archivo.read_text(encoding="utf-8")
        etiqueta = f'\n    <script>\n{contenido}\n    </script>'
        if ruta.endswith("src/main.js"):
            return etiqueta + "\n    " + inyeccion
        return etiqueta

    html = re.sub(RE_CSS, lambda m: f'\n  <style>\n{(RAIZ / m.group(1)).read_text(encoding="utf-8")}\n  </style>', html)
    html = re.sub(RE_SCRIPT, reemplazar_script, html)
    html = html.replace("</head>", "  <!-- build de un solo archivo: todo incrustado -->\n</head>")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(html, encoding="utf-8")

    peso = SALIDA.stat().st_size / 1024 / 1024
    print(f"listo: {SALIDA.relative_to(RAIZ)} ({peso:.2f} MB)")
    print(f"  archivos incrustados: {len(archivos)}")
    print(f"  fotos: {manifiesto['fotos'] or 'ninguna (pendientes: ' + ', '.join(manifiesto['fotosPendientes']) + ')'}")
    print(f"  mapas: {manifiesto['mapas']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
