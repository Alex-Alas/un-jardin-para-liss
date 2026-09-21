window.AG = window.AG || {};

AG.ASSETS = {
  atlas: 'assets/atlas.png',
  atlasDatos: 'assets/atlas.json',
  fuentePng: 'assets/font_pixel.png',
  fuenteDatos: 'assets/font_pixel.xml',
  mapas: {
    casa: 'assets/mapa_casa.png',
    pueblo: 'assets/mapa_pueblo.png',
    floreria: 'assets/mapa_floreria.png',
    parque: 'assets/mapa_parque.png',
    colina: 'assets/mapa_colina.png'
  },
  fotos: {}
};

AG.requiereAssets = function () {
  return AG.ASSETS_READY === true;
};
