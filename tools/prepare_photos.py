#!/usr/bin/env python3
"""Prepara las fotos de los recuerdos: de la foto del celular al polaroid del juego.

    .venv/bin/python tools/prepare_photos.py
    .venv/bin/python tools/prepare_photos.py --lado 720 --peso 300

Entra `assets/source/fotos/r1.jpg` … `r6.jpg` (cualquier formato que abra Pillow) y sale
`assets/fotos/recuerdo_r1.jpg` … `recuerdo_r6.jpg`, cuadradas y livianas.

Tres decisiones, y el porqué de cada una:

- **cuadradas**: el marco del polaroid es casi cuadrado (176 × 168 px) y el juego rellena
  recortando desde arriba-izquierda. Si la foto entra vertical, el juego se queda con la franja
  de arriba y corta a alguien. Recortando acá se elige el encuadre a mano y no por descarte.
- **el recorte se corre hacia arriba**: en una selfie las caras están en el tercio superior, no
  en el centro geométrico.
- **≤ 300 KB**: son seis fotos y el juego se abre desde el celular. La calidad JPEG baja sola
  hasta que entra en el peso; nunca por debajo de 70, que ya se ve sucio.

Cambiar qué foto va en qué recuerdo es renombrar archivos en `assets/source/fotos/`: el número
manda, y el texto de cada recuerdo vive en `src/data/personajes.js`.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "assets" / "source" / "fotos"
DESTINO = RAIZ / "assets" / "fotos"
IDS = [f"r{i}" for i in range(1, 7)]
LADO = 720
PESO_MAX_KB = 300
CALIDAD_MAX = 92
CALIDAD_MIN = 70
ALTURA_DEL_RECORTE = 0.36   # 0 = pegado arriba, 0.5 = centrado. Las caras caen arriba del centro.
EXTENSIONES = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".JPG", ".JPEG", ".PNG")


def buscar(ident: str) -> Path | None:
    for extension in EXTENSIONES:
        ruta = ORIGEN / f"{ident}{extension}"
        if ruta.exists():
            return ruta
    return None


def cuadrar(imagen: Image.Image, lado: int) -> Image.Image:
    """Recorta al cuadrado más grande que quepa, corrido hacia arriba, y escala a `lado`."""
    ancho, alto = imagen.size
    corte = min(ancho, alto)
    x = (ancho - corte) // 2
    y = int((alto - corte) * ALTURA_DEL_RECORTE)
    recorte = imagen.crop((x, y, x + corte, y + corte))
    return recorte.resize((lado, lado), Image.LANCZOS)


def guardar(imagen: Image.Image, destino: Path, peso_max: int) -> tuple[int, int]:
    """Guarda bajando la calidad hasta entrar en el peso. Devuelve (calidad, kb)."""
    for calidad in range(CALIDAD_MAX, CALIDAD_MIN - 1, -3):
        buffer = io.BytesIO()
        imagen.save(buffer, "JPEG", quality=calidad, optimize=True, progressive=True)
        if buffer.tell() <= peso_max * 1024 or calidad == CALIDAD_MIN:
            destino.write_bytes(buffer.getvalue())
            return calidad, round(buffer.tell() / 1024)
    raise AssertionError("inalcanzable: el bucle siempre guarda en la última vuelta")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fotos del celular → polaroids del juego.")
    parser.add_argument("--lado", type=int, default=LADO, help=f"lado en píxeles (por defecto {LADO})")
    parser.add_argument("--peso", type=int, default=PESO_MAX_KB, help=f"KB máximos (por defecto {PESO_MAX_KB})")
    args = parser.parse_args()

    if not ORIGEN.exists():
        print(f"No existe {ORIGEN.relative_to(RAIZ)}. Poné ahí r1.jpg … r6.jpg.", file=sys.stderr)
        return 1

    DESTINO.mkdir(parents=True, exist_ok=True)
    faltan = []
    for ident in IDS:
        origen = buscar(ident)
        if origen is None:
            faltan.append(ident)
            continue
        with Image.open(origen) as cruda:
            # exif_transpose: las fotos de celular vienen giradas por metadatos y sin esto se
            # recortarían de costado.
            imagen = ImageOps.exif_transpose(cruda).convert("RGB")
            original = imagen.size
            calidad, kb = guardar(cuadrar(imagen, args.lado), DESTINO / f"recuerdo_{ident}.jpg", args.peso)
        print(f"  · {ident}: {original[0]}×{original[1]} → {args.lado}×{args.lado}, "
              f"calidad {calidad}, {kb} KB  ({origen.name})")

    if faltan:
        print(f"faltan en {ORIGEN.relative_to(RAIZ)}: {', '.join(faltan)}", file=sys.stderr)
    print("Recordá correr tools/actualizar_manifest.py para que el juego las cargue.")
    return 1 if faltan else 0


if __name__ == "__main__":
    raise SystemExit(main())
