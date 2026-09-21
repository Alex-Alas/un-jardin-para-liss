# UN JARDÍN PARA LISS — Plan de implementación

**Regalo:** Día de las Flores Amarillas (21 de septiembre).
**Encargo:** juego corto jugable hoy, web, publicado en GitHub Pages, con Liss como protagonista.
**Reglas del encargo:** NO se toca `desktop-controller-powered-by-jev`. Repo nuevo, stack web sencillo, sin build-tools pesados. Repo y juego se llaman igual: **`un-jardin-para-liss`**.
**Plan compartible:** este documento vive en el repo para que Claude lo revise y co-implemente contigo (`docs/handoff.md` tiene el encargo tecnico derivado).

---

## 1. Concepto y diseño del juego

### Ficha
| | |
|---|---|
| Título | **UN JARDÍN PARA LISS** |
| Tono | Indie retro cozy, tipo Deltarune: humor tierno, cajas de diálogo, corazón de guardado, transiciones oscuras |
| Duración | 6–10 minutos, una sola partida, final garantizado (imposible perder) |
| Plataforma | Navegador (celular primero, desktop también), teclado + táctil |
| Premisa | Es 21 de septiembre. Liss despierta con una nota misteriosa: hoy el pueblo tiene flores amarillas para ella. |
| Mecánica núcleo | Exploración top-down + diálogos que revelan **mensajitos y fotos** de Alex, con **2 escenas de pétalos** que hacen avanzar la historia |

### Historia (Liss protagonista, ~5 beats)
1. **Casa de Liss** (tutorial): despierta, el espejo y el calendario le hablan. Una nota firmada "— A." le dice: *"Hoy es un día de flores amarillas. Busca tres y ven a la colina."* En el escritorio hay un **recuerdo** (foto).
2. **El pueblo**: calle, plaza, kiosco, florería. NPCs con humor (Doña Flora la florista, el kiosquero, una niña, un gato llamado Michi que solo habla en `*`). Cada NPC suelta un mensajito que Alex escribió.
3. **Escena de pétalos 1 — "Los pétalos de la plaza"**: caen pétalos amarillos; Liss los atrapa. Meta blanda, sin castigo. Recompensa: **flor 1** + recuerdo.
4. **Escena de pétalos 2 — "El viento del parque"**: versión escalada (viento lateral, hojas que restan). Recompensa: **flor 3** y abre el camino a la colina. (La flor 2 se gana con cariño: la niña del parque le regala la suya.)
5. **La colina (final)**: atardecer. Alex está esperando. Se muestran **todos los recuerdos** en un álbum, él le entrega el ramo y viene el **mensaje final** (texto pausado, se lee a su ritmo). Última elección: *"¿Me das un abrazo?"* → créditos con melodía y pétalos cayendo.

### Final propuesto (palabras de Alex, ya ajustadas ✓)
> *— Liss, buscaste flores por todo el pueblo… pero la flor más bonita siempre fuiste tú, amorcito :>*
> *Gracias por existir, por tu risa, por quedarte. Hoy el pueblo entero te dio flores amarillas,*
> *y yo solo quise ser el que te las entregara. Te amo <333 — Alex*
> Tarjeta final: **"Feliz Día de las Flores Amarillas 🌻 — 21.09"**

(El guion completo, con líneas de cada NPC y los 6 pies de foto, se escribe en `docs/guion.md`; todo editable.)

### Sistemas
- **Exploración top-down**: mapas baked (PNG) + grilla de colisión desde ASCII; puertas con fade.
- **Diálogo estilo Deltarune**: caja con retrato pixel art, efecto máquina de escribir, blips, animación del retrato al hablar, elecciones simples de 2 opciones.
- **Recuerdos**: objetos interactuables abren un **polaroid** con foto real de ustedes + pie de foto + mensajito de Alex. 6 en total. Pantalla **ÁLBUM** en el menú para volver a verlos.
- **2 escenas de pétalos** (núcleo, máximo 2): atrapar pétalos; la 1 es tutorial suave, la 2 tiene viento. Nunca se pierde (si se acaba el tiempo, un NPC te anima y sigue).
- **Guardado**: automático en localStorage + puntos de guardado con corazón. Retoma donde quedó.
- **Presentación**: transición con corazón, screen-shake, pétalos ambientales, 3 temas chiptune (pueblo / pétalos / final) + SFX generados por código.

---

## 2. Stack y arquitectura

