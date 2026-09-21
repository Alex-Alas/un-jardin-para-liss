#!/usr/bin/env python3
"""Normaliza la hoja de sprites de Liss y arma el atlas que carga el juego.

    .venv/bin/python tools/generate_sprites.py --inspeccionar   # reporte de la hoja, no escribe nada
    .venv/bin/python tools/generate_sprites.py                  # assets/atlas.png + assets/atlas.json
    .venv/bin/python tools/generate_sprites.py --contacto       # además, hoja de contacto en dist/

La hoja (`assets/source/liss-sheet.png`) es un render suave, no pixel art puro: trae 8 direcciones
en dos secciones (estático y movimiento), tres poses por fila y dos filas por sección. Este script
la recorta, le quita el fondo y la sombra, la baja a la escala del juego y la cuantiza a una sola
paleta compartida por todos los frames (si cada frame se cuantizara aparte, la animación titila).

Todo es determinista: misma hoja, mismo atlas.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
HOJA = RAIZ / "assets" / "source" / "liss-sheet.png"
ASSETS = RAIZ / "assets"

# --- marco técnico (ver docs/arte.md § La hoja de Liss manda) -----------------------------------
ALTO_OBJETIVO = 32          # alto en píxeles del sprite ya en escala de juego (2 tiles)
MAX_COLORES = 23            # 22 colores + transparencia, para cumplir el tope de docs/arte.md
UMBRAL_ALFA = 128           # alpha duro: adentro o afuera, nunca a medias
NITIDEZ = 1.6               # el reescalado grande ablanda la cara; esto le devuelve el contorno

# La hoja se lee por bandas horizontales; el orden de sus columnas es el de sus rótulos.
DIRECCIONES = [
    "abajo",            # S
    "abajo_derecha",    # SE
    "derecha",          # E
    "arriba_derecha",   # NE
    "arriba",           # N
    "arriba_izquierda", # NW
    "izquierda",        # W
    "abajo_izquierda",  # SW
]
POSES_POR_FILA = 3
FILAS_POR_SECCION = 2
SECCIONES = ["estatico", "movimiento"]

# Retratos: se eligen a mano porque la diferencia es la expresión, y eso no se mide con un umbral.
# (banda, columna dentro de la banda) de la sección estática, mirando al frente.
RETRATOS = {"normal": (1, 0), "feliz": (0, 1)}
ALTO_RETRATO = 48
PORCION_RETRATO = 0.52      # cuánto del alto del sprite entra en el retrato (cabeza y hombros)

# --- reconocimiento de la hoja ------------------------------------------------------------------
UMBRAL_TINTA = 140          # para encontrar bandas y columnas: el pelo y los contornos son oscuros
FONDO = (253, 250, 235)     # crema del papel de la hoja
DISTANCIA_FONDO = 60        # suma de diferencias RGB a partir de la cual un píxel ya no es fondo
SATURACION_MINIMA = 26
LUZ_MAXIMA = 200


def pixeles(imagen: Image.Image) -> list[tuple]:
    """Píxeles como lista de tuplas (Image.getdata quedó deprecado en Pillow 12)."""
    crudo = imagen.tobytes()
    bandas_ = len(imagen.getbands())
    return [tuple(crudo[i:i + bandas_]) for i in range(0, len(crudo), bandas_)]


def cargar_hoja() -> Image.Image:
    if not HOJA.exists():
        raise SystemExit(
            f"Falta la hoja de sprites en {HOJA.relative_to(RAIZ)}.\n"
            "Colocá ahí el PNG de Liss y volvé a correr este script."
        )
    return Image.open(HOJA).convert("RGB")


def _proyeccion(binaria: Image.Image) -> list[int]:
    """Cuenta píxeles marcados por fila de una imagen en blanco y negro."""
    ancho, alto = binaria.size
    datos = binaria.tobytes()
    return [datos[y * ancho:(y + 1) * ancho].count(255) for y in range(alto)]


def bandas(hoja: Image.Image) -> list[tuple[int, int]]:
    """Bandas horizontales con sprites (descarta el banner y los rótulos por su alto)."""
    binaria = hoja.convert("L").point(lambda v: 255 if v < UMBRAL_TINTA else 0)
    filas = _proyeccion(binaria)
    encontradas: list[tuple[int, int]] = []
    inicio = None
    for y, cuenta in enumerate(filas + [0]):
        if cuenta > 5 and inicio is None:
            inicio = y
        elif cuenta <= 5 and inicio is not None:
            if 60 < y - inicio < 140:
                encontradas.append((inicio, y - 1))
            inicio = None
    return encontradas


def columnas(hoja: Image.Image, banda: tuple[int, int]) -> list[tuple[int, int]]:
    """Columnas con sprites dentro de una banda."""
    y0, y1 = banda
    recorte = hoja.crop((0, y0, hoja.width, y1 + 1)).convert("L")
    binaria = recorte.point(lambda v: 255 if v < UMBRAL_TINTA + 10 else 0).transpose(
        Image.Transpose.ROTATE_90
    )
    cuentas = list(reversed(_proyeccion(binaria)))
    encontradas: list[tuple[int, int]] = []
    inicio = None
    for x, cuenta in enumerate(cuentas + [0]):
        if cuenta > 0 and inicio is None:
            inicio = x
        elif cuenta == 0 and inicio is not None:
            if x - inicio > 10:
                encontradas.append((inicio, x - 1))
            inicio = None
    return encontradas


def mascara(celda: Image.Image) -> list[bool]:
    """Silueta del personaje: color fuerte, más todo lo que quede encerrado por su contorno.

    Se inunda desde el borde por donde NO hay color fuerte; lo que la inundación no alcanza es
    interior (el vestido pálido, que casi se confunde con el papel). La sombra del piso queda
    afuera porque es gris clarito, y la que se cuela entre las piernas se descarta por color.
    """
    ancho, alto = celda.size
    tonos = pixeles(celda)
    fuerte = [False] * (ancho * alto)
    sombra = [False] * (ancho * alto)
    for i, (r, g, b) in enumerate(tonos):
        distancia = abs(r - FONDO[0]) + abs(g - FONDO[1]) + abs(b - FONDO[2])
        luz = (r + g + b) / 3
        saturacion = max(r, g, b) - min(r, g, b)
        fuerte[i] = distancia > DISTANCIA_FONDO and (saturacion > SATURACION_MINIMA or luz < LUZ_MAXIMA)
        sombra[i] = saturacion < 24 and 150 < luz < 232

    fuera = [False] * (ancho * alto)
    cola: deque[int] = deque()
    for x in range(ancho):
        for y in (0, alto - 1):
            i = y * ancho + x
            if not fuerte[i] and not fuera[i]:
                fuera[i] = True
                cola.append(i)
    for y in range(alto):
        for x in (0, ancho - 1):
            i = y * ancho + x
            if not fuerte[i] and not fuera[i]:
                fuera[i] = True
                cola.append(i)
    while cola:
        i = cola.popleft()
        x, y = i % ancho, i // ancho
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < ancho and 0 <= ny < alto:
                j = ny * ancho + nx
                if not fuera[j] and not fuerte[j]:
                    fuera[j] = True
                    cola.append(j)

    return [(fuerte[i] or not fuera[i]) and not sombra[i] for i in range(ancho * alto)]


def erosionar(marca: list[bool], ancho: int, alto: int) -> list[bool]:
    """Come un píxel de orilla: el borde de la hoja viene mezclado con el papel y ensucia el color."""
    salida = [False] * (ancho * alto)
    for y in range(alto):
        for x in range(ancho):
            i = y * ancho + x
            if not marca[i]:
                continue
            if x == 0 or y == 0 or x == ancho - 1 or y == alto - 1:
                continue
            if marca[i - 1] and marca[i + 1] and marca[i - ancho] and marca[i + ancho]:
                salida[i] = True
    return salida


class Frame:
    """Un sprite recortado de la hoja, todavía en la resolución original."""

    def __init__(self, celda: Image.Image, marca: list[bool], banda: int, columna: int):
        ancho, alto = celda.size
        self.banda = banda
        self.columna = columna
        self.direccion = DIRECCIONES[columna // POSES_POR_FILA]
        self.pose = columna % POSES_POR_FILA
        self.seccion = SECCIONES[banda // FILAS_POR_SECCION]

        xs = [i % ancho for i, v in enumerate(marca) if v]
        ys = [i // ancho for i, v in enumerate(marca) if v]
        self.x0, self.x1 = min(xs), max(xs)
        self.y0, self.y1 = min(ys), max(ys)
        self.ancho = self.x1 - self.x0 + 1
        self.alto = self.y1 - self.y0 + 1
        self.centro = round(sum(xs) / len(xs))
        self.pies = self.y1
        self.pixeles = len(xs)

        datos = pixeles(celda)
        self.imagen = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
        self.imagen.putdata([
            datos[i] + (255,) if marca[i] else (0, 0, 0, 0) for i in range(ancho * alto)
        ])

        # separación máxima de los pies: sirve para ordenar el ciclo de caminata
        corte = max(self.y0, self.y1 - 9)
        pies_xs = [i % ancho for i, v in enumerate(marca) if v and i // ancho >= corte]
        self.ancho_pies = (max(pies_xs) - min(pies_xs) + 1) if pies_xs else 0

    def recortar(self, ancho_caja: int, alto_caja: int) -> Image.Image:
        """Recorta con la misma caja para todos los frames, anclado en los pies y en el centro."""
        x = self.centro - ancho_caja // 2
        y = self.pies + 1 - alto_caja
        caja = Image.new("RGBA", (ancho_caja, alto_caja), (0, 0, 0, 0))
        caja.paste(self.imagen.crop((x, y, x + ancho_caja, y + alto_caja)), (0, 0))
        return caja


def leer_frames(hoja: Image.Image) -> list[Frame]:
    frames: list[Frame] = []
    lista_bandas = bandas(hoja)
    if len(lista_bandas) != len(SECCIONES) * FILAS_POR_SECCION:
        raise SystemExit(
            f"Se esperaban {len(SECCIONES) * FILAS_POR_SECCION} bandas de sprites y se encontraron "
            f"{len(lista_bandas)}: {lista_bandas}"
        )
    esperadas = len(DIRECCIONES) * POSES_POR_FILA
    for indice, banda in enumerate(lista_bandas):
        cols = columnas(hoja, banda)
        if len(cols) != esperadas:
            raise SystemExit(
                f"La banda {indice} ({banda}) tiene {len(cols)} columnas y se esperaban {esperadas}."
            )
        y0, y1 = banda
        for columna, (x0, x1) in enumerate(cols):
            celda = hoja.crop((max(0, x0 - 2), max(0, y0 - 2), min(hoja.width, x1 + 3),
                               min(hoja.height, y1 + 3)))
            marca = mascara(celda)
            marca = erosionar(marca, celda.width, celda.height)
            frames.append(Frame(celda, marca, indice, columna))
    return frames


# --- reducción a escala de juego ----------------------------------------------------------------

def reducir(imagen: Image.Image, ancho: int, alto: int) -> Image.Image:
    """Baja a escala de juego con alfa premultiplicado y deja el alfa duro (0 o 255)."""
    datos = pixeles(imagen)
    premultiplicada = Image.new("RGBA", imagen.size)
    premultiplicada.putdata([
        (r * a // 255, g * a // 255, b * a // 255, a) for (r, g, b, a) in datos
    ])
    chica = premultiplicada.resize((ancho, alto), Image.LANCZOS)

    salida = []
    for (r, g, b, a) in pixeles(chica):
        if a < UMBRAL_ALFA:
            salida.append((0, 0, 0, 0))
        else:
            salida.append((min(255, r * 255 // a), min(255, g * 255 // a), min(255, b * 255 // a), 255))
    final = Image.new("RGBA", (ancho, alto))
    final.putdata(salida)
    return nitidez(final)


def nitidez(imagen: Image.Image) -> Image.Image:
    """Realza el contorno sin tocar el alfa (ImageEnhance mezcla el borde con la transparencia)."""
    from PIL import ImageEnhance

    alfa = imagen.getchannel("A")
    color = ImageEnhance.Sharpness(imagen.convert("RGB")).enhance(NITIDEZ)
    color.putalpha(alfa)
    return color


def es_morado(color: tuple[int, int, int]) -> bool:
    """El morado del corazón que Liss lleva en las manos: el único acento frío de la hoja."""
    r, g, b = color
    luz = (r + g + b) / 3
    saturacion = (max(color) - min(color)) / max(1, max(color))
    return b > g + 20 and r > g + 20 and luz > 60 and saturacion > 0.35


def colores_insignia(cuenta: dict[tuple[int, int, int], int]) -> list[tuple[int, int, int]]:
    """Dos lugares de la paleta apartados para el corazón, uno claro y uno oscuro.

    Son pocos píxeles contra un vestido enorme: sin reservarlos, cualquier cuantización los pinta
    de café y Liss termina abrazando un ladrillo.
    """
    morados = [(color, veces) for color, veces in cuenta.items() if es_morado(color)]
    if sum(veces for _, veces in morados) < 12:
        return []
    morados.sort(key=lambda par: sum(par[0]))
    mitad = len(morados) // 2 or 1
    tonos = []
    for grupo in (morados[:mitad], morados[mitad:]):
        if not grupo:
            continue
        total = sum(veces for _, veces in grupo)
        tonos.append(tuple(
            round(sum(color[canal] * veces for color, veces in grupo) / total) for canal in range(3)
        ))
    return tonos


def paleta_comun(imagenes: list[Image.Image]) -> Image.Image:
    """Una sola paleta para todos los frames: sin esto, cada frame elige colores distintos.

    El peso de cada color va por raíz cuadrada de su frecuencia, para que el vestido —que es casi
    toda la superficie— no se quede con la paleta entera.
    """
    cuenta: dict[tuple[int, int, int], int] = {}
    for imagen in imagenes:
        for (r, g, b, a) in pixeles(imagen):
            if a == 255:
                cuenta[(r, g, b)] = cuenta.get((r, g, b), 0) + 1

    insignia = colores_insignia(cuenta)
    muestras = []
    for color, veces in sorted(cuenta.items()):
        if es_morado(color):
            continue
        muestras.extend([color] * max(1, round(veces ** 0.5)))
    tira = Image.new("RGB", (len(muestras), 1))
    tira.putdata(muestras)
    cupo = MAX_COLORES - 1 - len(insignia)
    crudo = tira.quantize(colors=cupo, method=Image.MEDIANCUT, dither=Image.NONE).getpalette()
    colores = [tuple(crudo[i:i + 3]) for i in range(0, cupo * 3, 3)] + insignia

    paleta = Image.new("P", (1, 1))
    relleno = colores + [colores[-1]] * (256 - len(colores))
    paleta.putpalette([canal for color in relleno for canal in color])
    return paleta


def aplicar_paleta(imagen: Image.Image, paleta: Image.Image) -> Image.Image:
    alfa = imagen.getchannel("A")
    plano = imagen.convert("RGB").quantize(palette=paleta, dither=Image.NONE).convert("RGB")
    salida = Image.new("RGBA", imagen.size, (0, 0, 0, 0))
    salida.paste(plano, (0, 0), alfa)  # el alfa 0 deja el píxel en (0,0,0,0): un solo color vacío
    return salida


# --- elección de poses ---------------------------------------------------------------------------

def elegir_idle(frames: list[Frame]) -> Frame:
    """La pose quieta más representativa: la que menos se aleja de la silueta promedio."""
    promedio_alto = sum(f.alto for f in frames) / len(frames)
    promedio_ancho = sum(f.ancho for f in frames) / len(frames)
    return min(frames, key=lambda f: abs(f.alto - promedio_alto) + abs(f.ancho - promedio_ancho))


def elegir_caminata(frames: list[Frame]) -> list[Frame]:
    """Ciclo de 4: paso abierto, paso junto, el otro paso abierto, paso junto.

    La hoja trae seis poses por dirección sin un orden de animación garantizado, así que el ciclo
    se arma midiendo cuánto se separan los pies: es lo que se lee a esta escala.
    """
    ordenados = sorted(frames, key=lambda f: f.ancho_pies)
    juntos = ordenados[:2]
    abiertos = ordenados[-2:]
    return [abiertos[1], juntos[0], abiertos[0], juntos[1]]


def recortar_retrato(frame: Frame, alto_caja: int) -> Image.Image:
    """Cabeza y hombros del frame elegido, a la resolución de la hoja (se reduce después)."""
    alto = round(frame.alto * PORCION_RETRATO)
    ancho = alto
    xs_cabeza = []
    datos = frame.imagen.load()
    for y in range(frame.y0, frame.y0 + alto):
        for x in range(frame.x0, frame.x1 + 1):
            if datos[x, y][3]:
                xs_cabeza.append(x)
    centro = round(sum(xs_cabeza) / len(xs_cabeza)) if xs_cabeza else frame.centro
    x = centro - ancho // 2
    caja = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    caja.paste(frame.imagen.crop((x, frame.y0, x + ancho, frame.y0 + alto)), (0, 0))
    return caja


# --- atlas ---------------------------------------------------------------------------------------

def empacar(frames: dict[str, Image.Image], separacion: int = 1) -> tuple[Image.Image, dict]:
    """Empaquetado en estantes: suficiente para medio centenar de frames del mismo alto."""
    nombres = sorted(frames, key=lambda n: (-frames[n].height, n))
    ancho_atlas = 256
    x = y = alto_estante = 0
    lugares: dict[str, tuple[int, int]] = {}
    for nombre in nombres:
        imagen = frames[nombre]
        if x + imagen.width > ancho_atlas:
            x = 0
            y += alto_estante + separacion
            alto_estante = 0
        lugares[nombre] = (x, y)
        x += imagen.width + separacion
        alto_estante = max(alto_estante, imagen.height)
    alto_atlas = y + alto_estante

    atlas = Image.new("RGBA", (ancho_atlas, alto_atlas), (0, 0, 0, 0))
    datos = {"frames": {}, "meta": {
        "app": "tools/generate_sprites.py",
        "image": "atlas.png",
        "format": "RGBA8888",
        "size": {"w": ancho_atlas, "h": alto_atlas},
        "scale": "1",
    }}
    for nombre, (px, py) in lugares.items():
        imagen = frames[nombre]
        atlas.paste(imagen, (px, py))
        datos["frames"][nombre] = {
            "frame": {"x": px, "y": py, "w": imagen.width, "h": imagen.height},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": imagen.width, "h": imagen.height},
            "sourceSize": {"w": imagen.width, "h": imagen.height},
        }
    return atlas, datos


def hoja_de_contacto(frames: dict[str, Image.Image], destino: Path, escala: int = 4) -> None:
    """Todos los frames sobre un tablero de ajedrez, para revisarlos a ojo."""
    nombres = sorted(frames)
    columnas_ = 12
    celda_w = max(f.width for f in frames.values()) + 4
    celda_h = max(f.height for f in frames.values()) + 4
    filas = (len(nombres) + columnas_ - 1) // columnas_
    hoja = Image.new("RGBA", (columnas_ * celda_w, filas * celda_h))
    for y in range(hoja.height):
        for x in range(hoja.width):
            tono = 90 if ((x // 8) + (y // 8)) % 2 else 70
            hoja.putpixel((x, y), (tono, tono, tono + 12, 255))
    for i, nombre in enumerate(nombres):
        imagen = frames[nombre]
        px = (i % columnas_) * celda_w + (celda_w - imagen.width) // 2
        py = (i // columnas_) * celda_h + (celda_h - imagen.height)
        hoja.paste(imagen, (px, py), imagen)
    destino.parent.mkdir(parents=True, exist_ok=True)
    hoja.resize((hoja.width * escala, hoja.height * escala), Image.NEAREST).save(destino)


# --- reporte ---------------------------------------------------------------------------------

def inspeccionar(hoja: Image.Image, frames: list[Frame]) -> dict:
    colores = hoja.getcolors(maxcolors=10 ** 7) or []
    por_banda = {}
    for banda in range(len(SECCIONES) * FILAS_POR_SECCION):
        de_la_banda = [f for f in frames if f.banda == banda]
        por_banda[banda] = {
            "seccion": SECCIONES[banda // FILAS_POR_SECCION],
            "frames": len(de_la_banda),
            "alto": [min(f.alto for f in de_la_banda), max(f.alto for f in de_la_banda)],
            "ancho": [min(f.ancho for f in de_la_banda), max(f.ancho for f in de_la_banda)],
        }
    return {
        "hoja": str(HOJA.relative_to(RAIZ)),
        "tamano": list(hoja.size),
        "coloresEnLaHoja": len(colores),
        "frames": len(frames),
        "direcciones": DIRECCIONES,
        "posesPorDireccion": {
            seccion: POSES_POR_FILA * FILAS_POR_SECCION for seccion in SECCIONES
        },
        "bandas": por_banda,
        "escalaDeJuego": {"altoObjetivo": ALTO_OBJETIVO, "maxColores": MAX_COLORES},
    }


def generar(contacto: bool) -> int:
    hoja = cargar_hoja()
    frames = leer_frames(hoja)

    # Una escala por banda: la hoja dibujó las cuatro bandas a tamaños apenas distintos y, sin
    # esto, Liss crece y encoge al pasar de estar quieta a caminar.
    escalas = {}
    for banda in range(len(SECCIONES) * FILAS_POR_SECCION):
        altos = sorted(f.alto for f in frames if f.banda == banda)
        escalas[banda] = ALTO_OBJETIVO / altos[len(altos) // 2]

    # Caja de destino: la más alta y la más ancha que haga falta, ya en escala de juego.
    alto_destino = max(round(f.alto * escalas[f.banda]) for f in frames) + 1
    ancho_destino = max(
        round(2 * max(f.centro - f.x0, f.x1 - f.centro) * escalas[f.banda]) for f in frames
    ) + 1

    # Cada banda recorta su propia caja, del tamaño que al reducirla da la caja de destino: así
    # todos los frames de una banda caen en la misma rejilla de píxeles y el sprite no titila.
    cajas = {
        banda: (round(ancho_destino / escala), round(alto_destino / escala))
        for banda, escala in escalas.items()
    }

    def a_escala(frame: Frame) -> Image.Image:
        ancho_caja, alto_caja = cajas[frame.banda]
        return reducir(frame.recortar(ancho_caja, alto_caja), ancho_destino, alto_destino)

    piezas: dict[str, Image.Image] = {}
    for direccion in DIRECCIONES:
        estaticos = [f for f in frames if f.direccion == direccion and f.seccion == "estatico"]
        andando = [f for f in frames if f.direccion == direccion and f.seccion == "movimiento"]

        base = a_escala(elegir_idle(estaticos))
        piezas[f"liss_idle_{direccion}_0"] = base
        piezas[f"liss_idle_{direccion}_1"] = respirar(base)

        for i, frame in enumerate(elegir_caminata(andando)):
            piezas[f"liss_camina_{direccion}_{i}"] = a_escala(frame)

    for emocion, (banda, columna) in RETRATOS.items():
        frente = next(f for f in frames if f.banda == banda and f.columna == columna)
        recorte = recortar_retrato(frente, ALTO_RETRATO)
        piezas[f"retrato_liss_{emocion}"] = reducir(recorte, ALTO_RETRATO, ALTO_RETRATO)

    paleta = paleta_comun(list(piezas.values()))
    piezas = {nombre: aplicar_paleta(imagen, paleta) for nombre, imagen in piezas.items()}

    atlas, datos = empacar(piezas)
    ASSETS.mkdir(parents=True, exist_ok=True)
    atlas.save(ASSETS / "atlas.png")
    (ASSETS / "atlas.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    usados = set(pixeles(atlas))
    print(f"  · atlas.png  {atlas.width}×{atlas.height}, {len(piezas)} frames, {len(usados)} colores")
    print(f"  · sprite de juego: {ancho_destino}×{alto_destino} px (alto objetivo {ALTO_OBJETIVO})")
    print(f"  · retratos: {ALTO_RETRATO}×{ALTO_RETRATO} px ({', '.join(sorted(RETRATOS))})")
    if contacto:
        destino = RAIZ / "dist" / "contacto_liss.png"
        hoja_de_contacto(piezas, destino)
        print(f"  · hoja de contacto: {destino.relative_to(RAIZ)}")
    print("Recordá correr tools/actualizar_manifest.py para que el juego cargue el atlas.")
    return 0


def respirar(imagen: Image.Image) -> Image.Image:
    """Segundo frame de la pose quieta: el torso baja un píxel y el cuerpo se comprime al respirar."""
    salida = imagen.copy()
    cintura = round(imagen.height * 0.55)
    torso = imagen.crop((0, 0, imagen.width, cintura))
    salida.paste(Image.new("RGBA", (imagen.width, cintura), (0, 0, 0, 0)), (0, 0))
    salida.paste(torso, (0, 1), torso)
    return salida


def main() -> int:
    parser = argparse.ArgumentParser(description="Hoja de Liss → atlas del juego.")
    parser.add_argument("--inspeccionar", action="store_true",
                        help="reporta cómo se lee la hoja y no escribe nada")
    parser.add_argument("--contacto", action="store_true",
                        help="además del atlas, guarda dist/contacto_liss.png")
    args = parser.parse_args()

    if args.inspeccionar:
        hoja = cargar_hoja()
        print(json.dumps(inspeccionar(hoja, leer_frames(hoja)), ensure_ascii=False, indent=2))
        return 0
    return generar(args.contacto)


if __name__ == "__main__":
    raise SystemExit(main())
