#!/usr/bin/env python3
"""Los pinceles de los mapas: terreno con textura y objetos dibujados, no bloques de color.

`tools/render_maps.py` importa este módulo y lo usa tile por tile. Está aparte porque son dos
trabajos distintos: acá se decide cómo se ve un pasto, allá cómo se arma un pueblo.

Dos reglas que valen para todo lo de este archivo:

- **el ruido se calcula con coordenadas de píxel globales**, no con la posición del tile. Si se
  usa la del tile, la textura se repite idéntica cada 16 px y el ojo ve una cuadrícula;
- **la luz viene de arriba-izquierda**: el lado claro de un objeto es el de arriba y el izquierdo,
  y su sombra cae abajo a la derecha (docs/arte.md § Reglas de estilo).
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from paleta import hex_a_rgb, rgb  # noqa: E402

TILE = 16

# Tonos intermedios que la paleta maestra no tiene y la textura sí necesita: son mezclas de dos
# colores que ya están en ella, no colores nuevos (docs/arte.md § Paleta).
VERDE_MEDIO = hex_a_rgb("#4d8a45")     # entre verde y verdeOscuro
TIERRA_MEDIA = hex_a_rgb("#a0713f")    # entre marron y marronClaro
MADERA_LUZ = hex_a_rgb("#d9a877")      # marronClaro aclarado, para la veta iluminada


def ruido(x: int, y: int, sal: int = 0) -> float:
    """Ruido determinista y barato: el mismo mapa cada vez que se regenera."""
    h = (x * 374761393 + y * 668265263 + sal * 1442695040888963407) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 0xFFFF


# --- terreno --------------------------------------------------------------------------------

def pasto(dib: ImageDraw.ImageDraw, px: int, py: int) -> None:
    """Pasto con textura de hojitas: base verde, moteado fino y matas de tres briznas.

    El moteado se decide píxel a píxel con las coordenadas globales, así el pasto es continuo de
    un tile al siguiente y no se ve la rejilla.
    """
    verde, oscuro, claro = rgb("verde"), rgb("verdeOscuro"), rgb("verdeClaro")
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=verde)

    for y in range(py, py + TILE):
        for x in range(px, px + TILE):
            n = ruido(x, y, 11)
            if n > 0.91:
                dib.point((x, y), fill=claro)
            elif n < 0.14:
                dib.point((x, y), fill=VERDE_MEDIO)

    # Matas: una cada tanto, en una rejilla de 4 px para que queden repartidas y no apelotonadas.
    for cy in range(py, py + TILE, 4):
        for cx in range(px, px + TILE, 4):
            if ruido(cx, cy, 12) < 0.74:
                continue
            dib.rectangle([cx + 1, cy + 1, cx + 1, cy + 2], fill=oscuro)
            dib.point((cx + 2, cy), fill=VERDE_MEDIO)
            dib.point((cx, cy + 2), fill=VERDE_MEDIO)
            if ruido(cx, cy, 13) > 0.6:
                dib.point((cx + 1, cy), fill=claro)


def flores(dib: ImageDraw.ImageDraw, px: int, py: int) -> None:
    """Pasto con flores amarillas: tres matitas con tallo y un pétalo claro arriba."""
    pasto(dib, px, py)
    am, cl, verde_o = rgb("amarillo"), rgb("amarilloClaro"), rgb("verdeOscuro")
    for dx, dy in ((3, 5), (9, 7), (6, 11)):
        dib.rectangle([px + dx, py + dy + 2, px + dx, py + dy + 4], fill=verde_o)   # tallo
        dib.rectangle([px + dx - 1, py + dy, px + dx + 1, py + dy + 1], fill=am)    # pétalos
        dib.point((px + dx, py + dy - 1), fill=am)
        dib.point((px + dx - 1, py + dy), fill=cl)
        dib.point((px + dx, py + dy), fill=rgb("ambar"))                            # centro


def camino(dib: ImageDraw.ImageDraw, px: int, py: int, x: int, y: int, es_camino) -> None:
    """Tierra pisada: base clara, piedritas y un borde dentado hacia el pasto."""
    claro, oscuro, crema = rgb("marronClaro"), rgb("marron"), rgb("crema")
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=claro)

    for gy in range(py, py + TILE):
        for gx in range(px, px + TILE):
            n = ruido(gx, gy, 21)
            if n > 0.93:
                dib.point((gx, gy), fill=crema)
            elif n < 0.16:
                dib.point((gx, gy), fill=TIERRA_MEDIA)

    for cy in range(py, py + TILE, 8):
        for cx in range(px, px + TILE, 8):
            if ruido(cx, cy, 22) > 0.8:
                dib.rectangle([cx + 2, cy + 3, cx + 3, cy + 4], fill=oscuro)   # piedrita
                dib.point((cx + 2, cy + 3), fill=crema)

    # Borde: en vez de una línea recta, un dentado de 1–2 px decidido por ruido. Un camino con
    # borde recto parece una alfombra; con borde dentado parece tierra.
    bordes = {
        "arriba": (not es_camino(x, y - 1), lambda i, g: (px + i, py + g)),
        "abajo": (not es_camino(x, y + 1), lambda i, g: (px + i, py + TILE - 1 - g)),
        "izquierda": (not es_camino(x - 1, y), lambda i, g: (px + g, py + i)),
        "derecha": (not es_camino(x + 1, y), lambda i, g: (px + TILE - 1 - g, py + i)),
    }
    for nombre, (hace_falta, punto) in bordes.items():
        if not hace_falta:
            continue
        for i in range(TILE):
            grosor = 1 + (ruido(px + i, py + i, hash(nombre) & 0xFF) > 0.62)
            for g in range(grosor):
                dib.point(punto(i, g), fill=oscuro)


def madera(dib: ImageDraw.ImageDraw, px: int, py: int) -> None:
    """Piso de duela: tablas de 8 px con junta oscura y veta clara."""
    claro, oscuro = rgb("marronClaro"), rgb("marron")
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=claro)
    for y in range(py, py + TILE):
        if y % 8 == 0:
            dib.rectangle([px, y, px + TILE - 1, y], fill=oscuro)
            continue
        for x in range(px, px + TILE):
            n = ruido(x, y, 31)
            if n > 0.9:
                dib.point((x, y), fill=MADERA_LUZ)
            elif n < 0.1:
                dib.point((x, y), fill=TIERRA_MEDIA)
    # Junta vertical entre tablas, desplazada una fila sí y otra no.
    for y in range(py, py + TILE):
        tabla = y // 8
        junta = px + (8 if tabla % 2 else 0)
        if px <= junta <= px + TILE - 1 and y % 8:
            dib.point((junta, y), fill=TIERRA_MEDIA)


def baldosa(dib: ImageDraw.ImageDraw, px: int, py: int) -> None:
    """Losas de 8 × 8: junta en sombra, luz arriba-izquierda y el desgaste apenas insinuado.

    El damero a dos tonos fuertes vibraba y se comía la vista de la plaza; acá la variación es
    de un tono y la que manda es la junta.
    """
    gris, oscuro, crema = rgb("gris"), rgb("grisOscuro"), rgb("crema")
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=gris)
    for by in (0, 8):
        for bx in (0, 8):
            gx, gy = px + bx, py + by
            if ruido(gx, gy, 71) > 0.55:
                dib.rectangle([gx, gy, gx + 7, gy + 7], fill=(*(v - 8 for v in gris),))
            dib.rectangle([gx, gy, gx + 6, gy], fill=crema)                      # luz de la losa
            dib.rectangle([gx, gy, gx, gy + 6], fill=crema)
            dib.rectangle([gx + 7, gy, gx + 7, gy + 7], fill=oscuro)             # junta en sombra
            dib.rectangle([gx, gy + 7, gx + 7, gy + 7], fill=oscuro)
            if ruido(gx, gy, 72) > 0.82:
                dib.point((gx + 3, gy + 4), fill=oscuro)                         # desgaste


def agua(dib: ImageDraw.ImageDraw, px: int, py: int, vecino_agua=lambda dx, dy: True) -> None:
    """Agua de la fuente: azul con ondas, destellos y brocal de piedra en el borde."""
    hondo, claro, blanco = rgb("cieloOscuro"), rgb("cielo"), rgb("blanco")
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=hondo)
    for y in range(py, py + TILE):
        for x in range(px, px + TILE):
            if ruido(x, y // 2, 41) > 0.82:
                dib.point((x, y), fill=claro)
    for cy in range(py, py + TILE, 8):
        for cx in range(px, px + TILE, 8):
            if ruido(cx, cy, 42) > 0.7:
                dib.rectangle([cx + 2, cy + 3, cx + 4, cy + 3], fill=blanco)

    # Brocal: sin borde, el agua parece una alfombra azul tirada sobre la plaza.
    piedra, sombra = rgb("gris"), rgb("grisOscuro")
    if not vecino_agua(0, -1):
        dib.rectangle([px, py, px + TILE - 1, py + 1], fill=piedra)
        dib.rectangle([px, py + 2, px + TILE - 1, py + 2], fill=sombra)
    if not vecino_agua(0, 1):
        dib.rectangle([px, py + TILE - 2, px + TILE - 1, py + TILE - 1], fill=piedra)
    if not vecino_agua(-1, 0):
        dib.rectangle([px, py, px + 1, py + TILE - 1], fill=piedra)
    if not vecino_agua(1, 0):
        dib.rectangle([px + TILE - 2, py, px + TILE - 1, py + TILE - 1], fill=piedra)


def pared(dib: ImageDraw.ImageDraw, px: int, py: int, x: int, y: int, tipo: str = "interior") -> None:
    """Muro: la fachada exterior en adobe claro, el interior en piedra oscura.

    La fachada NO va del color del techo: con el rojo repetido, la casa entera se lee como una
    mancha y no se distingue dónde termina el tejado y empieza la pared.
    """
    if tipo == "exterior":
        base, junta, luz = rgb("crema"), rgb("marronClaro"), rgb("blanco")
    else:
        base, junta, luz = rgb("tintaSuave"), rgb("tinta"), rgb("grisOscuro")

    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=base)
    for fila in range(0, TILE, 8):
        gy = py + fila
        dib.rectangle([px, gy + 7, px + TILE - 1, gy + 7], fill=junta)          # hilada
        desfase = 8 if ((y * 2 + fila // 8) % 2) else 0
        for borde in (0, 8):
            gx = px + (borde + desfase) % TILE
            dib.rectangle([gx, gy, gx, gy + 6], fill=junta)                     # junta vertical
            dib.rectangle([gx + 1, gy, gx + 6, gy], fill=luz)                   # luz del bloque

    if tipo == "exterior" and ruido(x, y, 81) > 0.45:
        ventana(dib, px, py)


def ventana(dib: ImageDraw.ImageDraw, px: int, py: int) -> None:
    """Ventana con marco y cruceta: es lo que hace que una fachada parezca una casa."""
    dib.rectangle([px + 3, py + 4, px + 12, py + 12], fill=rgb("marron"))
    dib.rectangle([px + 4, py + 5, px + 11, py + 11], fill=rgb("cielo"))
    dib.rectangle([px + 4, py + 5, px + 7, py + 7], fill=rgb("blanco"))         # reflejo
    dib.rectangle([px + 7, py + 5, px + 8, py + 11], fill=rgb("marron"))        # cruceta
    dib.rectangle([px + 4, py + 8, px + 11, py + 8], fill=rgb("marron"))
    dib.rectangle([px + 2, py + 12, px + 13, py + 13], fill=rgb("marronClaro"))  # repisa


def techo(dib: ImageDraw.ImageDraw, px: int, py: int, cumbrera: bool = False, alero: bool = False) -> None:
    """Tejado visto desde arriba: hiladas de teja, cumbrera clara arriba y alero oscuro abajo.

    Desde arriba una casa es casi todo techo: solo la última fila de un bloque es fachada. Con
    todo el bloque pintado de ladrillo, el pueblo parecía una tapia roja.
    """
    teja, sombra, luz = rgb("rojo"), rgb("marron"), rgb("naranja")
    dib.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=teja)
    for fila in range(0, TILE, 4):
        dib.rectangle([px, py + fila, px + TILE - 1, py + fila], fill=sombra)      # junta de hilada
        dib.rectangle([px, py + fila + 1, px + TILE - 1, py + fila + 1], fill=luz)  # canto de teja
        for x in range(px, px + TILE, 4):
            dib.rectangle([x, py + fila + 1, x, py + fila + 3], fill=sombra)        # canales
    if cumbrera:
        dib.rectangle([px, py, px + TILE - 1, py + 1], fill=rgb("crema"))
    if alero:
        dib.rectangle([px, py + TILE - 2, px + TILE - 1, py + TILE - 1], fill=rgb("tinta"))


def arbol(dib: ImageDraw.ImageDraw, px: int, py: int, x: int, y: int) -> None:
    """Árbol de copa redonda: sombra en el pasto, tronco con corteza y tres tonos de hoja.

    La copa se sale del tile y monta sobre el de arriba: un árbol que cabe justo en 16 px no
    parece un árbol, parece un arbusto.
    """
    oscuro, verde, claro = rgb("verdeOscuro"), rgb("verde"), rgb("verdeClaro")
    tronco, corteza = rgb("marron"), rgb("tinta")
    copa_y = py - TILE - 4

    dib.ellipse([px - 3, py + TILE - 5, px + TILE + 2, py + TILE - 1], fill=VERDE_MEDIO)  # sombra
    dib.rectangle([px + 6, py + 4, px + 9, py + TILE - 2], fill=tronco)
    dib.rectangle([px + 9, py + 4, px + 9, py + TILE - 2], fill=corteza)
    dib.point((px + 7, py + 9), fill=MADERA_LUZ)

    dib.ellipse([px - 5, copa_y, px + TILE + 4, py + 7], fill=oscuro)          # borde de la copa
    dib.ellipse([px - 4, copa_y + 1, px + TILE + 3, py + 5], fill=verde)       # masa de hoja
    dib.ellipse([px + 2, copa_y + 8, px + TILE + 3, py + 5], fill=VERDE_MEDIO)  # sombra abajo-der.
    dib.ellipse([px - 2, copa_y + 3, px + 6, copa_y + 11], fill=claro)         # luz arriba-izq.
    for cy in range(copa_y, py + 6, 3):
        for cx in range(px - 5, px + TILE + 5, 3):
            n = ruido(cx, cy, 51)
            if n > 0.78:
                dib.point((cx, cy), fill=oscuro)                               # hojitas sueltas
            elif n < 0.12:
                dib.point((cx, cy), fill=claro)


# --- objetos ---------------------------------------------------------------------------------

def _tabla(dib, px, py, x0, y0, x1, y1, color, luz, sombra):
    """Bloque con volumen: cara, brillo arriba-izquierda y sombra abajo-derecha."""
    dib.rectangle([px + x0, py + y0, px + x1, py + y1], fill=color)
    dib.rectangle([px + x0, py + y0, px + x1, py + y0], fill=luz)
    dib.rectangle([px + x0, py + y0, px + x0, py + y1], fill=luz)
    dib.rectangle([px + x1, py + y0, px + x1, py + y1], fill=sombra)
    dib.rectangle([px + x0, py + y1, px + x1, py + y1], fill=sombra)


def objeto(dib: ImageDraw.ImageDraw, px: int, py: int, tipo: str, vecino=lambda dx: False) -> None:
    """Dibuja el objeto de un tile. `vecino(dx)` dice si el tile de al lado es el mismo objeto.

    Lo usa el mostrador de la florería, que mide ocho tiles y tiene que verse como un mueble
    largo y no como ocho muebles pegados.
    """
    marron, marron_c, crema = rgb("marron"), rgb("marronClaro"), rgb("crema")
    blanco, tinta, gris = rgb("blanco"), rgb("tinta"), rgb("gris")

    if tipo == "cama":
        _tabla(dib, px, py, 1, 1, 14, 14, marron_c, crema, marron)
        dib.rectangle([px + 2, py + 2, px + 13, py + 7], fill=blanco)          # almohada y sábana
        dib.rectangle([px + 2, py + 8, px + 13, py + 13], fill=rgb("rosa"))
        dib.rectangle([px + 2, py + 8, px + 13, py + 8], fill=rgb("rojo"))
        dib.rectangle([px + 3, py + 3, px + 8, py + 4], fill=crema)
    elif tipo == "escritorio":
        _tabla(dib, px, py, 0, 5, 15, 9, marron_c, crema, marron)
        dib.rectangle([px + 2, py + 10, px + 3, py + 15], fill=marron)         # patas
        dib.rectangle([px + 12, py + 10, px + 13, py + 15], fill=marron)
        dib.rectangle([px + 5, py + 1, px + 10, py + 4], fill=blanco)          # polaroid apoyado
        dib.rectangle([px + 6, py + 2, px + 9, py + 3], fill=rgb("cielo"))
    elif tipo == "espejo":
        _tabla(dib, px, py, 3, 0, 12, 15, marron, marron_c, tinta)
        dib.rectangle([px + 5, py + 2, px + 10, py + 13], fill=rgb("cielo"))
        dib.rectangle([px + 5, py + 2, px + 6, py + 8], fill=blanco)           # reflejo
    elif tipo == "cuadro":
        _tabla(dib, px, py, 2, 2, 13, 12, marron, crema, tinta)
        dib.rectangle([px + 4, py + 4, px + 11, py + 10], fill=blanco)
        dib.rectangle([px + 5, py + 6, px + 10, py + 6], fill=rgb("amarillo"))  # el 21 marcado
        dib.rectangle([px + 7, py + 8, px + 8, py + 9], fill=rgb("amarillo"))
    elif tipo == "planta":
        dib.rectangle([px + 5, py + 10, px + 10, py + 15], fill=rgb("naranja"))  # maceta
        dib.rectangle([px + 5, py + 10, px + 10, py + 10], fill=rgb("ambar"))
        dib.rectangle([px + 7, py + 6, px + 8, py + 10], fill=rgb("verdeOscuro"))
        for dx, dy in ((4, 5), (10, 6), (7, 2)):
            dib.rectangle([px + dx - 1, py + dy, px + dx + 2, py + dy + 2], fill=rgb("verde"))
            dib.point((px + dx, py + dy), fill=rgb("verdeClaro"))
    elif tipo == "nota":
        dib.rectangle([px + 4, py + 6, px + 11, py + 12], fill=blanco)
        dib.rectangle([px + 4, py + 6, px + 11, py + 6], fill=crema)
        dib.rectangle([px + 5, py + 8, px + 9, py + 8], fill=gris)             # renglones
        dib.rectangle([px + 5, py + 10, px + 8, py + 10], fill=gris)
        dib.point((px + 11, py + 12), fill=rgb("grisOscuro"))                  # esquina doblada
    elif tipo == "mostrador":
        dib.rectangle([px, py + 4, px + 15, py + 15], fill=marron)
        dib.rectangle([px, py + 4, px + 15, py + 6], fill=marron_c)            # tabla de arriba
        dib.rectangle([px, py + 4, px + 15, py + 4], fill=crema)
        dib.rectangle([px, py + 9, px + 15, py + 9], fill=tinta)
        if not vecino(-1):
            dib.rectangle([px, py + 4, px, py + 15], fill=tinta)
        if not vecino(1):
            dib.rectangle([px + 15, py + 4, px + 15, py + 15], fill=tinta)
        if ruido(px, py, 61) > 0.55:                                            # un ramo encima
            dib.rectangle([px + 6, py + 1, px + 9, py + 3], fill=rgb("amarillo"))
            dib.point((px + 7, py + 2), fill=rgb("ambar"))
    elif tipo == "estante":
        _tabla(dib, px, py, 1, 1, 14, 14, marron, marron_c, tinta)
        for fila in (4, 9, 14):
            dib.rectangle([px + 2, py + fila, px + 13, py + fila], fill=marron_c)
        for fila, color in ((2, "amarillo"), (7, "rosa"), (12, "amarilloClaro")):
            for dx in (3, 7, 11):
                dib.rectangle([px + dx, py + fila, px + dx + 1, py + fila + 1], fill=rgb(color))
    elif tipo == "banco":
        dib.rectangle([px, py + 6, px + 15, py + 8], fill=marron_c)            # asiento
        dib.rectangle([px, py + 6, px + 15, py + 6], fill=crema)
        dib.rectangle([px, py + 2, px + 15, py + 4], fill=marron_c)            # respaldo
        dib.rectangle([px + 1, py + 4, px + 2, py + 6], fill=marron)
        dib.rectangle([px + 13, py + 4, px + 14, py + 6], fill=marron)
        dib.rectangle([px + 2, py + 9, px + 3, py + 13], fill=rgb("grisOscuro"))  # patas
        dib.rectangle([px + 12, py + 9, px + 13, py + 13], fill=rgb("grisOscuro"))
        dib.rectangle([px + 5, py + 4, px + 9, py + 5], fill=blanco)           # el polaroid
    elif tipo == "buzon":
        dib.rectangle([px + 7, py + 8, px + 8, py + 15], fill=marron)          # poste
        _tabla(dib, px, py, 4, 3, 11, 9, rgb("rojo"), rgb("naranja"), tinta)
        dib.rectangle([px + 5, py + 5, px + 10, py + 5], fill=tinta)           # ranura
        dib.rectangle([px + 11, py + 4, px + 12, py + 6], fill=rgb("amarillo"))  # banderita
    elif tipo == "lampara":
        dib.rectangle([px + 7, py + 5, px + 8, py + 15], fill=rgb("grisOscuro"))
        dib.rectangle([px + 7, py + 5, px + 7, py + 15], fill=gris)
        _tabla(dib, px, py, 5, 1, 10, 5, rgb("amarillo"), rgb("amarilloClaro"), rgb("ambar"))
        dib.rectangle([px + 5, py + 0, px + 10, py + 0], fill=rgb("grisOscuro"))  # capucha
        dib.rectangle([px + 9, py + 7, px + 12, py + 10], fill=blanco)         # polaroid colgado
        dib.rectangle([px + 8, py + 6, px + 9, py + 7], fill=rgb("amarillo"))  # hilo
    elif tipo == "cartel":
        dib.rectangle([px + 3, py + 10, px + 4, py + 15], fill=marron)         # patas
        dib.rectangle([px + 11, py + 10, px + 12, py + 15], fill=marron)
        _tabla(dib, px, py, 1, 2, 14, 11, crema, blanco, marron)
        dib.rectangle([px + 3, py + 4, px + 12, py + 5], fill=rgb("amarillo"))  # manchas de color
        dib.rectangle([px + 3, py + 7, px + 9, py + 8], fill=rgb("ambar"))
    elif tipo == "arbol_tallado":
        dib.rectangle([px + 3, py, px + 12, py + 15], fill=marron)             # tronco grueso
        dib.rectangle([px + 3, py, px + 4, py + 15], fill=marron_c)
        dib.rectangle([px + 11, py, px + 12, py + 15], fill=tinta)
        _tabla(dib, px, py, 5, 5, 10, 10, TIERRA_MEDIA, marron_c, tinta)       # corazón tallado
        dib.rectangle([px + 6, py + 6, px + 7, py + 7], fill=rgb("crema"))
        dib.rectangle([px + 8, py + 6, px + 9, py + 7], fill=rgb("crema"))
        dib.rectangle([px + 6, py + 7, px + 9, py + 8], fill=rgb("crema"))
        dib.rectangle([px + 7, py + 8, px + 8, py + 9], fill=rgb("crema"))
    elif tipo == "kiosco":
        _tabla(dib, px, py, 0, 3, 15, 15, marron_c, crema, marron)
        dib.rectangle([px, py + 1, px + 15, py + 3], fill=rgb("rojo"))
        dib.rectangle([px, py + 2, px + 15, py + 2], fill=rgb("amarillo"))
    else:
        _tabla(dib, px, py, 3, 3, 12, 12, gris, blanco, rgb("grisOscuro"))


def punto_guardado(dib: ImageDraw.ImageDraw, px: int, py: int) -> None:
    """La maceta del punto de guardado. El corazón que flota encima lo pone el motor."""
    dib.rectangle([px + 5, py + 9, px + 10, py + 14], fill=rgb("naranja"))
    dib.rectangle([px + 5, py + 9, px + 10, py + 9], fill=rgb("ambar"))
    dib.rectangle([px + 4, py + 8, px + 11, py + 9], fill=rgb("marronClaro"))
    dib.rectangle([px + 7, py + 5, px + 8, py + 9], fill=rgb("verdeOscuro"))
    dib.rectangle([px + 5, py + 3, px + 10, py + 6], fill=rgb("amarillo"))
    dib.rectangle([px + 6, py + 2, px + 9, py + 3], fill=rgb("amarilloClaro"))
    dib.rectangle([px + 7, py + 4, px + 8, py + 5], fill=rgb("ambar"))


def puerta(dib: ImageDraw.ImageDraw, px: int, py: int) -> None:
    """Puerta de madera con marco, herrajes y picaporte."""
    marron, marron_c, tinta = rgb("marron"), rgb("marronClaro"), rgb("tinta")
    dib.rectangle([px + 1, py + 1, px + 14, py + 15], fill=tinta)              # marco
    dib.rectangle([px + 2, py + 2, px + 13, py + 15], fill=marron)
    dib.rectangle([px + 3, py + 3, px + 12, py + 8], fill=marron_c)            # cuarterón de arriba
    dib.rectangle([px + 3, py + 10, px + 12, py + 14], fill=marron_c)
    dib.rectangle([px + 3, py + 3, px + 12, py + 3], fill=rgb("crema"))
    dib.rectangle([px + 11, py + 9, px + 12, py + 10], fill=rgb("ambar"))      # picaporte


# --- luz -------------------------------------------------------------------------------------

def atardecer(imagen) -> None:
    """Tiñe un mapa entero con la luz de las seis de la tarde, en su sitio.

    Es un remapeo de colores, no una capa encima: cada color del mapa se mezcla con el naranja
    del atardecer y se oscurece un poco. Así la colina llega naranja desde el PNG y no depende
    de que el motor le ponga un velo, que además teñiría también la caja de diálogo.
    """
    calido = rgb("atardecer")
    tabla = {}
    pixeles = imagen.load()
    for y in range(imagen.height):
        for x in range(imagen.width):
            color = pixeles[x, y]
            if color not in tabla:
                r, g, b, a = color
                tabla[color] = (
                    min(255, int(r * 0.78 + calido[0] * 0.30)),
                    min(255, int(g * 0.74 + calido[1] * 0.22)),
                    min(255, int(b * 0.72 + calido[2] * 0.16)),
                    a,
                )
            pixeles[x, y] = tabla[color]