- **Phaser 4.2.1** (MIT) vendorizado en `vendor/` y cargado con `<script>` clásico → cero npm, cero bundler, funciona incluso en `file://`.
- **JS clásico en `src/`** cargado en orden desde `index.html` (namespace global `AG`). Dividido por sistemas y escenas.
- **Assets 100% generados por scripts Python** (`tools/`, Pillow) → atlas PNG+JSON, mapas PNG, fuente bitmap, fotos procesadas.
- **Mapas como ASCII** (`maps/*.txt`): una sola fuente de verdad de la que se derivan (a) el PNG renderizado y (b) la grilla de colisión + puntos de interés exportados a JS. Autoria fácil y diffeable.
- **Fuente bitmap generada** desde Press Start 2P (OFL, subset latin-ext ⇒ acentos ✓) con Pillow → `assets/font_pixel.png/json`. Sin dependencias de fuentes del sistema, nítida a cualquier escala. Fallback: VT323 (OFL) o parche manual de glifos.
- **Música/SFX procedurales** con WebAudio (`src/audio/chiptune.js`): cero archivos de audio, cero licencias. Arranca con el gesto de "toca para empezar" (requisito de iOS).
- **Móvil primero**: `Scale.FIT` 16:9 con aviso no bloqueante "gira tu teléfono" si está vertical; D-pad táctil abajo-izquierda + botón A abajo-derecha; tap para avanzar diálogos.
- **Build de un solo archivo**: `tools/build_single.py` (stdlib) inlinea Phaser + assets base64 + fotos + código → `dist/un-jardin-para-liss.html`. Sirve como respaldo offline.
- **Publicación**: `main` en raíz del repo, Pages desde `/` → `https://<usuario>.github.io/un-jardin-para-liss/`.
- **Debug hooks**: `window.AG.debug.jump('escena')` para QA rápido de escenas sin jugar todo.

### Estructura del repo
```
un-jardin-para-liss/
├── index.html
├── README.md                 # carta corta a Liss + cómo jugar
├── LICENSE                   # código MIT; arte y fotos: todos los derechos reservados
├── .gitignore                # _referencias/, dist/, __pycache__, .venv
├── vendor/phaser.min.js      # + LICENSE-phaser.txt
├── src/
│   ├── main.js  config.js  assets.js        # assets.js: rutas (reescrito por el build a dataURI)
│   ├── audio/chiptune.js
│   ├── systems/  input.js  dialog.js  memories.js  save.js  fx.js
│   ├── scenes/   Boot  Title  Casa  Pueblo  Floreria  Parque  Colina  Final  Album  Creditos  Petalos
│   └── data/     dialogos.js  recuerdos.js  personajes.js  mapas.js   # mapas.js generado
├── maps/         casa.txt  pueblo.txt  floreria.txt  parque.txt  colina.txt
├── assets/
│   ├── source/liss-sheet.png                # ← la hoja que sube Alex (fuente de verdad del estilo)
│   ├── atlas.png / atlas.json               # sprites, tiles, retratos, UI
│   ├── mapa_*.png                           # mapas renderizados
│   ├── font_pixel.png / font_pixel.json
│   └── fotos/recuerdo_01..06.jpg            # fotos optimizadas (públicas, decidido por Alex)
├── tools/        requirements.txt  contact_sheet.py  render_maps.py  generate_font.py
│                 generate_sprites.py  prepare_photos.py  build_single.py  qa_assets.py
├── docs/         idea.md  guion.md  arte.md  plan-implementacion.md  handoff.md
├── _referencias/                            # NO se sube: fotos originales, notas de Alex
└── dist/                                    # NO se sube: HTML único
```

---

## 3. Fases y tareas

### F0 — Repo, scaffold y decisiones (base para que Alex coloque la hoja)
- [ ] Crear `~/Proyectitos/un-jardin-para-liss/`, `git init`, `.gitignore`, `README.md`, `LICENSE`.
- [ ] Scaffold de `index.html`, `src/` (esqueleto), `maps/`, `assets/`, `tools/`, `docs/`.
- [ ] Vendorizar Phaser 4.2.1 (`npm pack phaser@4.2.1` → copiar `dist/phaser.min.js`; si no existe el min, usar `dist/phaser.js`).
- [ ] Escribir `docs/idea.md`, `docs/guion.md` (borrador completo del guion y del final) y `docs/arte.md` (brief de arte).
- [ ] **Guardar este plan en `docs/plan-implementacion.md`** (autocontenido y en español: concepto, arquitectura, fases, decisiones y criterios de aceptación) **y `docs/handoff.md`** (encargo auto-contenido para Claude: contratos entre archivos, criterios de aceptación y checklist de revisión) — para compartir el repo con Claude y que lo revise antes de implementar.
- [ ] Avisar a Alex las rutas exactas donde colocar sus archivos:
  - `assets/source/liss-sheet.png` → hoja de sprites de Liss.
  - `_referencias/fotos/foto_01..06.jpg` → fotos para los recuerdos.
  - `_referencias/notas.md` → apodos, chistes internos, correcciones al guion, ¿canción significativa?
