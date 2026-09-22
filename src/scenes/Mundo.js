window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

  AG.Mundo = class Mundo extends Phaser.Scene {
    constructor(ajustes) {
      super(ajustes.clave);
      this.claveMapa = ajustes.mapa || ajustes.clave.toLowerCase();
      this.ajustes = ajustes;
    }

    init(datos) {
      this.datosEntrada = datos || {};
      this.hablando = false;
      this.bloqueoPuerta = 0;
      this.puertaRechazada = null;
      this.dir = { x: 0, y: 1 };
      this.objetosCercanos = [];
      this.cercano = null;
    }

    texturaMapa() {
      return `mapa_${this.claveMapa}`;
    }

    texturaFrentes() {
      return `frentes_${this.claveMapa}`;
    }

    preload() {
      const mapa = AG.MAPAS[this.claveMapa];
      if (mapa && AG.hayMapa(this.claveMapa) && !this.textures.exists(this.texturaMapa())) {
        // Por AG.ASSETS, no por la ruta cruda: en el build de un archivo el mapa es un data URI.
        this.load.image(this.texturaMapa(), AG.ASSETS.mapa(this.claveMapa));
      }
      if (mapa && mapa.frentes && AG.hayFrentes(this.claveMapa) && !this.textures.exists(this.texturaFrentes())) {
        this.load.image(this.texturaFrentes(), AG.ASSETS.frentes(this.claveMapa));
      }
    }

    /** Lo que la escena hija agrega: un método propio (Pueblo.alUsar) o, si no, uno de `ajustes`. */
    gancho(nombre) {
      if (typeof this[nombre] === 'function') return this[nombre];
      return typeof this.ajustes[nombre] === 'function' ? this.ajustes[nombre] : null;
    }

    /**
     * Un punto del mapa en píxeles del mundo. Los mapas pintados dan `{px, py}` (el punto donde
     * algo toca el piso); los ASCII, `{x, y}` en tiles, y ahí el pie queda abajo al centro del tile.
     */
    aMundo(punto) {
      const { TILE } = AG.CFG;
      if (punto.px !== undefined) return { x: this.desfase.x + punto.px, y: this.desfase.y + punto.py };
      return { x: this.desfase.x + punto.x * TILE + TILE / 2, y: this.desfase.y + punto.y * TILE + TILE };
    }

    create() {
      const { VIEW_W, VIEW_H, TILE, COLORES } = AG.CFG;
      const mapa = AG.MAPAS[this.claveMapa];
      if (!mapa) {
        console.error('[Mundo] Falta el mapa', this.claveMapa);
        this.scene.start('Title');
        return;
      }
      this.mapa = mapa;
      this.anchoPx = mapa.ancho * TILE;
      this.altoPx = mapa.alto * TILE;
      this.desfase = {
        x: Math.max(0, (VIEW_W - this.anchoPx) / 2),
        y: Math.max(0, (VIEW_H - this.altoPx) / 2)
      };

      if (this.textures.exists(this.texturaMapa())) {
        this.capa = this.add.image(this.desfase.x, this.desfase.y, this.texturaMapa()).setOrigin(0);
      } else {
        this.add.rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.verde)).setOrigin(0);
      }
      this.crearFrentes();

      // Los mapas ASCII chocan por tile; los pintados, por celdas más finas (mapa.celda px).
      this.celda = mapa.celda || TILE;
      this.colisiones = mapa.colisiones.map((fila) => fila.split(''));
      this.solidoExtra = [];

      this.entrada = new AG.Entrada(this);
      this.dialogo = new AG.Dialogo(this, this.entrada);
      this.recuerdos = new AG.Recuerdos(this);

      this.crearObjetos();
      this.crearJugador();
      this.crearCamara();
      AG.FX.petalosAmbientales(this, this.ajustes.petalos || 1);

      if (this.ajustes.musica) AG.Musica.tocar(this.ajustes.musica);
      if (this.ajustes.velo) AG.FX.washAtardecer(this);

      this.cameras.main.fadeIn(280, 11, 10, 16);
      this.registrarVisita();

      if (this.ajustes.intro && AG.Guardado.visto(`intro.${this.claveMapa}`)) {
        this.dialogo.abrir(this.ajustes.intro);
      }
    }

    registrarVisita() {
      AG.Guardado.datos.escena = this.scene.key;
      AG.Guardado.guardar();
    }

    /* ---------------------------------------------------------------- mundo */

    /**
     * Los frentes: recortes de la pintura (copas, techos, postes) que se dibujan encima de Liss
     * solo cuando ella tiene los pies más arriba que la línea donde ese objeto toca el piso.
     * Es el mismo orden por profundidad que ya usan Liss y los NPCs (depth = y del pie).
     */
    crearFrentes() {
      this.frentes = [];
      const frentes = this.mapa.frentes;
      const clave = this.texturaFrentes();
      if (!frentes || !this.textures.exists(clave)) return;
      const textura = this.textures.get(clave);
      frentes.piezas.forEach((pieza, i) => {
        const cuadro = `f${i}`;
        if (!textura.has(cuadro)) textura.add(cuadro, 0, pieza.ax, pieza.ay, pieza.w, pieza.h);
        const x0 = this.desfase.x + pieza.x;
        const y0 = this.desfase.y + pieza.y;
        const imagen = this.add.image(x0, y0, clave, cuadro).setOrigin(0).setDepth(this.desfase.y + pieza.piso);
        this.frentes.push({ imagen, x0, y0, x1: x0 + pieza.w, y1: y0 + pieza.h, piso: this.desfase.y + pieza.piso });
      });
    }

    /**
     * Si Liss queda casi toda detrás de un frente (la copa del roble, un pino), ese frente se
     * vuelve a medias transparente para que se la vea. Debajo está la misma pintura, así que el
     * árbol no cambia: lo único que se transparenta es Liss.
     */
    actualizarFrentes() {
      if (!this.frentes || !this.frentes.length) return;
      const { x, y } = this.jugador;
      const caja = { x0: x - 6, x1: x + 6, y0: y - 30, y1: y };
      const area = 12 * 30;
      this.frentes.forEach((frente) => {
        let objetivo = 1;
        if (y < frente.piso) {
          const ancho = Math.min(caja.x1, frente.x1) - Math.max(caja.x0, frente.x0);
          const alto = Math.min(caja.y1, frente.y1) - Math.max(caja.y0, frente.y0);
          if (ancho > 0 && alto > 0 && ancho * alto > area * 0.6) objetivo = 0.5;
        }
        const alfa = frente.imagen.alpha;
        if (alfa !== objetivo) frente.imagen.setAlpha(Math.abs(objetivo - alfa) < 0.02 ? objetivo : alfa + (objetivo - alfa) * 0.2);
      });
    }

    crearJugador() {
      const { COLORES } = AG.CFG;
      const inicio = this.datosEntrada.inicio || this.mapa.inicio || this.ajustes.inicio || { x: 4, y: 4 };
      const { x, y } = this.lugarLibre(this.aMundo(inicio));

      if (AG.hayAtlas()) {
        this.jugador = this.add.sprite(x, y, 'arte', 'liss_idle_abajo_0').setOrigin(0.5, 1);
        this.jugador.setScale(AG.CFG.ESCALA_JUGADOR || 1);
      } else {
        this.jugador = this.add.rectangle(x, y, 12, 20, c(COLORES.rosa)).setOrigin(0.5, 1);
      }
      this.jugador.setDepth(y);
      this.crearAnimaciones();
    }

    crearAnimaciones() {
      AG.crearAnimacionesDeLiss(this);
    }

    crearObjetos() {
      const { TILE, COLORES } = AG.CFG;
      this.objetos = [];

      (this.mapa.objetos || []).forEach((dato) => {
        const { x, y } = this.aMundo(dato);
        // Un NPC ocupa lo que ocupan sus pies: en un mapa ASCII eso cae justo en su tile.
        if (dato.tipo === 'npc') this.bloquearCaja(x - 6, y - 7, x + 6, y);
        const esNpc = dato.tipo === 'npc';
        const esGuardado = dato.tipo === 'guardado';
        let visual = null;

        // Los NPCs son sprites del atlas; los objetos ya vienen pintados en el PNG del mapa
        // (así el mostrador de ocho tiles se ve como un mueble y no como ocho).
        if (AG.hayAtlas() && (esNpc || esGuardado)) {
          const frame = esGuardado ? 'ui_corazon' : `npc_${dato.id}_abajo_0`;
          if (this.textures.get('arte').has(frame)) {
            visual = this.add.sprite(x, y, 'arte', frame).setOrigin(0.5, 1).setDepth(y);
            if (esGuardado) visual.y -= 6;
            const respira = esNpc && AG.crearAnimacionDeNpc(this, dato.id);
            if (respira) visual.play(respira);
          }
        }
        if (!visual && esGuardado) {
          visual = AG.UI.corazon(this, x, y - 6, 1.5).setDepth(y);
        }
        if (!visual && !esNpc && !esGuardado && !(this.textures.exists(this.texturaMapa()))) {
          visual = this.add.rectangle(x, y - 8, 14, 14, c(COLORES.gris)).setDepth(y);
        }
        // En un mapa ASCII un NPC sin sprite lo pinta el PNG; en uno pintado nadie lo haría.
        if (!visual && esNpc && this.mapa.pintado) {
          visual = this.add.rectangle(x, y, 12, 24, c(COLORES.rosa)).setOrigin(0.5, 1).setDepth(y);
        }

        const objeto = {
          id: `${dato.tipo}_${x}_${y}`,
          nombre: dato.id,
          letra: dato.letra,
          tipo: dato.tipo,
          dialogo: dato.dialogo,
          x,
          y,
          visual
        };
        this.objetos.push(objeto);
      });

      // Cada puerta es una zona en píxeles del mundo: la de un mapa pintado viene medida; la de
      // uno ASCII es su tile, con 6 px de más abajo para que se pueda pisar desde el borde.
      this.puertas = (this.mapa.puertas || []).map((p) => {
        if (p.px !== undefined) {
          const x0 = this.desfase.x + p.px;
          const y0 = this.desfase.y + p.py;
          return { ...p, x0, y0, x1: x0 + p.ancho, y1: y0 + p.alto };
        }
        const x0 = this.desfase.x + p.x * TILE;
        const y0 = this.desfase.y + p.y * TILE;
        return { ...p, x0, y0, x1: x0 + TILE, y1: y0 + TILE + 6 };
      });
    }

    /** Marca como sólidas las celdas que toca la caja [x0, x1) × [y0, y1), en píxeles del mundo. */
    bloquearCaja(x0, y0, x1, y1) {
      const desde = { x: Math.floor((x0 - this.desfase.x) / this.celda), y: Math.floor((y0 - this.desfase.y) / this.celda) };
      const hasta = { x: Math.floor((x1 - 1 - this.desfase.x) / this.celda), y: Math.floor((y1 - 1 - this.desfase.y) / this.celda) };
      for (let cy = desde.y; cy <= hasta.y; cy += 1) {
        for (let cx = desde.x; cx <= hasta.x; cx += 1) {
          if (this.colisiones[cy] && this.colisiones[cy][cx] !== undefined) this.colisiones[cy][cx] = '1';
        }
      }
    }

    esSolido(px, py) {
      const cx = Math.floor((px - this.desfase.x) / this.celda);
      const cy = Math.floor((py - this.desfase.y) / this.celda);
      if (cy < 0 || cy >= this.colisiones.length || cx < 0 || cx >= this.colisiones[0].length) return true;
      return this.colisiones[cy][cx] === '1';
    }

    /**
     * El lugar libre más cercano a un punto, buscando en espiral. Un guardado viejo o un destino
     * mal medido nunca deberían dejar a Liss metida en un árbol sin poder moverse.
     */
    lugarLibre(punto) {
      if (!this.bloqueadoEn(punto.x, punto.y)) return punto;
      for (let radio = 2; radio <= 96; radio += 2) {
        const pasos = Math.max(8, Math.round(radio * 1.5));
        for (let i = 0; i < pasos; i += 1) {
          const angulo = (i / pasos) * Math.PI * 2;
          const x = Math.round(punto.x + Math.cos(angulo) * radio);
          const y = Math.round(punto.y + Math.sin(angulo) * radio);
          if (!this.bloqueadoEn(x, y)) return { x, y };
        }
      }
      console.warn('[Mundo] No encontré un lugar libre cerca de', punto);
      return punto;
    }

    crearCamara() {
      const { VIEW_W, VIEW_H } = AG.CFG;
      const camara = this.cameras.main;
      camara.setBounds(0, 0, Math.max(this.anchoPx, VIEW_W), Math.max(this.altoPx, VIEW_H));
      if (this.anchoPx > VIEW_W || this.altoPx > VIEW_H) {
        camara.startFollow(this.jugador, true, 0.14, 0.14);
        camara.setDeadzone(80, 60);
      } else {
        camara.centerOn(VIEW_W / 2, VIEW_H / 2);
      }
    }

    /* ------------------------------------------------------------ interacción */

    objetoCercano() {
      const alcance = 22;
      let mejor = null;
      let mejorDistancia = alcance;
      this.objetos.forEach((objeto) => {
        const distancia = Phaser.Math.Distance.Between(this.jugador.x, this.jugador.y - 8, objeto.x, objeto.y - 6);
        if (distancia < mejorDistancia) {
          mejor = objeto;
          mejorDistancia = distancia;
        }
      });
      return mejor;
    }

    usarObjeto(objeto) {
      if (objeto.tipo === 'guardado') {
        AG.Guardado.registrarPos(
          this.scene.key,
          Math.round(this.jugador.x - this.desfase.x),
          Math.round(this.jugador.y - this.desfase.y)
        );
        AG.Musica.sfx('corazon');
        AG.FX.latido(this);
        this.dialogo.abrir('sistema.guardado');
        return;
      }
      if (!objeto.dialogo) return;
      let clave = objeto.dialogo;
      const charlas = AG.Guardado.charla(clave);
      const alUsar = this.gancho('alUsar');
      if (alUsar) clave = alUsar.call(this, objeto, clave, charlas) || clave;
      if (objeto.tipo === 'npc') this.mirarHacia(objeto);
      this.dialogo.abrir(clave, { charla: charlas });
    }

    mirarHacia(objeto) {
      if (Math.abs(objeto.x - this.jugador.x) > Math.abs(objeto.y - this.jugador.y)) {
        this.dir = { x: Math.sign(objeto.x - this.jugador.x), y: 0 };
      } else {
        this.dir = { x: 0, y: Math.sign(objeto.y - this.jugador.y) };
      }
      this.animarQuieto();
    }

    animarCaminando() {
      if (!AG.hayAtlas() || !this.jugador.play) return;
      const dir = AG.direccionDibujable(this, this.dir);
      if (this.anims.exists(`liss_camina_${dir}`)) this.jugador.play(`liss_camina_${dir}`, true);
    }

    animarQuieto() {
      if (!AG.hayAtlas() || !this.jugador.setFrame) return;
      const dir = AG.direccionDibujable(this, this.dir);
      if (this.anims.exists(`liss_idle_${dir}`)) this.jugador.play(`liss_idle_${dir}`, true);
      else this.jugador.setFrame(`liss_idle_${dir}_0`);
    }

    /* --------------------------------------------------------------- update */

    update(tiempo, delta) {
      if (!this.jugador) return;
      this.dialogo.actualizar(delta);
      if (this.dialogo.activo() || this.recuerdos.activo()) {
        this.recuerdos.actualizar();
        this.detenerAndar();
        return;
      }
      this.recuerdos.actualizar();
      this.mover(delta);
      this.actualizarFrentes();
      this.revisarPuertas(delta);
      this.resaltarCercano();
      if (this.entrada.accion()) {
        const objeto = this.objetoCercano();
        if (objeto) this.usarObjeto(objeto);
      }
    }

    detenerAndar() {
      if (this.andando) {
        this.andando = false;
        this.animarQuieto();
      }
    }

    mover(delta) {
      const dir = this.entrada.direccion();
      const segundos = delta / 1000;
      // En diagonal se reparte el paso entre los dos ejes: si no, Liss corre más al sesgo.
      const diagonal = dir.x && dir.y ? Math.SQRT1_2 : 1;
      const paso = AG.CFG.VELOCIDAD * segundos * diagonal;
      let anduvo = false;

      if (dir.x || dir.y) {
        this.dir = dir;
        const nuevoX = this.jugador.x + dir.x * paso;
        const nuevoY = this.jugador.y + dir.y * paso;
        if (!this.bloqueadoEn(nuevoX, this.jugador.y)) {
          this.jugador.x = nuevoX;
          anduvo = anduvo || Boolean(dir.x);
        }
        if (!this.bloqueadoEn(this.jugador.x, nuevoY)) {
          this.jugador.y = nuevoY;
          anduvo = anduvo || Boolean(dir.y);
        }
        this.jugador.setDepth(this.jugador.y);
      }

      if (anduvo) {
        this.andando = true;
        this.animarCaminando();
        this.contadorPasos = (this.contadorPasos || 0) + delta;
        if (this.contadorPasos > 340) {
          this.contadorPasos = 0;
          AG.Musica.sfx('paso');
        }
      } else {
        this.detenerAndar();
      }
    }

    /**
     * ¿La caja de los pies de Liss (10 × 4 px) toca algo sólido si pisa (px, py)?
     * Se mira en puntos separados a lo sumo una celda, así un poste de una celda de ancho no
     * se le cuela entre dos esquinas.
     */
    bloqueadoEn(px, py) {
      const ancho = 5;
      const alto = 4;
      const paso = Math.min(4, this.celda || AG.CFG.TILE);
      for (let x = px - ancho; ; x = Math.min(x + paso, px + ancho)) {
        if (this.esSolido(x, py - alto) || this.esSolido(x, py - 1)) return true;
        if (x >= px + ancho) return false;
      }
    }

    revisarPuertas(delta) {
      this.bloqueoPuerta = Math.max(0, this.bloqueoPuerta - delta);
      if (this.bloqueoPuerta > 0) return;
      const { x, y } = this.jugador;
      const puerta = this.puertas.find((p) => x > p.x0 && x < p.x1 && y > p.y0 && y < p.y1);
      if (!puerta) {
        this.puertaRechazada = null;
        return;
      }
      // Una puerta que dijo que no (la colina sin la tercera flor) no insiste hasta que Liss salga
      // de su zona: si no, el aviso se abriría otra vez apenas se cierra.
      if (puerta === this.puertaRechazada) return;
      const antesDePuerta = this.gancho('antesDePuerta');
      if (antesDePuerta && !antesDePuerta.call(this, puerta)) {
        this.puertaRechazada = puerta;
        return;
      }
      this.bloqueoPuerta = 900;
      AG.Musica.sfx('puerta');
      AG.FX.fundir(this, () =>
        this.scene.start(puerta.a, { inicio: puerta.destino, desde: this.claveMapa })
      );
    }

    resaltarCercano() {
      const objeto = this.objetoCercano();
      if (objeto === this.cercano) return;
      if (this.cercano && this.cercano.globo) {
        this.cercano.globo.destroy();
        this.cercano.globo = null;
      }
      this.cercano = objeto;
      if (!objeto) return;
      // Por encima de todo el mundo (también de las copas de los árboles) y debajo del diálogo.
      const globo = AG.UI.texto(this, objeto.x + 12, objeto.y - 30, '!', { color: AG.CFG.COLORES.amarillo })
        .setOrigin(0.5)
        .setDepth(650);
      this.tweens.add({ targets: globo, y: objeto.y - 34, duration: 420, yoyo: true, repeat: -1 });
      objeto.globo = globo;
    }
  };
})();
