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
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

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


def _luz(color) -> float:
    return 0.3 * color[0] + 0.59 * color[1] + 0.11 * color[2]


def _distancia(a, b) -> int:
    return 3 * (a[0] - b[0]) ** 2 + 4 * (a[1] - b[1]) ** 2 + 2 * (a[2] - b[2]) ** 2


def _vecinos4(x: int, y: int):
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


def recorte(imagen: Image.Image, formas: list[tuple], tronco: tuple | None = None,
            base: int | None = None, contorno: bool = True) -> Image.Image:
    """Un pedazo de la pintura listo para ir contra el cielo: sin un píxel del suelo que tenía.

    Los frentes de los mapas se recortan con una forma y un ajuste de borde, y algo de pasto
    les queda pegado: no importa, porque se dibujan encima del mismo pasto. Contra un cielo, en
    cambio, cada resto se ve. Así que acá:

    1. los colores del objeto salen de su núcleo (la forma achicada) y los del suelo de un anillo
       por fuera de la forma; cada color se queda del lado donde es más común;
    2. el suelo es lo que se alcanza desde el borde pasando solo por colores de suelo, así un
       verde de pasto adentro de la copa (rodeado de hojas) no se pierde;
    3. en `tronco` (x, desde, piso, medio ancho) manda otra regla: solo sobrevive la madera, que
       tira a rojo, y no el pasto de al lado ni la sombra del piso;
    4. con `base`, todo lo de abajo de esa fila se corta derecho (una casa apoya en una línea);
    5. limpieza: se abre la silueta (fuera lo de menos de 3 px de grueso), queda solo la parte
       más grande y sin agujeros, y se le pone un contorno oscuro con el tono más hondo del
       objeto, para que el borde se lea pintado y no recortado.

    No todo sale bien recortado: los pinos del pueblo están montados de a dos o tres y se llevan
    ramas del vecino. Por eso los fondos usan solo los árboles que quedan limpios.
    """
    mascara_forma = Image.new("L", imagen.size, 0)
    for forma in formas:
        escenarios.dibujar_forma(ImageDraw.Draw(mascara_forma), forma, 255)
    if tronco:
        tx, desde, piso, medio = tronco
        escenarios.dibujar_forma(ImageDraw.Draw(mascara_forma), ("rect", tx - medio, desde, tx + medio + 1, piso + 1), 255)
    x0, y0, x1, y1 = mascara_forma.getbbox()
    margen = 12
    caja = (max(0, x0 - margen), max(0, y0 - margen), min(imagen.width, x1 + margen),
            min(imagen.height, y1 + margen))
    zona = imagen.crop(caja).convert("RGB")
    ancho, alto = zona.size
    px = zona.load()
    forma = mascara_forma.crop(caja)
    lado = max(2, round(min(x1 - x0, y1 - y0) * 0.22))
    nucleo = forma.filter(ImageFilter.MinFilter(2 * lado + 1)).load()
    cerca = forma.filter(ImageFilter.MaxFilter(5)).load()        # la forma, 2 px más ancha
    lejos = forma.filter(ImageFilter.MaxFilter(9)).load()        # de acá para afuera es suelo

    def en_tronco(x: int, y: int) -> bool:
        if not tronco:
            return False
        gx, gy = x + caja[0], y + caja[1]
        return tx - medio - 2 <= gx <= tx + medio + 2 and gy >= desde

    del_objeto, del_suelo = {}, {}
    for y in range(alto):
        for x in range(ancho):
            if nucleo[x, y]:
                del_objeto[px[x, y]] = del_objeto.get(px[x, y], 0) + 1
            elif not lejos[x, y]:
                del_suelo[px[x, y]] = del_suelo.get(px[x, y], 0) + 1
    total_o, total_s = sum(del_objeto.values()) or 1, sum(del_suelo.values()) or 1
    conocidos = list(del_objeto) + list(del_suelo)
    clase: dict = {}

    def es_objeto(color) -> bool:
        if color not in clase:
            o, s_ = del_objeto.get(color, 0), del_suelo.get(color, 0)
            if o + s_ == 0:
                vecino = min(conocidos, key=lambda k: _distancia(k, color))
                o, s_ = del_objeto.get(vecino, 0), del_suelo.get(vecino, 0)
            clase[color] = (o + 0.3) / total_o >= (s_ + 0.3) / total_s
        return clase[color]

    def es_madera(color) -> bool:
        return color[0] >= color[1] - 2 or _luz(color) < 40

    def es_suelo(x: int, y: int) -> bool:
        if base is not None and y + caja[1] > base:
            return True
        if not cerca[x, y]:
            return True
        if en_tronco(x, y):
            return not es_madera(px[x, y])
        if nucleo[x, y]:
            return False
        return not es_objeto(px[x, y])

    suelo = [[False] * ancho for _ in range(alto)]
    cola = deque(p for p in [(x, y) for x in range(ancho) for y in (0, alto - 1)] +
                 [(x, y) for y in range(alto) for x in (0, ancho - 1)] if es_suelo(*p))
    for x, y in cola:
        suelo[y][x] = True
    while cola:
        x, y = cola.popleft()
        for nx, ny in _vecinos4(x, y):
            if 0 <= nx < ancho and 0 <= ny < alto and not suelo[ny][nx] and es_suelo(nx, ny):
                suelo[ny][nx] = True
                cola.append((nx, ny))

    marca = Image.new("L", (ancho, alto), 0)
    marca.putdata([0 if suelo[y][x] or not cerca[x, y] else 255 for y in range(alto) for x in range(ancho)])
    marca = limpiar(marca)

    pieza = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    pieza.paste(zona, (0, 0), marca)
    if contorno:
        hondos = sorted(del_objeto, key=_luz)[:max(1, len(del_objeto) // 12)]
        tinta = tuple(round(sum(c[i] for c in hondos) / len(hondos) * 0.65) for i in range(3))
        borde = ImageChops.subtract(marca.filter(ImageFilter.MaxFilter(3)), marca)
        pieza.paste(tinta + (255,), (0, 0), borde)
    return pieza.crop(pieza.getbbox())


def limpiar(marca: Image.Image) -> Image.Image:
    """La silueta sin basura: abierta (fuera los pelos y los grumos de menos de 3 px), la parte
    más grande sola y sin agujeros."""
    abierta = marca.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    ancho, alto = abierta.size
    datos = abierta.load()
    visto = [[False] * ancho for _ in range(alto)]
    mejor: list = []
    for y in range(alto):
        for x in range(ancho):
            if datos[x, y] and not visto[y][x]:
                parte, cola = [], deque([(x, y)])
                visto[y][x] = True
                while cola:
                    a, b = cola.popleft()
                    parte.append((a, b))
                    for na, nb in _vecinos4(a, b):
                        if 0 <= na < ancho and 0 <= nb < alto and datos[na, nb] and not visto[nb][na]:
                            visto[nb][na] = True
                            cola.append((na, nb))
                if len(parte) > len(mejor):
                    mejor = parte
    sola = Image.new("L", (ancho, alto), 0)
    sd = sola.load()
    for x, y in mejor:
        sd[x, y] = 255
    # Sin agujeros: lo vacío que no se alcanza desde el borde pasa a ser parte de la silueta.
    afuera = [[False] * ancho for _ in range(alto)]
    cola = deque(p for p in [(x, y) for x in range(ancho) for y in (0, alto - 1)] +
                 [(x, y) for y in range(alto) for x in (0, ancho - 1)] if not sd[p[0], p[1]])
    for x, y in cola:
        afuera[y][x] = True
    while cola:
        a, b = cola.popleft()
        for na, nb in _vecinos4(a, b):
            if 0 <= na < ancho and 0 <= nb < alto and not sd[na, nb] and not afuera[nb][na]:
                afuera[nb][na] = True
                cola.append((na, nb))
    for y in range(alto):
        for x in range(ancho):
            if not afuera[y][x]:
                sd[x, y] = 255
    return sola


def arbol(imagen: Image.Image, tronco: int, piso: int, medio: int, cx: int, cy: int, rx: int, ry: int) -> Image.Image:
    """Un árbol del pueblo recortado entero: copa y tronco. Mismos números que `#! arbol` en
    maps/pueblo.txt."""
    # La regla del tronco (solo madera) empieza abajo de la copa: si empezara adentro, se comería
    # las hojas que tapan el tronco y el tronco quedaría suelto.
    return recorte(imagen, [("elipse", cx, cy, rx, ry)], tronco=(tronco, cy + round(ry * 0.85), piso, medio))


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


def arboles(imagen: Image.Image) -> dict[str, Image.Image]:
    """Los árboles del pueblo que se recortan limpios: el roble grande y tres redondos. (Los mismos
    números que sus `#! arbol` en maps/pueblo.txt.)"""
    return {
        "roble": arbol(imagen, 298, 110, 10, 298, 38, 40, 36),
        "redondo": arbol(imagen, 744, 208, 4, 744, 188, 12, 18),
        "alto": arbol(imagen, 360, 52, 4, 360, 27, 12, 17),
        "claro": arbol(imagen, 230, 52, 4, 230, 27, 12, 17),
    }


def espejo(pieza: Image.Image) -> Image.Image:
    return pieza.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


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
    arbol_ = arboles(pueblo)
    lejanos = [arbol_["redondo"], arbol_["alto"], arbol_["claro"]]
    for i, x in enumerate(range(-6, ANCHO + 20, 22)):
        pieza = a_lo_lejos(lejanos[(i * 2) % len(lejanos)], celeste, 0.5)
        if ruido(i, 0, 73) > 0.5:                            # espejados, para que no se repitan
            pieza = espejo(pieza)
        apoyar(lienzo, pieza, x + int(ruido(i, 0, 71) * 8), HORIZONTE + 1 - int(ruido(i, 0, 72) * 4))

    lienzo.paste(pasto(verdes, [(214, 82, 72), (240, 236, 228), (122, 150, 214), (196, 132, 196)], 5),
                 (0, HORIZONTE))
    tierra = [(122, 86, 52), (168, 124, 76), (190, 146, 92), (206, 166, 110), (226, 198, 150)]
    camino(lienzo, (256, 278), (206, 334), tierra)

    # El techo llega a la columna 720 y la pared a la 718; justo al lado empieza un seto, que no va.
    floreria = recorte(pueblo, [("rect", 606, 77, 721, 138), ("rect", 606, 138, 719, 176)], base=174,
                       contorno=False)
    barriles = recorte(pueblo, [("rect", 722, 145, 738, 179)], base=178, contorno=False)
    sombra_al_pie(lienzo, 196, 340, HORIZONTE + 4, verdes[0])
    apoyar(lienzo, floreria, 268, HORIZONTE + 6)
    apoyar(lienzo, barriles, 338, HORIZONTE + 7)

    for pieza, x, piso in ((arbol_["roble"], 70, HORIZONTE + 14), (arbol_["redondo"], 150, HORIZONTE + 6),
                           (espejo(arbol_["alto"]), 404, HORIZONTE + 8), (arbol_["claro"], 446, HORIZONTE + 10)):
        sombra_al_pie(lienzo, x - pieza.width // 3, x + pieza.width // 3, piso - 1, verdes[0])
        apoyar(lienzo, pieza, x, piso)
    return lienzo.convert("RGB")


def fondo_petalos2() -> Image.Image:
    """El parque a las seis de la tarde: árboles, el banco del pícnic y el sol bajando."""
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
    arbol_ = arboles(pueblo)
    lejanos = [arbol_["alto"], arbol_["redondo"], arbol_["claro"]]
    suelo = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    for i, x in enumerate(range(-8, ANCHO + 20, 18)):
        pieza = a_lo_lejos(lejanos[(i * 2) % len(lejanos)], (200, 140, 130), 0.45)
        if ruido(i, 1, 73) > 0.5:
            pieza = espejo(pieza)
        apoyar(suelo, pieza, x + int(ruido(i, 1, 71) * 8), HORIZONTE + 1 - int(ruido(i, 1, 72) * 5))
    suelo.paste(pasto(verdes, [(214, 82, 72), (240, 236, 228), (196, 132, 196)], 9), (0, HORIZONTE))

    banco = recorte(pueblo, [("rect", 545, 358, 588, 387)], base=386, contorno=False)
    for pieza, x, piso in ((espejo(arbol_["roble"]), 404, HORIZONTE + 16), (arbol_["claro"], 70, HORIZONTE + 8),
                           (arbol_["alto"], 122, HORIZONTE + 12), (banco, 250, HORIZONTE + 14),
                           (espejo(arbol_["redondo"]), 316, HORIZONTE + 9)):
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
