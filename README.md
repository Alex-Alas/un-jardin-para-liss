# UN JARDÍN PARA LISS

Un jueguito corto, en pixel art y con olor a indie retro, hecho para Liss por el **Día de las
Flores Amarillas** (21 de septiembre).

Liss despierta, encuentra una nota y el pueblo entero la espera con flores amarillas. Se juega en
6–10 minutos, no se puede perder, y hay un final guardado para ella.

**Jugar:** https://alex-alas.github.io/un-jardin-para-liss/

- Celular: táctil (D-pad y botón A en pantalla).
- Compu: flechas o WASD para moverte, `Z` / `Enter` para hablar y confirmar, `Esc` para el menú.
- El audio arranca cuando tocas la pantalla por primera vez (culpa de los navegadores, no nuestra).

## Estado

| Fase | Qué | Estado |
|---|---|---|
| F0 | Repo, scaffold, docs | ✅ |
| F1 | Marco técnico a partir de la hoja de sprites de Liss | ⏳ |
| F2 | Pipeline de arte (`tools/`, Python + Pillow) | ⏳ |
| F3 | Núcleo jugable (movimiento, colisión, guardado) | ⏳ |
| F4 | Diálogos, recuerdos con fotos, música chiptune | ⏳ |
| F5 | Las 2 escenas de pétalos | ⏳ |
| F6 | Contenido completo y final | ⏳ |
| F7 | QA, build de un archivo, GitHub Pages | ⏳ |

Detalle completo en [`docs/plan-implementacion.md`](docs/plan-implementacion.md).

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
.venv/bin/python tools/render_maps.py      # mapas ASCII -> PNG + colisiones
.venv/bin/python tools/generate_font.py    # fuente bitmap desde Press Start 2P (OFL)
.venv/bin/python tools/build_single.py     # dist/un-jardin-para-liss.html (un solo archivo)
.venv/bin/python tools/qa_assets.py        # reporte de QA de assets
```

Sin bundler, sin `npm install`: Phaser va vendorizado (`vendor/phaser.min.js`) y el arte se genera
con scripts de Python. El juego corre también abriendo `index.html` directamente.

## Créditos y licencias

- Código: MIT (ver [`LICENSE`](LICENSE)).
- Pixel art, historia y fotos: © Alex-Alas — todos los derechos reservados. Este repo es un regalo.
- [Phaser](https://phaser.io) 4.2.1, MIT (ver [`vendor/LICENSE-phaser.md`](vendor/LICENSE-phaser.md)).
- Fuente [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) (CodeMan38), SIL Open Font License 1.1.
