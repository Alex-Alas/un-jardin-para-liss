# Arte — UN JARDÍN PARA LISS

## Marco técnico

| Cosa | Valor | Nota |
|---|---|---|
| Resolución interna | 480 × 270 | 16:9, escalado entero con `pixelArt: true` |
| Tile | 16 × 16 px | mapas de 30 × 17 tiles visibles |
| Sprite de personaje | 16 × 34 px | Liss mide 32 px (2 tiles); 8 direcciones, idle + 4 frames de caminata |
| Retrato de diálogo | 48 × 48 px | se dibuja a ×2 en la caja de diálogo |
| Polaorid / foto | 96 × 96 px (foto) | marco dibujado en código, foto real dentro |
| Iconos UI | 16 × 16 px | corazón, flor, pétalo, flecha |
| Filtrado | nearest neighbor | sin antialias, sin suavizado, sin escalados raros |

## La hoja de Liss manda

`assets/source/liss-sheet.png` es la fuente de verdad del estilo. `tools/generate_sprites.py
--inspeccionar` reporta cómo se lee; **todo** el arte nuevo se produce para encajar con ella:
mismos contornos, misma densidad de detalle, misma luz.

### Reporte de la hoja (F1, 21.09)

```
tamaño 1536 × 1024 · 213 938 colores (render suave, no pixel art puro) · 96 frames
banda 0  estático    24 frames   alto 108–110   ancho 43–53
banda 1  estático    24 frames   alto 107–110   ancho 42–52
banda 2  movimiento  24 frames   alto 107–113   ancho 43–52
banda 3  movimiento  24 frames   alto 110–116   ancho 42–52
```

Ocho direcciones rotuladas (S, SE, E, NE, N, NW, W, SW), tres poses por fila y dos filas por
sección: 6 poses quietas y 6 caminando por dirección. **E mira a la derecha de la pantalla.**

### Decisiones que salieron de ese reporte

- **No hay plan B**: la hoja trae las 8 direcciones, así que el juego se movió a 8 direcciones
  (diagonales incluidas en teclado y en el D-pad táctil, con el paso repartido entre ejes).
  Si alguna vez llega una hoja de 4, `AG.direccionDibujable()` cae sola al eje que manda.
- **Escala**: 32 px de alto (2 tiles) en una caja de 16 × 34. Es lo más chico donde la cara
  todavía se lee; se probó 24 y 28 y se pierde. El tile sigue en 16, así que los mapas no cambian.
- **Una escala por banda**: la hoja dibujó las cuatro bandas a tamaños apenas distintos y, sin
  normalizar por banda, Liss crecía un píxel al empezar a caminar.
- **Quieta**: una pose por dirección (la más cercana al promedio de las seis) más un segundo frame
  de respiración generado por código (el torso baja 1 px), a 1.4 fps.
- **Caminata**: ciclo de 4 a 8 fps armado midiendo cuánto se separan los pies —paso abierto, paso
  junto, el otro paso abierto, paso junto—, porque la hoja no garantiza un orden de animación.
- **Retratos**: 48 × 48, recortados de dos poses de frente elegidas a mano (una neutra y una
  sonriendo). Los demás personajes todavía muestran su inicial en la caja de diálogo.
- **La sombra del piso no se importa**: el juego pone la suya; la de la hoja se descarta por color.

## Paleta

`AG.CFG.COLORES` (en `src/config.js`) es la paleta maestra del mundo: 22 colores cálidos, con
amarillo de protagonista (`#ffd23f`) y su claro (`#ffe98a`).

Liss trae la suya, derivada de su hoja y compartida por sus 50 frames (23 entradas contando la
transparencia; una sola paleta para todos, porque si cada frame se cuantiza aparte la animación
titila):

```
#fef2df #fbddc9 #fbcfbb #fbc3ae #edc6b4   vestido y sus luces
#f1af9a #ed8f6e #cc9a8f #c07967 #b16757   piel y sombras de piel
#9c5347 #65454a #61305a #472d3a #352a3c   transiciones y contornos suaves
#362233 #2c2334 #2a2030 #271d2e #1f1727 #0e0918   pelo y tinta
#9a4a80   el corazón morado (se le reserva lugar a mano: es el único acento frío)
```

Reglas:

- Máximo **24 colores por asset**, contando la transparencia.
- El amarillo es del jugador y de las flores: nada más en el mapa compite con ese tono.
- Sombras con azul/morado frío, nunca con negro puro (el negro es solo contorno).
- Contorno de 1 px en tinta (`#1b1420`) para personajes y objetos interactuables; los fondos no
  llevan contorno.

## Reglas de estilo

