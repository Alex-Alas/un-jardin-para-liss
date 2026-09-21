window.AG = window.AG || {};

(function () {
  const { CFG } = AG;

  const config = {
    type: Phaser.AUTO,
    parent: 'juego',
    width: CFG.VIEW_W,
    height: CFG.VIEW_H,
    backgroundColor: CFG.COLORES.negro,
    pixelArt: true,
    roundPixels: true,
    antialias: false,
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    },
    render: {
      pixelArt: true,
      antialias: false
    },
    input: {
      activePointers: 2
    },
    scene: [AG.Boot, AG.Title]
  };

  AG.juego = new Phaser.Game(config);

  AG.debug = {
    escenas: () => AG.juego.scene.scenes.map((e) => e.scene.key),
    ir: (clave, datos) => AG.juego.scene.start(clave, datos),
    saltar: (clave) => AG.juego.scene.start(clave)
  };

  window.addEventListener('error', (e) => {
    console.error('[juego] error:', e.message);
  });
})();
