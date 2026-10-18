window.AG = window.AG || {};

AG.CFG = {
  TITULO: 'UN JARDÍN PARA LISS',
  VIEW_W: 480,
  VIEW_H: 270,
  TILE: 16,
  SPRITE_W: 16,
  SPRITE_H: 34,   // la hoja de Liss manda: 2 tiles de alto, con aire arriba (ver docs/arte.md)
  VELOCIDAD: 62,
  SAVE_KEY: 'un-jardin-para-liss:v1',
  FUENTE_CHICA: 'pixel8',
  FUENTE_GRANDE: 'pixel16',
  TEXTO: {
    VELOCIDAD: 34,
    BLIP_CADA: 3,
    MARGEN: 6
  },
  // Cuántas letras de 8 px entran por renglón en los recuerdos. Lo usan el polaroid, el álbum y
  // el validador de contenido, que avisa si un texto nuevo no cabe.
  POLAROID: {
    LETRAS_MARCO: 23, // título y pie: los 184 px entre los márgenes del marco
    RENGLONES_MARCO: 4,
    LETRAS_MENSAJE: 24, // la carta de al lado: 192 px
    RENGLONES_MENSAJE: 10,
    LETRAS_ALBUM: 16, // el título en la tarjeta del álbum: 128 px
    RENGLONES_ALBUM: 2
  },
  COLORES: {
    tinta: '#1b1420',
    tintaSuave: '#3b2f47',
    blanco: '#fff8ec',
    crema: '#f6e7c6',
    amarillo: '#ffd23f',
    amarilloClaro: '#ffe98a',
    ambar: '#e8a020',
    naranja: '#f2802c',
    rojo: '#d24b3f',
    rosa: '#f2a8b8',
    verde: '#63a852',
    verdeOscuro: '#2f6b3a',
    verdeClaro: '#a8d672',
    cielo: '#7fc7e8',
    cieloOscuro: '#4a7fb5',
    atardecer: '#f4a259',
    morado: '#6b4a8c',
    marron: '#8a5a3b',
    marronClaro: '#c08a5a',
    gris: '#8b8b9e',
    grisOscuro: '#4a4a5e',
    negro: '#0b0a10'
  }
};
