window.AG = window.AG || {};

AG.Casa = class Casa extends AG.Mundo {
  constructor() {
    super({
      clave: 'Casa',
      mapa: 'casa',
      musica: 'pueblo',
      intro: 'casa.despertar',
      petalos: 0
    });
  }
};