- [ ] Commit inicial: `feat: scaffold del proyecto y docs base`.
- **Gate:** el repo existe, el plan y el handoff están dentro (listos para que Claude los revise), y Alex puede colocar su hoja de sprites.

### F1 — Inspeccionar la hoja de Liss y fijar el marco técnico ✅
- [x] Con Pillow: reportar tamaño, grilla de frames, direcciones, paleta y conteo de colores de `liss-sheet.png` (`tools/generate_sprites.py --inspeccionar`; reporte pegado en `docs/arte.md`).
- [x] Decidir con datos: sprite de 16×34 con Liss de 32 px (2 tiles), tile de 16 y canvas de 480×270 sin cambios. La hoja trajo las 8 direcciones, así que el juego pasó a 8 (diagonales en teclado y en el D-pad).
- [x] Generar `assets/atlas.png` recortando y normalizando la hoja: 8 direcciones × (idle + respiración + ciclo de caminata de 4) y 2 retratos = 50 frames, 23 colores.
- [x] Congelar paleta de Liss + decisiones de escala y animación en `docs/arte.md`.
- **Gate:** ✅ hoja normalizada, hoja de contacto (`--contacto`) y partida completa revisada en navegador.

### F2 — Pipeline de arte completo
- [ ] `tools/generate_sprites.py`: Alex, Doña Flora, kiosquero, niña, gato, Liss con ramo — mismo marco, misma paleta y estilo que la hoja de Liss.
- [ ] `tools/generate_font.py`: fuente bitmap 8px (diálogo) y 16px (títulos) desde Press Start 2P; **probar `á é í ó ú ñ ¿ ¡`** y parchar si falta algún glifo.
- [ ] `tools/render_maps.py`: PNG de cada mapa desde `maps/*.txt` + export de colisiones/objetos a `src/data/mapas.js`.
- [ ] `tools/prepare_photos.py`: recorte cuadrado, máx 720px, JPEG q82, tinte cálido opcional → `assets/fotos/`.
- [ ] `tools/qa_assets.py` + `tools/contact_sheet.py`: reporte de tamaños/alpha/paleta y hoja de contacto para inspección visual.
- **Gate:** reporte QA en verde y contacto visual aprobado.

### F3 — Núcleo jugable
- [ ] `config.js` + `main.js`: canvas, `pixelArt: true`, escalado FIT, input teclado (flechas/WASD + Z/Enter/Esc) y táctil (D-pad + A).
- [ ] `input.js`: capa unificada de input (tecla y táctil indistinguibles para el juego).
- [ ] Movimiento 4 direcciones con colisión contra la grilla del mapa, cámara que sigue, depth por eje Y.
- [ ] Transiciones entre mapas (puertas con fade oscuro), `fx.js` (shake, fade, pétalos ambientales).
- [ ] `save.js`: flags (flores, recuerdos, escena, posición), autosave y puntos de guardado con corazón.
- **Gate:** se puede caminar por el pueblo, entrar a la casa, guardar y recargar sin perder progreso.

### F4 — Sistemas de historia
- [ ] `dialog.js`: cajas con retrato, typewriter, blips, saltar con A, elecciones de 2 opciones, cola de líneas.
- [ ] `memories.js`: modal polaroid con foto real (marco, cinta adhesiva, pie de foto, mensaje), desbloqueo y contador `n/6`; pantalla **ÁLBUM**.
- [ ] Interactuables del pueblo (espejo, buzón, calendario, kiosco, cartel, banco…) con mensajitos de Alex.
- [ ] `chiptune.js`: 3 temas + SFX (blip de texto, pasos, puerta, flor obtenida, recuerdo, pétalo, corazón).
- **Gate:** un recorrido de prueba muestra diálogos, un recuerdo y música sin errores en consola.

### F5 — Las 2 escenas de pétalos
- [ ] `Petalos.js` escena reutilizable parametrizada (meta, tiempo, viento, obstáculos, recompensa).
- [ ] Escena 1 (plaza): pétalos que caen, meta blanda, sin castigo → flor 1 + recuerdo.
- [ ] Escena 2 (parque): viento lateral y hojas secas que restan → flor 3 + abre la colina.
- [ ] Feedback juicy: escala/brillo al atrapar, combo, sonido ascendente, "¡Bien!" en pixel font.
- **Gate:** ambas escenas se completan en celular con el D-pad táctil sin frustración.

