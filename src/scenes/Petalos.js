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
    this.rafaga = { fuerza: 0, restante: 0, proxima: 3200 };
  }

  create() {
    this.fondo();

    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    const c = (v) => AG.UI.color(v);

    this.entrada = new AG.Entrada(this);
    this.dialogo = new AG.Dialogo(this, this.entrada);
    AG.Musica.tocar('petalos');

    if (AG.hayAtlas()) {
      this.jugador = this.add.sprite(VIEW_W / 2, VIEW_H - 12, 'arte', 'liss_idle_abajo_0').setOrigin(0.5, 1);
      AG.crearAnimacionesDeLiss(this);
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

  /** Cada ronda tiene su lugar y su hora: el patio de la florería de día, el parque al atardecer. */
  fondo() {
    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    const c = (v) => AG.UI.color(v);
    const horizonte = Math.round(VIEW_H * 0.62);
    const parque = this.tipo === 'petalos2';

    if (parque) {
      // Cielo en bandas, de morado arriba a ámbar en el horizonte. Sin degradado real: son
      // cuatro franjas planas, que es como se hace en pixel art.
      const bandas = [COLORES.morado, COLORES.cieloOscuro, COLORES.atardecer, COLORES.ambar];
      bandas.forEach((color, i) => {
        const alto = Math.ceil(horizonte / bandas.length);
        this.add.rectangle(0, i * alto, VIEW_W, alto, c(color)).setOrigin(0);
      });
      this.add.circle(VIEW_W - 76, horizonte - 26, 17, c(COLORES.amarilloClaro));
      this.add.circle(VIEW_W - 76, horizonte - 26, 22, c(COLORES.amarillo), 0.25);
      // Cerros lejanos: dos hileras de siluetas planas, la de atrás más alta y más fría.
      [[46, COLORES.morado, 96, 40], [30, COLORES.tintaSuave, 78, 0]].forEach(([alto, color, paso, desfase]) => {
        for (let i = -1; i < 8; i += 1) {
          this.add
            .triangle(i * paso + desfase, horizonte, -64, 0, 0, -alto, 64, 0, c(color))
            .setOrigin(0, 1);
        }
      });
    } else {
      this.add.rectangle(0, 0, VIEW_W, horizonte, c(COLORES.cielo)).setOrigin(0);
      for (let i = 0; i < 4; i += 1) {
        this.add.circle(50 + i * 130, 30 + (i % 2) * 22, 14, c(COLORES.blanco), 0.75);
        this.add.circle(64 + i * 130, 32 + (i % 2) * 22, 10, c(COLORES.blanco), 0.75);
      }
    }

    const pasto = parque ? COLORES.verdeOscuro : COLORES.verde;
    this.add.rectangle(0, horizonte, VIEW_W, VIEW_H - horizonte, c(pasto)).setOrigin(0);
    this.add.rectangle(0, horizonte - 3, VIEW_W, 3, c(COLORES.verdeOscuro)).setOrigin(0);
    for (let i = 0; i < 40; i += 1) {
      const x = (i * 71) % VIEW_W;
      const y = horizonte + 6 + ((i * 37) % (VIEW_H - horizonte - 8));
      this.add.rectangle(x, y, 2, 2, c(i % 3 ? COLORES.verde : COLORES.amarillo), 0.7).setOrigin(0);
    }

    // Árboles: tronco y tres bolas de copa, como los del mapa pero en silueta de fondo.
    const arboles = parque ? 6 : 3;
    for (let i = 0; i < arboles; i += 1) {
      const x = 40 + i * Math.round(VIEW_W / arboles);
      const base = horizonte + 2 + (i % 2) * 5;
      this.add.rectangle(x, base, 6, 26, c(COLORES.marron)).setOrigin(0.5, 1);
      [[0, -30, 19], [-11, -24, 13], [11, -25, 12]].forEach(([dx, dy, r]) => {
        this.add.circle(x + dx, base + dy, r, c(parque ? COLORES.verdeOscuro : COLORES.verde));
      });
      this.add.circle(x - 7, base - 36, 7, c(parque ? COLORES.verde : COLORES.verdeClaro));
    }

    if (parque) {
      // Velo cálido encima de todo: el parque es la ronda de las seis de la tarde.
      this.add
        .rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.atardecer), 0.14)
        .setOrigin(0)
        .setDepth(40)
        .setBlendMode('MULTIPLY');
    }
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
    const paso = 98 * (delta / 1000) * (dir.x && dir.y ? Math.SQRT1_2 : 1);
    this.jugador.x = Phaser.Math.Clamp(this.jugador.x + dir.x * paso, 12, AG.CFG.VIEW_W - 12);
    this.jugador.y = Phaser.Math.Clamp(this.jugador.y + dir.y * paso, AG.CFG.VIEW_H * 0.45, AG.CFG.VIEW_H - 4);
    this.animarJugador(dir);

    this.acumulador += delta;
    while (this.acumulador >= this.reglas.intervalo) {
      this.acumulador -= this.reglas.intervalo;
      this.crearPetalo();
    }

    this.actualizarRafaga(delta);
    this.moverPetalos(delta);
    this.recolectar();

    this.restante -= delta / 1000;
    this.actualizarHud();
    if (this.atrapados >= this.reglas.meta) this.terminar(true);
    else if (this.restante <= 0) this.terminar(false);
  }

  /** Liss camina mientras atrapa pétalos; quieta, respira mirando hacia abajo. */
  animarJugador(dir) {
    if (!AG.hayAtlas() || !this.jugador.play) return;
    const nombre = dir.x || dir.y ? AG.direccionDibujable(this, dir) : 'abajo';
    const clave = `liss_${dir.x || dir.y ? 'camina' : 'idle'}_${nombre}`;
    if (this.anims.exists(clave)) this.jugador.play(clave, true);
  }

  crearPetalo() {
    const { VIEW_W } = AG.CFG;
    const esHoja = this.reglas.hojas > 0 && Math.random() * 100 < this.reglas.hojas;
    const x = Phaser.Math.Between(12, VIEW_W - 12);
    const imagen = this.add
      .image(x, -8, esHoja ? 'hoja_seca' : 'petalo')
      .setDepth(10)
      .setScale(esHoja ? 1.5 : 1.3);   // las texturas de fx.js ya son más grandes
    imagen.esHoja = esHoja;
    imagen.vel = {
      x: (Math.random() * 2 - 1) * this.reglas.viento,
      y: this.reglas.motor + Math.random() * 22
    };
    this.petalos.push(imagen);
  }

  /**
   * El viento del parque no sopla parejo: sopla a ráfagas.
   *
   * Un viento constante solo desplaza todo un poco y se compensa caminando; una ráfaga avisada
   * obliga a decidir a dónde correr, que es de lo que habla Sofi antes de empezar. Solo existe
   * en las rondas con `viento`: la de Doña Flora se queda tranquila.
   */
  actualizarRafaga(delta) {
    if (!this.reglas.viento) return;

    if (this.rafaga.restante > 0) {
      this.rafaga.restante -= delta;
      if (this.rafaga.restante <= 0) this.textoAviso.setText('');
      return;
    }

    this.rafaga.proxima -= delta;
    if (this.rafaga.proxima > 0) return;

    const haciaLaDerecha = Math.random() < 0.5;
    this.rafaga.fuerza = (haciaLaDerecha ? 1 : -1) * this.reglas.viento * Phaser.Math.FloatBetween(1.6, 2.6);
    this.rafaga.restante = Phaser.Math.Between(900, 1500);
    this.rafaga.proxima = Phaser.Math.Between(2600, 4200);
    this.textoAviso.setText(haciaLaDerecha ? 'viento >>>' : '<<< viento');
    AG.Musica.sfx('paso');
    this.dibujarRafaga(haciaLaDerecha);
  }

  /** Rayitas horizontales que cruzan la pantalla: el aviso visual de la ráfaga. */
  dibujarRafaga(haciaLaDerecha) {
    const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
    for (let i = 0; i < 7; i += 1) {
      const y = Phaser.Math.Between(40, VIEW_H - 30);
      const largo = Phaser.Math.Between(16, 40);
      const desde = haciaLaDerecha ? -largo : VIEW_W + largo;
      const raya = this.add
        .rectangle(desde, y, largo, 1, AG.UI.color(COLORES.blanco), 0.5)
        .setOrigin(0, 0.5)
        .setDepth(30);
      this.tweens.add({
        targets: raya,
        x: haciaLaDerecha ? VIEW_W + largo : -largo,
        duration: Phaser.Math.Between(420, 700),
        delay: i * 55,
        onComplete: () => raya.destroy()
      });
    }
  }

  moverPetalos(delta) {
    const dt = delta / 1000;
    for (let i = this.petalos.length - 1; i >= 0; i -= 1) {
      const p = this.petalos[i];
      const empuje = this.rafaga.restante > 0 ? this.rafaga.fuerza : 0;
      p.x += (p.vel.x + empuje) * dt;
      p.y += p.vel.y * dt;
      p.setAngle(p.esHoja ? (p.x + p.y) * 0.2 : p.x * 2);
      // La ráfaga puede sacar un pétalo de pantalla por el costado: ahí también se perdió.
      if (p.y > AG.CFG.VIEW_H + 10 || p.x < -14 || p.x > AG.CFG.VIEW_W + 14) {
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
