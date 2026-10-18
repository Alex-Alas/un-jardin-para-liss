window.AG = window.AG || {};

AG.Creditos = class Creditos extends Phaser.Scene {
  constructor() {
    super('Creditos');
  }

  create() {
    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    const c = (v) => AG.UI.color(v);

    // El pueblo de noche del título, más oscuro: los créditos tienen que leerse mientras suben.
    const fondo = AG.ponerFondo(this, 'titulo');
    this.add.rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.negro), fondo ? 0.55 : 1).setOrigin(0);
    this.entrada = new AG.Entrada(this);
    AG.Musica.tocar('final');
    AG.FX.petalosAmbientales(this, 2);

    const lineas = [
      ['UN JARDÍN PARA LISS', COLORES.amarillo],
      ['', COLORES.blanco],
      ['Una aventura hecha a mano por Alex', COLORES.crema],
      ['(Y con ayuda de Claudio, jeje)', COLORES.gris],
      ['', COLORES.blanco],
      ['Historia, arte y fotos: Alex y Liss', COLORES.blanco],
      ['', COLORES.blanco],
      ['Gracias a Doña Flora, a Don Beto,', COLORES.crema],
      ['a Sofi y a Michi,', COLORES.crema],
      ['que son inventados, pero ayudaron muchísimo.', COLORES.crema],
      ['', COLORES.blanco],
      ['21 de septiembre.', COLORES.amarilloClaro],
      ['', COLORES.blanco],
      ['Feliz Día de las Flores Amarillas.', COLORES.amarillo],
      ['', COLORES.blanco],
      ['Y hoy, sobre todo:', COLORES.crema],
      ['¡FELIZ CUMPLEAÑOS, AMOYCHITO!', COLORES.amarillo],
      ['', COLORES.blanco],
      ['Gracias, mi chulita, por tu atención,', COLORES.crema],
      ['por tu cariño, por tu compromiso', COLORES.crema],
      ['y por tu inmenso amor.', COLORES.crema],
      ['', COLORES.blanco],
      ['Te deseo flores, mi osita preciosita,', COLORES.crema],
      ['y una vida llenísima', COLORES.crema],
      ['de bendiciones y amors.', COLORES.crema],
      ['', COLORES.blanco],
      ['Este jardín de flores es para ti,', COLORES.amarilloClaro],
      ['mi bellísima noviecita :>', COLORES.amarilloClaro],
      ['', COLORES.blanco],
      ['Te amo, mi Liss hermosa.', COLORES.rosa]
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
    // Siguen subiendo detrás de la pantalla final, para que no queden quietas debajo del velo.
    this.textos.forEach((t) => {
      t.y -= this.velocidad * dt;
    });
    if (!this.terminado) {
      const limite = AG.CFG.VIEW_H * 0.35;
      // La pantalla final llega cuando la última línea ya subió hasta arriba del centro: si se
      // esperara a la primera, el final de los créditos (el cumpleaños) quedaría tapado.
      const ultima = this.textos[this.textos.length - 1];
      if (ultima && ultima.y < limite) {
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
    AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 - 22, '¡Feliz cumpleaños, amorcito!', { color: COLORES.rosa })
      .setOrigin(0.5)
      .setDepth(51);
    AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 - 6, 'Gracias por jugar, te amo <333', { color: COLORES.amarillo })
      .setOrigin(0.5)
      .setDepth(51);
    AG.UI.texto(this, VIEW_W / 2, VIEW_H / 2 + 14, 'A o ESC para volver', { color: COLORES.gris })
      .setOrigin(0.5)
      .setDepth(51);
  }

  salir() {
    AG.FX.fundir(this, () => this.scene.start('Title'));
  }
};
