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
  sonriendo). Los de los NPCs no se recortan de su sprite: a 16 px de ancho la cara no tiene
  lugar para la expresión, así que se dibujan aparte a 24 × 24 y se duplican (`arte_extra.py`).
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
| `atlas.png` / `atlas.json` | 256×237 hoy, 68 frames | 1 | sprites, iconos, retratos | `tools/generate_sprites.py` |
| `font_pixel.png` / `.xml` | variable | 2 (8 px y 16 px) | todo el texto | `tools/generate_font.py` |
| `mapa_casa.png` | 20×14 tiles | 1 | interior | `tools/render_maps.py` |
| `mapa_pueblo.png` | 48×32 tiles | 1 | exterior principal | `tools/render_maps.py` |
| `mapa_floreria.png` | 16×12 tiles | 1 | interior | `tools/render_maps.py` |
| `mapa_colina.png` | 32×20 tiles | 1 | final, paleta de atardecer | `tools/render_maps.py` |
| `recuerdo_r1..r6.jpg` | 720×720 | 6 | polaroids | `tools/prepare_photos.py` (✅) |
| sprites de Liss | 16×34 | 8 direcciones × (2 idle + 4 caminata) | protagonista | `tools/generate_sprites.py` (✅ F1) |
| sprites de los demás | 16×34 | Alex, Flora, Beto, Sofi, Michi × (1 quieto + 1 respiración) | NPCs | `tools/arte_extra.py` (✅ F2) |
| retratos | 48×48 | Liss × 2 emociones + los 5 NPCs | diálogos | Liss: `generate_sprites.py`; el resto: `arte_extra.py` (✅) |
| iconos UI | 16×16 | `ui_corazon`, `ui_flor` | HUD y punto de guardado | `tools/arte_extra.py` (✅) |
| `ramo_0` | 16×24 | 1 | el ramo de la colina | `tools/arte_extra.py` (✅) |
| pétalo y hoja seca | 5×6 y 6×5 | 2 | partículas del minijuego | `src/systems/fx.js` (por código, no atlas) |
| terreno y objetos | 16×16 | 7 terrenos + 15 objetos | pintados dentro del PNG del mapa | `tools/tiles.py` (✅ F2) |

## Nombres de frames (contrato con el código)

Regla: `{personaje}_{accion}_{direccion}_{n}`. Las ocho direcciones, en español y en el orden de
la hoja: `abajo`, `abajo_derecha`, `derecha`, `arriba_derecha`, `arriba`, `arriba_izquierda`,
`izquierda`, `abajo_izquierda`.

```
liss_idle_<dirección>_0 / _1          # quieta + respiración         (16 frames)
liss_camina_<dirección>_0 .. _3       # ciclo de caminata            (32 frames)
retrato_liss_normal   retrato_liss_feliz                             ( 2 frames)
```

Lo que aporta `tools/arte_extra.py` (F2), con el mismo contrato:

```
npc_<id>_abajo_0 / _1       # Alex, Flora, Beto, Sofi, Michi: quieto + respiración
retrato_<id>_normal         # los cinco, 48×48
ui_corazon   ui_flor   ramo_0
```

Los NPCs traen una sola dirección porque en el juego nunca caminan. Si algún día uno se mueve,
se agregan las ocho con estos mismos nombres y `AG.direccionDibujable()` las toma sola.

**Los objetos no están en el atlas, y es a propósito.** El mostrador de la florería mide ocho
tiles y un sprite de 16 px no lo cubre; pintarlos dentro del PNG del mapa (`tools/tiles.py`) los
resuelve de cualquier tamaño. Los NPCs sí son sprites, porque respiran y se les habla:
`render_maps.py` deja de pintar en el mapa a cada NPC que ya tenga su frame —por personaje, no
todo o nada, para que el primero con arte no borre a los que aún no lo tienen.

## Mapas

Cada mapa se dibuja desde un archivo ASCII (`maps/*.txt`, ver leyenda en `docs/handoff.md`). El
script pinta el pasto con variación determinista, bordes de camino, sombras de árboles y detalles
(decoración de flores amarillas) y exporta la capa de colisión. Reglas:

- Los caminos siempre conectan con algo: nunca un camino que no lleve a ningún lado.
- Las zonas de interés tienen un color distinto en el piso (más claro) para guiar la vista.
- El mapa del pueblo es el más denso: NPCs a la vista desde lejos, nada escondido tras árboles.
- La colina usa la variante de atardecer: `#! luz: atardecer` en `maps/colina.txt` remapea los
  colores del PNG hacia el naranja. Es un remapeo y no una capa encima, así el mapa ya llega
  teñido; el velo del motor (`AG.FX.washAtardecer`) queda suave, solo para teñir a los sprites.

### Mapas pintados

La casa, el pueblo y la colina ya no se arman con tiles: son ilustraciones
(`assets/source/escenarios/*.webp`) escaladas al tamaño de siempre (256×256, 768×512 y 512×320),
así las distancias, los NPCs y las puertas quedaron donde estaban. Su `maps/<n>.txt` dice en
píxeles lo que la imagen no dice (formato en `tools/escenarios.py`):

- **colisión fina**: celdas de 4 px dibujadas con rectángulos, elipses y polígonos;
- **frentes**: recortes de la pintura (copas, pinos, techos, el farol, el cartel) con la línea
  donde tocan el piso. El motor los dibuja encima de Liss solo cuando ella pasa por detrás, y los
  vuelve a medias transparentes si la tapan casi entera. El borde de cada recorte se ajusta solo
  a la silueta pintada mirando colores (`#! ajuste: 3`);
- **retoques**: se borraron las marcas de agua y los muñequitos que marcaban los guardados, y al
  cuarto se le pintaron lo que el guion pide y la ilustración no trae: el espejo (en el costado
  del ropero), el 21 marcado en la libreta del escritorio y la nota junto a la puerta.

`node tools/validar_contenido.js` recorre cada mapa con la caja de pies de Liss y falla si alguna
puerta, objeto o NPC queda inalcanzable.

## QA de arte (puertas de calidad)

```bash
.venv/bin/python tools/generate_sprites.py --inspeccionar   # cómo se lee la hoja
.venv/bin/python tools/generate_sprites.py --contacto       # atlas + hoja de contacto en dist/
.venv/bin/python tools/arte_extra.py --contacto             # solo los NPCs, ampliados ×6
.venv/bin/python tools/qa_assets.py --json                  # tamaños, alpha, cantidad de colores
```

`qa_assets.py` cuenta los colores **por frame del atlas**, no del PNG entero: el tope de 24 es
por asset, y un atlas con Liss, cinco NPCs, siete retratos y los iconos suma 47 sin que ninguno
de ellos incumpla la regla.

Requisitos: cada sprite con su tamaño exacto, alpha de 0/255 (sin semitransparencias), ≤24 colores,
sin bordes recortados y legible sobre el pasto del pueblo. Un asset no está listo hasta verse a
tamaño real contra el fondo donde va a vivir.
