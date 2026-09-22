#!/usr/bin/env node
/**
 * Validador de contenido: caza referencias rotas sin abrir el navegador.
 *
 *   node tools/validar_contenido.js
 *
 * Revisa que cada diálogo referenciado por los mapas exista, que cada personaje de las líneas
 * esté definido, que las escenas y los recuerdos existan, y que no haya textos con comillas raras.
 */

const fs = require('fs');
const path = require('path');

const RAIZ = path.resolve(__dirname, '..');
// El navegador y Node comparten el mismo espacio global: así `window.AG = ...` crea `AG`.
global.window = globalThis;

function cargar(ruta) {
  const codigo = fs.readFileSync(path.join(RAIZ, ruta), 'utf8');
  new Function(codigo)();
}

['src/config.js', 'src/data/personajes.js', 'src/data/dialogos.js', 'src/data/mapas.js'].forEach(cargar);

const AG = globalThis.AG;
const errores = [];
const avisos = [];
const escenasValidas = ['Casa', 'Pueblo', 'Floreria', 'Colina', 'Petalos', 'Album', 'Creditos', 'Title'];
const efectosValidos = ['latido', 'temblor', 'florecer'];

Object.entries(AG.DIALOGOS).forEach(([clave, valor]) => {
  const variantes = Array.isArray(valor[0]) ? valor : [valor];
  variantes.forEach((lineas, i) => {
    lineas.forEach((linea, j) => {
      const donde = `${clave}[${i}][${j}]`;
      if (linea.quien && !AG.PERSONAJES[linea.quien]) errores.push(`${donde}: personaje desconocido "${linea.quien}"`);
      if (!linea.quien && !linea.narracion && !linea.eleccion && !linea.darFlor &&
          !linea.darRecuerdo && !linea.lanzarEscena && !linea.efecto && !linea.musica && !linea.verAlbum) {
        errores.push(`${donde}: línea vacía o con forma rara`);
      }
      if (linea.darRecuerdo && !AG.recuerdoPorId(linea.darRecuerdo)) {
        errores.push(`${donde}: recuerdo desconocido "${linea.darRecuerdo}"`);
      }
      if (linea.efecto && !efectosValidos.includes(linea.efecto)) {
        errores.push(`${donde}: efecto desconocido "${linea.efecto}"`);
      }
      if (linea.lanzarEscena && !escenasValidas.includes(linea.lanzarEscena.clave)) {
        errores.push(`${donde}: escena desconocida "${linea.lanzarEscena.clave}"`);
      }
      if (linea.lanzarEscena && !AG.DIALOGOS[`${linea.lanzarEscena.datos.tipo}.intro`]) {
        errores.push(`${donde}: falta el diálogo de entrada de "${linea.lanzarEscena.datos.tipo}"`);
      }
      if (linea.eleccion && linea.eleccion.length !== 2) {
        avisos.push(`${donde}: la elección tiene ${linea.eleccion.length} opciones (se esperan 2)`);
      }
      if (linea.eleccion && linea.eleccion.some((o) => !o.texto)) {
        errores.push(`${donde}: opción de elección sin texto`);
      }
    });
  });
});

/* ---------------------------------------------------------------- mapas
 * Lo mismo que hace el motor (src/scenes/Mundo.js), sin Phaser: puntos en píxeles del mapa,
 * celdas de colisión de `mapa.celda` px y la caja de los pies de Liss de 10 × 4 px.
 */
const TILE = AG.CFG.TILE;
const aPixeles = (p) => (p.px !== undefined ? { x: p.px, y: p.py } : { x: p.x * TILE + TILE / 2, y: p.y * TILE + TILE });

function grillaDe(mapa) {
  const celda = mapa.celda || TILE;
  const grilla = mapa.colisiones.map((fila) => fila.split(''));
  // Los NPCs ocupan sus pies, igual que en el juego.
  (mapa.objetos || []).filter((o) => o.tipo === 'npc').forEach((o) => {
    const { x, y } = aPixeles(o);
    for (let cy = Math.floor((y - 7) / celda); cy <= Math.floor((y - 1) / celda); cy += 1) {
      for (let cx = Math.floor((x - 6) / celda); cx <= Math.floor((x + 5) / celda); cx += 1) {
        if (grilla[cy] && grilla[cy][cx] !== undefined) grilla[cy][cx] = '1';
      }
    }
  });
  const solido = (px, py) => {
    const cx = Math.floor(px / celda);
    const cy = Math.floor(py / celda);
    return cy < 0 || cy >= grilla.length || cx < 0 || cx >= grilla[0].length || grilla[cy][cx] === '1';
  };
  const bloqueado = (px, py) => {
    const paso = Math.min(4, celda);
    for (let x = px - 5; ; x = Math.min(x + paso, px + 5)) {
      if (solido(x, py - 4) || solido(x, py - 1)) return true;
      if (x >= px + 5) return false;
    }
  };
  return { celda, bloqueado };
}

/** Todo lo que Liss puede pisar caminando desde `inicio`, en pasos de 2 px. */
function alcanzable(mapa, bloqueado, inicio) {
  const ancho = mapa.ancho * TILE;
  const alto = mapa.alto * TILE;
  const paso = 2;
  const clave = (x, y) => y * ancho + x;
  const visto = new Set();
  const cola = [];
  const x0 = Math.round(inicio.x / paso) * paso;
  const y0 = Math.round(inicio.y / paso) * paso;
  if (bloqueado(x0, y0)) return { visto, cola: [] };
  visto.add(clave(x0, y0));
  cola.push([x0, y0]);
  for (let i = 0; i < cola.length; i += 1) {
    const [x, y] = cola[i];
    [[paso, 0], [-paso, 0], [0, paso], [0, -paso]].forEach(([dx, dy]) => {
      const nx = x + dx;
      const ny = y + dy;
      if (nx < 0 || ny < 0 || nx > ancho || ny > alto || visto.has(clave(nx, ny)) || bloqueado(nx, ny)) return;
      visto.add(clave(nx, ny));
      cola.push([nx, ny]);
    });
  }
  return { visto, cola };
}

