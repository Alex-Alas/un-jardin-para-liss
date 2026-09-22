# Handoff — UN JARDÍN PARA LISS

Encargo técnico autocontenido para co-implementar (Claude Code, Claude web, o quien siga). Si solo
lees un documento, lee este.

## Qué es esto

Juego web corto (6–10 min) de exploración top-down en pixel art, para Liss, por el Día de las Flores
Amarillas. Phaser 4 vendorizado, sin bundler, sin npm, sin backend. El arte se genera con scripts de
Python. Todo el texto está en español (El Salvador), tuteando.

**No tocar** `desktop-controller-powered-by-jev` (otro proyecto, en la carpeta de al lado).

## Estado actual

- **F0 ✅** repo, scaffold, Phaser 4.2.1 vendorizado, docs, esqueleto ejecutable.
- **F1 ✅** la hoja de Liss llegó, está normalizada y Liss camina en 8 direcciones (ver
  `docs/arte.md § La hoja de Liss manda`).
- **F2 🟡** falta el arte de los demás: NPCs, objetos, tiles e iconos (hoy los pinta el mapa).
- F3, F6 ✅ · F4, F5, F7 🟡 (faltan fotos, la 2ª escena de pétalos y publicar en Pages).

El manifiesto (`assets/manifest.js`, generado por `tools/actualizar_manifest.py`) dice qué arte
existe y el juego se adapta: sin atlas dibuja formas, sin fuente bitmap usa la del sistema, sin
fotos muestra el marco con "foto pendiente".

## Cómo correr

```bash
python3 -m http.server 8000                     # http://localhost:8000
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/<script>.py              # pipeline de arte
```

También funciona abriendo `index.html` directo (`file://`): por eso no hay ES modules ni `fetch` de
assets en runtime.

## Arquitectura

Namespace global `AG` (`window.AG`), scripts clásicos cargados en orden desde `index.html`:

```
vendor/phaser.min.js → assets/manifest.js → src/config.js → src/assets.js
→ src/audio/chiptune.js → src/systems/*.js → src/scenes/*.js → src/data/*.js → src/main.js
```

- `src/config.js` — `AG.CFG`: resolución, tile, velocidades, paleta, claves de guardado.
- `src/assets.js` — manifest de rutas. `AG.requiereAssets()` decide si hay arte generado.
- `src/main.js` — crea el `Phaser.Game` y expone `AG.debug` (`AG.debug.ir('Colina')` para saltar de
  escena en QA).
- `src/scenes/*.js` — una escena por lugar: `Boot`, `Title`, `Casa`, `Pueblo`, `Floreria`, `Parque`,
  `Colina`, `Final`, `Album`, `Creditos`, `Petalos` (escena parametrizada, se reutiliza para las dos
  escenas de pétalos).
- `src/systems/*.js` — `input`, `dialog`, `fotos`, `memories`, `save`, `fx`.
- `src/data/*.js` — contenido: `dialogos`, `recuerdos`, `personajes`, `mapas` (este último generado).
- `tools/*.py` — pipeline de arte y build. `tools/generate_sprites.py` convierte la hoja de Liss
  en el atlas; `tools/build_single.py` inlinea todo en un solo HTML (lee los `<script src>` de
  `index.html` en orden y los reemplaza por su contenido).

## Contratos de datos

### Diálogos (`src/data/dialogos.js`)

```js
AG.DIALOGOS = {
  'casa.nota': [
    { narracion: 'Hay una nota doblada en cuatro, con una letra que Liss conoce de memoria.' },
    { narracion: '«Hoy el pueblo entero tiene flores amarillas para ti.»' },
    { narracion: '«Busca tres y ven a la colina. Te espero. — A.»' }
  ],
  'flora.saludo': [
    { quien: 'flora', texto: '¡Liss! Justo a quien necesitaba.' }
  ],
  'colina.abrazo': [
    { quien: 'alex', texto: '¿Me das un abrazo?' },
    { eleccion: [ { texto: 'Sí' }, { texto: 'Sí, y otro más' } ] },
    { quien: 'alex', texto: '(Se queda callado un rato, sonriendo.)' }
  ]
};
```

Entradas disponibles: `narracion`, `quien` + `texto`, `eleccion` (2 opciones), `darFlor` (1|2|3),
`darRecuerdo` ('r1'..'r6'), `lanzarEscena` ({ clave, datos }), `musica` (clave del tema),
`efecto` ('fundido', 'temblor', 'petalos'…). Texto exacto en `docs/guion.md` (las claves del guion
son las claves de este objeto).

### Recuerdos (`src/data/personajes.js`)

```js
AG.RECUERDOS = [
  { id: 'r1', titulo: 'Pegaditos bien gonitos', pie: 'La primera vez q te tuve tan cómoda cerca de mí',
    mensaje: 'Antes de esta foto yo ya estaba nervioso. Después también :P',
    foto: 'assets/fotos/recuerdo_r1.jpg' }
];
```

Si la foto no existe todavía, `memories.js` dibuja un marco vacío con el texto "foto pendiente" en
lugar de romperse.

Las fotos **no** se dibujan dentro del canvas: `memories.js` le pasa a `AG.Fotos`
(`src/systems/fotos.js`) la caja en píxeles del juego, y esa capa HTML (`#fotos`, encima del canvas)
pega la foto al canvas real. El juego mide 480 × 270 y se agranda en bloques (`image-rendering:
pixelated`), así que una foto adentro saldría pixelada; afuera se ve con toda su resolución. La capa
no recibe toques (`pointer-events: none`), así que el álbum y el polaroid se siguen manejando desde
Phaser.

