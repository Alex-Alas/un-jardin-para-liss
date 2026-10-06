window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

  /** Los frames pintados del atlas (tools/arte_extra.py) que reemplazan a las texturas de acá. */
  const PINTADAS = { petalo: 'fx_petalo', hoja_seca: 'fx_hoja' };

  AG.FX = {
    /**
     * La textura de una partícula: el frame pintado del atlas si está, si no la que se dibuja
     * en `crearTexturas` (que queda de respaldo, para jugar sin el arte generado).
     */
    textura(scene, nombre) {
      const frame = PINTADAS[nombre];
      if (frame && AG.tieneFrame(scene, frame)) return { clave: 'arte', frame };
      return { clave: nombre, frame: undefined };
    },

    /** Configuración de partículas con su textura: el `frame` solo va si es un frame del atlas. */
    particulas(scene, x, y, nombre, config) {
      const { clave, frame } = this.textura(scene, nombre);
      if (!scene.textures.exists(clave)) return null;
      return scene.add.particles(x, y, clave, frame ? { frame, ...config } : config);
    },

    crearTexturas(scene) {
      if (!scene.textures.exists('corazon')) {
        const g = scene.add.graphics();
        const px = (x, y, w, h, color) => {
          g.fillStyle(c(color), 1);
          g.fillRect(x, y, w, h);
        };
        px(1, 0, 2, 1, AG.CFG.COLORES.amarillo);
        px(5, 0, 2, 1, AG.CFG.COLORES.amarillo);
        px(0, 1, 8, 3, AG.CFG.COLORES.amarillo);
        px(1, 4, 6, 1, AG.CFG.COLORES.amarillo);
        px(2, 5, 4, 1, AG.CFG.COLORES.amarillo);
        px(3, 6, 2, 1, AG.CFG.COLORES.amarillo);
        g.generateTexture('corazon', 8, 7);
        g.clear();

        // Pétalo: gota de 5x6 con el canto claro arriba-izquierda, como el resto del arte.
        const petalo = AG.CFG.COLORES.amarillo;
        px(2, 0, 1, 1, petalo);
        px(1, 1, 3, 1, petalo);
        px(0, 2, 5, 2, petalo);
        px(1, 4, 3, 1, petalo);
        px(2, 5, 1, 1, AG.CFG.COLORES.ambar);
        px(1, 1, 2, 2, AG.CFG.COLORES.amarilloClaro);
        g.generateTexture('petalo', 5, 6);
        g.clear();

        // Hoja seca: la trampa. Ancha y marrón, para que de un vistazo no se confunda con un
        // pétalo. La nervadura es corta a propósito: larga, la hoja parecía un palito.
        px(1, 0, 4, 1, AG.CFG.COLORES.marron);
        px(0, 1, 6, 3, AG.CFG.COLORES.marron);
        px(1, 4, 4, 1, AG.CFG.COLORES.marron);
        px(1, 1, 2, 1, AG.CFG.COLORES.marronClaro);
        px(2, 2, 2, 1, AG.CFG.COLORES.tinta);
        g.generateTexture('hoja_seca', 6, 5);
        g.clear();

        px(0, 0, 2, 2, AG.CFG.COLORES.blanco);
        g.generateTexture('chispa', 2, 2);
        g.destroy();
      }
      return this;
    },

    fundir(scene, alEntrar, alSalir) {
      const camara = scene.cameras.main;
      camara.fadeOut(260, 11, 10, 16);
      scene.time.delayedCall(280, () => {
        if (alEntrar) alEntrar();
        camara.fadeIn(300, 11, 10, 16);
        if (alSalir) alSalir();
      });
    },

    temblor(scene, duracion = 220, intensidad = 0.006) {
      scene.cameras.main.shake(duracion, intensidad);
    },

    latido(scene) {
      const { VIEW_W, VIEW_H } = AG.CFG;
      const corazon = AG.UI.corazon(scene, VIEW_W / 2, VIEW_H / 2 - 10, 4).setDepth(900).setScrollFactor(0);
      const base = corazon.scaleX;   // depende de qué corazón tocó: el pintado o el de respaldo
      scene.tweens.add({
        targets: corazon,
        scale: { from: base, to: base * 1.35 },
        duration: 140,
        yoyo: true,
        repeat: 2,
        onComplete: () => corazon.destroy()
      });
    },

    petalosAmbientales(scene, cantidad = 1) {
      const emisor = this.particulas(scene, 0, 0, 'petalo', {
        x: { min: 0, max: AG.CFG.VIEW_W },
        y: -8,
        lifespan: 9000,
        speedY: { min: 14, max: 26 },
        speedX: { min: -8, max: 8 },
        rotate: { min: 0, max: 360 },
        scale: { min: 0.7, max: 1.4 },
        alpha: { start: 0.9, end: 0.5 },
        frequency: cantidad > 1 ? 420 : 900,
        quantity: cantidad,
        blendMode: 'NORMAL'
      });
      if (!emisor) return null;
      emisor.setDepth(500).setScrollFactor(0);
      return emisor;
    },

    florecer(scene, x, y) {
      const emisor = this.particulas(scene, x, y, 'petalo', {
        lifespan: 1400,
        speed: { min: 20, max: 70 },
        angle: { min: 200, max: 340 },
        gravityY: 30,
        rotate: { min: 0, max: 360 },
        scale: { start: 1.4, end: 0.6 },
        emitting: false
      });
      if (!emisor) return;
      emisor.setDepth(800);
      emisor.explode(26);
      scene.time.delayedCall(2200, () => emisor.destroy());
    },

    /** Velo cálido de las seis de la tarde. Suave a propósito: el mapa de la colina ya viene
     *  teñido desde el PNG (tools/tiles.py § atardecer) y con los dos al full quemaba la escena. */
    washAtardecer(scene) {
      const capa = scene.add
        .rectangle(0, 0, AG.CFG.VIEW_W, AG.CFG.VIEW_H, c(AG.CFG.COLORES.atardecer), 0.12)
        .setOrigin(0)
        .setScrollFactor(0)
        .setDepth(600)
        .setBlendMode('MULTIPLY');
      return capa;
    }
  };
})();
