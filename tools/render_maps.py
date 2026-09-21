#!/usr/bin/env python3
"""Renderiza los mapas ASCII a PNG y exporta colisiones/objetos a src/data/mapas.js.

Una letra por tile en maps/*.txt (leyenda en docs/handoff.md). Los comentarios son //. Las líneas que empiezan con
'#!' son metadatos: definen qué es cada letra y a dónde llevan las puertas.

    .venv/bin/python tools/render_maps.py
    .venv/bin/python tools/render_maps.py --mapa pueblo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from paleta import rgb, rgba  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "maps"
DESTINO = RAIZ / "assets"
SALIDA_JS = RAIZ / "src" / "data" / "mapas.js"
TILE = 16

BLOQUEAN = set("#~T")
TERRENO_PASTO = {".": "pasto", "f": "pasto"}
META_RE = re.compile(r"^#!\s*(\w+)\s*(.*)$")


def leer_mapa(ruta: Path) -> dict:
    meta = {"objetos": {}, "puertas": {}, "zonas": {}}
    filas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("#!"):
            clave, resto = META_RE.match(linea).groups()
            if resto.startswith(":"):
                resto = resto[1:].strip()
            partes = resto.split()
            if clave == "objeto":
                letra, tipo, resto_id = partes[0], partes[1], partes[2:]
                meta["objetos"][letra] = {"tipo": tipo, "id": resto_id[0] if resto_id else tipo,
                                          "dialogo": resto_id[1] if len(resto_id) > 1 else None}
            elif clave == "puerta":
                letra, destino, x, y = partes
                meta["puertas"][letra] = {"a": destino, "destino": {"x": int(x), "y": int(y)}}
            elif clave == "zona":
                letra, clave_zona = partes
                meta["zonas"][letra] = clave_zona
            else:
                meta[clave] = resto
            continue
        if linea.startswith("//"):
            continue
        if linea.strip():
            filas.append(linea.rstrip("\n"))

    ancho = max(len(f) for f in filas)
    filas = [f.ljust(ancho, ".") for f in filas]
    return {"nombre": ruta.stem, "ancho": ancho, "alto": len(filas), "filas": filas, "meta": meta}


def ruido(x: int, y: int, sal: int = 0) -> float:
    """Ruido determinista y barato: siempre el mismo mapa al regenerarlo."""
    h = (x * 374761393 + y * 668265263 + sal * 1442695040888963407) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 0xFFFF


def pinta_pasto(dib: ImageDraw.ImageDraw, px: int, py: int, x: int, y: int) -> None:
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=rgb("verde"))
    if ruido(x, y, 1) > 0.72:
        dib.rectangle([px + 3, py + 5, px + 4, py + 6], fill=rgb("verdeOscuro"))
        dib.rectangle([px + 10, py + 4, px + 11, py + 5], fill=rgb("verdeOscuro"))
    if ruido(x, y, 2) > 0.86:
        dib.rectangle([px + 6, py + 10, px + 8, py + 11], fill=rgb("verdeClaro"))


def pinta_camino(dib, px, py, x, y, es_camino) -> None:
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=rgb("marronClaro"))
    if ruido(x, y, 3) > 0.6:
        dib.rectangle([px + 4, py + 6, px + 5, py + 7], fill=rgb("marron"))
    if ruido(x, y, 4) > 0.85:
        dib.rectangle([px + 9, py + 10, px + 11, py + 11], fill=rgb("crema"))
    borde = rgb("marron")
    if not es_camino(x, y - 1):
        dib.rectangle([px, py, px + TILE - 1, py + 1], fill=borde)
    if not es_camino(x, y + 1):
        dib.rectangle([px, py + TILE - 2, px + TILE - 1, py + TILE - 1], fill=borde)
    if not es_camino(x - 1, y):
        dib.rectangle([px, py, px + 1, py + TILE - 1], fill=borde)
    if not es_camino(x + 1, y):
        dib.rectangle([px + TILE - 2, py, px + TILE - 1, py + TILE - 1], fill=borde)


def pinta_baldosa(dib, px, py, x, y) -> None:
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=rgb("gris"))
    dib.rectangle([px, py, px + TILE - 1, py], fill=rgb("grisOscuro"))
    dib.rectangle([px, py, px, py + TILE - 1], fill=rgb("grisOscuro"))


def pinta_madera(dib, px, py, x, y) -> None:
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=rgb("marronClaro"))
    dib.rectangle([px, py + 7, px + TILE - 1, py + 8], fill=rgb("marron"))
    if ruido(x, y, 5) > 0.8:
        dib.rectangle([px + 2, py + 3, px + 5, py + 4], fill=rgb("marron"))


def pinta_pared(dib, px, py, tipo: str = "interior") -> None:
    if tipo == "exterior":
        dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=rgb("rojo"))
        dib.rectangle([px, py, px + TILE - 1, py + 2], fill=rgb("naranja"))
        dib.rectangle([px, py + 12, px + TILE - 1, py + TILE - 1], fill=rgb("crema"))
    else:
        dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=rgb("tintaSuave"))
        dib.rectangle([px, py, px + TILE - 1, py + 3], fill=rgb("tinta"))
        dib.rectangle([px, py + 13, px + TILE - 1, py + TILE - 1], fill=rgb("tinta"))


def pinta_agua(dib, px, py, x, y) -> None:
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=rgb("cieloOscuro"))
    offset = int(ruido(x, y, 6) * 8)
    dib.rectangle([px + offset, py + 4, px + offset + 5, py + 5], fill=rgb("cielo"))
    dib.rectangle([px + ((offset + 5) % 8), py + 11, px + ((offset + 5) % 8) + 3, py + 12], fill=rgb("cielo"))


def pinta_arbol(dib, px, py) -> None:
    copa_y = py - TILE
    dib.rectangle([px + 6, py + 8, px + 9, py + TILE - 1], fill=rgb("marron"))
    dib.rectangle([px - 3, copa_y + 3, px + TILE + 2, py + 3], fill=rgb("verdeOscuro"))
    dib.rectangle([px - 1, copa_y - 3, px + TILE, py + 1], fill=rgb("verde"))
    dib.rectangle([px + 2, copa_y - 1, px + 7, copa_y + 2], fill=rgb("verdeClaro"))


def pinta_flor(dib, px, py, x, y) -> None:
    pinta_pasto(dib, px, py, x, y)
    desplazamientos = [(3, 4), (9, 6), (5, 10)]
    for i, (dx, dy) in enumerate(desplazamientos):
        dib.rectangle([px + dx, py + dy, px + dx + 1, py + dy + 1], fill=rgb("amarillo"))
        dib.rectangle([px + dx, py + dy + 2, px + dx, py + dy + 3], fill=rgb("verdeOscuro"))


def pinta_detalle_objeto(dib, px, py, tipo: str) -> None:
    """Bloques de gris para que el greybox sea legible: el sprite real lo pone el motor."""
    formas = {
        "cama": [(1, 2, 14, 13), (1, 1, 14, 3)],
        "escritorio": [(1, 4, 14, 12)],
        "espejo": [(4, 1, 11, 14)],
        "cuadro": [(2, 3, 13, 11)],
        "planta": [(4, 4, 11, 14)],
        "nota": [(6, 7, 9, 9)],
        "mostrador": [(0, 4, 15, 12)],
        "estante": [(1, 2, 14, 13)],
        "banco": [(0, 6, 15, 10)],
        "buzon": [(5, 3, 10, 14)],
        "lampara": [(7, 0, 8, 15)],
        "cartel": [(2, 4, 13, 12)],
        "arbol_tallado": [(6, 6, 9, 9)],
        "kiosco": [(0, 2, 15, 14)],
        "fuente": [(0, 0, 15, 15)]
    }
    for i, (x0, y0, x1, y1) in enumerate(formas.get(tipo, [(3, 3, 12, 12)])):
        tono = "gris" if i == 0 else "blanco"
        dib.rectangle([px + x0, py + y0, px + x1, py + y1], fill=rgba(tono, 210))


def render(mapa: dict, salida: Path) -> dict:
    sin_objetos = (DESTINO / "atlas.png").exists()
    ancho, alto = mapa["ancho"], mapa["alto"]
    def es_camino(cx: int, cy: int) -> bool:
        return 0 <= cy < alto and 0 <= cx < ancho and mapa["filas"][cy][cx] == ","

    imagen = Image.new("RGBA", (ancho * TILE, alto * TILE), rgb("verde") + (255,))
    dib = ImageDraw.Draw(imagen)

    for y, fila in enumerate(mapa["filas"]):
        for x, ch in enumerate(fila):
            px, py = x * TILE, y * TILE
            if ch in TERRENO_PASTO:
                pinta_pasto(dib, px, py, x, y)
            elif ch == ",":
                pinta_camino(dib, px, py, x, y, es_camino)
            elif ch == "=":
                pinta_baldosa(dib, px, py, x, y)
            elif ch == "w":
                pinta_madera(dib, px, py, x, y)
            elif ch == "b":
                pinta_baldosa(dib, px, py, x, y)
            elif ch == "#":
                pinta_pared(dib, px, py, mapa["meta"].get("tipo", "interior"))
            elif ch == "~":
                pinta_agua(dib, px, py, x, y)
            elif ch == "T":
                pinta_pasto(dib, px, py, x, y)
            elif ch == "f":
                pinta_flor(dib, px, py, x, y)

    for y, fila in enumerate(mapa["filas"]):
        for x, ch in enumerate(fila):
            px, py = x * TILE, y * TILE
            if ch == "T":
                pinta_arbol(dib, px, py)
            elif ch == "D":
                dib.rectangle([px + 2, py + 2, px + 13, py + 15], fill=rgb("marron"))
                dib.rectangle([px + 3, py + 3, px + 12, py + 9], fill=rgb("ambar"))
                dib.rectangle([px + 11, py + 10, px + 12, py + 12], fill=rgb("crema"))
            elif ch == "S":
                dib.rectangle([px + 4, py + 6, px + 11, py + 10], fill=rgb("amarillo"))
                dib.rectangle([px + 5, py + 5, px + 6, py + 7], fill=rgb("amarillo"))
                dib.rectangle([px + 9, py + 5, px + 10, py + 7], fill=rgb("amarillo"))
                dib.rectangle([px + 6, py + 11, px + 9, py + 12], fill=rgb("amarillo"))
            elif ch in mapa["meta"]["objetos"] and not sin_objetos:
                pinta_detalle_objeto(dib, px, py, mapa["meta"]["objetos"][ch]["tipo"])

    imagen.save(salida)

    colisiones = []
    objetos = []
    letras_usadas = set()
    puertas = []
    zonas = []
    for y, fila in enumerate(mapa["filas"]):
        linea = []
        for x, ch in enumerate(fila):
            linea.append("1" if ch in BLOQUEAN else "0")
            if ch == "S":
                objetos.append({"x": x, "y": y, "letra": "S", "tipo": "guardado",
                                "id": "guardado", "dialogo": "sistema.guardado"})
            if ch in mapa["meta"]["objetos"] and ch not in letras_usadas:
                dato = dict(mapa["meta"]["objetos"][ch])
                objetos.append({"x": x, "y": y, "letra": ch, **dato})
                letras_usadas.add(ch)
            if ch in mapa["meta"]["puertas"]:
                puertas.append({"x": x, "y": y, "letra": ch, **mapa["meta"]["puertas"][ch]})
            if ch in mapa["meta"]["zonas"]:
                zonas.append({"x": x, "y": y, "letra": ch, "clave": mapa["meta"]["zonas"][ch]})
        colisiones.append("".join(linea))

    return {
        "ancho": ancho,
        "alto": alto,
        "tile": TILE,
        "imagen": f"assets/mapa_{mapa['nombre']}.png",
        "colisiones": colisiones,
        "objetos": objetos,
        "puertas": puertas,
        "zonas": zonas
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Renderiza mapas ASCII a PNG + JS.")
    parser.add_argument("--mapa", help="renderiza solo este mapa")
    args = parser.parse_args()

    DESTINO.mkdir(parents=True, exist_ok=True)
    rutas = sorted(ORIGEN.glob("*.txt"))
    if args.mapa:
        rutas = [r for r in rutas if r.stem == args.mapa]
    if not rutas:
        print("No hay mapas en maps/*.txt", file=sys.stderr)
        return 1

    datos = {}
    for ruta in rutas:
        mapa = leer_mapa(ruta)
        png = DESTINO / f"mapa_{mapa['nombre']}.png"
        datos[mapa["nombre"]] = render(mapa, png)
        print(f"{mapa['nombre']:9s} {mapa['ancho']}x{mapa['alto']} tiles -> {png.relative_to(RAIZ)} "
              f"({len(datos[mapa['nombre']]['objetos'])} objetos, {len(datos[mapa['nombre']]['puertas'])} puertas)")

    SALIDA_JS.parent.mkdir(parents=True, exist_ok=True)
    SALIDA_JS.write_text(
        "// Generado por tools/render_maps.py — no editar a mano.\n"
        "window.AG = window.AG || {};\n"
        f"AG.MAPAS = {json.dumps(datos, ensure_ascii=False, indent=2)}\n;",
        encoding="utf-8"
    )
    print(f"exportado: {SALIDA_JS.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