### Personajes (`src/data/personajes.js`)

```js
AG.PERSONAJES = {
  liss: { nombre: 'Liss', sprite: 'liss', retrato: 'liss', color: '#f2a8b8' }
};
```

### Mapas ASCII (`maps/*.txt`)

Una letra por tile. Leyenda:

```
#  pared / bloquea          T  árbol (bloquea)          S  punto de guardado (corazón)
.  pasto                   f  flores decorativas       D  puerta
,  camino de tierra        w  piso de madera           1-9  NPCs y objetos (se definen en el mapa)
=  baldosa / acera         b  azulejo de interior
~  agua (bloquea)          // comentario (se ignora)
```

Líneas de metadatos: `#! objeto 3 banco banco pueblo.banco` (letra, tipo, sprite/id, diálogo) y
`#! puerta D casa 9 12` (letra, mapa destino, x, y). Los mapas son cuatro: `casa`, `pueblo`
(incluye plaza, kiosco, florería por dentro y parque), `floreria` y `colina`.

`tools/render_maps.py` produce `assets/mapa_<nombre>.png` **y** `src/data/mapas.js`:

```js
AG.MAPAS = {
  pueblo: {
    ancho: 48, alto: 32, tile: 16, imagen: 'assets/mapa_pueblo.png',
    colisiones: ['1111....', '1000..11'],           // '1' bloquea, '0' libre
    objetos: [ { x: 12, y: 8, tipo: 'npc', id: 'flora', sprite: 'flora', dialogo: 'flora.saludo' } ],
    puertas: [ { x: 5, y: 20, a: 'casa', destino: { x: 4, y: 9 } } ]
  }
};
```

### Frames del atlas

Nombres exactos en `docs/arte.md` § Nombres de frames. Regla: `{personaje}_{accion}_{direccion}_{n}`;
direcciones en español y en ocho sentidos (`abajo`, `abajo_derecha`, `derecha`, `arriba_derecha`,
`arriba`, `arriba_izquierda`, `izquierda`, `abajo_izquierda`).

Hoy el atlas es solo de Liss: `liss_idle_<dir>_0/_1`, `liss_camina_<dir>_0..3`,
`retrato_liss_normal` y `retrato_liss_feliz` (50 frames, 16×34 px el sprite y 48×48 el retrato).
El código pide los frames que faltan con guardas (`AG.tieneFrame`), así que agregar personajes es
agregar frames, sin tocar escenas.

## Reglas de ingeniería

- **Español** en identificadores de dominio, comentarios de intención y todo el texto visible.
- Sin frameworks, sin bundler, sin dependencias JS: si algo se puede resolver con Phaser, se resuelve.
- Sin `fetch` ni ES modules: todo por `<script>` clásico (requisito `file://`).
- El juego debe arrancar igual desde `file://`, desde `http://localhost` y desde GitHub Pages.
- **Nunca** commitear `_referencias/` ni `dist/`.
- Nada de perder: no hay daño, no hay game over, no hay temporizador que termine la historia.
- Accesibilidad mínima: D-pad táctil y botón A de 44 px o más, textos legibles en celular, sin
  depender del color para entender algo.

## Criterios de aceptación

1. Partida completa en 6–10 min, sin errores en consola, sin forma de perder.
2. 3 flores, 6 recuerdos con foto, 2 escenas de pétalos, final con ramo + mensaje + créditos.
3. Celular (táctil, 390×844) y desktop (teclado) funcionan; el audio arranca tras el primer toque.
4. Guarda y retoma (flores, recuerdos, escena) con `localStorage`.
5. `python3 tools/qa_assets.py` en verde; nada de assets con tamaño incorrecto o alpha sucio.
6. `dist/un-jardin-para-liss.html` abre y se juega con `file://` sin red.
7. La URL de GitHub Pages carga el juego y las fotos.

## Checklist de revisión (para quien co-implemente)

- [ ] ¿El guion está transcrito sin cambiarle las palabras a Alex?
- [ ] ¿Liss no habla nunca, salvo en las elecciones?
- [ ] ¿Los 2 minijuegos son los únicos minijuegos?
- [ ] ¿Se puede terminar sin leer instrucciones, solo caminando y tocando todo?
- [ ] ¿El pueblo se siente vivo (pétalos, sonidos, NPCs que reaccionan) sin sacrificar claridad?
- [ ] ¿Las fotos se ven grandes y bien, o quedan diminutas? (96 px en pantalla de 480 es el mínimo)
- [ ] ¿El final se puede leer al ritmo de quien juega? (sin auto-avance en el mensaje)
- [ ] ¿Algo del juego le contaría un secreto a alguien que no sea Liss? Si sí, se recorta.

## Riesgos conocidos

- ~~**Hoja de Liss**~~: resuelto en F1. Vino en 8 direcciones y con render suave (no pixel art
  puro): el pipeline la recorta, le quita fondo y sombra, la baja a 32 px de alto y la cuantiza a
  una paleta común. Si la hoja se reemplaza, se vuelve a correr `tools/generate_sprites.py`.
- **Acentos**: la fuente bitmap se genera desde Press Start 2P (OFL, latin-ext). Verificar
  `á é í ó ú ü ñ ¿ ¡` en pantalla antes de escribir el guion final.
- **iOS**: audio necesita gesto del usuario (pantalla de título) y `touch-action: none` (ya está).
- **Peso del build único**: si supera ~4 MB, bajar calidad de las fotos antes de subir al repo.
