#!/usr/bin/env python3
"""Renderiza los mapas a PNG y exporta colisiones/objetos a src/data/mapas.js.

Hay dos clases de mapa en maps/*.txt:

- **ASCII**: una letra por tile (leyenda en docs/handoff.md). Los comentarios son //. Las líneas
  que empiezan con '#!' son metadatos: definen qué es cada letra y a dónde llevan las puertas.
- **pintados**: los que tienen `#! pintura:`. La imagen viene hecha y el archivo describe, en
  píxeles, qué bloquea, qué tapa a Liss y dónde está cada cosa. Los resuelve `escenarios.py`.

    .venv/bin/python tools/render_maps.py
    .venv/bin/python tools/render_maps.py --mapa pueblo
    .venv/bin/python tools/render_maps.py --ver        # además, dist/mapa_<n>_revision.png
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import escenarios  # noqa: E402
import tiles  # noqa: E402
from paleta import rgb  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "maps"
DESTINO = RAIZ / "assets"
SALIDA_JS = RAIZ / "src" / "data" / "mapas.js"
TILE = 16

BLOQUEAN = set("#~T")
# Las letras que son piso. Todo lo demás (objetos, puertas, NPCs, árboles) se apoya encima de
# alguna de ellas, nunca en el vacío.
TERRENOS = set(".f,=wb~")
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


def npcs_con_sprite() -> set[str]:
    """Qué NPCs ya tienen sprite en el atlas: esos los dibuja el motor, no el PNG del mapa.

    Es por personaje y no todo-o-nada: si bastara con que el atlas existiera, el primer NPC
    dibujado borraría del mapa a los que todavía no tienen arte.
    """
    datos = DESTINO / "atlas.json"
    if not (DESTINO / "atlas.png").exists() or not datos.exists():
        return set()
    frames = json.loads(datos.read_text(encoding="utf-8")).get("frames", {})
    return {n[len("npc_"):-len("_abajo_0")] for n in frames if n.startswith("npc_") and n.endswith("_abajo_0")}


def render(mapa: dict, salida: Path, resolver_destino) -> dict:
    del_motor = npcs_con_sprite()
    ancho, alto = mapa["ancho"], mapa["alto"]
    filas = mapa["filas"]
    objetos_meta = mapa["meta"]["objetos"]
    exterior = mapa["meta"].get("tipo", "interior") == "exterior"

    def letra(cx: int, cy: int) -> str:
        return filas[cy][cx] if 0 <= cy < alto and 0 <= cx < ancho else " "

    def es_camino(cx: int, cy: int) -> bool:
        return letra(cx, cy) == ","

    def es_muro(cx: int, cy: int) -> bool:
        """La puerta es parte de la fachada: sin esto, el tile de arriba se pinta de ladrillo
        en medio del tejado y parece una chimenea torcida."""
        ch = letra(cx, cy)
        if ch == "#" or ch in mapa["meta"]["puertas"]:
            return True
        # Un objeto o un NPC metido en un hueco del muro (el kiosco de Don Beto) sigue siendo
        # fachada: si no, el tile de arriba se pinta de pared en medio del tejado.
        return ch in objetos_meta and letra(cx - 1, cy) == "#" and letra(cx + 1, cy) == "#"

    # Suelo por defecto: el terreno más repetido del mapa. Los tiles que no son terreno (un
    # objeto, una puerta, un árbol) igual necesitan piso debajo; sin esto, la cama de Liss
    # flotaba sobre un parche de pasto dentro de su propia casa.
    conteo = Counter(ch for fila in filas for ch in fila if ch in TERRENOS)
    suelo = conteo.most_common(1)[0][0] if conteo else "."

    def terreno_de(cx: int, cy: int) -> str:
        """Qué piso va debajo de este tile: el suyo si es terreno, si no el del vecino que mande."""
        ch = letra(cx, cy)
        if ch in TERRENOS:
            return ch
        vecinos = Counter(
            letra(cx + dx, cy + dy)
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1))
            if letra(cx + dx, cy + dy) in TERRENOS
        )
        return vecinos.most_common(1)[0][0] if vecinos else suelo

    imagen = Image.new("RGBA", (ancho * TILE, alto * TILE), rgb("verde") + (255,))
    dib = ImageDraw.Draw(imagen)

    # --- primera pasada: el suelo y los muros
    for y, fila in enumerate(filas):
        for x, bruto in enumerate(fila):
            px, py = x * TILE, y * TILE
            ch = bruto if bruto == "#" else terreno_de(x, y)
            if ch == ",":
                tiles.camino(dib, px, py, x, y, es_camino)
            elif ch == "=":
                tiles.baldosa(dib, px, py)
            elif ch == "w":
                tiles.madera(dib, px, py)
            elif ch == "b":
                tiles.baldosa(dib, px, py)
            elif ch == "#":
                # Desde arriba una casa es techo salvo su última fila, que es la fachada.
                if exterior and es_muro(x, y + 1):
                    tiles.techo(
                        dib, px, py,
                        cumbrera=not es_muro(x, y - 1),
                        alero=not es_muro(x, y + 2),
                    )
                else:
                    tiles.pared(dib, px, py, x, y, mapa["meta"].get("tipo", "interior"))
            elif ch == "~":
                tiles.agua(dib, px, py,
                           vecino_agua=lambda dx, dy, _x=x, _y=y: letra(_x + dx, _y + dy) == "~")
            elif ch == "f":
                tiles.flores(dib, px, py)
            else:
                tiles.pasto(dib, px, py)

    # --- segunda pasada: lo que se apoya encima del suelo
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            px, py = x * TILE, y * TILE
            if ch == "T":
                tiles.arbol(dib, px, py, x, y)
            elif ch in mapa["meta"]["puertas"]:
                tiles.puerta(dib, px, py)
            elif ch == "S":
                tiles.punto_guardado(dib, px, py)
            elif ch in objetos_meta:
                dato = objetos_meta[ch]
                # Los NPCs con sprite los dibuja el motor: si además los pintara el mapa, cada
                # uno quedaría con un doble pegado al piso.
                if dato["tipo"] == "npc":
                    if dato["id"] not in del_motor:
                        tiles.objeto(dib, px, py, "npc")
                    continue
                tiles.objeto(dib, px, py, dato["tipo"], vecino=lambda dx, _x=x, _y=y: letra(_x + dx, _y) == ch)

    if mapa["meta"].get("luz") == "atardecer":
        tiles.atardecer(imagen)

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
                puerta = dict(mapa["meta"]["puertas"][ch])
                puerta["destino"] = resolver_destino(puerta["a"], (puerta["destino"]["x"], puerta["destino"]["y"]))
                puertas.append({"x": x, "y": y, "letra": ch, **puerta})
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
    parser.add_argument("--ver", action="store_true",
                        help="guarda una vista de revisión de cada mapa pintado en dist/")
    args = parser.parse_args()

    DESTINO.mkdir(parents=True, exist_ok=True)
    todas = sorted(ORIGEN.glob("*.txt"))
    rutas = [r for r in todas if not args.mapa or r.stem == args.mapa]
    if not rutas:
        print("No hay mapas en maps/*.txt", file=sys.stderr)
        return 1

    pintados = {r.stem for r in todas if escenarios.es_pintado(r)}

    def resolver_destino(escena: str, punto: tuple[int, int]) -> dict:
        """El destino de una puerta va en las unidades del mapa al que lleva: píxeles si ese
        mapa es pintado, tiles si es ASCII."""
        if escena.lower() in pintados:
            return {"px": punto[0], "py": punto[1]}
        return {"x": punto[0], "y": punto[1]}

    # Con --mapa se regenera uno solo, pero mapas.js lleva todos: los demás se conservan.
    datos = {}
    if args.mapa and SALIDA_JS.exists():
        previo = re.search(r"AG\.MAPAS = (\{.*\})\s*;", SALIDA_JS.read_text(encoding="utf-8"), re.S)
        if previo:
            datos = json.loads(previo.group(1))

    for ruta in rutas:
        nombre = ruta.stem
        if nombre in pintados:
            pintado = escenarios.leer(ruta)
            datos[nombre] = escenarios.render(pintado, resolver_destino)
            if args.ver:
                escenarios.depurar(pintado, datos[nombre], RAIZ / "dist" / f"mapa_{nombre}_revision.png")
            detalle = f"pintado, {len(datos[nombre].get('frentes', {}).get('piezas', []))} frentes"
        else:
            mapa = leer_mapa(ruta)
            datos[nombre] = render(mapa, DESTINO / f"mapa_{nombre}.png", resolver_destino)
            detalle = "ASCII"
        print(f"{nombre:9s} {datos[nombre]['ancho']}x{datos[nombre]['alto']} tiles -> assets/mapa_{nombre}.png "
              f"({detalle}; {len(datos[nombre]['objetos'])} objetos, {len(datos[nombre]['puertas'])} puertas)")

    datos = dict(sorted(datos.items()))

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
