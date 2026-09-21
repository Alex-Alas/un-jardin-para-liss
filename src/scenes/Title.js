window.AG = window.AG || {};

AG.Title = class Title extends Phaser.Scene {
  constructor() {
    super('Title');
  }

  create() {
    const { VIEW_W, VIEW_H, COLORES, FUENTE_GRANDE, FUENTE_CHICA } = AG.CFG;
    const c = (v) => AG.UI.color(v);
    this.fase = 'empezar';
    this.opciones = [];
    this.cursor = 0;

    this.add.rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.negro)).setOrigin(0);
    for (let i = 0; i < 22; i += 1) {
      this.add.circle(
        Phaser.Math.Between(0, VIEW_W),
        Phaser.Math.Between(0, VIEW_H),
        Phaser.Math.Between(1, 2),
        c(COLORES.crema),
        Phaser.Math.FloatBetween(0.2, 0.7)
      );
    }

    const titulo1 = AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 - 58, 'UN JARDÍN', {
      escala: 2,
      color: COLORES.amarillo
    })
      .setOrigin(0.5)
      .setScale(FUENTE_GRANDE === 'pixel16' ? 1.6 : 1.4);
    const titulo2 = AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 - 34, 'PARA LISS', {
      escala: 2,
      color: COLORES.amarilloClaro
    })
      .setOrigin(0.5)
      .setScale(1.6);
    AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 - 6, '21 de septiembre', { color: COLORES.crema }).setOrigin(0.5);

    this.pista = AG.UI.texto(this, VIEW_W / 2, VIEW_H - 30, 'TOCA O PRESIONA Z PARA EMPEZAR', {
      color: COLORES.blanco
    }).setOrigin(0.5);
    this.tweens.add({ targets: this.pista, alpha: { from: 1, to: 0.2 }, duration: 620, yoyo: true, repeat: -1 });
    this.tweens.add({ targets: [titulo1, titulo2], y: '-=2', duration: 1800, yoyo: true, repeat: -1 });

    AG.Musica.tocar('titulo');
    this.input.once('pointerdown', () => this.desbloquear());
    this.input.keyboard.once('keydown-Z', () => this.desbloquear());
    this.input.keyboard.once('keydown-ENTER', () => this.desbloquear());
  }

  desbloquear() {
    AG.Musica.desbloquear();
    AG.Musica.tocar('titulo');
    if (this.fase !== 'empezar') return;
    this.fase = 'menu';
    this.pista.setVisible(false);
    this.abrirMenu();
  }

  abrirMenu() {
    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    const hayPartida = Boolean(AG.Guardado.datos.flores || AG.Guardado.datos.recuerdos.length);
    const definiciones = [];
    if (hayPartida) definiciones.push({ texto: 'CONTINUAR', accion: () => this.continuar() });
    definiciones.push({ texto: 'EMPEZAR DESDE EL PRINCIPIO', accion: () => this.empezarNuevo() });
    definiciones.push({ texto: 'ÁLBUM DE RECUERDOS', accion: () => this.scene.start('Album') });
    definiciones.push({ texto: 'CRÉDITOS', accion: () => this.scene.start('Creditos') });

    this.opciones = definiciones.map((definicion, i) => {
      const texto = AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 + 16 + i * 18, '  ' + definicion.texto, {
        color: COLORES.blanco
      })
        .setOrigin(0.5)
        .setInteractive({ useHandCursor: true });
      texto.accion = definicion.accion;
      texto.on('pointerdown', () => definicion.accion());
      texto.on('pointerover', () => {
        this.cursor = i;
        this.pintarCursor();
      });
      return texto;
    });
    this.cursorCorazon = AG.UI.corazon(this, 0, 0, 1).setVisible(false);
    this.cursor = 0;
    this.pintarCursor();
  }

  pintarCursor() {
    const opcion = this.opciones[this.cursor];
    if (!opcion) return;
    this.cursorCorazon.setVisible(true);
    this.cursorCorazon.setPosition(opcion.x - opcion.width / 2 - 14, opcion.y + 3);
    this.opciones.forEach((o, i) => o.setAlpha(i === this.cursor ? 1 : 0.55));
  }

  mover(paso) {
    if (!this.opciones.length) return;
    this.cursor = (this.cursor + paso + this.opciones.length) % this.opciones.length;
    AG.Musica.sfx('blip');
    this.pintarCursor();
  }

  update() {
    if (this.fase !== 'menu') return;
    const entrada = this.entrada || (this.entrada = { dir: { x: 0, y: 0 } });
    if (!this.teclas) {
      this.teclas = this.input.keyboard.addKeys({
        arriba: 'UP',
        abajo: 'DOWN',
        w: 'W',
        s: 'S',
        accion: 'Z',
        accion2: 'ENTER'
      });
    }
    if (Phaser.Input.Keyboard.JustDown(this.teclas.arriba) || Phaser.Input.Keyboard.JustDown(this.teclas.w)) {
      this.mover(-1);
    }
    if (Phaser.Input.Keyboard.JustDown(this.teclas.abajo) || Phaser.Input.Keyboard.JustDown(this.teclas.s)) {
      this.mover(1);
    }
    if (
      Phaser.Input.Keyboard.JustDown(this.teclas.accion) ||
      Phaser.Input.Keyboard.JustDown(this.teclas.accion2)
    ) {
      const opcion = this.opciones[this.cursor];
      if (opcion) opcion.accion();
    }
  }

  continuar() {
    const datos = AG.Guardado.datos;
    AG.Musica.sfx('corazon');
    AG.FX.fundir(this, () =>
      this.scene.start(datos.escena || 'Casa', { inicio: datos.pos || undefined })
    );
  }

  empezarNuevo() {
    AG.Guardado.reiniciar();
    AG.Musica.sfx('corazon');
    AG.FX.fundir(this, () => this.scene.start('Casa', { inicio: { x: 9, y: 11 } }));
  }
};