Object.entries(AG.MAPAS).forEach(([nombre, mapa]) => {
  (mapa.objetos || []).forEach((objeto) => {
    if (objeto.dialogo && !AG.DIALOGOS[objeto.dialogo]) {
      errores.push(`mapa ${nombre}: el objeto "${objeto.id}" usa un diálogo inexistente: ${objeto.dialogo}`);
    }
  });

  const celda = mapa.celda || TILE;
  const filas = (mapa.alto * TILE) / celda;
  const columnas = (mapa.ancho * TILE) / celda;
  if (mapa.colisiones.length !== filas) errores.push(`mapa ${nombre}: la colisión tiene ${mapa.colisiones.length} filas y no ${filas}`);
  mapa.colisiones.forEach((fila, i) => {
    if (fila.length !== columnas) errores.push(`mapa ${nombre}: la fila ${i} de colisión no mide ${columnas}`);
  });

  (mapa.puertas || []).forEach((puerta) => {
    if (!escenasValidas.includes(puerta.a)) {
      errores.push(`mapa ${nombre}: la puerta lleva a un mapa desconocido: ${puerta.a}`);
      return;
    }
    const destino = AG.MAPAS[puerta.a.toLowerCase()];
    if (!destino) return;
    const { x, y } = aPixeles(puerta.destino);
    if (x < 0 || y < 0 || x > destino.ancho * TILE || y > destino.alto * TILE) {
      errores.push(`mapa ${nombre}: la puerta a ${puerta.a} deja a Liss fuera del mapa (${x},${y})`);
    } else if (grillaDe(destino).bloqueado(x, y)) {
      errores.push(`mapa ${nombre}: la puerta a ${puerta.a} deja a Liss dentro de algo sólido en (${x},${y})`);
    }
  });
});

/* Que todo se pueda alcanzar: desde el inicio de cada mapa (y desde cada lugar donde una puerta
 * deja a Liss) se recorre lo pisable y se revisa cada puerta y cada cosa que se toca. */
const INICIOS = { casa: { x: 9, y: 11 }, pueblo: { x: 6, y: 9 }, floreria: { x: 7, y: 10 }, colina: { x: 16, y: 17 } };
Object.entries(AG.MAPAS).forEach(([nombre, mapa]) => {
  const { bloqueado } = grillaDe(mapa);
  const llegadas = [aPixeles(mapa.inicio || INICIOS[nombre])];
  Object.values(AG.MAPAS).forEach((otro) =>
    (otro.puertas || []).filter((p) => p.a.toLowerCase() === nombre).forEach((p) => llegadas.push(aPixeles(p.destino)))
  );
  llegadas.forEach((llegada) => {
    if (bloqueado(llegada.x, llegada.y)) errores.push(`mapa ${nombre}: Liss aparece dentro de algo sólido en (${llegada.x},${llegada.y})`);
  });

  const { cola } = alcanzable(mapa, bloqueado, llegadas[0]);
  const posiciones = cola;
  const cerca = (o) => {
    const { x, y } = aPixeles(o);
    return posiciones.some(([px, py]) => Math.hypot(px - x, py - 8 - (y - 6)) < 22);
  };
  (mapa.objetos || []).forEach((o) => {
    if (!cerca(o)) errores.push(`mapa ${nombre}: no se puede llegar a "${o.id}" (${JSON.stringify(aPixeles(o))})`);
  });
  (mapa.puertas || []).forEach((p) => {
    const zona = p.px !== undefined
      ? { x0: p.px, y0: p.py, x1: p.px + p.ancho, y1: p.py + p.alto }
      : { x0: p.x * TILE, y0: p.y * TILE, x1: p.x * TILE + TILE, y1: p.y * TILE + TILE + 6 };
    const llega = posiciones.some(([px, py]) => px > zona.x0 && px < zona.x1 && py > zona.y0 && py < zona.y1);
    if (!llega) errores.push(`mapa ${nombre}: no se puede llegar a la puerta a ${p.a}`);
  });
  llegadas.slice(1).forEach((llegada) => {
    if (!posiciones.some(([px, py]) => Math.abs(px - llegada.x) <= 3 && Math.abs(py - llegada.y) <= 3)) {
      errores.push(`mapa ${nombre}: desde (${llegada.x},${llegada.y}) no se llega al resto del mapa`);
    }
  });
});

const usados = new Set();
Object.values(AG.MAPAS).forEach((mapa) => (mapa.objetos || []).forEach((o) => usados.add(o.dialogo)));
Object.keys(AG.DIALOGOS).forEach((clave) => {
  if (!usados.has(clave) && !clave.startsWith('petalos') && clave !== 'album.vacio') {
    avisos.push(`diálogo sin usar en los mapas: ${clave}`);
  }
});

if (avisos.length) {
  console.log('\nAvisos:');
  avisos.forEach((a) => console.log('  ·', a));
}
if (errores.length) {
  console.log('\nErrores:');
  errores.forEach((e) => console.log('  ✗', e));
  console.log(`\n${errores.length} errores.`);
  process.exit(1);
}
console.log('\nContenido válido: diálogos, personajes, mapas, puertas y recuerdos en orden.');
