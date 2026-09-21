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
      activePointers: 3
    },
    scene: [AG.Boot, AG.Title, AG.Casa, AG.Pueblo, AG.Floreria, AG.Colina, AG.Petalos, AG.Album, AG.Creditos]
  };

  AG.juego = new Phaser.Game(config);

  AG.debug = {
    escenas: () => AG.juego.scene.scenes.map((e) => e.scene.key),
    ir: (clave, datos) => {
      AG.juego.scene.getScenes(true).forEach((escena) => {
        if (escena.scene.key !== clave) AG.juego.scene.stop(escena.scene.key);
      });
      AG.juego.scene.start(clave, datos);
    },
    saltar: (clave) => AG.debug.ir(clave),
    flores: (n) => {
      AG.Guardado.datos.flores = n;
      AG.Guardado.guardar();
      return n;
    },
    olvidar: () => {
      AG.Guardado.reiniciar();
      return 'guardado borrado';
    }
  };

  window.addEventListener('error', (e) => {
    console.error('[juego] error:', e.message);
  });
})();
