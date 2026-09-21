#!/usr/bin/env python3
"""Revisa qué arte existe en assets/ y escribe el manifiesto que lee el juego.

Genera assets/manifest.json (fuente de verdad) y assets/manifest.js (lo que carga index.html).
Correr después de cualquier paso del pipeline de arte; el juego se adapta a lo que haya.

    .venv/bin/python tools/actualizar_manifest.py
"""

from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
MAPAS = ["casa", "pueblo", "floreria", "colina"]


def detectar() -> dict:
    fuentes = sorted(p.stem.replace("font_", "") for p in ASSETS.glob("font_*.png"))
    mapas = [m for m in MAPAS if (ASSETS / f"mapa_{m}.png").exists()]
    fotos = sorted(p.stem.replace("recuerdo_", "") for p in (ASSETS / "fotos").glob("*.jpg"))
    return {
        "fuente": bool(fuentes),
        "fuentes": fuentes,
        "atlas": (ASSETS / "atlas.png").exists() and (ASSETS / "atlas.json").exists(),
        "mapas": mapas,
        "fotos": fotos,
        "fotosPendientes": [
            f"r{i}" for i in range(1, 7) if f"r{i}" not in fotos
        ],
    }


def main() -> int:
    datos = detectar()
    (ASSETS / "manifest.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ASSETS / "manifest.js").write_text(
        "// Generado por tools/actualizar_manifest.py — no editar a mano.\n"
        "window.AG = window.AG || {};\n"
        f"AG.MANIFIESTO = {json.dumps(datos, ensure_ascii=False)}\n;",
        encoding="utf-8",
    )
    print(json.dumps(datos, ensure_ascii=False, indent=2))
    faltan = [m for m in MAPAS if m not in datos["mapas"]]
    print(f"mapas presentes: {datos['mapas'] or 'ninguno'} | faltan: {faltan or 'ninguno'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
