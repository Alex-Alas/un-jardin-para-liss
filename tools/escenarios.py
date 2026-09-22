#!/usr/bin/env python3
"""Mapas pintados: una ilustración de fondo más la geometría que el motor necesita.

Los mapas con grilla ASCII se pintan tile por tile con `tiles.py`. Los mapas pintados son otra
cosa: la imagen ya viene hecha (`assets/source/escenarios/`) y lo que falta es todo lo que una
imagen no dice:

- **qué se puede pisar**: colisiones finas, en celdas de 4 px, dibujadas con formas;
- **qué tapa a Liss cuando pasa por detrás**: los *frentes*, recortes de la pintura (la copa de
  un árbol, un techo, un poste) con la línea donde tocan el piso. El motor dibuja cada frente
  encima de Liss solo cuando ella tiene los pies más arriba que esa línea;
- **dónde está cada cosa**: objetos, puertas y el punto donde aparece Liss, en píxeles.

`render_maps.py` reconoce un mapa pintado por su línea `#! pintura:` y le pasa el trabajo a este
módulo. El formato está explicado en docs/handoff.md § Mapas pintados; en corto:

    #! pintura: escenarios/pueblo.webp       la ilustración, relativa a assets/source/
    #! tamaño: 48 32                          tiles de 16 px: la pintura se escala hasta cubrirlo
    #! inicio: 146 180                        dónde aparece Liss si nadie dice otra cosa
    #! objeto banco banco pueblo.banco 548 380       tipo, id, diálogo y el punto donde toca el piso
    #! guardado 216 250
    #! puerta Casa 136 138 160 160 70 196     zona x0 y0 x1 y1 y destino (en unidades del destino)
    #! solido rect 48 110 232 157             también: elipse cx cy rx ry · poli x,y x,y …
    #! frente 157 poli 48,35 232,35 232,157 48,157     piso y forma (varias, unidas con +)
    #! frente 190 ajuste 8 rect 484 134 513 165        con una franja de ajuste más ancha
    #! arbol 75 336 7 75 290 40 38            tronco x, piso, medio ancho; copa cx cy rx ry

Todas las coordenadas son píxeles del mapa ya escalado (lo que mide el PNG final).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import tiles  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "assets" / "source"
DESTINO = RAIZ / "assets"
TILE = 16
CELDA = 4                 # lado de la celda de colisión; Liss pisa con una caja de 10 × 4 px
ANCHO_ATLAS = 512         # los frentes se empacan en filas dentro de este ancho

META_RE = re.compile(r"^#!\s*(\w+)\s*(.*)$")


# --- lectura --------------------------------------------------------------------------------

def es_pintado(ruta: Path) -> bool:
    return any(linea.startswith("#! pintura:") for linea in ruta.read_text(encoding="utf-8").splitlines())


def _numeros(texto: list[str]) -> list[int]:
    return [int(round(float(t))) for t in texto]


def _formas(tokens: list[str]) -> list[tuple]:
    """`rect 1 2 3 4 + elipse 5 6 7 8 + poli 1,2 3,4 5,6` -> lista de formas."""
    formas, actual = [], []
    for token in tokens + ["+"]:
        if token == "+":
            if actual:
                formas.append(_forma(actual))
            actual = []
        else:
            actual.append(token)
    return formas


def _forma(tokens: list[str]) -> tuple:
    tipo, resto = tokens[0], tokens[1:]
    if tipo == "rect":
        return ("rect", *_numeros(resto[:4]))
    if tipo == "elipse":
        return ("elipse", *_numeros(resto[:4]))
    if tipo == "poli":
        puntos = [tuple(_numeros(p.split(","))) for p in resto]
        if len(puntos) < 3:
            raise ValueError(f"un polígono necesita tres puntos o más: {' '.join(tokens)}")
        return ("poli", puntos)
    raise ValueError(f"forma desconocida: {tipo}")


def leer(ruta: Path) -> dict:
    mapa = {
        "nombre": ruta.stem, "meta": {}, "retoques": [], "objetos": [], "puertas": [],
        "pinceladas": [], "frentes": [], "fondo": "libre", "inicio": None,
    }
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.startswith("#!"):
            continue
        linea = linea.split("//", 1)[0].rstrip()
        clave, resto = META_RE.match(linea).groups()
        if resto.startswith(":"):
            resto = resto[1:].strip()
        partes = resto.split()
        try:
            if clave == "pintura":
                mapa["pintura"] = resto
            elif clave == "tamaño":
                mapa["ancho"], mapa["alto"] = _numeros(partes[:2])
            elif clave == "inicio":
                mapa["inicio"] = tuple(_numeros(partes[:2]))
            elif clave == "fondo":
                mapa["fondo"] = partes[0]
            elif clave == "colores":
                mapa["colores"] = int(partes[0])
            elif clave == "ajuste":
                mapa["ajuste"] = int(partes[0])
            elif clave == "retoque":
                mapa["retoques"].append(partes)
            elif clave == "objeto":
                tipo, ident, dialogo = partes[:3]
                x, y = _numeros(partes[3:5])
                mapa["objetos"].append({"tipo": tipo, "id": ident,
                                        "dialogo": None if dialogo == "-" else dialogo, "px": x, "py": y})
            elif clave == "guardado":
                x, y = _numeros(partes[:2])
                mapa["objetos"].append({"tipo": "guardado", "id": "guardado",
                                        "dialogo": "sistema.guardado", "px": x, "py": y})
            elif clave == "puerta":
                destino = partes[0]
                x0, y0, x1, y1, dx, dy = _numeros(partes[1:7])
                mapa["puertas"].append({"a": destino, "zona": (x0, y0, x1, y1), "destino": (dx, dy)})
            elif clave in ("solido", "libre"):
                mapa["pinceladas"].extend((clave, forma) for forma in _formas(partes))
            elif clave == "frente":
                frente = {"piso": int(partes[0])}
                if partes[1] == "ajuste":           # un objeto finito (un farol) pide más franja
                    frente["ajuste"], partes = int(partes[2]), partes[:1] + partes[3:]
                frente["formas"] = _formas(partes[1:])
                mapa["frentes"].append(frente)
            elif clave == "arbol":
                tx, piso, medio, cx, cy, rx, ry = _numeros(partes[:7])
                # El tronco bloquea solo donde toca el piso; la copa y el tronco tapan a Liss
                # cuando ella pasa por detrás.
                mapa["pinceladas"].append(("solido", ("elipse", tx, piso - 2, medio + 2, 3)))
                mapa["frentes"].append({"piso": piso, "formas": [
                    ("elipse", cx, cy, rx, ry), ("rect", tx - medio, cy, tx + medio + 1, piso + 1)]})
            elif clave == "arbusto":
                cx, cy, rx, ry = _numeros(partes[:4])
                # Un arbusto bloquea su mitad de abajo (su sombra en el piso) y tapa entero.
                mapa["pinceladas"].append(("solido", ("elipse", cx, cy + ry // 3, max(2, rx - 2), max(2, ry // 2))))
                mapa["frentes"].append({"piso": cy + ry, "formas": [("elipse", cx, cy, rx, ry)]})
            else:
                mapa["meta"][clave] = resto
        except (ValueError, IndexError) as error:
            raise SystemExit(f"{ruta.name}:{numero}: no entiendo «{linea}» ({error})") from error

    for requerido in ("pintura", "ancho"):
        if requerido not in mapa:
            raise SystemExit(f"{ruta.name}: falta `#! {'pintura' if requerido == 'pintura' else 'tamaño'}:`")
    return mapa


# --- la pintura -----------------------------------------------------------------------------

def escalar(imagen: Image.Image, ancho: int, alto: int) -> Image.Image:
    """Escala hasta cubrir el mapa y recorta lo que sobra, centrado: nunca deforma."""
    escala = max(ancho / imagen.width, alto / imagen.height)
    nuevo = (round(imagen.width * escala), round(imagen.height * escala))
    imagen = imagen.resize(nuevo, Image.LANCZOS)
    x0, y0 = (nuevo[0] - ancho) // 2, (nuevo[1] - alto) // 2
    return imagen.crop((x0, y0, x0 + ancho, y0 + alto))


def _color(texto: str) -> tuple:
    texto = texto.lstrip("#")
    return tuple(int(texto[i:i + 2], 16) for i in (0, 2, 4))


def retocar(imagen: Image.Image, retoques: list[list[str]]) -> None:
    """Arreglos a mano sobre la pintura ya escalada, en orden.

    - `copiar x0 y0 x1 y1 a dx dy`   tapa algo con un parche de la misma pintura
    - `espejar x0 y0 x1 y1 a dx dy`  igual, pero dado vuelta (para objetos simétricos)
    - `rellenar x0 y0 x1 y1 #rrggbb`
    - `dibujo <nombre> x y`          uno de los dibujitos de DIBUJOS (abajo)
    """
    for partes in retoques:
        orden = partes[0]
        if orden in ("copiar", "espejar"):
            x0, y0, x1, y1 = _numeros(partes[1:5])
            dx, dy = _numeros(partes[6:8])
            parche = imagen.crop((x0, y0, x1, y1))
            if orden == "espejar":
                parche = parche.transpose(Image.FLIP_LEFT_RIGHT)
            imagen.paste(parche, (dx, dy))
        elif orden == "rellenar":
            x0, y0, x1, y1 = _numeros(partes[1:5])
            ImageDraw.Draw(imagen).rectangle([x0, y0, x1 - 1, y1 - 1], fill=_color(partes[5]))
        elif orden == "dibujo":
            x, y = _numeros(partes[2:4])
            DIBUJOS[partes[1]](ImageDraw.Draw(imagen), x, y)
        else:
            raise SystemExit(f"retoque desconocido: {' '.join(partes)}")


# Dibujitos que la pintura no trae y el guion sí necesita. Se dibujan con los colores de la
# propia pintura para que no parezcan pegados.

def _nota(dib: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """La nota doblada en cuatro, tirada junto a la puerta: 8 × 6 px con su sombra.

    Un poco más clara que la almohada, que es lo más claro del cuarto de noche: tiene que verse
    sin gritar.
    """
    papel, luz, pliegue = (226, 203, 184), (242, 226, 210), (178, 148, 132)
    tinta, sombra = (104, 68, 82), (40, 26, 32)
    dib.rectangle([x + 1, y + 1, x + 8, y + 6], fill=sombra)
    dib.rectangle([x, y, x + 7, y + 5], fill=papel)
    dib.rectangle([x, y, x + 3, y + 2], fill=luz)
    dib.line([x + 4, y, x + 4, y + 5], fill=pliegue)            # los dos dobleces
    dib.line([x, y + 3, x + 7, y + 3], fill=pliegue)
    dib.point((x + 1, y + 1), fill=tinta)                         # la letra de A., asomando
    dib.point((x + 2, y + 1), fill=tinta)
    dib.point((x + 6, y + 4), fill=(242, 200, 75))                # una esquinita amarilla


def _marca_calendario(dib: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """La libreta del escritorio pasa a ser el calendario: franja de arriba y el 21 en círculo.

    (x, y) es la esquina de arriba a la izquierda del papel.
    """
    rojo, amarillo, ambar = (168, 64, 66), (242, 200, 75), (206, 150, 58)
    dib.line([x + 1, y, x + 11, y], fill=rojo)                    # la tira del calendario
    cx, cy = x + 7, y + 2                                         # el círculo, 5 × 5
    dib.line([cx + 1, cy, cx + 3, cy], fill=amarillo)
    dib.line([cx, cy + 1, cx, cy + 3], fill=amarillo)
    dib.line([cx + 4, cy + 1, cx + 4, cy + 3], fill=ambar)
    dib.line([cx + 1, cy + 4, cx + 3, cy + 4], fill=ambar)


def _espejo_ropero(dib: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Un espejo angosto en el costado del ropero, el que mira hacia el cuarto: 6 × 24 px.

    El vidrio usa los azules de la ventana, para que refleje la misma noche.
    """
    marco, vidrio, vidrio_luz, brillo = (60, 42, 42), (74, 72, 139), (114, 92, 147), (200, 186, 226)
    dib.rectangle([x, y, x + 5, y + 23], fill=marco)
    dib.rectangle([x + 1, y + 1, x + 4, y + 22], fill=vidrio)
    dib.line([x + 1, y + 2, x + 1, y + 19], fill=vidrio_luz)      # el borde que recibe la luz
    dib.rectangle([x + 1, y + 1, x + 4, y + 2], fill=vidrio_luz)
    for dx, dy in ((3, 4), (2, 5), (1, 6), (4, 9), (3, 10)):      # dos reflejos en diagonal
        dib.point((x + dx, y + dy), fill=brillo)


