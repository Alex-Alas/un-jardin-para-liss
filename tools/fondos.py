#!/usr/bin/env python3
"""Fondos pintados para las pantallas que no son mapas: el título, los créditos y los pétalos.

Antes eran rectángulos y círculos planos dibujados por el motor, y desentonaban con todo lo
demás. Ahora salen de las mismas ilustraciones que los mapas, a la misma escala (1 px de pintura
= 1 px de juego), así no hay un píxel de otro tamaño en ninguna pantalla:

- **título y créditos**: el pueblo de noche, alrededor de la casa de Liss y la plaza;
- **pétalos 1** (el patio de la florería, de día): un escenario de costado, porque Liss corre de
  un lado a otro bajo los pétalos que caen. El cielo y el pasto se pintan acá con la paleta del
  pueblo, y encima van recortes de la pintura del pueblo: la florería, sus barriles y árboles;
- **pétalos 2** (el parque, a las seis de la tarde): igual, con pinos, el banco del pícnic y la
  luz del atardecer de la colina.

En el pasto no hay flores amarillas: el amarillo es de los pétalos que hay que atrapar.

    .venv/bin/python tools/fondos.py           # assets/fondo_<nombre>.png
    .venv/bin/python tools/fondos.py --ver     # además, dist/fondos.png con los tres juntos
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import escenarios  # noqa: E402
import tiles  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
ANCHO, ALTO = 480, 270                 # la pantalla del juego
HORIZONTE = 167                       # el mismo 62 % que usa la escena de pétalos

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def ruido(x: int, y: int, sal: int = 0) -> float:
    return tiles.ruido(x, y, sal)


def ruido_suave(x: float, y: float, escala: float, sal: int) -> float:
    """Ruido de valor interpolado: manchas grandes y suaves, como pinceladas."""
    gx, gy = x / escala, y / escala
    x0, y0 = int(gx), int(gy)
    tx, ty = gx - x0, gy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b = ruido(x0, y0, sal), ruido(x0 + 1, y0, sal)
    c, d = ruido(x0, y0 + 1, sal), ruido(x0 + 1, y0 + 1, sal)
    return (a + (b - a) * tx) * (1 - ty) + (c + (d - c) * tx) * ty


def mezclar(a, b, t: float):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


# --- la pintura de los mapas --------------------------------------------------------------------

def mapa(nombre: str) -> Image.Image:
    ruta = ASSETS / f"mapa_{nombre}.png"
    if not ruta.exists():
        raise SystemExit(f"falta {ruta.relative_to(RAIZ)}: corré antes tools/render_maps.py")
    return Image.open(ruta).convert("RGB")


def recorte(imagen: Image.Image, formas: list[tuple], ajuste: int = 3) -> Image.Image:
    """Un pedazo de la pintura con fondo transparente, con el borde pegado a la silueta pintada
    (la misma receta que los frentes de los mapas)."""
    mascara = escenarios.mascara_frente({"formas": formas}, imagen, ajuste)
    caja = mascara.getbbox()
    pieza = imagen.crop(caja).convert("RGBA")
    pieza.putalpha(mascara.crop(caja).point(lambda v: 255 if v > 127 else 0))
    return pieza


def arbol(imagen: Image.Image, tronco: int, piso: int, medio: int, cx: int, cy: int, rx: int, ry: int) -> Image.Image:
    """Un árbol del pueblo recortado entero: copa y tronco. Mismos números que `#! arbol` en
    maps/pueblo.txt."""
    return recorte(imagen, [("elipse", cx, cy, rx, ry), ("rect", tronco - medio, cy, tronco + medio + 1, piso + 1)])


def a_lo_lejos(pieza: Image.Image, cielo: tuple, cuanto: float) -> Image.Image:
    """Lo lejano se aclara hacia el color del cielo: perspectiva de aire, sin achicar el píxel."""
    lejos = pieza.copy()
    datos = lejos.load()
    for y in range(lejos.height):
        for x in range(lejos.width):
            r, g, b, a = datos[x, y]
            if a:
                datos[x, y] = mezclar((r, g, b), cielo, cuanto) + (a,)
    return lejos


def apoyar(lienzo: Image.Image, pieza: Image.Image, x: int, piso: int) -> None:
    """Pega una pieza con su base en la línea `piso` y centrada en `x`."""
    lienzo.alpha_composite(pieza, (x - pieza.width // 2, piso - pieza.height))


# --- cielo y pasto ------------------------------------------------------------------------------

def cielo(paradas: list[tuple[float, tuple]], alto: int = HORIZONTE + 4) -> Image.Image:
    """Cielo en franjas, con el paso de una a otra tramado: degradado de pixel art, no de foto."""
    imagen = Image.new("RGB", (ANCHO, alto))
    datos = imagen.load()
    for y in range(alto):
        t = y / (alto - 1)
        for (t0, c0), (t1, c1) in zip(paradas, paradas[1:]):
            if t0 <= t <= t1:
                local = (t - t0) / max(1e-6, t1 - t0)
                break
        for x in range(ANCHO):
            umbral = (BAYER[y % 4][x % 4] + 0.5) / 16
            datos[x, y] = c1 if local > umbral else c0
    return imagen


def nube(lienzo: Image.Image, x: int, y: int, ancho: int, sal: int, tonos: tuple) -> None:
    """Una nube de bultos: sombra abajo, cuerpo y luz arriba a la izquierda, en tres tonos."""
    sombra, cuerpo, luz = tonos
    dib = ImageDraw.Draw(lienzo)
    bultos = []
    paso = max(6, ancho // 5)
    for i, bx in enumerate(range(x, x + ancho, paso)):
        radio = round(paso * (0.75 + 0.6 * ruido(i, sal, 91)))
        alza = round(radio * 0.6 * ruido(i, sal, 92)) if 0 < i < ancho // paso - 1 else 0
        bultos.append((bx, y - alza, radio))
    for bx, by, r in bultos:
        dib.ellipse([bx - r, by - r + 3, bx + r, by + r * 0.7 + 3], fill=sombra)
    for bx, by, r in bultos:
        dib.ellipse([bx - r, by - r, bx + r, by + r * 0.7], fill=cuerpo)
    for bx, by, r in bultos:
        dib.ellipse([bx - r + 2, by - r + 1, bx + r * 0.35, by - r * 0.15], fill=luz)


def paleta_de_pasto(imagen: Image.Image, colores: int = 7) -> list[tuple]:
    """Los verdes de la pintura, del más oscuro al más claro: el pasto pintado acá usa esos."""
    chica = imagen.resize((imagen.width // 2, imagen.height // 2))
    crudo = chica.tobytes()
    muestras = [tuple(crudo[i:i + 3]) for i in range(0, len(crudo), 3)]
    muestras = [c for c in muestras if c[1] > c[0] + 12 and c[1] > c[2] + 8]
    verdes = Image.new("RGB", (len(muestras), 1))
    verdes.putdata(muestras)
    crudo = verdes.quantize(colors=colores, method=Image.Quantize.MEDIANCUT).getpalette()[:colores * 3]
    tonos = [tuple(crudo[i:i + 3]) for i in range(0, len(crudo), 3)]
    return sorted(tonos, key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])


def pasto(verdes: list[tuple], flores: list[tuple], sal: int = 0) -> Image.Image:
    """El piso de la escena: manchas de verde, matas de briznas y florcitas que no son amarillas.

    Hacia abajo (más cerca de quien mira) las manchas y las matas son más grandes: así el piso
    se va, aunque los píxeles sean todos del mismo tamaño.
    """
    alto = ALTO - HORIZONTE
    imagen = Image.new("RGB", (ANCHO, alto))
    datos = imagen.load()
    n = len(verdes)
    for y in range(alto):
        cerca = y / alto
        escala = 6 + 26 * cerca
        for x in range(ANCHO):
            v = ruido_suave(x, y * 1.8, escala, sal) * 0.75 + ruido(x, y, sal + 3) * 0.25
            indice = 1 + int(v * (n - 2.2) + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.9)
            datos[x, y] = verdes[max(0, min(n - 1, indice))]
    dib = ImageDraw.Draw(imagen)
    # Matas de pasto: tres briznas, la del medio más alta y con la punta iluminada.
    for i in range(int(ANCHO * alto / 34)):
        x = int(ruido(i, sal, 41) * ANCHO)
        y = int((ruido(i, sal, 42) ** 0.8) * alto)
        alto_mata = 2 + round(3 * y / alto)
        oscuro, claro = verdes[0], verdes[-1] if ruido(i, sal, 43) > 0.5 else verdes[-2]
        dib.line([x, y, x, y - alto_mata], fill=oscuro)
        dib.point((x, y - alto_mata), fill=claro)
        dib.line([x - 1, y, x - 2, y - alto_mata + 1], fill=verdes[1])
        dib.line([x + 1, y, x + 2, y - alto_mata + 1], fill=verdes[1])
    for i in range(int(ANCHO * alto / 260)):
        x = int(ruido(i, sal, 51) * ANCHO)
        y = 2 + int(ruido(i, sal, 52) * (alto - 3))
        color = flores[int(ruido(i, sal, 53) * len(flores)) % len(flores)]
        dib.point((x, y + 1), fill=verdes[0])
        dib.point((x, y), fill=color)
        if y > alto * 0.45:                                  # las cercanas, de cuatro pétalos
            for dx, dy in ((1, 0), (-1, 0), (0, -1)):
                dib.point((x + dx, y + dy), fill=color)
            dib.point((x, y - 1), fill=mezclar(color, (255, 255, 255), 0.4))
    return imagen


def camino(lienzo: Image.Image, arriba: tuple[int, int], abajo: tuple[int, int], tierra: list[tuple]) -> None:
    """Un sendero de tierra que baja de la puerta y se abre hacia quien mira, con borde mordido."""
    datos = lienzo.load()
    for y in range(HORIZONTE + 2, ALTO):
        t = (y - HORIZONTE) / (ALTO - HORIZONTE)
        x0 = arriba[0] + (abajo[0] - arriba[0]) * t
        x1 = arriba[1] + (abajo[1] - arriba[1]) * t
        for x in range(max(0, int(x0) - 3), min(ANCHO, int(x1) + 4)):
            borde = min(x - x0, x1 - x)
            if borde < -1.5 + 3 * ruido(x, y, 61):
                continue
            v = ruido_suave(x, y * 2, 5 + 10 * t, 62) * 0.7 + ruido(x, y, 63) * 0.3
            color = tierra[min(len(tierra) - 1, int(v * len(tierra)))]
            if borde < 2.5:
                color = tierra[0]                            # el canto del sendero, en sombra
            datos[x, y] = color
            if ruido(x, y, 64) > 0.985:
                datos[x, y] = tierra[-1]                     # piedritas


def sombra_al_pie(lienzo: Image.Image, x0: int, x1: int, y: int, color: tuple) -> None:
    """La franja de sombra donde las cosas del fondo tocan el pasto."""
    dib = ImageDraw.Draw(lienzo)
    dib.ellipse([x0, y - 3, x1, y + 4], fill=color)


# --- las escenas ----------------------------------------------------------------------------

def fondo_petalos1() -> Image.Image:
    """El patio de la florería, de día: la florería al fondo, árboles y el sendero de la puerta."""
    pueblo = mapa("pueblo")
    celeste = (176, 214, 238)
    lienzo = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 255))
    lienzo.paste(cielo([(0.0, (94, 146, 206)), (0.45, (128, 180, 228)), (0.8, (164, 206, 238)),
                        (1.0, celeste)]), (0, 0))
    tonos_nube = ((198, 214, 236), (238, 243, 250), (255, 255, 255))
    for x, y, w, sal in ((24, 38, 70, 1), (150, 22, 56, 2), (318, 46, 84, 3), (420, 18, 40, 4)):
        nube(lienzo, x, y, w, sal, tonos_nube)

    verdes = paleta_de_pasto(pueblo)
    lejanos = [arbol(pueblo, 744, 208, 4, 744, 188, 12, 18), arbol(pueblo, 40, 205, 4, 41, 185, 13, 16),
               arbol(pueblo, 360, 52, 4, 360, 27, 12, 17), arbol(pueblo, 230, 52, 4, 230, 27, 12, 17)]
    for i, x in enumerate(range(-6, ANCHO + 20, 22)):
        pieza = a_lo_lejos(lejanos[(i * 3) % len(lejanos)], celeste, 0.5)
        if ruido(i, 0, 73) > 0.5:                            # espejados, para que no se repitan
            pieza = pieza.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        apoyar(lienzo, pieza, x + int(ruido(i, 0, 71) * 8), HORIZONTE + 1 - int(ruido(i, 0, 72) * 4))

    lienzo.paste(pasto(verdes, [(214, 82, 72), (240, 236, 228), (122, 150, 214), (196, 132, 196)], 5),
                 (0, HORIZONTE))
    tierra = [(122, 86, 52), (168, 124, 76), (190, 146, 92), (206, 166, 110), (226, 198, 150)]
    camino(lienzo, (256, 278), (206, 334), tierra)

    floreria = recorte(pueblo, [("rect", 606, 77, 723, 176)])
    barriles = recorte(pueblo, [("rect", 720, 145, 738, 179)])
    sombra_al_pie(lienzo, 196, 340, HORIZONTE + 4, verdes[0])
    apoyar(lienzo, floreria, 268, HORIZONTE + 6)
    apoyar(lienzo, barriles, 338, HORIZONTE + 7)

    roble = arbol(pueblo, 298, 110, 10, 298, 38, 40, 36)
    pino = recorte(pueblo, [("poli", [(466, 44), (480, 56), (490, 80), (494, 96), (486, 106), (470, 108),
                                       (470, 126), (462, 126), (462, 108), (448, 106), (444, 96), (448, 76),
                                       (456, 56)])])
    redondo = arbol(pueblo, 744, 208, 4, 744, 188, 12, 18)
    for pieza, x, piso in ((roble, 70, HORIZONTE + 14), (redondo, 150, HORIZONTE + 6),
                           (pino, 410, HORIZONTE + 10), (redondo, 452, HORIZONTE + 8)):
        sombra_al_pie(lienzo, x - pieza.width // 3, x + pieza.width // 3, piso - 1, verdes[0])
        apoyar(lienzo, pieza, x, piso)
    return lienzo.convert("RGB")


def fondo_petalos2() -> Image.Image:
    """El parque a las seis de la tarde: pinos, el banco del pícnic y el sol bajando."""
    pueblo = mapa("pueblo")
    horizonte_cielo = (244, 178, 98)
    lienzo = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 255))
    lienzo.paste(cielo([(0.0, (86, 62, 124)), (0.3, (112, 92, 158)), (0.55, (196, 120, 128)),
                        (0.8, (236, 150, 96)), (1.0, horizonte_cielo)]), (0, 0))
    dib = ImageDraw.Draw(lienzo)
    sol_x, sol_y = ANCHO - 104, HORIZONTE - 74
    for radio, color in ((26, (246, 170, 90)), (21, (250, 196, 110)), (16, (255, 226, 150))):
        dib.ellipse([sol_x - radio, sol_y - radio, sol_x + radio, sol_y + radio], fill=color)
    tonos_nube = ((150, 92, 128), (214, 130, 120), (246, 186, 140))
    for x, y, w, sal in ((30, 44, 80, 6), (190, 28, 60, 7), (300, 70, 64, 8)):
        nube(lienzo, x, y, w, sal, tonos_nube)

    verdes = paleta_de_pasto(pueblo)
    lejanos = [arbol(pueblo, 744, 208, 4, 744, 188, 12, 18), arbol(pueblo, 360, 52, 4, 360, 27, 12, 17)]
    pinos = [recorte(pueblo, [("poli", puntos)]) for puntos in (
        [(580, 266), (598, 290), (604, 318), (600, 340), (592, 346), (592, 352), (580, 352), (580, 346),
         (566, 342), (560, 318), (564, 292)],
        [(708, 394), (718, 410), (728, 428), (738, 448), (740, 462), (724, 468), (716, 470), (716, 481),
         (706, 481), (706, 470), (690, 466), (674, 460), (676, 444), (688, 428), (698, 410)],
    )]
    suelo = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    for i, x in enumerate(range(-8, ANCHO + 20, 20)):
        pieza = a_lo_lejos((lejanos + pinos)[(i * 3) % 4], (200, 140, 130), 0.45)
        if ruido(i, 1, 73) > 0.5:
            pieza = pieza.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        apoyar(suelo, pieza, x + int(ruido(i, 1, 71) * 8), HORIZONTE + 1 - int(ruido(i, 1, 72) * 5))
    suelo.paste(pasto(verdes, [(214, 82, 72), (240, 236, 228), (196, 132, 196)], 9), (0, HORIZONTE))

    banco = recorte(pueblo, [("rect", 545, 358, 588, 387)])
    canasta = recorte(pueblo, [("rect", 586, 372, 606, 396)])
    roble = arbol(pueblo, 537, 158, 10, 535, 92, 40, 36)
    for pieza, x, piso in ((roble, 92, HORIZONTE + 16), (pinos[0], 196, HORIZONTE + 10),
                           (banco, 272, HORIZONTE + 14), (canasta, 304, HORIZONTE + 16),
                           (pinos[1], 404, HORIZONTE + 12)):
        sombra_al_pie(suelo, x - pieza.width // 3, x + pieza.width // 3, piso - 1, verdes[0])
        apoyar(suelo, pieza, x, piso)

    # La luz de la colina: el mismo remapeo que tiñe el mapa del final.
    tiles.atardecer(suelo)
    lienzo.alpha_composite(suelo)
    return lienzo.convert("RGB")


def noche(imagen: Image.Image) -> Image.Image:
    """El pueblo a la hora azul: oscuro y frío, con lo claro todavía un poco tibio."""
    resultado = imagen.copy()
    datos = resultado.load()
    tabla = {}
    for y in range(resultado.height):
        for x in range(resultado.width):
            color = datos[x, y]
            if color not in tabla:
                r, g, b = color
                luz = 0.3 * r + 0.59 * g + 0.11 * b
                tabla[color] = (round(r * 0.30 + luz * 0.10 + 10), round(g * 0.32 + luz * 0.10 + 12),
                                round(b * 0.42 + luz * 0.22 + 34))
            datos[x, y] = tabla[color]
    return resultado


# Las ventanas de la casa de Liss en maps/pueblo (x0 y0 x1 y1): de noche tienen la luz prendida.
VENTANAS = [(64, 125, 76, 138), (96, 125, 108, 138), (196, 124, 209, 138)]


def ventanas_prendidas(imagen: Image.Image, origen: tuple[int, int]) -> None:
    """El vidrio oscuro de cada ventana pasa a luz tibia, y alrededor queda un halo tramado."""
    datos = imagen.load()
    ox, oy = origen
    for x0, y0, x1, y1 in VENTANAS:
        x0, y0, x1, y1 = x0 - ox, y0 - oy, x1 - ox, y1 - oy
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for y in range(max(0, y0 - 14), min(imagen.height, y1 + 14)):
            for x in range(max(0, x0 - 14), min(imagen.width, x1 + 14)):
                r, g, b = datos[x, y]
                if x0 <= x < x1 and y0 <= y < y1:
                    luz = 0.3 * r + 0.59 * g + 0.11 * b
                    if luz < 40:
                        datos[x, y] = (255, 214, 128) if (x + y) % 5 else (236, 168, 84)
                    continue
                distancia = max(abs(x - cx) - (x1 - x0) / 2, abs(y - cy) - (y1 - y0) / 2)
                tibio = max(0.0, 1 - distancia / 14) ** 2 * 0.4
                if tibio > (BAYER[y % 4][x % 4] + 0.5) / 16 * 0.4:
                    datos[x, y] = mezclar((r, g, b), (236, 168, 84), tibio)


def fondo_titulo() -> Image.Image:
    """El pueblo de noche, de la casa de Liss a la plaza, con un velo que deja leer el título."""
    pueblo = mapa("pueblo")
    origen = (56, 40)
    imagen = noche(pueblo.crop((origen[0], origen[1], origen[0] + ANCHO, origen[1] + ALTO)))
    # Viñeta y una banda más oscura detrás del título: el texto amarillo se lee sin recuadro.
    datos = imagen.load()
    for y in range(ALTO):
        for x in range(ANCHO):
            dx, dy = (x - ANCHO / 2) / (ANCHO / 2), (y - ALTO / 2) / (ALTO / 2)
            borde = min(1.0, (dx * dx + dy * dy) ** 0.5)
            banda = max(0.0, 1 - abs(y - 92) / 70)
            oscuro = 0.18 + 0.42 * borde ** 2 + 0.28 * banda
            oscuro = min(0.82, oscuro + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.06)
            datos[x, y] = mezclar(datos[x, y], (12, 10, 26), oscuro)
    ventanas_prendidas(imagen, origen)
    return imagen


FONDOS = {"titulo": fondo_titulo, "petalos1": fondo_petalos1, "petalos2": fondo_petalos2}


def guardar(nombre: str, imagen: Image.Image) -> Path:
    destino = ASSETS / f"fondo_{nombre}.png"
    # 256 colores sin tramado: pesa poco y a esta escala no se nota (igual que los mapas pintados).
    imagen.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(destino, optimize=True)
    return destino


def main() -> int:
    parser = argparse.ArgumentParser(description="Fondos pintados: título, créditos y pétalos.")
    parser.add_argument("--ver", action="store_true", help="guarda dist/fondos.png con los tres juntos")
    args = parser.parse_args()

    hechos = {}
    for nombre, hacer in FONDOS.items():
        hechos[nombre] = hacer()
        destino = guardar(nombre, hechos[nombre])
        print(f"  · {destino.relative_to(RAIZ)}  {destino.stat().st_size // 1024} KB")
    if args.ver:
        hoja = Image.new("RGB", (ANCHO, ALTO * len(hechos)))
        for i, nombre in enumerate(hechos):
            hoja.paste(Image.open(ASSETS / f"fondo_{nombre}.png").convert("RGB"), (0, ALTO * i))
        destino = RAIZ / "dist" / "fondos.png"
        destino.parent.mkdir(exist_ok=True)
        hoja.resize((ANCHO * 2, ALTO * 2 * len(hechos)), Image.NEAREST).save(destino)
        print(f"  · {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
