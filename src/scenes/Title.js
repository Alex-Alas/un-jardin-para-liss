window.AG = window.AG || {};

AG.Title = class Title extends Phaser.Scene {
  constructor() {
    super('Title');
  }

  create() {
    const { VIEW_W, VIEW_H } = AG.CFG;

    this.add.rectangle(0, 0, VIEW_W, VIEW_H, 0x0b0a10).setOrigin(0);

    const fuente = this.textures.exists('arte') ? 'pixel16' : undefined;

    this.add
      .text(VIEW_W / 2, VIEW_H / 2 - 40, 'UN JARDÍN', {
        fontFamily: fuente ? 'pixel16' : 'monospace',
        fontSize: '24px',
        color: '#ffd23f'
      })
      .setOrigin(0.5);

    this.add
      .text(VIEW_W / 2, VIEW_H / 2 - 12, 'PARA LISS', {
        fontFamily: fuente ? 'pixel16' : 'monospace',
        fontSize: '24px',
        color: '#ffe98a'
      })
      .setOrigin(0.5);

    this.add
      .text(VIEW_W / 2, VIEW_H - 40, '21 de septiembre', {
        fontFamily: fuente ? 'pixel8' : 'monospace',
        fontSize: '8px',
        color: '#f6e7c6'
      })
      .setOrigin(0.5);

    const empezar = this.add
      .text(VIEW_W / 2, VIEW_H - 22, 'TOCA O PRESIONA Z PARA EMPEZAR', {
        fontFamily: fuente ? 'pixel8' : 'monospace',
        fontSize: '8px',
        color: '#fff8ec'
      })
      .setOrigin(0.5);

    this.tweens.add({
      targets: empezar,
      alpha: { from: 1, to: 0.25 },
      duration: 620,
      yoyo: true,
      repeat: -1
    });

    this.input.once('pointerdown', () => this.empezar());
    this.input.keyboard.once('keydown-Z', () => this.empezar());
    this.input.keyboard.once('keydown-ENTER', () => this.empezar());
  }

  empezar() {
    AG.musica && AG.musica.desbloquear();
    this.cameras.main.flash(240, 255, 244, 214);
    this.time.delayedCall(160, () => {
      this.scene.start(AG.ASSETS_READY ? 'Casa' : 'Title');
      if (!AG.ASSETS_READY) this.avisarEsqueleto();
    });
  }

  avisarEsqueleto() {
    this.add
      .text(AG.CFG.VIEW_W / 2, AG.CFG.VIEW_H - 6, 'esqueleto: falta generar el arte', {
        fontFamily: 'monospace',
        fontSize: '8px',
        color: '#8b8b9e'
      })
      .setOrigin(0.5);
  }
};
