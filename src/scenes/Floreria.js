window.AG = window.AG || {};

AG.Floreria = class Floreria extends AG.Mundo {
  constructor() {
    super({
      clave: 'Floreria',
      mapa: 'floreria',
      musica: 'floreria',
      inicio: { px: 155, py: 210 },
      petalos: 0
    });
  }

  /** Doña Flora da la última flor, con la ronda del parque; antes manda a Liss con Beto o con Sofi. */
  alUsar(objeto, clave) {
    if (objeto.tipo !== 'npc') return clave;
    if (!AG.Guardado.tieneFlorDe('beto')) return 'pueblo.flora.beto';
    if (!AG.Guardado.tieneFlorDe('sofi')) return 'pueblo.flora.sofi';
    if (!AG.Guardado.tieneFlorDe('flora')) return 'pueblo.flora.saludo';
    return 'pueblo.flora.gracias';
  }
};