DIBUJOS = {"nota": _nota, "marca_calendario": _marca_calendario, "espejo_ropero": _espejo_ropero}


def pintura(mapa: dict) -> Image.Image:
    """La pintura lista para el juego: escalada, retocada y teñida si hace falta.

    Con `#! colores: N` sale en modo paleta (PNG de 8 bits, bastante más liviano); si no, en RGB.
    """
    ancho, alto = mapa["ancho"] * TILE, mapa["alto"] * TILE
    fuente = FUENTES / mapa["pintura"]
    if not fuente.exists():
        raise SystemExit(f"falta la pintura {fuente.relative_to(RAIZ)}")
    imagen = escalar(Image.open(fuente).convert("RGB"), ancho, alto)
    retocar(imagen, mapa["retoques"])
    if mapa["meta"].get("luz") == "atardecer":
        imagen = imagen.convert("RGBA")
        tiles.atardecer(imagen)
        imagen = imagen.convert("RGB")
    if mapa.get("colores"):
        # Menos colores = PNG más liviano; a este tamaño el ojo no nota la diferencia.
        imagen = imagen.quantize(colors=mapa["colores"], method=Image.Quantize.MEDIANCUT,
                                 dither=Image.Dither.NONE)
    return imagen


# --- geometría ------------------------------------------------------------------------------

