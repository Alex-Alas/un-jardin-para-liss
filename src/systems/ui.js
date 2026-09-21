window.AG = window.AG || {};

(function () {
  const { COLORES, FUENTE_CHICA } = AG.CFG;

  function color(valor) {
    return Number.parseInt(String(valor).replace('#', '0x'), 16);
  }

  AG.UI = {
    color: color,

    texto(scene, x, y, cadena, opciones = {}) {
      const tamano = opciones.tamano === 'grande' ? FUENTE_CHICA : FUENTE_CHICA;
      const escala = opciones.escala || 1;
      if (AG.hayFuente()) {
        const t = scene.add.bitmapText(x, y, tamano, cadena, 8);
        return t.setScale(escala).setScrollFactor(opciones.fijo ? 0 : 1).setDepth(opciones.profundidad || 0);
      }
      const t = scene.add.text(x, y, cadena, {
        fontFamily: 'monospace',
        fontSize: `${Math.round(11 * escala)}px`,
        color: opciones.color || COLORES.blanco
      });
      return t.setScrollFactor(opciones.fijo ? 0 : 1).setDepth(opciones.profundidad || 0);
    },

    caja(scene, x, y, ancho, alto, opciones = {}) {
      const alfa = opciones.alfa === undefined ? 0.94 : opciones.alfa;
      const fondo = scene.add
        .rectangle(x, y, ancho, alto, color(opciones.color || COLORES.tinta), alfa)
        .setOrigin(0)
        .setDepth(opciones.profundidad || 0);
      if (opciones.borde === false) return fondo;
      const grosor = opciones.grosor || 2;
      const borde = scene.add
        .rectangle(x, y, ancho, alto, color(opciones.bordeColor || COLORES.blanco), 0)
        .setOrigin(0)
        .setStrokeStyle(grosor, color(opciones.bordeColor || COLORES.blanco), 1)
        .setDepth((opciones.profundidad || 0) + 1);
      return { fondo, borde };
    },

    /** Envuelve texto en líneas de `maximo` caracteres (fuente monoespaciada). */
    envolver(cadena, maximo) {
      const palabras = String(cadena).split(' ');
      const lineas = [];
      let actual = '';
      palabras.forEach((palabra) => {
        if (!actual.length) {
          actual = palabra;
        } else if ((actual + ' ' + palabra).length <= maximo) {
          actual += ' ' + palabra;
        } else {
          lineas.push(actual);
          actual = palabra;
        }
      });
      if (actual.length) lineas.push(actual);
      return lineas;
    },

    /** Reparte las líneas en páginas de `porPagina` renglones. */
    paginar(lineas, porPagina) {
      const paginas = [];
      for (let i = 0; i < lineas.length; i += porPagina) {
        paginas.push(lineas.slice(i, i + porPagina));
      }
      return paginas.length ? paginas : [['']];
    },

    corazon(scene, x, y, escala = 1) {
      if (scene.textures.exists('corazon')) {
        return scene.add.image(x, y, 'corazon').setScale(escala);
      }
      return scene.add.rectangle(x, y, 7 * escala, 6 * escala, color(COLORES.amarillo));
    }
  };
})();
