# Arte — UN JARDÍN PARA LISS

## Marco técnico

| Cosa | Valor | Nota |
|---|---|---|
| Resolución interna | 480 × 270 | 16:9, escalado entero con `pixelArt: true` |
| Tile | 16 × 16 px | mapas de 30 × 17 tiles visibles |
| Sprite de personaje | 16 × 24 px | 2 frames de caminata + idle, 4 direcciones |
| Retrato de diálogo | 48 × 48 px | se dibuja a ×2 en la caja de diálogo |
| Polaorid / foto | 96 × 96 px (foto) | marco dibujado en código, foto real dentro |
| Iconos UI | 16 × 16 px | corazón, flor, pétalo, flecha |
| Filtrado | nearest neighbor | sin antialias, sin suavizado, sin escalados raros |

**Se resuelve en F1:** si la hoja de Liss usa otra grilla (p. ej. 32×32), se adopta *su* tamaño como
medida del proyecto y se ajusta `AG.CFG` (tile, sprite, resolución) en un solo lugar.

## La hoja de Liss manda

`assets/source/liss-sheet.png` es la fuente de verdad del estilo. Antes de dibujar nada se corre
`tools/generate_sprites.py --inspeccionar`, que reporta: tamaño total, grilla de frames, direcciones
presentes, paleta exacta y cantidad de colores. Ese reporte se pega acá abajo y **todo** el arte
nuevo se produce para encajar: mismos contornos, misma densidad de detalle, misma luz.

**Si la hoja no tiene 4 direcciones o animación:**
- Plan B1: una sola pose → se usa para las 4 direcciones con espejado horizontal y un ciclo de
  caminata mínimo (respiración de 2 px).
- Plan B2: solo frente y espalda → izquierda/derecha se resuelven espejando el frente.
- Plan B3: se redibuja el ciclo completo imitando su estilo. Se documenta la decisión acá.

## Paleta

`AG.CFG.COLORES` (en `src/config.js`) es la paleta maestra: 22 colores cálidos, con amarillo de
protagonista (`#ffd23f`) y su claro (`#ffe98a`). Reglas:

- Máximo **24 colores por asset**, contando la transparencia.
- El amarillo es del jugador y de las flores: nada más en el mapa compite con ese tono.
- Sombras con azul/morado frío, nunca con negro puro (el negro es solo contorno).
- Contorno de 1 px en tinta (`#1b1420`) para personajes y objetos interactuables; los fondos no
  llevan contorno.

## Reglas de estilo

- **Formas:** redondeadas y gorditas; siluetas legibles a 1×. Un objeto, una idea.
- **Luz:** viene de arriba-izquierda, suave, sin degradados largos (2 tonos por material).
- **Detalle:** caras simples (2 px de ojo), sin dientes, sin líneas de nariz.
- **Animación:** 2 frames por paso, 150 ms por frame; al hablar, el retrato se mueve 1 px y el
  personaje hace un pequeño rebote.
- **Nada de texto dentro del arte**: el texto lo pone el motor (fuente bitmap), nunca el PNG.
- Emoción > realismo: si un detalle no se lee a tamaño real, se elimina.

## Manifiesto de assets

| Asset | Tamaño | Cantidad | Uso | Origen |
|---|---|---|---|---|
| `atlas.png` / `atlas.json` | 512×512 aprox. | 1 | sprites, tiles, iconos, retratos | `tools/generate_sprites.py` |
| `font_pixel.png` / `.xml` | variable | 2 (8 px y 16 px) | todo el texto | `tools/generate_font.py` |
| `mapa_casa.png` | 20×14 tiles | 1 | interior | `tools/render_maps.py` |
| `mapa_pueblo.png` | 48×32 tiles | 1 | exterior principal | `tools/render_maps.py` |
| `mapa_floreria.png` | 16×12 tiles | 1 | interior | `tools/render_maps.py` |
| `mapa_colina.png` | 32×20 tiles | 1 | final, paleta de atardecer | `tools/render_maps.py` |
| `recuerdo_01..06.jpg` | 720 px lado mayor | 6 | polaroids | `tools/prepare_photos.py` |
| sprites de personajes | 16×24 | 6 personajes | Liss, Alex, Flora, Beto, Sofi, Michi | `tools/generate_sprites.py` |
| retratos | 48×48 | 6 personajes × 2 emociones | diálogos | `tools/generate_sprites.py` |
| iconos UI | 16×16 | corazón, flor, pétalo, hoja seca | HUD y escenas | `tools/generate_sprites.py` |

## Nombres de frames (contrato con el código)

```
liss_idle_abajo_0        liss_camina_abajo_0 / _1
liss_idle_arriba_0       liss_camina_arriba_0 / _1
liss_idle_izquierda_0    liss_camina_izquierda_0 / _1
liss_idle_derecha_0      liss_camina_derecha_0 / _1
retrato_liss_normal      retrato_liss_feliz
tile_pasto_0..2   tile_camino_0..2   tile_agua_0..1   tile_arbol_0..1
ui_corazon   ui_flor   ui_petalo   ui_hoja_seca
```

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
.venv/bin/python tools/qa_assets.py --json          # tamaños, alpha, cantidad de colores
.venv/bin/python tools/contact_sheet.py             # hoja de contacto sobre tablero de ajedrez
```

Requisitos: cada sprite con su tamaño exacto, alpha de 0/255 (sin semitransparencias), ≤24 colores,
sin bordes recortados y legible sobre el pasto del pueblo. Un asset no está listo hasta verse a
tamaño real contra el fondo donde va a vivir.
