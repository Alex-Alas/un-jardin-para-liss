window.AG = window.AG || {};

AG.Boot = class Boot extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    this.load.on('loaderror', (archivo) => {
      console.warn('[Boot] No se pudo cargar:', archivo && archivo.key);
    });

    if (AG.hayFuente()) {
      Object.entries(AG.ASSETS.fuentes).forEach(([clave, rutas]) => {
        this.load.bitmapFont(clave, rutas.png, rutas.xml);
      });
    } else {
      console.info('[Boot] Sin fuente bitmap todavía: se usa la fuente del sistema.');
    }

    if (AG.hayAtlas()) {
      this.load.atlas('arte', AG.ASSETS.atlas, AG.ASSETS.atlasDatos);
    } else {
      console.info('[Boot] Sin atlas todavía: se dibuja con formas.');
    }
  }

  create() {
    AG.arte = { fuente: AG.hayFuente(), atlas: AG.hayAtlas() };
    this.scene.start('Title');
  }
};
