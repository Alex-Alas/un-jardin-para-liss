#!/usr/bin/env python3
"""Genera la fuente bitmap del juego (BMFont XML + PNG) desde Press Start 2P.

Sin antialias, un pixel por pixel: lo que se ve en pantalla es exactamente lo que hay en el PNG.
Produce dos tamaños (8 px para diálogos, 16 px para títulos) y una imagen de prueba.

    .venv/bin/python tools/generate_font.py
    .venv/bin/python tools/generate_font.py --prueba
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from paleta import PALETA, rgb  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FUENTE_TTF = RAIZ / "assets" / "source" / "PressStart2P-Regular.ttf"
DESTINO = RAIZ / "assets"

ASCII = [chr(c) for c in range(32, 127)]
ESPANOL = list("áéíóúüñÁÉÍÓÚÜÑ¿¡«»—…“”‘’€ºª")
GLIFOS = ASCII + [c for c in ESPANOL if c not in ASCII]

TAMANOS = [(8, "pixel8"), (16, "pixel16")]


def binarizar(imagen: Image.Image, umbral: int = 110) -> Image.Image:
    return imagen.point(lambda p: 255 if p >= umbral else 0)


def medir_glifo(fuente: ImageFont.FreeTypeFont, ch: str, alto: int) -> dict:
    """Devuelve el mapa de bits binario del glifo y su ubicación respecto a la línea base."""
    lienzo = Image.new("L", (alto * 2, alto * 2), 0)
    ImageDraw.Draw(lienzo).text((alto, 0), ch, font=fuente, fill=255)
    lienzo = binarizar(lienzo)
    caja = lienzo.getbbox()
    avance = round(fuente.getlength(ch))
    if caja is None:
        return {"bitmap": None, "xoffset": 0, "yoffset": 0, "ancho": 0, "alto": 0, "avance": avance}
    recorte = lienzo.crop(caja)
    return {
        "bitmap": recorte,
        "xoffset": caja[0] - alto,
        "yoffset": caja[1],
        "ancho": recorte.width,
        "alto": recorte.height,
        "avance": avance,
    }


def generar_tamano(punto: int, clave: str) -> dict:
    fuente = ImageFont.truetype(str(FUENTE_TTF), punto)
    ascenso, descenso = fuente.getmetrics()
    alto_linea = ascenso + descenso

    glifos = {}
    faltantes = []
    for ch in GLIFOS:
        datos = medir_glifo(fuente, ch, alto_linea)
        if ch == " " or datos["bitmap"] is None:
            if ch != " ":
                faltantes.append(ch)
            datos["bitmap"] = Image.new("L", (1, 1), 0)
            datos["ancho"], datos["alto"] = 0, 0
        glifos[ch] = datos

    ancho_atlas = max(64, punto * 32)
    filas = []
    x, y, alto_fila = 1, 1, 0
    for ch in GLIFOS:
        g = glifos[ch]
        if x + g["ancho"] + 1 > ancho_atlas:
            filas.append((x, y, alto_fila))
            x, y, alto_fila = 1, y + alto_fila + 1, 0
        g["x"], g["y"] = x, y
        x += g["ancho"] + 1
        alto_fila = max(alto_fila, g["alto"])
    alto_atlas = max(32, y + alto_fila + 1)

    atlas = Image.new("RGBA", (ancho_atlas, alto_atlas), (0, 0, 0, 0))
    for ch in GLIFOS:
        g = glifos[ch]
        if g["ancho"] and g["alto"]:
            tinta = Image.new("RGBA", (g["ancho"], g["alto"]), rgb("blanco") + (255,))
            atlas.paste(tinta, (g["x"], g["y"]), g["bitmap"])

    filtro = Image.NEAREST
    atlas = atlas.crop((0, 0, _potencia(ancho_atlas), _potencia(alto_atlas)))
    atlas = atlas.resize(atlas.size, filtro)

    png = DESTINO / f"font_{clave}.png"
    xml = DESTINO / f"font_{clave}.xml"
    atlas.save(png)

    caracteres = []
    for ch in GLIFOS:
        g = glifos[ch]
        codigo = ord(ch)
        caracteres.append(
            f'<char id="{codigo}" x="{g["x"]}" y="{g["y"]}" width="{g["ancho"]}" '
            f'height="{g["alto"]}" xoffset="{g["xoffset"]}" yoffset="{g["yoffset"]}" '
            f'xadvance="{g["avance"]}" page="0" chnl="15" />'
        )

    xml.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<font>\n"
        f'  <info face="Press Start 2P" size="{punto}" bold="0" italic="0" charset="" unicode="1" '
        'stretchH="100" smooth="0" aa="1" padding="0,0,0,0" spacing="0,0" />\n'
        f'  <common lineHeight="{alto_linea}" base="{ascenso}" scaleW="{atlas.width}" '
        f'scaleH="{atlas.height}" pages="1" packed="0" />\n'
        "  <pages>\n"
        f'    <page id="0" file="{png.name}" />\n'
        "  </pages>\n"
        f'  <chars count="{len(caracteres)}">\n    '
        + "\n    ".join(caracteres)
        + "\n  </chars>\n"
        '  <kernings count="0" />\n'
        "</font>\n",
        encoding="utf-8",
    )

    return {
        "clave": clave,
        "punto": punto,
        "atlas": [atlas.width, atlas.height],
        "lineHeight": alto_linea,
        "base": ascenso,
        "glifos": len(caracteres),
        "faltantes": faltantes,
        "archivos": [str(png.relative_to(RAIZ)), str(xml.relative_to(RAIZ))],
    }


def _potencia(valor: int) -> int:
    p = 1
    while p < valor:
        p *= 2
    return p


def hoja_de_prueba() -> Path:
    """Una imagen con frases reales del juego para revisar acentos y legibilidad a tamaño real."""
    lineas = [
        ("pixel16", "UN JARDÍN PARA LISS"),
        ("pixel8", "ÁÉÍÓÚÜÑ áéíóúüñ ¿¡«»—…"),
        ("pixel8", "DOÑA FLORA: ¡Liss! Justo a quien"),
        ("pixel8", "necesitaba. Se me volaron los"),
        ("pixel8", "pétalos del ramo más bonito."),
        ("pixel8", "* La cama está tibia todavía."),
        ("pixel8", "«Busca tres y ven a la colina.»"),
    ]
    fuentes = {
        "pixel8": ImageFont.truetype(str(FUENTE_TTF), 8),
        "pixel16": ImageFont.truetype(str(FUENTE_TTF), 16),
    }
    ancho, alto = 480, 200
    hoja = Image.new("RGB", (ancho, alto), PALETA["negro"])
    dibujo = ImageDraw.Draw(hoja)
    y = 12
    for clave, texto in lineas:
        fuente = fuentes[clave]
        capa = Image.new("L", (ancho, 40), 0)
        ImageDraw.Draw(capa).text((10, 0), texto, font=fuente, fill=255)
        capa = binarizar(capa)
        tinta = Image.new("RGB", capa.size, PALETA["blanco"])
        hoja.paste(tinta, (0, y), capa)
        y += fuente.getmetrics()[0] + fuente.getmetrics()[1] + 6
    ruta = DESTINO / "fuente_prueba.png"
    hoja.save(ruta)
    return ruta


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera la fuente bitmap del juego.")
    parser.add_argument("--prueba", action="store_true", help="también escribe assets/fuente_prueba.png")
    args = parser.parse_args()

    if not FUENTE_TTF.exists():
        print(f"Falta la fuente: {FUENTE_TTF}", file=sys.stderr)
        return 1

    DESTINO.mkdir(parents=True, exist_ok=True)
    reportes = [generar_tamano(punto, clave) for punto, clave in TAMANOS]

    if args.prueba:
        ruta = hoja_de_prueba()
        print(f"prueba: {ruta.relative_to(RAIZ)}")

    print(json.dumps(reportes, ensure_ascii=False, indent=2))
    for r in reportes:
        if r["faltantes"]:
            print(f"AVISO {r['clave']}: glifos sin dibujo -> {''.join(r['faltantes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
