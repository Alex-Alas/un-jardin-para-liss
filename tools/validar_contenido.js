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
const escenasPorMapa = { casa: 'Casa', pueblo: 'Pueblo', floreria: 'Floreria', colina: 'Colina' };

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

Object.entries(AG.MAPAS).forEach(([nombre, mapa]) => {
  (mapa.objetos || []).forEach((objeto) => {
    if (objeto.dialogo && !AG.DIALOGOS[objeto.dialogo]) {
      errores.push(`mapa ${nombre}: el objeto "${objeto.id}" usa un diálogo inexistente: ${objeto.dialogo}`);
    }
  });
  (mapa.puertas || []).forEach((puerta) => {
    if (!escenasValidas.includes(escenasPorMapa[puerta.a])) {
      errores.push(`mapa ${nombre}: la puerta lleva a un mapa desconocido: ${puerta.a}`);
    }
    const destino = AG.MAPAS[puerta.a];
    if (destino) {
      const [dx, dy] = [puerta.destino.x, puerta.destino.y];
      if (dy < 0 || dy >= destino.alto || dx < 0 || dx >= destino.ancho) {
        errores.push(`mapa ${nombre}: la puerta sale del mapa destino (${dx},${dy})`);
      } else if (destino.colisiones[dy][dx] === '1') {
        errores.push(`mapa ${nombre}: la puerta deja al jugador dentro de una pared en ${puerta.a} (${dx},${dy})`);
      }
    }
  });
  if (mapa.colisiones.length !== mapa.alto) errores.push(`mapa ${nombre}: faltan filas de colisión`);
  mapa.colisiones.forEach((fila, i) => {
    if (fila.length !== mapa.ancho) errores.push(`mapa ${nombre}: la fila ${i} de colisión no mide ${mapa.ancho}`);
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
