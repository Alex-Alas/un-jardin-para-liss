window.AG = window.AG || {};

AG.MANIFIESTO = AG.MANIFIESTO || { fuente: false, atlas: false, mapas: [], fotos: [] };

/** En el build de un solo archivo estas rutas se reemplazan por data URIs. */
AG.ruta = function (ruta) {
  if (AG.ARCHIVOS_DATOS && AG.ARCHIVOS_DATOS[ruta]) return AG.ARCHIVOS_DATOS[ruta];
  return ruta;
};

AG.ASSETS = {
  atlas: () => AG.ruta('assets/atlas.png'),
  atlasDatos: () => AG.ruta('assets/atlas.json'),
  fuentes: {
    pixel8: {
      png: () => AG.ruta('assets/font_pixel8.png'),
      xml: () => AG.ruta('assets/font_pixel8.xml')
    },
    pixel16: {
      png: () => AG.ruta('assets/font_pixel16.png'),
      xml: () => AG.ruta('assets/font_pixel16.xml')
    }
  },
  mapa: (clave) => AG.ruta(`assets/mapa_${clave}.png`),
  foto: (id) => AG.ruta(`assets/fotos/recuerdo_${id}.jpg`)
};

AG.hayFuente = () => AG.MANIFIESTO.fuente === true;
AG.hayAtlas = () => AG.MANIFIESTO.atlas === true;
AG.hayMapa = (clave) => (AG.MANIFIESTO.mapas || []).indexOf(clave) !== -1;
AG.hayFoto = (id) => (AG.MANIFIESTO.fotos || []).indexOf(id) !== -1;
AG.hayArte = () => AG.hayFuente() && AG.hayAtlas();
