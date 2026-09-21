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
- **F1 ⏳** esperando `assets/source/liss-sheet.png` (hoja de sprites de Liss, la aporta Alex).
- F2–F7 pendientes (ver `docs/plan-implementacion.md`).

Mientras `AG.ASSETS_READY === false` (lo pone `assets/manifest.js`, generado por `tools/`), el juego
arranca en modo esqueleto: sin atlas, sin fuente bitmap, usando la fuente del sistema.

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
- `src/systems/*.js` — `input`, `dialog`, `memories`, `save`, `fx`.
- `src/data/*.js` — contenido: `dialogos`, `recuerdos`, `personajes`, `mapas` (este último generado).
- `tools/*.py` — pipeline de arte y build. `tools/build_single.py` inlinea todo en un solo HTML
  (lee los `<script src>` de `index.html` en orden y los reemplaza por su contenido).

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

### Recuerdos (`src/data/recuerdos.js`)

```js
AG.RECUERDOS = [
  { id: 'r1', titulo: 'La primera vez', pie: 'El día que nos conocimos',
    mensaje: 'Antes de esta foto yo ya estaba nervioso. Después también.',
    foto: 'assets/fotos/recuerdo_01.jpg' }
];
```

Si la foto no existe todavía, `memories.js` dibuja un marco vacío con el texto "foto pendiente" en
lugar de romperse.

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

Nombres exactos en `docs/arte.md` § Nombres de frames. Regla: `{personaje}_{accion}_{direccion}_{n}`
y `{accion}_{direccion}_{n}`; direcciones en español (`abajo`, `arriba`, `izquierda`, `derecha`).

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

- **Hoja de Liss**: si su grilla no es 16×24, se reajusta `AG.CFG` y `docs/arte.md` (protoloco en F1).
- **Acentos**: la fuente bitmap se genera desde Press Start 2P (OFL, latin-ext). Verificar
  `á é í ó ú ü ñ ¿ ¡` en pantalla antes de escribir el guion final.
- **iOS**: audio necesita gesto del usuario (pantalla de título) y `touch-action: none` (ya está).
- **Peso del build único**: si supera ~4 MB, bajar calidad de las fotos antes de subir al repo.
