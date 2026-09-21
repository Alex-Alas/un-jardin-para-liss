window.AG = window.AG || {};

AG.Boot = class Boot extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    this.load.on('loaderror', (archivo) => {
      console.warn('[Boot] No se pudo cargar:', archivo && archivo.key);
    });

    if (!AG.requiereAssets()) {
      console.info('[Boot] Sin arte generado todavía: arrancando en modo esqueleto.');
      return;
    }

    this.load.atlas('arte', AG.ASSETS.atlas, AG.ASSETS.atlasDatos);
    this.load.bitmapFont(AG.CFG.FUENTE_CHICA, AG.ASSETS.fuentePng, AG.ASSETS.fuenteDatos);
  }

  create() {
    AG.arte = { listo: this.textures.exists('arte') };
    this.scene.start('Title');
  }
};