def dibujar_forma(dib: ImageDraw.ImageDraw, forma: tuple, relleno: int) -> None:
    tipo = forma[0]
    if tipo == "rect":
        _, x0, y0, x1, y1 = forma
        dib.rectangle([x0, y0, x1 - 1, y1 - 1], fill=relleno)
    elif tipo == "elipse":
        _, cx, cy, rx, ry = forma
        dib.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=relleno)
    else:
        dib.polygon(forma[1], fill=relleno)


def mascara_solida(mapa: dict, ancho: int, alto: int) -> Image.Image:
    mascara = Image.new("L", (ancho, alto), 255 if mapa["fondo"] == "solido" else 0)
    dib = ImageDraw.Draw(mascara)
    for clave, forma in mapa["pinceladas"]:
        dibujar_forma(dib, forma, 255 if clave == "solido" else 0)
    return mascara


def celdas(mascara: Image.Image) -> list[str]:
    """Pasa la máscara de píxeles a celdas: una celda bloquea si la mitad o más bloquea."""
    ancho, alto = mascara.size
    datos = mascara.load()
    filas = []
    for cy in range(alto // CELDA):
        fila = []
        for cx in range(ancho // CELDA):
            llenos = sum(1 for y in range(cy * CELDA, cy * CELDA + CELDA)
                         for x in range(cx * CELDA, cx * CELDA + CELDA) if datos[x, y] > 127)
            fila.append("1" if llenos * 2 >= CELDA * CELDA else "0")
        filas.append("".join(fila))
    return filas


def ajustar_borde(mascara: Image.Image, imagen: Image.Image, banda: int) -> Image.Image:
    """Pega el borde de un frente a la silueta pintada, mirando colores.

    Una elipse nunca calza con una copa de árbol hecha de bultos: se come pasto en unos lados y
    deja hojas afuera en otros. Si ese pasto quedara en el frente, taparía a Liss con un
    rectángulo verde cuando pasa por detrás. Así que en una franja de `banda` píxeles alrededor
    del borde de la forma, cada píxel se decide por su color: se queda si ese color es más común
    adentro de la forma (el objeto) que en el anillo de afuera (el piso). El centro de la forma
    no se toca, y lo que está lejos del borde tampoco.
    """
    if banda <= 0:
        return mascara
    caja = mascara.getbbox()
    if not caja:
        return mascara
    margen = banda + 8
    x0, y0 = max(0, caja[0] - margen), max(0, caja[1] - margen)
    x1, y1 = min(imagen.width, caja[2] + margen), min(imagen.height, caja[3] + margen)
    local = mascara.crop((x0, y0, x1, y1))
    colores = list(imagen.crop((x0, y0, x1, y1)).getdata())

    lado = 2 * banda + 1
    nucleo = list(local.filter(ImageFilter.MinFilter(lado)).getdata())
    halo = list(local.filter(ImageFilter.MaxFilter(lado)).getdata())
    lejos = list(local.filter(ImageFilter.MaxFilter(lado + 10)).getdata())

    adentro, afuera = {}, {}
    for color, n, h, lj in zip(colores, nucleo, halo, lejos):
        if n:
            adentro[color] = adentro.get(color, 0) + 1
        elif lj and not h:
            afuera[color] = afuera.get(color, 0) + 1
    total_adentro, total_afuera = max(1, sum(adentro.values())), max(1, sum(afuera.values()))

    resultado = []
    for color, n, h, original in zip(colores, nucleo, halo, local.getdata()):
        if n:
            resultado.append(255)
        elif not h:
            resultado.append(0)
        elif color in adentro or color in afuera:
            del_objeto = (adentro.get(color, 0) + 0.5) / total_adentro
            del_piso = (afuera.get(color, 0) + 0.5) / total_afuera
            resultado.append(255 if del_objeto >= del_piso else 0)
        else:
            resultado.append(original)
    ajustada = Image.new("L", local.size)
    ajustada.putdata(resultado)
    # Un filtro de moda de 3 × 3 borra los píxeles sueltos que el color decidió mal.
    ajustada = ajustada.filter(ImageFilter.ModeFilter(3))
    salida = Image.new("L", mascara.size, 0)
    salida.paste(ajustada, (x0, y0))
    return salida


def mascara_frente(frente: dict, imagen: Image.Image, ajuste: int) -> Image.Image:
    """La silueta de un frente: cada forma se ajusta por su cuenta y después se unen.

    Por separado porque cada forma tiene sus colores: si la copa y el tronco se ajustaran
    juntos, los verdes de la copa harían pasar por «árbol» al pasto que rodea el tronco.
    """
    ajuste = frente.get("ajuste", ajuste)
    total = Image.new("L", imagen.size, 0)
    for forma in frente["formas"]:
        mascara = Image.new("L", imagen.size, 0)
        dibujar_forma(ImageDraw.Draw(mascara), forma, 255)
        total = ImageChops.lighter(total, ajustar_borde(mascara, imagen, ajuste))
    return total


def recortar_frentes(mapa: dict, imagen: Image.Image) -> tuple[Image.Image | None, list[dict]]:
    """Recorta cada frente de la pintura con su forma y los empaca en un atlas por filas."""
    piezas = []
    for frente in mapa["frentes"]:
        mascara = mascara_frente(frente, imagen, mapa.get("ajuste", 0))
        caja = mascara.getbbox()
        if not caja:
            continue
        recorte = imagen.crop(caja).convert("RGBA")
        recorte.putalpha(mascara.crop(caja))
        piezas.append({"x": caja[0], "y": caja[1], "w": caja[2] - caja[0], "h": caja[3] - caja[1],
                       "piso": frente["piso"], "imagen": recorte})
    if not piezas:
        return None, []

    # Empaque en estantes: de la más alta a la más baja, con un píxel de aire entre piezas.
    orden = sorted(range(len(piezas)), key=lambda i: -piezas[i]["h"])
    x = y = alto_fila = 0
    for i in orden:
        pieza = piezas[i]
        if x + pieza["w"] > ANCHO_ATLAS:
            x, y, alto_fila = 0, y + alto_fila + 1, 0
        pieza["ax"], pieza["ay"] = x, y
        x += pieza["w"] + 1
        alto_fila = max(alto_fila, pieza["h"])
    atlas = Image.new("RGBA", (ANCHO_ATLAS, y + alto_fila), (0, 0, 0, 0))
    for pieza in piezas:
        atlas.paste(pieza.pop("imagen"), (pieza["ax"], pieza["ay"]))
    return atlas, piezas


# --- exportar -------------------------------------------------------------------------------

def render(mapa: dict, resolver_destino) -> dict:
    """Escribe los PNG del mapa y devuelve lo que va en AG.MAPAS[nombre].

    `resolver_destino(nombre_escena, (x, y))` traduce el destino de una puerta a lo que entiende
    el motor: `{px, py}` si el mapa destino es pintado, `{x, y}` en tiles si es ASCII.
    """
    nombre = mapa["nombre"]
    ancho, alto = mapa["ancho"] * TILE, mapa["alto"] * TILE
    imagen = pintura(mapa)
    imagen.save(DESTINO / f"mapa_{nombre}.png", optimize=True)
    imagen = imagen.convert("RGB")            # los frentes se recortan de lo mismo que se guardó

    atlas, piezas = recortar_frentes(mapa, imagen)
    ruta_frentes = DESTINO / f"mapa_{nombre}_frentes.png"
    if atlas:
        atlas.save(ruta_frentes, optimize=True)
    elif ruta_frentes.exists():
        ruta_frentes.unlink()

    datos = {
        "ancho": mapa["ancho"],
        "alto": mapa["alto"],
        "tile": TILE,
        "imagen": f"assets/mapa_{nombre}.png",
        "pintado": True,
        "celda": CELDA,
        "colisiones": celdas(mascara_solida(mapa, ancho, alto)),
        "objetos": mapa["objetos"],
        "puertas": [
            {"px": p["zona"][0], "py": p["zona"][1],
             "ancho": p["zona"][2] - p["zona"][0], "alto": p["zona"][3] - p["zona"][1],
             "a": p["a"], "destino": resolver_destino(p["a"], p["destino"])}
            for p in mapa["puertas"]
        ],
        "zonas": [],
    }
    if mapa["inicio"]:
        datos["inicio"] = {"px": mapa["inicio"][0], "py": mapa["inicio"][1]}
    if piezas:
        datos["frentes"] = {"imagen": f"assets/mapa_{nombre}_frentes.png", "piezas": piezas}
    return datos


def depurar(mapa: dict, datos: dict, salida: Path) -> None:
    """Una vista para revisar a ojo: colisión en rojo, frentes en azul con su línea de piso,
    objetos en amarillo, puertas en verde y el inicio en celeste. Ampliada ×2."""
    base = Image.open(DESTINO / datos["imagen"].split("/", 1)[1]).convert("RGBA")
    capa = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dib = ImageDraw.Draw(capa)
    for cy, fila in enumerate(datos["colisiones"]):
        for cx, valor in enumerate(fila):
            if valor == "1":
                dib.rectangle([cx * CELDA, cy * CELDA, cx * CELDA + CELDA - 1, cy * CELDA + CELDA - 1],
                              fill=(255, 40, 40, 110))
    for frente in mapa["frentes"]:
        mascara = mascara_frente(frente, base.convert("RGB"), mapa.get("ajuste", 0))
        borde = mascara.filter(ImageFilter.FIND_EDGES)
        capa.paste((60, 140, 255, 230), (0, 0), borde)
        caja = mascara.getbbox()
        if caja:
            dib.line([caja[0], frente["piso"], caja[2], frente["piso"]], fill=(60, 140, 255, 255))
    for objeto in datos["objetos"]:
        x, y = objeto["px"], objeto["py"]
        dib.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 230, 0, 255))
        dib.ellipse([x - 22, y - 6 - 22 + 8, x + 22, y - 6 + 22 + 8], outline=(255, 230, 0, 90))
    for puerta in datos["puertas"]:
        dib.rectangle([puerta["px"], puerta["py"], puerta["px"] + puerta["ancho"] - 1,
                       puerta["py"] + puerta["alto"] - 1], outline=(40, 255, 90, 255))
    if datos.get("inicio"):
        x, y = datos["inicio"]["px"], datos["inicio"]["py"]
        dib.rectangle([x - 5, y - 4, x + 5, y - 1], outline=(40, 230, 255, 255))
    vista = Image.alpha_composite(base, capa)
    vista = vista.resize((vista.width * 2, vista.height * 2), Image.NEAREST)
    salida.parent.mkdir(parents=True, exist_ok=True)
    vista.save(salida)
