# UN JARDÍN PARA LISS

Un jueguito corto, en pixel art y con olor a indie retro, hecho para Liss por el **Día de las
Flores Amarillas** (21 de septiembre).

Liss despierta, encuentra una nota y el pueblo entero la espera con flores amarillas. Se juega en
6–10 minutos, no se puede perder, y hay un final guardado para ella.

**Jugar:** https://alex-alas.github.io/un-jardin-para-liss/

- Celular: táctil (D-pad y botón A en pantalla).
- Compu: flechas o WASD para moverte (también en diagonal), `Z` / `Enter` para hablar y confirmar,
  `Esc` para el menú.
- El audio arranca cuando tocas la pantalla por primera vez (culpa de los navegadores, no nuestra).

## Estado

| Fase | Qué | Estado |
|---|---|---|
| F0 | Repo, scaffold, docs | ✅ |
| F1 | Hoja de sprites de Liss → sprite jugable | ✅ (camina en 8 direcciones) |
| F2 | Pipeline de arte (`tools/`, Python + Pillow) | 🟡 (falta el arte de NPCs, objetos y tiles) |
| F3 | Núcleo jugable (movimiento, colisión, guardado) | ✅ |
| F4 | Diálogos, recuerdos con fotos, música chiptune | 🟡 (faltan las fotos y los `.wav`; hoy hay melodías sintetizadas) |
| F5 | Las escenas de pétalos | 🟡 (la del pueblo está; falta la segunda variante) |
| F6 | Contenido completo y final | ✅ |
| F7 | QA, build de un archivo, GitHub Pages | 🟡 (QA y build listos; falta publicar en Pages) |

Detalle completo en [`docs/plan-implementacion.md`](docs/plan-implementacion.md).

### Qué se puede jugar hoy

La partida está completa de punta a punta: despertar en la casa, el pueblo, la florería, el
minijuego de pétalos, el álbum y la escena final en la colina con su mensaje y los créditos.
Se verificó con un QA automático en un navegador real, en escritorio y en celular:

```bash
tools/qa_navegador.sh     # juega la partida completa y guarda capturas
```

### Qué falta

1. El arte de los demás: Alex, Doña Flora y el resto de NPCs, los objetos del pueblo y los tiles
   (hoy son bloques de color pintados dentro del mapa). Liss ya está, y su hoja manda el estilo.
2. Las fotos de verdad en `assets/fotos/` (hoy el marco dice "foto pendiente").
3. La segunda escena de pétalos y publicar en GitHub Pages.


## Para co-crear con Claude

- [`docs/idea.md`](docs/idea.md) — qué es el juego y por qué así.
- [`docs/guion.md`](docs/guion.md) — historia, diálogos y recuerdos (todo editable).
- [`docs/arte.md`](docs/arte.md) — brief de arte, paleta y reglas de estilo.
- [`docs/plan-implementacion.md`](docs/plan-implementacion.md) — plan por fases y criterios de aceptación.
- [`docs/handoff.md`](docs/handoff.md) — encargo técnico autocontenido: contratos entre archivos, formatos de datos y checklist de revisión.

## Desarrollo

```bash
python3 -m http.server 8000     # servir el juego en http://localhost:8000
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/generate_sprites.py # hoja de Liss -> assets/atlas.png + atlas.json
.venv/bin/python tools/render_maps.py      # mapas ASCII -> PNG + colisiones
.venv/bin/python tools/generate_font.py    # fuente bitmap desde Press Start 2P (OFL)
.venv/bin/python tools/build_single.py     # dist/un-jardin-para-liss.html (un solo archivo)
.venv/bin/python tools/actualizar_manifest.py  # qué arte existe (lo lee el juego al arrancar)
.venv/bin/python tools/qa_assets.py        # reporte de QA de assets
```

Sin bundler, sin `npm install`: Phaser va vendorizado (`vendor/phaser.min.js`) y el arte se genera
con scripts de Python. El juego corre también abriendo `index.html` directamente.

## Créditos y licencias

- Código: MIT (ver [`LICENSE`](LICENSE)).
- Pixel art, historia y fotos: © Alex-Alas — todos los derechos reservados. Este repo es un regalo.
- [Phaser](https://phaser.io) 4.2.1, MIT (ver [`vendor/LICENSE-phaser.md`](vendor/LICENSE-phaser.md)).
- Fuente [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) (CodeMan38), SIL Open Font License 1.1.