### F6 — Contenido completo y final
- [ ] Mapas definitivos: casa, pueblo (plaza/kiosco/florería/parque), colina al atardecer.
- [ ] Guion íntegro en `src/data/dialogos.js` (≈60–90 líneas), NPCs colocados, 3 flores, 6 recuerdos.
- [ ] `Final.js`: escena de la colina, entrega del ramo, álbum de recuerdos, mensaje final pausado (palabras de Alex ya ajustadas), elección del abrazo, créditos con melodía y pétalos.
- [ ] `Title.js`: "toca para empezar" (desbloquea audio) + menú Jugar / Álbum / Créditos.
- **Gate:** partida completa de principio a fin, 6 recuerdos y el mensaje final visibles.

### F7 — QA, build y entrega
- [ ] QA de assets (`qa_assets.py` + hoja de contacto) y smoke test en navegador real con el skill **agent-browser**: título → casa → diálogo → recuerdo → pétalos 1 → pueblo → parque → pétalos 2 → final; screenshots de cada etapa en desktop y en viewport 390x844 (móvil).
- [ ] `build_single.py` → abrir `dist/…html` con `file://` y confirmar que funciona sin servidor ni red.
- [ ] Playtest manual de Alex con `docs/handoff.md` como checklist.
- [ ] `gh repo create un-jardin-para-liss --public --source=. --push` y activar Pages (`gh api -X POST repos/Alex-Alas/un-jardin-para-liss/pages -f source[branch]=main -f source[path]=/`).
- [ ] Compartir el repo con Claude (rama lista + `docs/plan-implementacion.md` y `docs/handoff.md` al día) para su revisión y co-implementación.
- [ ] Verificar el link en celular con agent-browser (viewport móvil) y pasárselo a Liss con una nota sugerida.
- [ ] Commits convencionales en español durante todo el proceso (`feat:`, `docs:`, `fix:`, `art:`, `chore:`).

---

## 4. Verificación

1. **Assets:** `python3 tools/qa_assets.py --json` (tamaños exactos, alpha válido, ≤N colores por sprite) + `contact_sheet.py` para inspección visual a escala real de juego.
2. **En navegador (agent-browser):** lista de pasos F7 con screenshots adjuntos que yo reviso (comparo contra la intención de diseño y `docs/arte.md`).
3. **Móvil:** viewport 390x844 y 844x390 — D-pad usable, texto legible, audio tras el gesto inicial, sin scroll accidental.
4. **Guardado:** avanzar, recargar, verificar que retoma con flores y recuerdos intactos.
5. **Offline / respaldo:** abrir el HTML único con `file://` (sin servidor) y jugar hasta el primer diálogo.
6. **Producción:** abrir la URL de Pages con agent-browser, verificar HTTP 200, que carga Phaser desde el repo y que las fotos se sirven bien.
7. **Prueba de la usuaria real:** que Liss pueda terminarlo sola, en su celular, sin instrucciones.

## 5. Criterios de aceptación
- Se juega entero en 6–10 min, **sin forma de perder** y sin errores en consola.
- 3 flores, 6 recuerdos con foto y mensajito, 2 escenas de pétalos, final con ramo + mensaje + créditos.
- Funciona en celular (táctil) y desktop (teclado); audio solo tras el gesto inicial.
- Guarda y retoma; arranca igual desde `file://` que desde Pages.
- `docs/` contiene idea, guion, arte, el plan y el handoff: listo para compartir el repo con Claude y seguir co-creando.
- `desktop-controller-powered-by-jev` intacto.

## 6. Riesgos y mitigaciones
- **La hoja de Liss no tiene 4 direcciones/animaciones** → plan B documentado (espejar L/R, ciclo simple ↑↓) o redibujar en su mismo estilo; se decide en F1 con datos.
- **Fuente sin acentos** → verificado en F2 con glifos de prueba; fallback VT323 o parche manual de glifos.
- **Fotos pesadas** → compresión a ≤200 KB c/u y carga diferida; el build único las inlinea.
- **iOS y autoplay de audio** → pantalla "toca para empezar".
- **Alcance en un solo día** → orden de recorte si falta tiempo: (1) escena 2 de pétalos en versión mínima, (2) álbum en menú, (3) pétalos ambientales. **Nunca** se recorta el final emotivo.
- **Privacidad** → Alex eligió fotos públicas en el link; los originales viven en `_referencias/` (gitignored).

## 7. Decisiones abiertas (Alex edita después)
- Mensaje final: **ya ajustado con las palabras de Alex ✓** (queda pendiente solo revisar el render en pantalla, línea por línea, en F6).
- Pies de foto de los 6 recuerdos (borrador en `docs/guion.md`).
- Nombres reales de NPCs (hoy: Doña Flora, el kiosquero, la niña, Michi el gato).
- ¿Melodía significativa para ellos? Por defecto compongo una original; si hay canción, se versiona a chiptune.
