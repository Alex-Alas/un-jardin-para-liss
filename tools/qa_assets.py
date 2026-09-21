#!/usr/bin/env python3
"""Revisa que el arte generado cumpla las reglas de docs/arte.md.

    .venv/bin/python tools/qa_assets.py
    .venv/bin/python tools/qa_assets.py --json

Comprueba tamaños, canal alfa limpio (0 o 255), cantidad de colores, que la fuente tenga sus
glifos y los acentos, y que cada mapa mida lo que dice su grilla de colisión.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
TILE = 16
MAX_COLORES = 32
ANCHO_MIN_FOTO = 480
PESO_MAX_FOTO = 320 * 1024
ACENTOS = "áéíóúüñÁÉÍÓÚÜÑ¿¡«»"


def revisar_png(ruta: Path, informe: list, avisos: list, max_colores: int = MAX_COLORES) -> None:
    with Image.open(ruta) as imagen:
        modo = imagen.mode
        ancho, alto = imagen.size
        colores = imagen.convert("RGBA").getcolors(maxcolors=200000) or []
        cantidad = len(colores)
        alfas = {valor[3] for _, valor in colores}
        sucio = sorted(a for a in alfas if a not in (0, 255))
        informe.append({"archivo": str(ruta.relative_to(RAIZ)), "tamano": [ancho, alto], "modo": modo,
                        "colores": cantidad, "alfaSucio": sucio[:6]})
        if cantidad > max_colores:
            avisos.append(f"{ruta.name}: {cantidad} colores (máximo {max_colores})")
        if sucio:
            avisos.append(f"{ruta.name}: alpha con valores intermedios ({sucio[:4]})")
        return None


def revisar_fuente(informe: list, avisos: list, errores: list) -> None:
    for clave in ("pixel8", "pixel16"):
        png = ASSETS / f"font_{clave}.png"
        xml = ASSETS / f"font_{clave}.xml"
        if not png.exists() or not xml.exists():
            errores.append(f"falta la fuente {clave} (png + xml)")
            continue
        contenido = xml.read_text(encoding="utf-8")
        codigos = {int(c) for c in re.findall(r'<char id="(\d+)"', contenido)}
        faltan = [ch for ch in ACENTOS if ord(ch) not in codigos]
        informe.append({"fuente": clave, "glifos": len(codigos), "acentosFaltantes": faltan})
        if faltan:
            errores.append(f"fuente {clave}: faltan glifos {''.join(faltan)}")
        if len(codigos) < 90:
            avisos.append(f"fuente {clave}: solo {len(codigos)} glifos")


def revisar_mapas(informe: list, avisos: list, errores: list) -> None:
    datos = json.loads(re.search(r"AG\.MAPAS = (\{.*\})\s*;", (RAIZ / "src/data/mapas.js").read_text(encoding="utf-8"), re.S).group(1))
    for nombre, mapa in datos.items():
        png = ASSETS / f"mapa_{nombre}.png"
        if not png.exists():
            errores.append(f"falta el PNG del mapa {nombre}")
            continue
        with Image.open(png) as imagen:
            esperado = (mapa["ancho"] * mapa["tile"], mapa["alto"] * mapa["tile"])
            informe.append({"mapa": nombre, "png": list(imagen.size), "esperado": list(esperado),
                            "objetos": len(mapa["objetos"]), "puertas": len(mapa["puertas"])})
            if imagen.size != esperado:
                errores.append(f"mapa {nombre}: mide {imagen.size}, se esperaba {esperado}")
            if len(mapa["colisiones"]) != mapa["alto"]:
                errores.append(f"mapa {nombre}: colisiones con {len(mapa['colisiones'])} filas")


def revisar_fotos(informe: list, avisos: list, errores: list) -> None:
    for foto in sorted((ASSETS / "fotos").glob("*.jpg")):
        peso = foto.stat().st_size
        with Image.open(foto) as imagen:
            ancho, alto = imagen.size
        informe.append({"foto": foto.name, "tamano": [ancho, alto], "kb": round(peso / 1024)})
        if max(ancho, alto) < ANCHO_MIN_FOTO:
            errores.append(f"{foto.name}: {max(ancho, alto)}px, mínimo {ANCHO_MIN_FOTO}px")
        if peso > PESO_MAX_FOTO:
            avisos.append(f"{foto.name}: {round(peso / 1024)} KB (ideal ≤ {PESO_MAX_FOTO // 1024} KB)")


def main() -> int:
    parser = argparse.ArgumentParser(description="QA de los assets del juego.")
    parser.add_argument("--json", action="store_true", help="imprime el informe en JSON")
    args = parser.parse_args()

    informe: list = []
    avisos: list = []
    errores: list = []

    for png in sorted(ASSETS.glob("*.png")):
        if png.name.startswith("fuente_prueba"):
            continue
        revisar_png(png, informe, avisos)

    revisar_fuente(informe, avisos, errores)
    revisar_mapas(informe, avisos, errores)
    revisar_fotos(informe, avisos, errores)

    if args.json:
        print(json.dumps({"informe": informe, "avisos": avisos, "errores": errores}, ensure_ascii=False, indent=2))
    else:
        for fila in informe:
            print("  ·", json.dumps(fila, ensure_ascii=False))
        for aviso in avisos:
            print("  ! ", aviso)
        for error in errores:
            print("  ✗ ", error)
        print(f"\n{len(informe)} revisados, {len(avisos)} avisos, {len(errores)} errores.")

    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
