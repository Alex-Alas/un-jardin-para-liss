window.AG = window.AG || {};

AG.Casa = class Casa extends AG.Mundo {
  constructor() {
    super({
      clave: 'Casa',
      mapa: 'casa',
      musica: 'casa',
      intro: 'casa.despertar',
      petalos: 0
    });
  }
};
