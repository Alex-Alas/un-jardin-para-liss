#!/usr/bin/env python3
"""Todo el arte de personajes y objetos que no sale de la hoja de Liss.

NPCs, sus retratos, el ramo y los iconos de la UI salen de `assets/source/personajes-sheet.png`,
una hoja pintada en el mismo estilo que Liss (pixel art de render suave, contornos tibios, cachetes
rosados). Se recortan y se bajan a la escala del juego con la misma receta que Liss, así todos
parecen del mismo dibujo. `tools/generate_sprites.py` importa `piezas()` y los empaca en el mismo
atlas que los frames de Liss, así el juego sigue cargando un solo PNG.

La hoja no trae a los personajes tal como los pide el guion, así que a algunos se les retoca:

- **Doña Flora**: la chica de lentes, con canas y una flor amarilla en el pelo;
- **Don Beto**: el chico de lentes, canoso y con bigote;
- **Sofi**: la niña de la sudadera crema, castaña y con coletas de listón amarillo, para que no se
  confunda con Alex. Su cabeza sale del retrato y el cuerpo se pinta acá, porque la hoja no la
  trae de cuerpo entero mirando al frente.

El pétalo, la hoja seca y el corazón chico del motor se pintan grandes con degradados y se bajan
igual que todo lo demás: así una partícula de 7 px tiene el mismo modelado que Liss.

Reglas que manda `docs/arte.md` y que este módulo respeta: pies apoyados en la última fila
(origen 0.5, 1 en el motor), alpha duro (0 o 255) y ≤ 24 colores por asset.

    .venv/bin/python tools/arte_extra.py --contacto   # dist/contacto_extra.png
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))

RAIZ = Path(__file__).resolve().parent.parent
HOJA = RAIZ / "assets" / "source" / "personajes-sheet.png"

ALTO_CAJA = 34        # la caja de Liss: los personajes de pie miden lo mismo de alto
RETRATO = 48
FONDO_MAXIMO = 10     # el fondo de la hoja es negro: hasta este valor de canal es fondo
TINTA_HOJA = 14       # para encontrar bandas y columnas basta con "no es negro"


# --- leer la hoja -------------------------------------------------------------------------------

class Hoja:
    """La hoja de personajes, leída por bandas horizontales y columnas, como la de Liss.

    Bandas (de arriba abajo): 0 retratos de gente, 1 retrato del gato + Liss, 2 Alex, 3 el chico
    de lentes, 4 la chica de lentes, 5 la niña de vestido, 6 el gato, 7 Alex de frente + objetos.
    """

    def __init__(self, ruta: Path = HOJA):
        if not ruta.exists():
            raise SystemExit(f"Falta la hoja de personajes en {ruta.relative_to(RAIZ)}.")
        self.imagen = Image.open(ruta).convert("RGB")
        self.px = self.imagen.load()
        self._bandas = None
        self._columnas = {}

    def _oscuro(self, x: int, y: int) -> bool:
        return max(self.px[x, y]) < TINTA_HOJA

    def bandas(self) -> list[tuple[int, int]]:
        if self._bandas is None:
            ancho, alto = self.imagen.size
            filas = [sum(1 for x in range(ancho) if not self._oscuro(x, y)) for y in range(alto)]
            self._bandas = _tramos(filas, minimo=2, largo=8)
        return self._bandas

    def columnas(self, banda: int) -> list[tuple[int, int]]:
        if banda not in self._columnas:
            y0, y1 = self.bandas()[banda]
            cuentas = [sum(1 for y in range(y0, y1 + 1) if not self._oscuro(x, y))
                       for x in range(self.imagen.width)]
            self._columnas[banda] = _tramos(cuentas, minimo=0, largo=6)
        return self._columnas[banda]

    def recortar(self, banda: int, columna: int) -> Image.Image:
        """La figura de una celda con el fondo negro vuelto transparente.

        El fondo se inunda desde el borde de la celda: así el contorno oscuro de la figura, que
        también es casi negro, se queda (solo se va lo que toca el borde sin cruzar color).
        """
        y0, y1 = self.bandas()[banda]
        x0, x1 = self.columnas(banda)[columna]
        celda = self.imagen.crop((x0 - 3, y0 - 3, x1 + 4, y1 + 4))
        ancho, alto = celda.size
        datos = celda.load()

        def fondo(x: int, y: int) -> bool:
            return max(datos[x, y]) < FONDO_MAXIMO

        fuera = [[False] * ancho for _ in range(alto)]
        cola = deque((x, y) for x in range(ancho) for y in (0, alto - 1))
        cola.extend((x, y) for y in range(alto) for x in (0, ancho - 1))
        cola = deque(p for p in cola if fondo(*p))
        for x, y in cola:
            fuera[y][x] = True
        while cola:
            x, y = cola.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < ancho and 0 <= ny < alto and not fuera[ny][nx] and fondo(nx, ny):
                    fuera[ny][nx] = True
                    cola.append((nx, ny))

        figura = Image.new("RGBA", (ancho, alto))
        figura.putdata([datos[x, y] + ((0,) if fuera[y][x] else (255,))
                        for y in range(alto) for x in range(ancho)])
        return figura.crop(figura.getbbox())


def _tramos(cuentas: list[int], minimo: int, largo: int) -> list[tuple[int, int]]:
    """Tramos seguidos donde la cuenta supera `minimo`, de al menos `largo` de largo."""
    tramos, inicio = [], None
    for i, cuenta in enumerate(cuentas + [0]):
        if cuenta > minimo and inicio is None:
            inicio = i
        elif cuenta <= minimo and inicio is not None:
            if i - inicio > largo:
                tramos.append((inicio, i - 1))
            inicio = None
    return tramos


# --- pelo -----------------------------------------------------------------------------------

# Rampas por luminosidad: el tono más oscuro (el contorno) se queda casi igual de oscuro para que
# la silueta no pierda su borde; el resto sube al color nuevo con las mismas luces y sombras.
CANAS = [(0, (28, 20, 32)), (16, (64, 58, 76)), (34, (124, 118, 136)), (54, (174, 170, 186)),
         (80, (220, 216, 230))]
CANOSO = [(0, (24, 18, 28)), (16, (46, 42, 54)), (34, (90, 86, 100)), (54, (134, 130, 144)),
          (80, (176, 172, 186))]
CASTANO = [(0, (30, 16, 22)), (16, (60, 32, 30)), (34, (114, 62, 42)), (54, (160, 98, 58)),
           (80, (202, 140, 86))]


def _luz(color) -> float:
    return 0.3 * color[0] + 0.59 * color[1] + 0.11 * color[2]


def _es_pelo(color) -> bool:
    """El pelo de la hoja es café oscuro tirando a morado: más rojo que verde y nada claro."""
    r, g, _ = color[:3]
    return color[3] > 0 and _luz(color) < 112 and r - g > 2 and r < 160


def _rampa(tramos, valor: float) -> tuple[int, int, int]:
    for (l0, c0), (l1, c1) in zip(tramos, tramos[1:]):
        if valor <= l1:
            t = max(0.0, min(1.0, (valor - l0) / max(1, l1 - l0)))
            return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
    return tramos[-1][1]


def teñir_pelo(figura: Image.Image, tramos, hasta: float, ojos: tuple[int, int, int, int]) -> Image.Image:
    """Cambia el color del pelo conservando su modelado.

    Es pelo lo oscuro y café que está conectado con la coronilla, de `hasta` (fracción del alto)
    para arriba: así no se tiñen la ropa oscura ni los zapatos. Los ojos también son oscuros y a
    veces tocan el flequillo por las cejas, así que su caja `ojos` (x0 y0 x1 y1, en píxeles del
    recorte) queda fuera.
    """
    figura = figura.copy()
    ancho, alto = figura.size
    datos = figura.load()
    tope = int(alto * hasta)
    marca = [[False] * ancho for _ in range(alto)]
    cola = deque((x, y) for x in range(ancho) for y in range(max(2, alto // 12)) if _es_pelo(datos[x, y]))
    for x, y in cola:
        marca[y][x] = True
    while cola:
        x, y = cola.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < ancho and 0 <= ny < tope and not marca[ny][nx] and _es_pelo(datos[nx, ny]):
                marca[ny][nx] = True
                cola.append((nx, ny))
    x0, y0, x1, y1 = ojos
    for y in range(alto):
        for x in range(ancho):
            if marca[y][x] and not (x0 <= x < x1 and y0 <= y < y1):
                datos[x, y] = _rampa(tramos, _luz(datos[x, y])) + (datos[x, y][3],)
    return figura


# --- retoques a escala de juego ---------------------------------------------------------------

def pintar(imagen: Image.Image, x: int, y: int, dibujo: list[str], colores: dict[str, tuple]) -> set:
    """Pega un dibujito de píxeles: cada letra es un color de `colores` y el punto no pinta.

    Devuelve los colores que usó: la paleta los tiene que conservar tal cual (ver `cuantizar`).
    """
    datos = imagen.load()
    usados = set()
    for fila, linea in enumerate(dibujo):
        for col, letra in enumerate(linea):
            if letra == "." or not (0 <= x + col < imagen.width and 0 <= y + fila < imagen.height):
                continue
            datos[x + col, y + fila] = tuple(colores[letra]) + (255,)
            usados.add(tuple(colores[letra]))
    return usados


def espejo(dibujo: list[str]) -> list[str]:
    return [linea[::-1] for linea in dibujo]


AMARILLOS = {"Y": (255, 236, 150), "y": (255, 210, 63), "a": (232, 160, 32), "c": (176, 96, 32),
             "o": (96, 52, 38)}

BIGOTE = {"o": (36, 30, 42), "m": (88, 84, 98), "l": (140, 136, 150)}
BIGOTE_RETRATO = [mitad + mitad[::-1] for mitad in (   # simétrico: la mitad y su espejo
    "..ommo",
    ".omllm",
    "ommmmm",
    "oo....",
)]
BIGOTE_SPRITE = [
    "mmmm",
]

TINTA_SOFI = (44, 28, 40)
# Los ojos de Alex, repintados: al bajar el retrato, el brillo de un ojo quedaba a un lado y el del
# otro al otro (y la paleta lo teñía de verde). Los dos iguales, con la luz de arriba a la izquierda.
OJO = {"k": (22, 12, 26), "n": (74, 46, 66), "W": (252, 246, 236), "w": (196, 186, 198)}
OJO_RETRATO = [
    "kkkk",
    "kWwk",
    "kWkk",
    "kkkk",
    "knnk",
]

COLETA = {"o": TINTA_SOFI, "d": (100, 54, 38), "m": (148, 88, 54), "l": (196, 134, 82),
          **{k: v for k, v in AMARILLOS.items() if k in "Yya"}}
COLETA_RETRATO = [      # cuelga por delante del hombro: a los lados de la cara no hay lugar
    "..oooo..",
    ".oYYyao.",
    ".oyyaao.",
    "..oaao..",
    "..odmo..",
    ".odmlmo.",
    ".odmllmo",
    "odmmlmo.",
    "odmlmmo.",
    "odmmlmo.",
    "odmmmmo.",
    ".odmmo..",
    ".odmmo..",
    "..odmo..",
    "..odo...",
    "...o....",
]
COLETA_SPRITE = [
    ".oy",
    "odm",
    "odm",
    "odl",
    ".od",
]

# El cuerpo de Sofi: sudadera crema como la del retrato, falda verde (su color en los diálogos) y
# zapatitos. Luz de arriba a la izquierda, contorno tibio como el de la hoja.
CUERPO_SOFI = {
    "o": TINTA_SOFI, "C": (244, 234, 216), "c": (214, 200, 184), "s": (168, 146, 142),
    "k": (46, 50, 66), "p": (238, 176, 136), "q": (198, 128, 104), "G": (190, 222, 132),
    "g": (140, 184, 96), "v": (88, 134, 74), "r": (156, 66, 60),
}
CUERPO_SOFI_DIBUJO = [      # brazos separados del torso por una línea, como en la hoja
    "....oCCkCco....",
    "..oCCCCkcccso..",
    ".oCcoCCCccocso.",
    ".oCcoCCcccocso.",
    ".oCcoCccccocso.",
    ".oppocccssoqqo.",
    "...oGGGgggvo...",
    "..oGGGggggvvo..",
    "..oGGgggggvvo..",
    "..ooooooooooo..",
    "....oqo.oqo....",
    "....oCo.oCo....",
    "...orro.orro...",
    "...ooo...ooo...",
]


# --- reducción y paleta -------------------------------------------------------------------------

def a_escala(figura: Image.Image, alto: int) -> Image.Image:
    """Baja una figura a `alto` píxeles con la misma receta que Liss (alfa premultiplicado)."""
    from generate_sprites import reducir

    ancho = max(1, round(figura.width * alto / figura.height))
    return reducir(figura, ancho, alto)


def en_caja(imagen: Image.Image, ancho: int, alto: int) -> Image.Image:
    """Centra horizontalmente y apoya en la última fila: los pies van abajo de la caja."""
    caja = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    caja.paste(imagen, ((ancho - imagen.width) // 2, alto - imagen.height), imagen)
    return caja


def cuadrado(figura: Image.Image) -> Image.Image:
    """Un retrato va en un cuadrado apoyado abajo: hombros en el borde, la cabeza centrada."""
    lado = max(figura.size)
    caja = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    caja.paste(figura, ((lado - figura.width) // 2, lado - figura.height))
    return caja


def cuantizar(*imagenes: Image.Image, colores: int = 23, fijos: set = frozenset()) -> list[Image.Image]:
    """Una paleta de ≤ 23 colores (más la transparencia) compartida por las imágenes de un asset.

    Corte por la mediana para empezar y unas vueltas de k-medias para acomodar la paleta, con
    cada píxel al color más cercano de verdad. La conversión a paleta de Pillow es aproximada y,
    en las zonas planas (la sudadera de Sofi), mezclaba crema, verde y piel en diagonales.

    `fijos` son los colores de los retoques pintados a mano: entran a la paleta tal cual y no se
    mueven, y lo pintado de la hoja también puede caer en ellos (la piel y el pelo de Sofi).
    """
    from generate_sprites import pixeles

    cuenta: dict[tuple, int] = {}
    for imagen in imagenes:
        for color in pixeles(imagen):
            if color[3] == 255:
                cuenta[color[:3]] = cuenta.get(color[:3], 0) + 1
    if len(cuenta) <= colores:
        return list(imagenes)

    fijos = [tuple(c) for c in sorted(fijos)]
    libres = colores - len(fijos)
    muestras = [c for c, n in cuenta.items() if c not in fijos for _ in range(max(1, round(n ** 0.5)))]
    tira = Image.new("RGB", (len(muestras), 1))
    tira.putdata(muestras)
    crudo = tira.quantize(colors=libres, method=Image.Quantize.MEDIANCUT,
                          dither=Image.Dither.NONE).getpalette()
    paleta = fijos + [tuple(crudo[i:i + 3]) for i in range(0, libres * 3, 3)]

    def cercano(color, paleta_):
        return min(range(len(paleta_)), key=lambda i: (
            (color[0] - paleta_[i][0]) ** 2 * 3 + (color[1] - paleta_[i][1]) ** 2 * 4 +
            (color[2] - paleta_[i][2]) ** 2 * 2))

    for _ in range(6):
        sumas = [[0.0, 0.0, 0.0, 0.0] for _ in paleta]
        for color, n in cuenta.items():
            peso = n ** 0.75
            s_ = sumas[cercano(color, paleta)]
            for canal in range(3):
                s_[canal] += color[canal] * peso
            s_[3] += peso
        paleta = [paleta[i] if i < len(fijos) or not s_[3] else tuple(round(s_[k] / s_[3]) for k in range(3))
                  for i, s_ in enumerate(sumas)]

    mapa = {color: paleta[cercano(color, paleta)] for color in cuenta}
    salida = []
    for imagen in imagenes:
        nueva = imagen.copy()
        nueva.putdata([mapa[c[:3]] + (255,) if c[3] == 255 else (0, 0, 0, 0) for c in pixeles(imagen)])
        salida.append(nueva)
    return salida


def respiracion(imagen: Image.Image, cintura: int | None = None) -> Image.Image:
    """Segundo frame quieto: el torso baja 1 px. Mismo truco que usa Liss."""
    salida = imagen.copy()
    corte = cintura if cintura is not None else round(imagen.height * 0.5)
    torso = imagen.crop((0, 0, imagen.width, corte))
    salida.paste(Image.new("RGBA", (imagen.width, corte), (0, 0, 0, 0)), (0, 0))
    salida.paste(torso, (0, 1), torso)
    return salida


# --- personajes -----------------------------------------------------------------------------

# Qué celda de la hoja es cada uno y a qué alto va. Los adultos miden lo que Liss (32) o casi;
# Doña Flora es un poco más bajita y Sofi es una niña.
PERSONAJES = {
    "alex": {"cuerpo": (7, 0), "alto": 33, "retrato": (0, 0)},
    "beto": {"cuerpo": (3, 0), "alto": 32, "retrato": (0, 1), "pelo": CANOSO,
             "ojos_cuerpo": (14, 27, 52, 40), "ojos_retrato": (45, 62, 140, 108)},
    "flora": {"cuerpo": (4, 0), "alto": 30, "retrato": (0, 2), "pelo": CANAS,
              "ojos_cuerpo": (22, 28, 58, 40), "ojos_retrato": (48, 66, 150, 104)},
    "sofi": {"alto": 26, "retrato": (0, 3), "pelo": CASTANO, "ojos_retrato": (45, 80, 140, 118)},
    "michi": {"cuerpo": (6, 0), "alto": 18, "retrato": (1, 0)},
}


def retrato(hoja: Hoja, ident: str) -> tuple[Image.Image, set]:
    """El retrato de 48 × 48 y los colores pintados a mano que lleva encima."""
    receta = PERSONAJES[ident]
    fijos: set = set()
    figura = hoja.recortar(*receta["retrato"])
    if "pelo" in receta:
        figura = teñir_pelo(figura, receta["pelo"], 0.68, receta["ojos_retrato"])
    imagen = a_escala(cuadrado(figura), RETRATO)
    if ident == "alex":
        for x in (17, 29):
            fijos |= pintar(imagen, x, 24, OJO_RETRATO, OJO)
    elif ident == "flora":
        flor = flor_del_pelo(hoja, 11)
        imagen.alpha_composite(flor, (32, 3))
    elif ident == "beto":
        # Centrado en la boca (x 24.5) y justo encima: las puntas caen a los lados de la sonrisa.
        fijos |= pintar(imagen, 19, 27, BIGOTE_RETRATO, BIGOTE)
    elif ident == "sofi":
        fijos |= pintar(imagen, 1, 23, COLETA_RETRATO, COLETA)
        fijos |= pintar(imagen, RETRATO - 9, 23, espejo(COLETA_RETRATO), COLETA)
    return imagen, fijos


def cuerpo_sofi(hoja: Hoja) -> tuple[Image.Image, set]:
    """Sofi de cuerpo entero: su cabeza sale del retrato (así se le reconoce la cara) y el cuerpo
    se pinta con el dibujo de arriba."""
    receta = PERSONAJES["sofi"]
    figura = teñir_pelo(hoja.recortar(*receta["retrato"]), receta["pelo"], 0.68, receta["ojos_retrato"])
    # Solo la cabeza: los hombros del retrato son de adulto, el cuerpo de una niña es más angosto.
    cabeza = a_escala(figura.crop((0, 0, figura.width, round(figura.height * 0.74))), 13)
    alto, ancho = receta["alto"], 20
    lienzo = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    fijos = pintar(lienzo, 2, alto - len(CUERPO_SOFI_DIBUJO), CUERPO_SOFI_DIBUJO, CUERPO_SOFI)
    lienzo.alpha_composite(cabeza, ((ancho - cabeza.width) // 2, 0))
    # Las coletas salen de debajo del pelo y se asoman por los costados de la cabeza.
    izquierda = (ancho - cabeza.width) // 2 - 2
    fijos |= pintar(lienzo, izquierda, 6, COLETA_SPRITE, COLETA)
    fijos |= pintar(lienzo, izquierda + cabeza.width + 1, 6, espejo(COLETA_SPRITE), COLETA)
    return lienzo, fijos


def cuerpo(hoja: Hoja, ident: str) -> tuple[Image.Image, set]:
    """El personaje de pie en su caja y los colores pintados a mano que lleva encima."""
    receta = PERSONAJES[ident]
    fijos: set = set()
    if ident == "sofi":
        imagen, fijos = cuerpo_sofi(hoja)
    else:
        figura = hoja.recortar(*receta["cuerpo"])
        if "pelo" in receta:
            figura = teñir_pelo(figura, receta["pelo"], 0.5, receta["ojos_cuerpo"])
        imagen = a_escala(figura, receta["alto"])
    if ident == "flora":
        # Del lado del pelo, no de la cara: de tres cuartos, la cara queda a la derecha.
        flor = flor_del_pelo(hoja, 5)
        imagen.alpha_composite(flor, (1, 4))
    elif ident == "beto":
        fijos |= pintar(imagen, imagen.width // 2 - 2, 13, BIGOTE_SPRITE, BIGOTE)
    if ident == "michi":
        return en_caja(imagen, max(14, imagen.width + 1), imagen.height + 1), fijos
    return en_caja(imagen, max(16, imagen.width + (imagen.width % 2)), ALTO_CAJA), fijos


# --- objetos e iconos -------------------------------------------------------------------------

OBJETOS = {
    # nombre: (celda, alto de la figura, caja)
    "ramo_0": ((7, 2), 24, (16, 24)),
    "ui_corazon": ((7, 3), 13, (16, 16)),
    "ui_flor": ((7, 4), 15, (16, 16)),
    "ui_corazon_chico": ((7, 3), 7, (9, 8)),
}


def flor_del_pelo(hoja: Hoja, alto: int) -> Image.Image:
    """La flor amarilla de Doña Flora: la flor del icono sin el tallo.

    El pétalo de abajo de la flor de la hoja está tapado por el tallo, así que se toma la mitad
    de arriba (hasta el centro naranja) y se completa con su espejo: queda entera y simétrica.
    """
    flor = hoja.recortar(*OBJETOS["ui_flor"][0])
    datos = flor.load()
    naranjas = [y for y in range(flor.height) for x in range(flor.width)
                if datos[x, y][3] and datos[x, y][0] > 200 and 90 < datos[x, y][1] < 170 and datos[x, y][2] < 90]
    centro = round(sum(naranjas) / len(naranjas)) if naranjas else flor.height // 2
    mitad = flor.crop((0, 0, flor.width, centro + 1))
    entera = Image.new("RGBA", (flor.width, 2 * centro + 1), (0, 0, 0, 0))
    entera.paste(mitad, (0, 0))
    entera.paste(mitad.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (0, centro))
    return a_escala(entera, alto)


def objeto(hoja: Hoja, celda: tuple[int, int], alto: int, caja: tuple[int, int]) -> Image.Image:
    imagen = a_escala(hoja.recortar(*celda), alto)
    lienzo = Image.new("RGBA", caja, (0, 0, 0, 0))
    lienzo.paste(imagen, ((caja[0] - imagen.width) // 2, (caja[1] - imagen.height) // 2), imagen)
    return lienzo


# --- partículas -------------------------------------------------------------------------------

def _degradado(mascara: Image.Image, luz: tuple, sombra: tuple, borde: tuple) -> Image.Image:
    """Rellena una silueta grande con luz de arriba-izquierda y un borde tibio.

    Se pinta a 8× y se baja con la receta de siempre: a 7 px queda el modelado, no el dibujo.
    """
    ancho, alto = mascara.size
    imagen = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    datos, m = imagen.load(), mascara.load()
    interior = mascara.filter(ImageFilter.MinFilter(9))
    adentro = interior.load()
    for y in range(alto):
        for x in range(ancho):
            if not m[x, y]:
                continue
            t = min(1.0, max(0.0, (x / ancho * 0.45 + y / alto * 0.75)))
            color = tuple(round(a + (b - a) * t) for a, b in zip(luz, sombra))
            datos[x, y] = (color if adentro[x, y] else borde) + (255,)
    return imagen


def petalo() -> Image.Image:
    """Pétalo amarillo en gota, con la vena del centro apenas marcada."""
    mascara = Image.new("L", (48, 56), 0)
    dib = ImageDraw.Draw(mascara)
    dib.ellipse([4, 14, 44, 54], fill=255)
    dib.polygon([(24, 0), (8, 26), (40, 26)], fill=255)
    imagen = _degradado(mascara, (255, 244, 170), (236, 162, 30), (150, 86, 30))
    ImageDraw.Draw(imagen).line([(24, 14), (25, 46)], fill=(232, 168, 44, 255), width=4)
    from generate_sprites import reducir
    return reducir(imagen, 6, 7)


def hoja_seca() -> Image.Image:
    """La trampa del minijuego: hoja café, ancha y con nervadura, que no se confunde con un pétalo."""
    mascara = Image.new("L", (64, 48), 0)
    ImageDraw.Draw(mascara).ellipse([2, 6, 62, 44], fill=255)
    ImageDraw.Draw(mascara).polygon([(0, 24), (10, 16), (10, 32)], fill=255)
    imagen = _degradado(mascara, (196, 140, 88), (110, 64, 42), (58, 34, 34))
    dib = ImageDraw.Draw(imagen)
    dib.line([(6, 25), (56, 25)], fill=(84, 48, 36, 255), width=4)
    for x in (22, 38):
        dib.line([(x, 25), (x + 10, 14)], fill=(84, 48, 36, 255), width=3)
        dib.line([(x, 25), (x + 10, 36)], fill=(84, 48, 36, 255), width=3)
    from generate_sprites import reducir
    return reducir(imagen, 8, 6)


# --- todo junto -------------------------------------------------------------------------------

def piezas() -> dict[str, Image.Image]:
    """Todos los frames que este módulo aporta al atlas, listos para empacar."""
    hoja = Hoja()
    salida: dict[str, Image.Image] = {}
    for ident in PERSONAJES:
        quieto, fijos = cuerpo(hoja, ident)
        cintura = round(quieto.height * (0.5 if ident == "michi" else 0.52))
        quieto, = cuantizar(quieto, fijos=fijos)
        salida[f"npc_{ident}_abajo_0"] = quieto
        salida[f"npc_{ident}_abajo_1"] = respiracion(quieto, cintura)
        cara, fijos = retrato(hoja, ident)
        salida[f"retrato_{ident}_normal"], = cuantizar(cara, fijos=fijos)

    for nombre, (celda, alto, caja) in OBJETOS.items():
        salida[nombre], = cuantizar(objeto(hoja, celda, alto, caja))

    salida["fx_petalo"], = cuantizar(petalo())
    salida["fx_hoja"], = cuantizar(hoja_seca())
    return salida


def main() -> int:
    parser = argparse.ArgumentParser(description="NPCs, retratos e iconos desde la hoja de personajes.")
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
