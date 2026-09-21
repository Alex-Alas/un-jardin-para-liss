window.AG = window.AG || {};

AG.Album = class Album extends Phaser.Scene {
  constructor() {
    super('Album');
  }

  create() {
    this.entrada = new AG.Entrada(this);
    this.entrada.mostrarControles(false);
    AG.Musica.tocar('titulo');
    this.recuerdos = new AG.Recuerdos(this);
    this.recuerdos.abrirAlbum({ alCerrar: () => this.volver() });
  }

  volver() {
    AG.FX.fundir(this, () => this.scene.start('Title'));
  }

  update(tiempo, delta) {
    this.recuerdos.actualizar(delta);
  }
};
