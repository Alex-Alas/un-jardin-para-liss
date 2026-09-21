window.AG = window.AG || {};

AG.Casa = class Casa extends AG.Mundo {
  constructor() {
    super({
      clave: 'Casa',
      mapa: 'casa',
      musica: 'pueblo',
      inicio: { x: 9, y: 11 },
      intro: 'casa.despertar',
      petalos: 0
    });
  }
};
