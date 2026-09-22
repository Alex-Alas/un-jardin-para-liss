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
  frentes: (clave) => AG.ruta(`assets/mapa_${clave}_frentes.png`),
  foto: (id) => AG.ruta(`assets/fotos/recuerdo_${id}.jpg`)
};

/** Las ocho direcciones de la hoja de Liss, en el orden en que se leen sus rótulos. */
AG.DIRECCIONES = [
  'abajo',
  'abajo_derecha',
  'derecha',
  'arriba_derecha',
  'arriba',
  'arriba_izquierda',
  'izquierda',
  'abajo_izquierda'
];

/** Nombre de dirección de un vector de movimiento (8 sentidos). */
AG.nombreDireccion = function (dir) {
  const vertical = dir.y < 0 ? 'arriba' : dir.y > 0 ? 'abajo' : '';
  const horizontal = dir.x < 0 ? 'izquierda' : dir.x > 0 ? 'derecha' : '';
  if (vertical && horizontal) return `${vertical}_${horizontal}`;
  return vertical || horizontal || 'abajo';
};

AG.tieneFrame = function (escena, nombre) {
  return escena.textures.exists('arte') && escena.textures.get('arte').has(nombre);
};

/** Frames `prefijo_0`, `prefijo_1`… que existan en el atlas, en orden. */
AG.framesDe = function (escena, prefijo, maximo = 8) {
  const frames = [];
  for (let i = 0; i < maximo; i += 1) {
    const nombre = `${prefijo}_${i}`;
    if (!AG.tieneFrame(escena, nombre)) break;
    frames.push(nombre);
  }
  return frames;
};

/**
 * Dirección que sí tiene sprites: si el atlas no trae diagonales, cae al eje que manda.
 * Así el juego funciona igual con una hoja de 4 direcciones que con una de 8.
 */
AG.direccionDibujable = function (escena, dir, personaje = 'liss') {
  const nombre = AG.nombreDireccion(dir);
  if (!AG.hayAtlas() || AG.tieneFrame(escena, `${personaje}_idle_${nombre}_0`)) return nombre;
  if (Math.abs(dir.x) >= Math.abs(dir.y)) return dir.x < 0 ? 'izquierda' : 'derecha';
  return dir.y < 0 ? 'arriba' : 'abajo';
};

/**
 * Animaciones de Liss: una de caminata y una de respiración por cada dirección con frames.
 * Se crean una vez por escena; si el atlas no está, no hay nada que crear.
 */
AG.crearAnimacionesDeLiss = function (escena) {
  if (!AG.hayAtlas()) return;
  AG.DIRECCIONES.forEach((dir) => {
    [
      { clave: `liss_camina_${dir}`, fps: 8 },
      { clave: `liss_idle_${dir}`, fps: 1.4 }
    ].forEach(({ clave, fps }) => {
      if (escena.anims.exists(clave)) return;
      const frames = AG.framesDe(escena, clave);
      if (frames.length < 2) return;
      escena.anims.create({
        key: clave,
        frames: frames.map((frame) => ({ key: 'arte', frame })),
        frameRate: fps,
        repeat: -1
      });
    });
  });
};

/**
 * Respiración de un NPC: los frames `npc_<id>_abajo_0/1` en bucle lento.
 * Devuelve la clave de la animación, o null si ese NPC todavía no tiene arte.
 */
AG.crearAnimacionDeNpc = function (escena, id) {
  const clave = `npc_${id}_idle`;
  if (escena.anims.exists(clave)) return clave;
  const frames = AG.framesDe(escena, `npc_${id}_abajo`, 2);
  if (frames.length < 2) return null;
  escena.anims.create({
    key: clave,
    frames: frames.map((frame) => ({ key: 'arte', frame })),
    frameRate: 1.2,
    repeat: -1
  });
  return clave;
};

AG.hayFuente = () => AG.MANIFIESTO.fuente === true;
AG.hayAtlas = () => AG.MANIFIESTO.atlas === true;
AG.hayMapa = (clave) => (AG.MANIFIESTO.mapas || []).indexOf(clave) !== -1;
AG.hayFrentes = (clave) => (AG.MANIFIESTO.frentes || []).indexOf(clave) !== -1;
AG.hayFoto = (id) => (AG.MANIFIESTO.fotos || []).indexOf(id) !== -1;
AG.hayArte = () => AG.hayFuente() && AG.hayAtlas();
