"""Paleta maestra compartida por los scripts de arte.

Espejo de AG.CFG.COLORES en src/config.js. Si cambia un color, cambia en los dos lados.
"""

PALETA = {
    "tinta": "#1b1420",
    "tintaSuave": "#3b2f47",
    "blanco": "#fff8ec",
    "crema": "#f6e7c6",
    "amarillo": "#ffd23f",
    "amarilloClaro": "#ffe98a",
    "ambar": "#e8a020",
    "naranja": "#f2802c",
    "rojo": "#d24b3f",
    "rosa": "#f2a8b8",
    "verde": "#63a852",
    "verdeOscuro": "#2f6b3a",
    "verdeClaro": "#a8d672",
    "cielo": "#7fc7e8",
    "cieloOscuro": "#4a7fb5",
    "atardecer": "#f4a259",
    "morado": "#6b4a8c",
    "marron": "#8a5a3b",
    "marronClaro": "#c08a5a",
    "gris": "#8b8b9e",
    "grisOscuro": "#4a4a5e",
    "negro": "#0b0a10",
}


def rgb(nombre):
    """Devuelve la tupla RGB de un color de la paleta."""
    return hex_a_rgb(PALETA[nombre])


def hex_a_rgb(valor):
    valor = valor.lstrip("#")
    return tuple(int(valor[i : i + 2], 16) for i in (0, 2, 4))


def rgba(nombre, alfa=255):
    return rgb(nombre) + (alfa,)
