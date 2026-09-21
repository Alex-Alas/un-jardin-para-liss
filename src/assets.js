window.AG = window.AG || {};

AG.MANIFIESTO = AG.MANIFIESTO || { fuente: false, atlas: false, mapas: [], fotos: [] };

AG.ASSETS = {
  atlas: 'assets/atlas.png',
  atlasDatos: 'assets/atlas.json',
  fuentes: {
    pixel8: { png: 'assets/font_pixel8.png', xml: 'assets/font_pixel8.xml' },
    pixel16: { png: 'assets/font_pixel16.png', xml: 'assets/font_pixel16.xml' }
  },
  mapa: (clave) => `assets/mapa_${clave}.png`,
  foto: (id) => `assets/fotos/recuerdo_${id}.jpg`
};

AG.hayFuente = () => AG.MANIFIESTO.fuente === true;
AG.hayAtlas = () => AG.MANIFIESTO.atlas === true;
AG.hayMapa = (clave) => (AG.MANIFIESTO.mapas || []).indexOf(clave) !== -1;
AG.hayFoto = (id) => (AG.MANIFIESTO.fotos || []).indexOf(id) !== -1;
AG.hayArte = () => AG.hayFuente() && AG.hayAtlas();
