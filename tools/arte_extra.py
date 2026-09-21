#!/usr/bin/env python3
"""Dibuja a mano (con código) todo el arte que no sale de la hoja de Liss.

NPCs, sus retratos, el ramo y los iconos de la UI. `tools/generate_sprites.py` importa
`piezas()` y los empaca en el mismo atlas que los frames de Liss, así el juego sigue cargando
un solo PNG.

Reglas que manda `docs/arte.md` y que este módulo respeta:

- caja de personaje 16 × 34, con los pies apoyados en la última fila (origen 0.5, 1 en el motor);
- las proporciones de Liss: cabezota (filas 2–15), torso (16–28), piernas (29–31), pies (32–33);
- contorno de 1 px en tinta, luz desde arriba-izquierda, 2 tonos por material;
- alpha duro (0 o 255) y ≤ 24 colores por asset;
- nada de texto dentro del arte.

No depende de la hoja de Liss: es determinista y se puede correr solo para mirar el resultado.

    .venv/bin/python tools/arte_extra.py --contacto   # dist/contacto_extra.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from paleta import hex_a_rgb, rgb  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent

CAJA_W, CAJA_H = 16, 34
RETRATO = 48          # el retrato se dibuja a 24 y se duplica: mismo píxel, sin inventar detalle

# Tonos de piel y pelo: los mismos hexadecimales que salieron de la hoja de Liss, para que los
# NPCs y ella parezcan del mismo dibujo (ver docs/arte.md § Paleta).
PIEL = {
    "clara":  ("#fbc3ae", "#f1af9a", "#cc9a8f"),
    "media":  ("#f1af9a", "#ed8f6e", "#c07967"),
    "morena": ("#ed8f6e", "#c07967", "#9c5347"),
}
TINTA = hex_a_rgb("#1b1420")


def c(valor: str) -> tuple[int, int, int]:
    """Color desde hexadecimal o desde un nombre de la paleta maestra."""
    return hex_a_rgb(valor) if valor.startswith("#") else rgb(valor)


class Lienzo:
    """Un PNG chiquito con dibujo por píxel. Todo en coordenadas inclusivas, como el pixel art."""

    def __init__(self, ancho: int, alto: int):
        self.imagen = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
        self.dib = ImageDraw.Draw(self.imagen)
        self.ancho = ancho
        self.alto = alto

    def rect(self, x0: int, y0: int, x1: int, y1: int, color) -> None:
        if x1 < x0 or y1 < y0:
            return
        self.dib.rectangle([x0, y0, x1, y1], fill=color)

    def px(self, x: int, y: int, color) -> None:
        if 0 <= x < self.ancho and 0 <= y < self.alto:
            self.imagen.putpixel((x, y), tuple(color) + (255,))

    def contorno(self, color=TINTA) -> None:
        """Rodea la silueta con 1 px de tinta, sin tapar lo que ya está dibujado."""
        opaco = [[self.imagen.getpixel((x, y))[3] > 0 for x in range(self.ancho)]
                 for y in range(self.alto)]
        for y in range(self.alto):
            for x in range(self.ancho):
                if opaco[y][x]:
                    continue
                vecino = any(
                    0 <= y + dy < self.alto and 0 <= x + dx < self.ancho and opaco[y + dy][x + dx]
                    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0))
                )
                if vecino:
                    self.px(x, y, color)

    def sombra_piso(self, cx: int, y: int, radio: int = 4) -> None:
        """La sombrita elíptica que apoya al personaje en el pasto."""
        self.dib.ellipse([cx - radio, y - 1, cx + radio, y + 1], fill=hex_a_rgb("#2f6b3a"))


# --- personajes -----------------------------------------------------------------------------

def cuerpo(
    piel: str = "media",
    pelo: str = "#271d2e",
    pelo_luz: str = "#362233",
    ropa: str = "crema",
    ropa_sombra: str = "marronClaro",
    pantalon: str = "tintaSuave",
    peinado: str = "corto",
    accesorio: str | None = None,
    delantal: str | None = None,
    nino: bool = False,
) -> Lienzo:
    """Un personaje de frente en la caja de 16 × 34, con las proporciones de Liss.

    `peinado` cambia la masa de pelo (corto, rizado, chongo, coletas, gorra) y `delantal` pinta
    un mandil encima del torso. `nino` baja y encoge todo tres píxeles: Sofi es más chiquita.
    """
    lz = Lienzo(CAJA_W, CAJA_H)
    claro, base, sombra = (c(v) for v in PIEL[piel])
    pelo_c, pelo_l = c(pelo), c(pelo_luz)
    ropa_c, ropa_s = c(ropa), c(ropa_sombra)
    pant = c(pantalon)

    d = 3 if nino else 0           # desplazamiento vertical: los niños ocupan menos caja
    estrecho = 1 if nino else 0    # y son un píxel más angostos de cada lado

    cabeza_y0, cabeza_y1 = 2 + d, 15
    torso_y0, torso_y1 = 16, 27
    piernas_y0, piernas_y1 = 28, 31

    # --- cabeza
    cx0, cx1 = 3 + estrecho, 12 - estrecho
    lz.rect(cx0, cabeza_y0 + 2, cx1, cabeza_y1, base)
    lz.rect(cx0, cabeza_y0 + 2, cx1, cabeza_y0 + 6, pelo_c)          # nacimiento del pelo
    lz.rect(cx0 + 1, cabeza_y0 + 2, cx1 - 1, cabeza_y0 + 3, pelo_l)  # brillo de arriba-izquierda
    lz.rect(cx0, cabeza_y0 + 2, cx0 + 1, cabeza_y1 - 3, pelo_c)      # patillas
    lz.rect(cx1 - 1, cabeza_y0 + 2, cx1, cabeza_y1 - 3, pelo_c)
    lz.rect(cx0 + 2, cabeza_y1 - 1, cx1 - 2, cabeza_y1, claro)       # mentón iluminado

    if peinado == "rizado":
        for x in range(cx0 - 1, cx1 + 2, 2):
            lz.rect(x, cabeza_y0, x + 1, cabeza_y0 + 3, pelo_c)
            lz.px(x, cabeza_y0 + 1, pelo_l)
        lz.rect(cx0 - 1, cabeza_y0 + 2, cx0, cabeza_y1 - 5, pelo_c)
        lz.rect(cx1, cabeza_y0 + 2, cx1 + 1, cabeza_y1 - 5, pelo_c)
    elif peinado == "chongo":
        lz.rect(cx0 + 3, cabeza_y0 - 1, cx1 - 3, cabeza_y0 + 2, pelo_c)
        lz.rect(cx0 + 4, cabeza_y0 - 1, cx0 + 5, cabeza_y0, pelo_l)
    elif peinado == "coletas":
        lz.rect(cx0 - 1, cabeza_y0 + 4, cx0, cabeza_y1 - 4, pelo_c)
        lz.rect(cx1, cabeza_y0 + 4, cx1 + 1, cabeza_y1 - 4, pelo_c)
        lz.px(cx0 - 1, cabeza_y0 + 4, pelo_l)
    elif peinado == "gorra":
        lz.rect(cx0 - 1, cabeza_y0 + 1, cx1 + 1, cabeza_y0 + 4, c("naranja"))
        lz.rect(cx0 - 1, cabeza_y0 + 5, cx1 + 1, cabeza_y0 + 5, c("ambar"))   # visera
        lz.rect(cx0, cabeza_y0 + 1, cx1 - 3, cabeza_y0 + 2, c("amarillo"))

    # --- cara: dos píxeles de ojo y nada más (docs/arte.md § Reglas de estilo)
    ojo_y = cabeza_y1 - 4
    lz.rect(cx0 + 2, ojo_y, cx0 + 2, ojo_y + 1, TINTA)
    lz.rect(cx1 - 2, ojo_y, cx1 - 2, ojo_y + 1, TINTA)
    medio = (cx0 + cx1) // 2
    lz.rect(medio, ojo_y + 3, medio + 1, ojo_y + 3, sombra)          # sonrisa
    if accesorio == "bigote":
        lz.rect(cx0 + 2, ojo_y + 2, cx1 - 2, ojo_y + 2, c("#65454a"))
    if accesorio == "flor":
        lz.rect(cx1 - 1, cabeza_y0 + 3, cx1, cabeza_y0 + 4, c("amarillo"))
        lz.px(cx1, cabeza_y0 + 3, c("ambar"))
    if accesorio == "lentes":
        lz.rect(cx0 + 1, ojo_y - 1, cx1 - 1, ojo_y - 1, c("grisOscuro"))

    # --- torso y brazos
    tx0, tx1 = 4 + estrecho, 11 - estrecho
    lz.rect(tx0, torso_y0 + d, tx1, torso_y1, ropa_c)
    lz.rect(tx0, torso_y0 + d, tx0 + 1, torso_y1, ropa_s)            # pliegue del lado en sombra
    lz.rect(tx0, torso_y0 + d, tx1, torso_y0 + d, ropa_s)            # cuello
    lz.rect(tx0 - 2, torso_y0 + 1 + d, tx0 - 1, torso_y1 - 2, ropa_c)
    lz.rect(tx1 + 1, torso_y0 + 1 + d, tx1 + 2, torso_y1 - 2, ropa_c)
    lz.rect(tx0 - 2, torso_y1 - 2, tx0 - 1, torso_y1 - 1, base)      # manos
    lz.rect(tx1 + 1, torso_y1 - 2, tx1 + 2, torso_y1 - 1, base)

    if delantal:
        del_c = c(delantal)
        lz.rect(tx0 + 1, torso_y0 + 3 + d, tx1 - 1, torso_y1, del_c)
        lz.rect(tx0 + 2, torso_y0 + 2 + d, tx0 + 2, torso_y0 + 3 + d, del_c)
        lz.rect(tx1 - 2, torso_y0 + 2 + d, tx1 - 2, torso_y0 + 3 + d, del_c)
        lz.rect(tx0 + 3, torso_y1 - 2, tx1 - 3, torso_y1 - 2, c("blanco"))   # bolsillo

    # --- piernas y pies
    lz.rect(tx0 + 1, piernas_y0, tx1 - 1, piernas_y1, pant)
    lz.rect(7, piernas_y0, 8, piernas_y1, c("tinta"))                # separación de las piernas
    lz.rect(tx0 + 1, piernas_y1 + 1, tx0 + 2, piernas_y1 + 2, c("marron"))
    lz.rect(tx1 - 2, piernas_y1 + 1, tx1 - 1, piernas_y1 + 2, c("marron"))

    lz.contorno()
    return lz


def gato() -> Lienzo:
    """Michi, sentado y con cara de que sabe algo. Ocupa el fondo de la caja de 16 × 34."""
    lz = Lienzo(CAJA_W, CAJA_H)
    gris, claro, oscuro = c("gris"), c("#c4c4d4"), c("grisOscuro")
    base_y = 33

    lz.rect(4, base_y - 10, 11, base_y - 1, gris)          # cuerpo
    lz.rect(4, base_y - 10, 5, base_y - 1, oscuro)         # lado en sombra
    lz.rect(11, base_y - 4, 13, base_y - 3, gris)          # cola
    lz.rect(13, base_y - 7, 13, base_y - 4, gris)
    lz.rect(4, base_y - 1, 6, base_y, oscuro)              # patitas
    lz.rect(9, base_y - 1, 11, base_y, oscuro)

    lz.rect(4, base_y - 17, 11, base_y - 10, gris)         # cabeza
    lz.rect(5, base_y - 17, 9, base_y - 15, claro)
    lz.rect(4, base_y - 19, 5, base_y - 17, gris)          # orejas
    lz.rect(10, base_y - 19, 11, base_y - 17, gris)
    lz.px(5, base_y - 18, c("rosa"))
    lz.px(10, base_y - 18, c("rosa"))
    lz.rect(5, base_y - 14, 5, base_y - 13, TINTA)         # ojos
    lz.rect(10, base_y - 14, 10, base_y - 13, TINTA)
    lz.px(7, base_y - 12, c("rosa"))                       # naricita
    lz.rect(6, base_y - 11, 9, base_y - 11, claro)         # hocico

    lz.contorno()
    return lz


def aclarar(color: tuple[int, int, int], cuanto: int = 26) -> tuple[int, int, int]:
    """Sube un tono el color: sirve igual para pelo negro que para canas."""
    return tuple(min(255, v + cuanto) for v in color)


def retrato(
    personaje: Lienzo,
    piel: str,
    pelo: str,
    peinado: str = "corto",
    accesorio: str | None = None,
) -> Image.Image:
    """Cabeza y hombros a 24 × 24, duplicados a 48: el mismo píxel, más grande.

    Se dibuja aparte y no se recorta del sprite: a 16 px de ancho la cara no tiene lugar para la
    expresión, y el retrato es justamente donde se lee. Lleva el mismo peinado y el mismo
    accesorio que el cuerpo, para que se reconozca a quién se está oyendo hablar.
    """
    lz = Lienzo(24, 24)
    claro, base, sombra = (c(v) for v in PIEL[piel])
    pelo_c = c(pelo)
    pelo_l = aclarar(pelo_c)

    # Hombros: el color sale del torso del sprite, así el retrato y el muñequito visten igual.
    torso = personaje.imagen.getpixel((8, 24))
    ropa = torso[:3] if torso[3] > 0 else c("tintaSuave")
    lz.rect(3, 20, 20, 23, ropa)
    lz.rect(5, 19, 18, 19, ropa)
    lz.rect(9, 18, 14, 19, base)                            # cuello

    lz.rect(5, 5, 18, 18, base)                             # cara
    lz.rect(6, 4, 17, 4, base)                              # frente redondeada
    lz.rect(5, 18, 6, 18, (0, 0, 0, 0))                     # mentón en punta, no cuadrado
    lz.rect(17, 18, 18, 18, (0, 0, 0, 0))

    lz.rect(6, 3, 17, 8, pelo_c)                            # masa de pelo
    lz.rect(5, 5, 6, 15, pelo_c)
    lz.rect(17, 5, 18, 15, pelo_c)
    lz.rect(7, 4, 12, 5, pelo_l)                            # luz de arriba-izquierda

    if peinado == "rizado":
        # Masa maciza primero y los rulos encima: con los rulos sueltos, entre uno y otro se veía
        # el fondo y el pelo parecía una corona.
        lz.rect(5, 2, 18, 8, pelo_c)
        for x in range(4, 20, 3):
            lz.rect(x, 0, x + 2, 3, pelo_c)
            lz.px(x, 1, pelo_l)
        lz.rect(4, 4, 5, 13, pelo_c)
        lz.rect(18, 4, 19, 13, pelo_c)
    elif peinado == "chongo":
        lz.rect(9, 0, 14, 3, pelo_c)
        lz.rect(10, 0, 12, 1, pelo_l)
    elif peinado == "coletas":
        lz.rect(3, 7, 5, 14, pelo_c)
        lz.rect(18, 7, 20, 14, pelo_c)
        lz.rect(3, 7, 4, 8, pelo_l)
    elif peinado == "gorra":
        lz.rect(5, 2, 18, 6, c("naranja"))
        lz.rect(4, 7, 19, 7, c("ambar"))                    # visera
        lz.rect(6, 3, 12, 4, c("amarillo"))

    lz.rect(8, 11, 9, 13, TINTA)                            # ojos
    lz.rect(14, 11, 15, 13, TINTA)
    lz.px(8, 11, c("blanco"))
    lz.px(14, 11, c("blanco"))
    lz.rect(7, 10, 9, 10, pelo_c)                           # cejas
    lz.rect(14, 10, 16, 10, pelo_c)
    lz.rect(10, 16, 13, 16, sombra)                         # boca
    lz.px(9, 15, sombra)
    lz.px(14, 15, sombra)
    lz.rect(6, 13, 7, 14, c("#f2a8b8"))                     # cachetes
    lz.rect(16, 13, 17, 14, c("#f2a8b8"))

    if accesorio == "bigote":
        lz.rect(8, 14, 15, 15, c("#65454a"))
        lz.rect(10, 16, 13, 16, c("#65454a"))
    if accesorio == "flor":
        lz.rect(17, 3, 19, 5, c("amarillo"))
        lz.px(18, 4, c("ambar"))
        lz.px(17, 3, c("amarilloClaro"))

    lz.contorno()
    return lz.imagen.resize((RETRATO, RETRATO), Image.NEAREST)


# --- objetos e iconos -------------------------------------------------------------------------

def ramo() -> Lienzo:
    """El ramo de la colina: papel crema, tallos verdes y flores amarillas."""
    lz = Lienzo(16, 24)
    lz.rect(5, 14, 10, 23, c("crema"))                      # papel
    lz.rect(5, 14, 6, 23, c("marronClaro"))
    lz.rect(6, 8, 9, 15, c("verdeOscuro"))                  # tallos
    for cx, cy in ((4, 6), (11, 7), (7, 3), (2, 10), (13, 11)):
        lz.rect(cx - 1, cy - 1, cx + 1, cy + 1, c("amarillo"))
        lz.px(cx - 1, cy - 1, c("amarilloClaro"))
        lz.px(cx, cy, c("ambar"))
    lz.rect(5, 18, 10, 18, c("amarillo"))                   # lacito
    lz.contorno()
    return lz


def corazon_ui() -> Lienzo:
    """El corazón del punto de guardado, más gordito que el de partículas."""
    lz = Lienzo(16, 16)
    am, cl, ox = c("amarillo"), c("amarilloClaro"), c("ambar")
    lz.rect(3, 4, 6, 5, am)
    lz.rect(9, 4, 12, 5, am)
    lz.rect(2, 5, 13, 8, am)
    lz.rect(3, 9, 12, 9, am)
    lz.rect(4, 10, 11, 10, ox)
    lz.rect(5, 11, 10, 11, ox)
    lz.rect(6, 12, 9, 12, ox)
    lz.rect(7, 13, 8, 13, ox)
    lz.rect(4, 5, 6, 6, cl)                                  # brillo arriba-izquierda
    lz.contorno()
    return lz


def flor_ui() -> Lienzo:
    """El icono de flor del HUD: cinco pétalos y un centro ámbar."""
    lz = Lienzo(16, 16)
    am, cl, ox = c("amarillo"), c("amarilloClaro"), c("ambar")
    for cx, cy in ((7, 3), (3, 6), (11, 6), (5, 10), (10, 10)):
        lz.rect(cx - 1, cy - 1, cx + 2, cy + 2, am)
        lz.px(cx - 1, cy - 1, cl)
    lz.rect(6, 6, 9, 9, ox)
    lz.rect(7, 11, 8, 14, c("verdeOscuro"))
    lz.rect(9, 12, 11, 12, c("verde"))
    lz.contorno()
    return lz


def piezas() -> dict[str, Image.Image]:
    """Todos los frames que este módulo aporta al atlas, listos para empacar."""
    gente = {
        # Alex: pelo negro rizado y camiseta del color con el que habla (cielo).
        "alex": dict(
            args=dict(piel="morena", peinado="rizado", ropa="cielo", ropa_sombra="cieloOscuro",
                      pantalon="tintaSuave"),
            piel="morena", pelo="#271d2e",
        ),
        # Doña Flora: canas en chongo, delantal verde y una flor amarilla en el pelo.
        "flora": dict(
            args=dict(piel="clara", peinado="chongo", pelo="#c8c2cc", pelo_luz="#e6e2e8",
                      ropa="crema", ropa_sombra="marronClaro", delantal="verde",
                      accesorio="flor", pantalon="marron"),
            piel="clara", pelo="#c8c2cc",
        ),
        # Don Beto: gorra de kiosquero, bigote y camisa naranja.
        "beto": dict(
            args=dict(piel="media", peinado="gorra", ropa="naranja", ropa_sombra="#b9531a",
                      delantal="crema", accesorio="bigote", pantalon="grisOscuro"),
            piel="media", pelo="#271d2e",
        ),
        # Sofi: niña, coletas y vestido verde claro.
        "sofi": dict(
            args=dict(piel="media", peinado="coletas", ropa="verdeClaro", ropa_sombra="verde",
                      pantalon="verdeOscuro", nino=True),
            piel="media", pelo="#271d2e",
        ),
    }

    salida: dict[str, Image.Image] = {}
    for ident, receta in gente.items():
        lz = cuerpo(**receta["args"])
        salida[f"npc_{ident}_abajo_0"] = lz.imagen
        salida[f"npc_{ident}_abajo_1"] = respiracion(lz.imagen)
        salida[f"retrato_{ident}_normal"] = retrato(
            lz,
            receta["piel"],
            receta["pelo"],
            peinado=receta["args"].get("peinado", "corto"),
            accesorio=receta["args"].get("accesorio"),
        )

    michi = gato()
    salida["npc_michi_abajo_0"] = michi.imagen
    salida["npc_michi_abajo_1"] = respiracion(michi.imagen, cintura=26)
    salida["retrato_michi_normal"] = retrato_gato()

    salida["ramo_0"] = ramo().imagen
    salida["ui_corazon"] = corazon_ui().imagen
    salida["ui_flor"] = flor_ui().imagen
    return salida


def retrato_gato() -> Image.Image:
    """Michi de cerca. Mismo tratamiento que los retratos de gente, pero con orejas."""
    lz = Lienzo(24, 24)
    gris, claro, oscuro = c("gris"), c("#c4c4d4"), c("grisOscuro")
    lz.rect(4, 7, 19, 21, gris)
    lz.rect(4, 7, 8, 21, oscuro)
    lz.rect(4, 3, 8, 8, gris)                                # orejas
    lz.rect(15, 3, 19, 8, gris)
    lz.rect(5, 5, 7, 8, c("rosa"))
    lz.rect(16, 5, 18, 8, c("rosa"))
    lz.rect(8, 12, 10, 15, TINTA)                            # ojos
    lz.rect(13, 12, 15, 15, TINTA)
    lz.rect(9, 12, 9, 13, c("verdeClaro"))
    lz.rect(14, 12, 14, 13, c("verdeClaro"))
    lz.rect(10, 17, 13, 18, claro)                           # hocico
    lz.rect(11, 16, 12, 16, c("rosa"))                       # nariz
    lz.rect(2, 17, 7, 17, claro)                             # bigotes
    lz.rect(16, 17, 21, 17, claro)
    lz.contorno()
    return lz.imagen.resize((RETRATO, RETRATO), Image.NEAREST)


def respiracion(imagen: Image.Image, cintura: int | None = None) -> Image.Image:
    """Segundo frame quieto: el torso baja 1 px. Mismo truco que usa Liss."""
    salida = imagen.copy()
    corte = cintura if cintura is not None else round(imagen.height * 0.5)
    torso = imagen.crop((0, 0, imagen.width, corte))
    salida.paste(Image.new("RGBA", (imagen.width, corte), (0, 0, 0, 0)), (0, 0))
    salida.paste(torso, (0, 1), torso)
    return salida


def main() -> int:
    parser = argparse.ArgumentParser(description="Arte dibujado por código: NPCs, retratos, iconos.")
    parser.add_argument("--contacto", action="store_true", help="guarda dist/contacto_extra.png")
    args = parser.parse_args()

    trozos = piezas()
    for nombre, imagen in sorted(trozos.items()):
        colores = len(imagen.getcolors(maxcolors=4096) or [])
        print(f"  · {nombre:24s} {imagen.width:2d}×{imagen.height:2d}  {colores:2d} colores")

    if args.contacto:
        from generate_sprites import hoja_de_contacto  # import perezoso: solo hace falta acá

        destino = RAIZ / "dist" / "contacto_extra.png"
        hoja_de_contacto(trozos, destino, escala=6)
        print(f"hoja de contacto: {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
