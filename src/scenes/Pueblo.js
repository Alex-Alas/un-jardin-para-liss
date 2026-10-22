window.AG = window.AG || {};

AG.Pueblo = class Pueblo extends AG.Mundo {
  constructor() {
    super({
      clave: 'Pueblo',
      mapa: 'pueblo',
      musica: 'pueblo',
      intro: 'casa.salir',
      petalos: 2
    });
  }

  /** Al salir de su casa sin la flor de Don Beto, él la llama desde la plaza. */
  alLlegar() {
    if (this.datosEntrada.desde !== 'casa' || AG.Guardado.tieneFlorDe('beto')) return;
    const beto = this.objetos.find((objeto) => objeto.nombre === 'beto');
    const globo = beto && AG.UI.texto(this, beto.x, beto.y - 40, '!', { color: AG.CFG.COLORES.amarillo })
      .setOrigin(0.5)
      .setDepth(650);
    if (globo) this.tweens.add({ targets: globo, y: globo.y - 4, duration: 300, yoyo: true, repeat: -1 });
    this.dialogo.abrir('pueblo.beto.llamado', { alCerrar: () => globo && globo.destroy() });
  }

  /**
   * Una flor de cada uno, en orden: Don Beto, Sofi (la ronda tranquila) y Doña Flora (la del
   * viento). Quien todavía no le toca manda a Liss con quien sí.
   */
  alUsar(objeto, clave) {
    const flor = (quien) => AG.Guardado.tieneFlorDe(quien);
    if (objeto.nombre === 'beto') {
      if (!flor('beto')) return 'pueblo.beto.saludo';
      if (AG.Guardado.visto('pueblo.beto.chisme')) return 'pueblo.beto.chisme';
      if (!flor('sofi')) return 'pueblo.beto.pista.sofi';
      if (!flor('flora')) return 'pueblo.beto.pista.flora';
      return 'pueblo.beto.pista.colina';
    }
    if (objeto.nombre === 'sofi') {
      if (!flor('beto')) return 'pueblo.sofi.antes';
      if (!flor('sofi')) return 'pueblo.sofi.saludo';
      if (!flor('flora')) return 'pueblo.sofi.gracias';
      return 'pueblo.sofi.final';
    }
    return clave;
  }

  antesDePuerta(puerta) {
    if (puerta.a === 'Colina' && !AG.Guardado.tieneTodasLasFlores()) {
      this.dialogo.abrir('pueblo.colina.bloqueada');
      return false;
    }
    return true;
  }
};
