window.AG = window.AG || {};

AG.Floreria = class Floreria extends AG.Mundo {
  constructor() {
    super({
      clave: 'Floreria',
      mapa: 'floreria',
      musica: 'pueblo',
      inicio: { x: 7, y: 10 },
      petalos: 0
    });
  }

  /** Doña Flora entrega la primera flor; antes de eso, manda a juntar pétalos. */
  alUsar(objeto, clave) {
    if (objeto.tipo !== 'npc') return clave;
    if (!AG.Guardado.datos.visto['petalos1.listo']) return 'pueblo.flora.saludo';
    if (!AG.Guardado.tieneFlor(1)) return 'pueblo.flora.post';
    return 'pueblo.flora.gracias';
  }
};
