window.AG = window.AG || {};

AG.Title = class Title extends Phaser.Scene {
  constructor() {
    super('Title');
  }

  create() {
    const { VIEW_W, VIEW_H, COLORES, FUENTE_CHICA, FUENTE_GRANDE } = AG.CFG;
    const conFuente = AG.hayFuente();
    this.aviso = null;

    this.add.rectangle(0, 0, VIEW_W, VIEW_H, 0x0b0a10).setOrigin(0);

    this.rotulo(VIEW_W / 2, VIEW_H / 2 - 46, 'UN JARDÍN', FUENTE_GRANDE, COLORES.amarillo, conFuente);
    this.rotulo(VIEW_W / 2, VIEW_H / 2 - 24, 'PARA LISS', FUENTE_GRANDE, COLORES.amarilloClaro, conFuente);
    this.rotulo(VIEW_W / 2, VIEW_H / 2 + 8, '21 de septiembre', FUENTE_CHICA, COLORES.crema, conFuente);

    const empezar = this.rotulo(
      VIEW_W / 2,
      VIEW_H - 26,
      'TOCA O PRESIONA Z PARA EMPEZAR',
      FUENTE_CHICA,
      COLORES.blanco,
      conFuente
    );

    this.tweens.add({
      targets: empezar,
      alpha: { from: 1, to: 0.2 },
      duration: 640,
      yoyo: true,
      repeat: -1
    });

    this.input.once('pointerdown', () => this.empezar());
    this.input.keyboard.once('keydown-Z', () => this.empezar());
    this.input.keyboard.once('keydown-ENTER', () => this.empezar());
  }

  rotulo(x, y, texto, fuente, color, conFuente) {
    if (conFuente) {
      return this.add.bitmapText(x, y, fuente, texto, fuente === AG.CFG.FUENTE_GRANDE ? 16 : 8).setOrigin(0.5);
    }
    return this.add
      .text(x, y, texto, {
        fontFamily: 'monospace',
        fontSize: fuente === AG.CFG.FUENTE_GRANDE ? '20px' : '11px',
        color: color
      })
      .setOrigin(0.5);
  }

  empezar() {
    AG.musica && AG.musica.desbloquear();
    this.cameras.main.flash(240, 255, 244, 214);
    if (!AG.hayArte()) {
      this.mostrarAviso();
      return;
    }
    this.scene.start('Casa');
  }

  mostrarAviso() {
    if (this.aviso) return;
    this.aviso = this.add
      .text(AG.CFG.VIEW_W / 2, AG.CFG.VIEW_H - 8, 'falta generar el arte: corre tools/render_maps.py', {
        fontFamily: 'monospace',
        fontSize: '8px',
        color: '#8b8b9e'
      })
      .setOrigin(0.5);
  }
};
