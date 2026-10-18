window.AG = window.AG || {};

(function () {
  const SEMITONOS = { C: 0, 'C#': 1, D: 2, 'D#': 3, E: 4, F: 5, 'F#': 6, G: 7, 'G#': 8, A: 9, 'A#': 10, B: 11 };

  function frecuencia(nombre) {
    const partes = /^([A-G]#?)(\d)$/.exec(nombre);
    if (!partes) return 0;
    const semis = SEMITONOS[partes[1]] + (Number.parseInt(partes[2], 10) + 1) * 12;
    return 440 * Math.pow(2, (semis - 69) / 12);
  }

  const TEMAS = {
    pueblo: {
      paso: 0.34,
      melodia: ['C5', null, 'E5', null, 'G5', null, 'E5', null, 'A4', null, 'C5', null, 'E5', null, 'C5', null,
                'F4', null, 'A4', null, 'C5', null, 'A4', null, 'G4', null, 'B4', null, 'D5', null, 'B4', null],
      bajo: ['C3', null, null, null, 'A2', null, null, null, 'F2', null, null, null, 'G2', null, null, null]
    },
    petalos: {
      paso: 0.17,
      melodia: ['G5', 'A5', 'B5', 'D6', null, 'B5', 'A5', 'G5', 'E5', 'G5', 'B5', 'G5', 'A5', 'G5', 'E5', 'D5'],
      bajo: ['G2', null, 'G2', null, 'E2', null, 'E2', null, 'C2', null, 'C2', null, 'D2', null, 'D2', null]
    },
    final: {
      paso: 0.52,
      melodia: ['C5', null, 'E5', null, 'G5', null, null, null, 'A4', null, 'C5', null, 'E5', null, null, null,
                'F4', null, 'A4', null, 'C5', null, null, null, 'G4', null, 'B4', null, 'D5', null, null, null],
      bajo: ['C3', null, null, null, 'A2', null, null, null, 'F2', null, null, null, 'G2', null, null, null]
    },
    titulo: {
      paso: 0.42,
      melodia: ['E5', null, 'G5', null, 'A5', null, 'G5', null, 'E5', null, null, null, 'D5', null, 'E5', null,
                'C5', null, 'E5', null, 'G5', null, 'E5', null, 'A4', null, 'B4', null, 'C5', null, null, null],
      bajo: ['A2', null, null, null, 'E2', null, null, null, 'F2', null, null, null, 'C3', null, null, null]
    }
  };

  /**
   * Las pistas grabadas (assets/musica/, las arma tools/preparar_musica.py): qué archivo suena con
   * cada tema. La casa y la florería comparten la de interiores, y el título y el álbum suenan con
   * la de los créditos, así el juego termina con la misma canción con la que empezó.
   */
  const PISTAS = {
    titulo: 'creditos',
    casa: 'interiores',
    floreria: 'interiores',
    pueblo: 'pueblo',
    petalos1: 'petalos1',
    petalos2: 'petalos2',
    colina: 'colina',
    final: 'final',
    creditos: 'creditos'
  };

  /** Si una pista falta o el navegador no la puede leer (index.html abierto desde el disco), suena este chiptune. */
  const RESPALDO = {
    casa: 'pueblo',
    floreria: 'pueblo',
    colina: 'pueblo',
    petalos1: 'petalos',
    petalos2: 'petalos',
    creditos: 'final'
  };

  // Las pistas llegan a -16 LUFS y acá quedan a ~-22. El chiptune y los efectos se escribieron con
  // ganancias chiquitas: se suben para que los blips del diálogo se oigan encima de una pista.
  const VOLUMEN = { pistas: 0.5, chiptune: 1.6, efectos: 2 };
  const FUNDIDO = { entrada: 1.2, salida: 0.7 };
  // Una pista decodificada ocupa ~65 MB: se guardan la que suena y la anterior (pueblo ↔ florería).
  const DECODIFICADAS = 2;

  /** decodeAudioData como promesa, también en los Safari viejos que solo aceptan callbacks. */
  function decodificarAudio(ctx, bytes) {
    return new Promise((resolver, rechazar) => {
      const promesa = ctx.decodeAudioData(bytes, resolver, rechazar);
      if (promesa && promesa.then) promesa.then(resolver, rechazar);
    });
  }

  /** resume() y suspend() rechazan si el navegador todavía no deja: no es un error, se reintenta. */
  function sinQueja(promesa) {
    if (promesa && promesa.catch) promesa.catch(() => {});
  }

  AG.Musica = {
    ctx: null,
    buses: null,
    tema: null,
    temaPendiente: null,
    chip: null,
    paso: 0,
    proximo: 0,
    temporizador: null,
    desbloqueado: false,
    sonando: null,
    pedido: 0,
    posiciones: {},
    bytes: new Map(),
    buffers: new Map(),
    fallidas: new Set(),
    precargando: false,

    desbloquear() {
      if (!this.ctx) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return false;
        this.ctx = new Ctx();
        // Limitador al final: un efecto encima del pico de una pista no satura.
        const limitador = this.ctx.createDynamicsCompressor();
        limitador.threshold.value = -4;
        limitador.knee.value = 4;
        limitador.ratio.value = 12;
        limitador.attack.value = 0.003;
        limitador.release.value = 0.25;
        limitador.connect(this.ctx.destination);
        this.buses = {};
        Object.keys(VOLUMEN).forEach((nombre) => {
          const bus = this.ctx.createGain();
          bus.gain.value = VOLUMEN[nombre];
          bus.connect(limitador);
          this.buses[nombre] = bus;
        });
        this.vigilarPestana();
      }
      if (this.ctx.state !== 'running') sinQueja(this.ctx.resume());
      this.desbloqueado = true;
      if (this.temaPendiente) {
        const pendiente = this.temaPendiente;
        this.temaPendiente = null;
        this.tocar(pendiente);
      }
      return true;
    },

    /**
     * Con la pestaña escondida la música se pausa y vuelve al volver. Si el navegador pide un gesto
     * para reanudar (iOS después de una llamada), vuelve con el próximo toque.
     */
    vigilarPestana() {
      const reanudar = () => {
        if (!document.hidden && this.ctx.state !== 'running') sinQueja(this.ctx.resume());
      };
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) sinQueja(this.ctx.suspend());
        else reanudar();
      });
      ['pointerdown', 'touchend', 'keydown'].forEach((evento) => document.addEventListener(evento, reanudar, true));
    },

    tocar(clave) {
      if (!TEMAS[clave] && !PISTAS[clave]) return;
      const archivo = this.archivoDe(clave);
      if (archivo) this.descargar(archivo); // la descarga no espera al primer toque
      if (!this.desbloqueado) {
        this.temaPendiente = clave;
        return;
      }
      if (this.tema === clave) return;
      this.tema = clave;
      if (archivo) this.ponerPista(clave, archivo);
      else this.ponerChiptune(clave);
    },

    archivoDe(clave) {
      const archivo = PISTAS[clave];
      return archivo && AG.hayMusica(archivo) && !this.fallidas.has(archivo) ? archivo : null;
    },

    parar() {
      this.pedido += 1;
      this.soltarPista();
      this.pararChiptune();
      this.tema = null;
    },

    ponerPista(clave, archivo) {
      this.pararChiptune();
      if (this.sonando && this.sonando.archivo === archivo) return; // de la casa a la florería sigue la misma
      this.soltarPista();
      const pedido = (this.pedido += 1);
      this.decodificar(archivo)
        .then((buffer) => {
          if (pedido === this.pedido) this.arrancarPista(archivo, buffer);
        })
        .catch((error) => {
          console.warn(`[Musica] No se pudo cargar ${archivo}.mp3: suena el chiptune.`, error);
          this.fallidas.add(archivo);
          if (pedido === this.pedido) this.ponerChiptune(clave);
        });
    },

    /** Arranca donde se había quedado: volver al pueblo no lo empieza de cero cada vez. */
    arrancarPista(archivo, buffer) {
      const t = this.ctx.currentTime;
      const fuente = this.ctx.createBufferSource();
      const vol = this.ctx.createGain();
      fuente.buffer = buffer;
      fuente.loop = true;
      vol.gain.setValueAtTime(0, t);
      vol.gain.linearRampToValueAtTime(1, t + FUNDIDO.entrada);
      fuente.connect(vol);
      vol.connect(this.buses.pistas);
      const desde = (this.posiciones[archivo] || 0) % buffer.duration;
      fuente.start(t, desde);
      this.sonando = { archivo, fuente, vol, inicio: t - desde, duracion: buffer.duration };
      this.precargarTodo();
    },

    soltarPista() {
      const pista = this.sonando;
      if (!pista) return;
      this.sonando = null;
      const t = this.ctx.currentTime;
      this.posiciones[pista.archivo] = (t - pista.inicio) % pista.duracion;
      pista.vol.gain.cancelScheduledValues(t);
      pista.vol.gain.setValueAtTime(pista.vol.gain.value, t);
      pista.vol.gain.linearRampToValueAtTime(0, t + FUNDIDO.salida);
      pista.fuente.stop(t + FUNDIDO.salida + 0.05);
    },

    descargar(archivo) {
      if (!this.bytes.has(archivo)) {
        const promesa = fetch(AG.ASSETS.musica(archivo)).then((respuesta) => {
          if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
          return respuesta.arrayBuffer();
        });
        sinQueja(promesa); // el error lo atiende quien la decodifica
        this.bytes.set(archivo, promesa);
      }
      return this.bytes.get(archivo);
    },

    decodificar(archivo) {
      let promesa = this.buffers.get(archivo);
      if (promesa) {
        this.buffers.delete(archivo); // vuelve al final de la fila: es la más reciente
      } else {
        // slice: decodeAudioData se queda con los bytes, y la copia descargada sirve para otra vez.
        promesa = this.descargar(archivo).then((bytes) => decodificarAudio(this.ctx, bytes.slice(0)));
      }
      this.buffers.set(archivo, promesa);
      while (this.buffers.size > DECODIFICADAS) this.buffers.delete(this.buffers.keys().next().value);
      return promesa;
    },

    /** Con la primera pista sonando se bajan las demás, de a una: los cambios de escena no esperan a la red. */
    precargarTodo() {
      if (this.precargando) return;
      this.precargando = true;
      const archivos = [...new Set(Object.values(PISTAS))].filter((archivo) => AG.hayMusica(archivo));
      archivos.reduce((cadena, archivo) => cadena.then(() => this.descargar(archivo)).catch(() => {}), Promise.resolve());
    },

    ponerChiptune(clave) {
      const tema = TEMAS[clave] ? clave : RESPALDO[clave];
      this.pedido += 1;
      this.soltarPista();
      if (this.chip === tema) return;
      this.pararChiptune();
      this.chip = tema;
      this.paso = 0;
      this.proximo = this.ctx.currentTime + 0.08;
      this.temporizador = window.setInterval(() => this.planificar(), 60);
    },

    pararChiptune() {
      if (this.temporizador) window.clearInterval(this.temporizador);
      this.temporizador = null;
      this.chip = null;
    },

    /** Programa las notas que caen dentro de la ventana de anticipación. */
    planificar() {
      if (!this.ctx || !this.chip) return;
      const tema = TEMAS[this.chip];
      while (this.proximo < this.ctx.currentTime + 0.3) {
        const i = this.paso % tema.melodia.length;
        const nota = tema.melodia[i];
        const bajo = tema.bajo[i % tema.bajo.length];
        if (nota) this.suena(nota, this.proximo, tema.paso * 0.9, 'triangle', 0.16, this.buses.chiptune);
        if (bajo) this.suena(bajo, this.proximo, tema.paso * 1.6, 'square', 0.1, this.buses.chiptune);
        this.proximo += tema.paso;
        this.paso += 1;
      }
    },

    suena(nota, tiempo, duracion, tipo, ganancia, bus = this.buses.efectos) {
      const osc = this.ctx.createOscillator();
      const vol = this.ctx.createGain();
      osc.type = tipo;
      osc.frequency.value = frecuencia(nota);
      vol.gain.setValueAtTime(0.0001, tiempo);
      vol.gain.linearRampToValueAtTime(ganancia, tiempo + 0.012);
      vol.gain.exponentialRampToValueAtTime(0.0001, tiempo + duracion);
      osc.connect(vol);
      vol.connect(bus);
      osc.start(tiempo);
      osc.stop(tiempo + duracion + 0.03);
    },

    sfx(nombre, extra = 0) {
      if (!this.desbloqueado || !this.ctx) return;
      const t = this.ctx.currentTime;
      const casos = {
        blip: () => this.pulso('square', 620, 0.035, 0.05),
        paso: () => this.pulso('triangle', 120, 0.05, 0.04),
        puerta: () => {
          this.pulso('square', 320, 0.07, 0.06);
          this.suena('F4', t + 0.07, 0.12, 'square', 0.05);
        },
        flor: () => ['C5', 'E5', 'G5', 'C6'].forEach((n, i) => this.suena(n, t + i * 0.07, 0.18, 'triangle', 0.09)),
        recuerdo: () => {
          this.suena('A4', t, 0.25, 'triangle', 0.09);
          this.suena('E5', t + 0.14, 0.35, 'triangle', 0.08);
        },
        petalo: () => this.pulso('square', 880 + Math.min(extra, 8) * 60, 0.05, 0.05),
        corazon: () => {
          this.suena('C5', t, 0.16, 'triangle', 0.08);
          this.suena('E5', t + 0.12, 0.3, 'triangle', 0.07);
        },
        error: () => this.pulso('square', 150, 0.16, 0.05)
      };
      (casos[nombre] || (() => {}))();
    },

    pulso(tipo, hz, duracion, ganancia) {
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const vol = this.ctx.createGain();
      osc.type = tipo;
      osc.frequency.value = hz;
      vol.gain.setValueAtTime(ganancia, t);
      vol.gain.exponentialRampToValueAtTime(0.0001, t + duracion);
      osc.connect(vol);
      vol.connect(this.buses.efectos);
      osc.start(t);
      osc.stop(t + duracion + 0.02);
    }
  };
})();