- **Formas:** redondeadas y gorditas; siluetas legibles a 1×. Un objeto, una idea.
- **Luz:** viene de arriba-izquierda, suave, sin degradados largos (2 tonos por material).
- **Detalle:** caras simples (2 px de ojo), sin dientes, sin líneas de nariz.
- **Animación:** ciclo de caminata de 4 frames a 8 fps; quieta, respira con 2 frames a 1.4 fps.
  Al hablar, el retrato se mueve 1 px y el personaje hace un pequeño rebote.
- **Nada de texto dentro del arte**: el texto lo pone el motor (fuente bitmap), nunca el PNG.
- Emoción > realismo: si un detalle no se lee a tamaño real, se elimina.

## Manifiesto de assets

| Asset | Tamaño | Cantidad | Uso | Origen |
|---|---|---|---|---|
| `atlas.png` / `atlas.json` | 256×153 hoy | 1 | sprites, iconos, retratos | `tools/generate_sprites.py` |
| `font_pixel.png` / `.xml` | variable | 2 (8 px y 16 px) | todo el texto | `tools/generate_font.py` |
| `mapa_casa.png` | 20×14 tiles | 1 | interior | `tools/render_maps.py` |
| `mapa_pueblo.png` | 48×32 tiles | 1 | exterior principal | `tools/render_maps.py` |
| `mapa_floreria.png` | 16×12 tiles | 1 | interior | `tools/render_maps.py` |
| `mapa_colina.png` | 32×20 tiles | 1 | final, paleta de atardecer | `tools/render_maps.py` |
| `recuerdo_01..06.jpg` | 720 px lado mayor | 6 | polaroids | `tools/prepare_photos.py` |
| sprites de Liss | 16×34 | 8 direcciones × (2 idle + 4 caminata) | protagonista | `tools/generate_sprites.py` (✅ F1) |
| sprites de los demás | 16×34 | Alex, Flora, Beto, Sofi, Michi | NPCs | pendiente: hoy los pinta el mapa |
| retratos | 48×48 | Liss × 2 emociones (✅); el resto pendiente | diálogos | `tools/generate_sprites.py` |
| iconos UI | 16×16 | corazón, flor, pétalo, hoja seca | HUD y escenas | `tools/generate_sprites.py` |

## Nombres de frames (contrato con el código)

Regla: `{personaje}_{accion}_{direccion}_{n}`. Las ocho direcciones, en español y en el orden de
la hoja: `abajo`, `abajo_derecha`, `derecha`, `arriba_derecha`, `arriba`, `arriba_izquierda`,
`izquierda`, `abajo_izquierda`.

```
liss_idle_<dirección>_0 / _1          # quieta + respiración         (16 frames)
liss_camina_<dirección>_0 .. _3       # ciclo de caminata            (32 frames)
retrato_liss_normal   retrato_liss_feliz                             ( 2 frames)
```

Lo que el código busca y todavía no existe (cae con elegancia a formas o a la inicial del nombre):

```
npc_<id>_abajo_0   retrato_<id>_normal      # Alex, Flora, Beto, Sofi, Michi
ui_corazon   ui_flor   ui_petalo   ui_hoja_seca      ramo_0
tile_pasto_0..2   tile_camino_0..2   tile_agua_0..1   tile_arbol_0..1
```

Mientras el atlas no traiga frames `npc_`/`objeto_`, `tools/render_maps.py` sigue pintando los
objetos dentro del PNG del mapa (si no, los bancos y los NPCs desaparecerían del pueblo).

## Mapas

Cada mapa se dibuja desde un archivo ASCII (`maps/*.txt`, ver leyenda en `docs/handoff.md`). El
script pinta el pasto con variación determinista, bordes de camino, sombras de árboles y detalles
(decoración de flores amarillas) y exporta la capa de colisión. Reglas:

- Los caminos siempre conectan con algo: nunca un camino que no lleve a ningún lado.
- Las zonas de interés tienen un color distinto en el piso (más claro) para guiar la vista.
- El mapa del pueblo es el más denso: NPCs a la vista desde lejos, nada escondido tras árboles.
- La colina usa la variante de atardecer: cielo naranja, sombras largas hacia la derecha.

## QA de arte (puertas de calidad)

```bash
.venv/bin/python tools/generate_sprites.py --inspeccionar   # cómo se lee la hoja
.venv/bin/python tools/generate_sprites.py --contacto       # atlas + hoja de contacto en dist/
.venv/bin/python tools/qa_assets.py --json                  # tamaños, alpha, cantidad de colores
```

Requisitos: cada sprite con su tamaño exacto, alpha de 0/255 (sin semitransparencias), ≤24 colores,
sin bordes recortados y legible sobre el pasto del pueblo. Un asset no está listo hasta verse a
tamaño real contra el fondo donde va a vivir.
