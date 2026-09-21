window.AG = window.AG || {};

AG.Creditos = class Creditos extends Phaser.Scene {
  constructor() {
    super('Creditos');
  }

  create() {
    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    const c = (v) => AG.UI.color(v);

    this.add.rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.negro)).setOrigin(0);
    this.entrada = new AG.Entrada(this);
    AG.Musica.tocar('final');
    AG.FX.petalosAmbientales(this, 2);

    const lineas = [
      ['UN JARDÍN PARA LISS', COLORES.amarillo],
      ['', COLORES.blanco],
      ['Una aventura hecha a mano por Alex,', COLORES.crema],
      ['con ayuda de Claude.', COLORES.crema],
      ['', COLORES.blanco],
      ['Historia, arte y fotos: Alex y Liss', COLORES.blanco],
      ['Motor: Phaser 4', COLORES.gris],
      ['Fuente: Press Start 2P (OFL)', COLORES.gris],
      ['Música: chiptune generado en vivo', COLORES.gris],
      ['', COLORES.blanco],
      ['Gracias a Doña Flora, a Don Beto,', COLORES.crema],
      ['a Sofi y a Michi,', COLORES.crema],
      ['que son inventados, pero ayudaron muchísimo.', COLORES.crema],
      ['', COLORES.blanco],
      ['21 de septiembre.', COLORES.amarilloClaro],
      ['', COLORES.blanco],
      ['Feliz Día de las Flores Amarillas.', COLORES.amarillo],
      ['', COLORES.blanco],
      ['Te amo, Liss.', COLORES.rosa]
    ];

    let y = VIEW_H + 10;
    this.textos = lineas.map(([texto, color]) => {
      const objeto = AG.UI.texto(this, VIEW_W / 2, y, texto || ' ', { color, escala: 1.2 }).setOrigin(0.5, 0);
      y += objeto.height + 6;
      return objeto;
    });
    this.alto = y;

    this.velocidad = 16;
    this.terminado = false;
  }

  update(tiempo, delta) {
    const dt = delta / 1000;
    if (!this.terminado) {
      const limite = AG.CFG.VIEW_H * 0.35;
      this.textos.forEach((t) => {
        t.y -= this.velocidad * dt;
      });
      const primera = this.textos[0];
      if (primera && primera.y < -60) {
        this.terminado = true;
        this.mostrarFinal();
      }
    }
    if (this.entrada.accion() || this.entrada.pausa()) this.salir();
  }

  mostrarFinal() {
    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    const c = (v) => AG.UI.color(v);
    this.add
      .rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.negro), 0.85)
      .setOrigin(0)
      .setDepth(50);
    AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 - 10, 'Gracias por jugar, Liss.', { color: COLORES.amarillo })
      .setOrigin(0.5)
      .setDepth(51);
    AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 + 10, 'A o ESC para volver', { color: COLORES.gris })
      .setOrigin(0.5)
      .setDepth(51);
  }

  salir() {
    AG.FX.fundir(this, () => this.scene.start('Title'));
  }
};
