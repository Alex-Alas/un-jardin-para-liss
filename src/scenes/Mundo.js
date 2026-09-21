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
      this.dir = { x: 0, y: 1 };
      this.objetosCercanos = [];
      this.cercano = null;
    }

    texturaMapa() {
      return `mapa_${this.claveMapa}`;
    }

    preload() {
      const mapa = AG.MAPAS[this.claveMapa];
      if (mapa && AG.hayMapa(this.claveMapa) && !this.textures.exists(this.texturaMapa())) {
        this.load.image(this.texturaMapa(), mapa.imagen);
      }
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

    crearJugador() {
      const { TILE, COLORES } = AG.CFG;
      const inicio = this.datosEntrada.inicio || this.ajustes.inicio || { x: 4, y: 4 };
      const x = this.desfase.x + inicio.x * TILE + TILE / 2;
      const y = this.desfase.y + inicio.y * TILE + TILE;

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
      if (!AG.hayAtlas()) return;
      ['abajo', 'arriba', 'izquierda', 'derecha'].forEach((dir) => {
        const clave = `liss_camina_${dir}`;
        if (this.anims.exists(clave)) return;
        this.anims.create({
          key: clave,
          frames: [
            { key: 'arte', frame: `liss_camina_${dir}_0` },
            { key: 'arte', frame: `liss_camina_${dir}_1` }
          ],
          frameRate: 7,
          repeat: -1
        });
      });
    }

    crearObjetos() {
      const { TILE, COLORES } = AG.CFG;
      this.objetos = [];

      (this.mapa.objetos || []).forEach((dato) => {
        if (dato.tipo === 'npc') this.bloquear(dato.x, dato.y);
        const x = this.desfase.x + dato.x * TILE + TILE / 2;
        const y = this.desfase.y + dato.y * TILE + TILE;
        const esNpc = dato.tipo === 'npc';
        const esGuardado = dato.tipo === 'guardado';
        let visual = null;

        if (AG.hayAtlas()) {
          const frame = esGuardado ? 'ui_corazon' : `npc_${dato.id || dato.tipo}_abajo_0`;
          if (this.textures.get('arte').has(frame)) {
            visual = this.add.sprite(x, y, 'arte', frame).setOrigin(0.5, 1).setDepth(y);
            if (esNpc && this.anims.exists(`caminar_${dato.id}`)) visual.play(`caminar_${dato.id}`);
          }
        }
        if (!visual && esGuardado) {
          visual = AG.UI.corazon(this, x, y - 6, 1.5).setDepth(y);
        }
        if (!visual && !esNpc && !esGuardado && !(this.textures.exists(this.texturaMapa()))) {
          visual = this.add.rectangle(x, y - 8, 14, 14, c(COLORES.gris)).setDepth(y);
        }

        const objeto = {
          id: `${dato.tipo}_${dato.x}_${dato.y}`,
          letra: dato.letra,
          tipo: dato.tipo,
          dialogo: dato.dialogo,
          x,
          y,
          visual
        };
        this.objetos.push(objeto);
      });

      this.puertas = (this.mapa.puertas || []).map((p) => ({
        ...p,
        px: this.desfase.x + p.x * AG.CFG.TILE,
        py: this.desfase.y + p.y * AG.CFG.TILE
      }));
    }

    bloquear(tx, ty) {
      if (this.colisiones[ty] && this.colisiones[ty][tx] !== undefined) this.colisiones[ty][tx] = '1';
    }

    esSolido(px, py) {
      const { TILE } = AG.CFG;
      const tx = Math.floor((px - this.desfase.x) / TILE);
      const ty = Math.floor((py - this.desfase.y) / TILE);
      if (ty < 0 || ty >= this.mapa.alto || tx < 0 || tx >= this.mapa.ancho) return true;
      return this.colisiones[ty][tx] === '1';
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
          Math.floor((this.jugador.x - this.desfase.x) / AG.CFG.TILE),
          Math.floor((this.jugador.y - this.desfase.y) / AG.CFG.TILE)
        );
        AG.Musica.sfx('corazon');
        AG.FX.latido(this);
        this.dialogo.abrir('sistema.guardado');
        return;
      }
      if (!objeto.dialogo) return;
      let clave = objeto.dialogo;
      const charlas = AG.Guardado.charla(clave);
      if (this.ajustes.alUsar) clave = this.ajustes.alUsar.call(this, objeto, clave, charlas) || clave;
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
      const dir = this.dir.y < 0 ? 'arriba' : this.dir.y > 0 ? 'abajo' : this.dir.x < 0 ? 'izquierda' : 'derecha';
      this.jugador.play(`liss_camina_${dir}`, true);
    }

    animarQuieto() {
      if (!AG.hayAtlas() || !this.jugador.setFrame) return;
      const dir = this.dir.y < 0 ? 'arriba' : this.dir.y > 0 ? 'abajo' : this.dir.x < 0 ? 'izquierda' : 'derecha';
      this.jugador.stop();
      this.jugador.setFrame(`liss_idle_${dir}_0`);
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
      const paso = AG.CFG.VELOCIDAD * segundos;
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

    bloqueadoEn(px, py) {
      const ancho = 5;
      const alto = 4;
      const puntos = [
        [px - ancho, py - alto],
        [px + ancho, py - alto],
        [px - ancho, py - 1],
        [px + ancho, py - 1]
      ];
      return puntos.some(([x, y]) => this.esSolido(x, y));
    }

    revisarPuertas(delta) {
      this.bloqueoPuerta = Math.max(0, this.bloqueoPuerta - delta);
      if (this.bloqueoPuerta > 0) return;
      const puerta = this.puertas.find(
        (p) =>
          this.jugador.x > p.px &&
          this.jugador.x < p.px + AG.CFG.TILE &&
          this.jugador.y > p.py &&
          this.jugador.y < p.py + AG.CFG.TILE + 6
      );
      if (!puerta) return;
      if (this.ajustes.antesDePuerta && !this.ajustes.antesDePuerta.call(this, puerta)) return;
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
      const globo = AG.UI.texto(this, objeto.x + 12, objeto.y - 30, '!', { color: AG.CFG.COLORES.amarillo })
        .setOrigin(0.5)
        .setDepth(objeto.y + 1);
      this.tweens.add({ targets: globo, y: objeto.y - 34, duration: 420, yoyo: true, repeat: -1 });
      objeto.globo = globo;
    }
  };
})();
