window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

  AG.FX = {
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

        const petalo = AG.CFG.COLORES.amarillo;
        px(1, 0, 1, 1, petalo);
        px(0, 1, 3, 2, petalo);
        px(1, 3, 1, 1, petalo);
        g.generateTexture('petalo', 3, 4);
        g.clear();

        px(0, 0, 3, 3, AG.CFG.COLORES.marron);
        px(0, 2, 1, 1, AG.CFG.COLORES.tinta);
        g.generateTexture('hoja_seca', 3, 3);
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
      scene.tweens.add({
        targets: corazon,
        scale: { from: 4, to: 5.4 },
        duration: 140,
        yoyo: true,
        repeat: 2,
        onComplete: () => corazon.destroy()
      });
    },

    petalosAmbientales(scene, cantidad = 1) {
      if (!scene.textures.exists('petalo')) return null;
      const emisor = scene.add.particles(0, 0, 'petalo', {
        x: { min: 0, max: AG.CFG.VIEW_W },
        y: -8,
        lifespan: 9000,
        speedY: { min: 14, max: 26 },
        speedX: { min: -8, max: 8 },
        scale: { min: 0.8, max: 1.6 },
        alpha: { start: 0.9, end: 0.5 },
        frequency: cantidad > 1 ? 420 : 900,
        quantity: cantidad,
        blendMode: 'NORMAL'
      });
      emisor.setDepth(500).setScrollFactor(0);
      return emisor;
    },

    florecer(scene, x, y) {
      if (!scene.textures.exists('petalo')) return;
      const emisor = scene.add.particles(x, y, 'petalo', {
        lifespan: 1400,
        speed: { min: 20, max: 70 },
        angle: { min: 200, max: 340 },
        gravityY: 30,
        scale: { start: 1.6, end: 0.6 },
        emitting: false
      });
      emisor.setDepth(800);
      emisor.explode(26);
      scene.time.delayedCall(2200, () => emisor.destroy());
    },

    washAtardecer(scene) {
      const capa = scene.add
        .rectangle(0, 0, AG.CFG.VIEW_W, AG.CFG.VIEW_H, c(AG.CFG.COLORES.atardecer), 0.22)
        .setOrigin(0)
        .setScrollFactor(0)
        .setDepth(600)
        .setBlendMode('MULTIPLY');
      return capa;
    }
  };
})();
