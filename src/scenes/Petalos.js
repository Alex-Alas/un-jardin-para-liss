window.AG = window.AG || {};

AG.Petalos = class Petalos extends Phaser.Scene {
  constructor() {
    super('Petalos');
  }

  init(datos) {
    const datos_ = datos || {};
    this.tipo = datos_.tipo || 'petalos1';
    this.volverA = datos_.volver || 'Floreria';
    this.inicioVolver = datos_.inicio || { x: 7, y: 10 };
    this.reglas = {
      petalos1: { meta: 10, segundos: 45, viento: 0, hojas: 0, motor: 26, intervalo: 300 },
      petalos2: { meta: 14, segundos: 50, viento: 30, hojas: 22, motor: 34, intervalo: 240 }
    }[this.tipo];
    this.atrapados = 0;
    this.restante = this.reglas.segundos;
    this.fase = 'intro';
    this.petalos = [];
    this.acumulador = 0;
    this.combo = 0;
  }

  create() {
    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    const c = (v) => AG.UI.color(v);

    this.add.rectangle(0, 0, VIEW_W, VIEW_H * 0.62, c(COLORES.cielo)).setOrigin(0);
    this.add.rectangle(0, VIEW_H * 0.62, VIEW_W, VIEW_H * 0.38, c(COLORES.verde)).setOrigin(0);
    this.add.rectangle(0, VIEW_H * 0.62 - 3, VIEW_W, 3, c(COLORES.verdeOscuro)).setOrigin(0);
    if (this.tipo === 'petalos2') {
      for (let i = 0; i < 6; i += 1) {
        this.add
          .rectangle(40 + i * 78, VIEW_H * 0.62 - 22 - (i % 2) * 6, 6, 26, c(COLORES.marron))
          .setOrigin(0.5, 0);
        this.add.circle(40 + i * 78, VIEW_H * 0.62 - 26 - (i % 2) * 6, 18, c(COLORES.verdeOscuro), 0.9);
      }
    }

    this.entrada = new AG.Entrada(this);
    this.dialogo = new AG.Dialogo(this, this.entrada);
    AG.Musica.tocar('petalos');

    if (AG.hayAtlas()) {
      this.jugador = this.add.sprite(VIEW_W / 2, VIEW_H - 12, 'arte', 'liss_idle_abajo_0').setOrigin(0.5, 1);
    } else {
      this.jugador = this.add.rectangle(VIEW_W / 2, VIEW_H - 12, 14, 22, c(COLORES.rosa)).setOrigin(0.5, 1);
    }
    this.jugador.setDepth(20);

    this.textoMeta = AG.UI.texto(this, 12, 12, '', { color: COLORES.blanco }).setDepth(50);
    this.textoTiempo = AG.UI.texto(this, VIEW_W - 12, 12, '', { color: COLORES.blanco })
      .setOrigin(1, 0)
      .setDepth(50);
    this.textoAviso = AG.UI.texto(this, VIEW_W / 2, VIEW_H * 0.3, '', { color: COLORES.amarillo })
      .setOrigin(0.5)
      .setDepth(50);
    this.actualizarHud();

    this.dialogo.abrir(`${this.tipo}.intro`, { alCerrar: () => this.empezarJuego() });
  }

  empezarJuego() {
    this.fase = 'juego';
    this.acumulador = 0;
    this.textoAviso.setText('');
  }

  actualizarHud() {
    this.textoMeta.setText(`PETALOS ${this.atrapados}/${this.reglas.meta}`);
    this.textoTiempo.setText(`${Math.max(0, Math.ceil(this.restante))}s`);
  }

  update(tiempo, delta) {
    this.dialogo.actualizar(delta);
    if (this.fase !== 'juego') return;

    const dir = this.entrada.direccion();
    const paso = 98 * (delta / 1000);
    this.jugador.x = Phaser.Math.Clamp(this.jugador.x + dir.x * paso, 12, AG.CFG.VIEW_W - 12);
    this.jugador.y = Phaser.Math.Clamp(this.jugador.y + dir.y * paso, AG.CFG.VIEW_H * 0.45, AG.CFG.VIEW_H - 4);

    this.acumulador += delta;
    while (this.acumulador >= this.reglas.intervalo) {
      this.acumulador -= this.reglas.intervalo;
      this.crearPetalo();
    }

    this.moverPetalos(delta);
    this.recolectar();

    this.restante -= delta / 1000;
    this.actualizarHud();
    if (this.atrapados >= this.reglas.meta) this.terminar(true);
    else if (this.restante <= 0) this.terminar(false);
  }

  crearPetalo() {
    const { VIEW_W } = AG.CFG;
    const esHoja = this.reglas.hojas > 0 && Math.random() * 100 < this.reglas.hojas;
    const x = Phaser.Math.Between(12, VIEW_W - 12);
    const imagen = this.add
      .image(x, -8, esHoja ? 'hoja_seca' : 'petalo')
      .setDepth(10)
      .setScale(esHoja ? 2.2 : 1.8);
    imagen.esHoja = esHoja;
    imagen.vel = {
      x: (Math.random() * 2 - 1) * this.reglas.viento,
      y: this.reglas.motor + Math.random() * 22
    };
    this.petalos.push(imagen);
  }

  moverPetalos(delta) {
    const dt = delta / 1000;
    for (let i = this.petalos.length - 1; i >= 0; i -= 1) {
      const p = this.petalos[i];
      p.x += p.vel.x * dt;
      p.y += p.vel.y * dt;
      p.setAngle(p.esHoja ? (p.x + p.y) * 0.2 : p.x * 2);
      if (p.y > AG.CFG.VIEW_H + 10) {
        p.destroy();
        this.petalos.splice(i, 1);
      }
    }
  }

  recolectar() {
    for (let i = this.petalos.length - 1; i >= 0; i -= 1) {
      const p = this.petalos[i];
      const distancia = Phaser.Math.Distance.Between(p.x, p.y, this.jugador.x, this.jugador.y - 14);
      if (distancia > 17) continue;
      if (p.esHoja) {
        this.combo = 0;
        this.atrapados = Math.max(0, this.atrapados - 1);
        AG.Musica.sfx('error');
        AG.FX.temblor(this, 110, 0.004);
      } else {
        this.combo += 1;
        this.atrapados += 1;
        AG.Musica.sfx('petalo', this.combo);
        this.mostrarCombo();
      }
      p.destroy();
      this.petalos.splice(i, 1);
    }
  }

  mostrarCombo() {
    if (this.combo < 3) return;
    const aviso = AG.UI.texto(this, this.jugador.x, this.jugador.y - 40, `${this.combo} seguidas`, {
      color: AG.CFG.COLORES.amarillo
    })
      .setOrigin(0.5)
      .setDepth(60);
    this.tweens.add({
      targets: aviso,
      y: aviso.y - 14,
      alpha: 0,
      duration: 700,
      onComplete: () => aviso.destroy()
    });
  }

  limpiarPetalos() {
    this.petalos.forEach((p) => p.destroy());
    this.petalos = [];
  }

  terminar(gano) {
    if (this.fase !== 'juego') return;
    this.fase = 'fin';
    this.limpiarPetalos();

    if (!gano) {
      this.dialogo.abrir(`${this.tipo}.reintento`, {
        alCerrar: () => {
          this.atrapados = 0;
          this.combo = 0;
          this.restante = this.reglas.segundos;
          this.actualizarHud();
          this.fase = 'intro';
          this.dialogo.abrir(`${this.tipo}.intro`, { alCerrar: () => this.empezarJuego() });
        }
      });
      return;
    }

    AG.Guardado.marcar(`${this.tipo}.listo`);
    this.dialogo.abrir(`${this.tipo}.victoria`, { alCerrar: () => this.volver() });
  }

  volver() {
    AG.FX.fundir(this, () => this.scene.start(this.volverA, { inicio: this.inicioVolver }));
  }
};
