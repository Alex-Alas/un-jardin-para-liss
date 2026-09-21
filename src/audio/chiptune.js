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

  AG.Musica = {
    ctx: null,
    maestro: null,
    tema: null,
    temaPendiente: null,
    paso: 0,
    proximo: 0,
    temporizador: null,
    desbloqueado: false,
    volumen: 0.22,

    desbloquear() {
      if (!this.ctx) {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return false;
        this.ctx = new Ctx();
        this.maestro = this.ctx.createGain();
        this.maestro.gain.value = this.volumen;
        this.maestro.connect(this.ctx.destination);
      }
      if (this.ctx.state === 'suspended') this.ctx.resume();
      this.desbloqueado = true;
      if (this.temaPendiente) {
        const pendiente = this.temaPendiente;
        this.temaPendiente = null;
        this.tocar(pendiente);
      }
      return true;
    },

    tocar(clave) {
      const tema = TEMAS[clave];
      if (!tema) return;
      if (!this.desbloqueado) {
        this.temaPendiente = clave;
        return;
      }
      if (this.tema === clave) return;
      this.parar();
      this.tema = clave;
      this.paso = 0;
      this.proximo = this.ctx.currentTime + 0.08;
      this.temporizador = window.setInterval(() => this.planificar(), 60);
    },

    parar() {
      if (this.temporizador) window.clearInterval(this.temporizador);
      this.temporizador = null;
      this.tema = null;
    },

    /** Programa las notas que caen dentro de la ventana de anticipación. */
    planificar() {
      if (!this.ctx || !this.tema) return;
      const tema = TEMAS[this.tema];
      while (this.proximo < this.ctx.currentTime + 0.3) {
        const i = this.paso % tema.melodia.length;
        const nota = tema.melodia[i];
        const bajo = tema.bajo[i % tema.bajo.length];
        if (nota) this.suena(nota, this.proximo, tema.paso * 0.9, 'triangle', 0.16);
        if (bajo) this.suena(bajo, this.proximo, tema.paso * 1.6, 'square', 0.1);
        this.proximo += tema.paso;
        this.paso += 1;
      }
    },

    suena(nota, tiempo, duracion, tipo, ganancia) {
      const osc = this.ctx.createOscillator();
      const vol = this.ctx.createGain();
      osc.type = tipo;
      osc.frequency.value = frecuencia(nota);
      vol.gain.setValueAtTime(0.0001, tiempo);
      vol.gain.linearRampToValueAtTime(ganancia, tiempo + 0.012);
      vol.gain.exponentialRampToValueAtTime(0.0001, tiempo + duracion);
      osc.connect(vol);
      vol.connect(this.maestro);
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
      vol.connect(this.maestro);
      osc.start(t);
      osc.stop(t + duracion + 0.02);
    }
  };
})();
