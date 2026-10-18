#!/usr/bin/env python3
"""Prepara la música: de los .mp3 que salen de Gemini a las pistas que carga el juego.

    .venv/bin/python tools/preparar_musica.py
    .venv/bin/python tools/preparar_musica.py --kbps 96

Entran los originales en `assets/source/musica/` (con el nombre que les puso Gemini, con o sin
prefijo) y sale `assets/musica/<pista>.mp3`. Necesita `ffmpeg` instalado en el sistema.

Tres decisiones, y el porqué de cada una:

- **misma sonoridad para todas** (-16 LUFS, normalización en dos pasadas): Gemini entrega cada
  pista a su volumen, y sin esto el pueblo grita y el final susurra. El volumen de la música en
  el juego lo pone después `src/audio/chiptune.js`, uno solo para todas.
- **sin silencio al principio ni al final**: las pistas se repiten en loop, y medio segundo de
  aire de más se nota en cada vuelta.
- **128 kbps**: son siete pistas de dos a tres minutos y el juego se abre desde el celular.
  Así pesan ~18 MB entre todas, en vez de los 27 MB originales.

Qué original va en qué pista es el diccionario PISTAS: para cambiar una canción, se cambia el
nombre ahí (o se reemplaza el archivo) y se vuelve a correr esto y tools/actualizar_manifest.py.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "assets" / "source" / "musica"
DESTINO = RAIZ / "assets" / "musica"

# pista del juego -> título que le puso Gemini. Dónde suena cada una: src/audio/chiptune.js.
PISTAS = {
    "interiores": "petals_by_the_window_pane",   # la casa y la florería
    "pueblo": "yellow_petals_on_the_path",
    "petalos1": "golden_petals_afternoon",
    "petalos2": "chasing_golden_leaves",
    "colina": "hillside_promise",
    "final": "last_light_at_the_summit",
    "creditos": "after_the_final_petal",         # también el título y el álbum
}

LUFS = -16
PICO = -1.5
UMBRAL_SILENCIO = "-55dB"
# Recorte: de arriba se deja apenas un respiro; del final, lo justo para que la cola no corte.
RECORTE = (
    f"silenceremove=start_periods=1:start_threshold={UMBRAL_SILENCIO}:start_silence=0.05,"
    "areverse,"
    f"silenceremove=start_periods=1:start_threshold={UMBRAL_SILENCIO}:start_silence=0.3,"
    "areverse"
)


def buscar(titulo: str) -> Path | None:
    candidatos = sorted(ORIGEN.glob(f"*{titulo}*.mp3"))
    return candidatos[0] if candidatos else None


def medir(ruta: Path) -> dict:
    """Primera pasada de loudnorm: mide el original ya recortado."""
    proceso = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(ruta),
         "-af", f"{RECORTE},loudnorm=I={LUFS}:TP={PICO}:LRA=11:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    salida = proceso.stderr
    return json.loads(salida[salida.rindex("{"):salida.rindex("}") + 1])


def convertir(ruta: Path, destino: Path, kbps: int) -> dict:
    m = medir(ruta)
    filtro = (
        f"{RECORTE},loudnorm=I={LUFS}:TP={PICO}:LRA=11"
        f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
        f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
        f":offset={m['target_offset']}:linear=true,aresample=44100"
    )
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(ruta),
         "-af", filtro, "-map_metadata", "-1", "-fflags", "+bitexact",
         "-c:a", "libmp3lame", "-b:a", f"{kbps}k", str(destino)],
        check=True,
    )
    return m


def duracion(ruta: Path) -> float:
    proceso = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
        capture_output=True, text=True, check=True,
    )
    return float(proceso.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kbps", type=int, default=128, help="bitrate de salida (por defecto 128)")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        print("Falta ffmpeg: instalalo (apt install ffmpeg / brew install ffmpeg) y volvé a correr.", file=sys.stderr)
        return 1
    DESTINO.mkdir(parents=True, exist_ok=True)

    faltan = []
    total = 0
    for pista, titulo in PISTAS.items():
        original = buscar(titulo)
        if not original:
            faltan.append(f"{pista} ({titulo}.mp3)")
            continue
        destino = DESTINO / f"{pista}.mp3"
        medida = convertir(original, destino, args.kbps)
        peso = destino.stat().st_size
        total += peso
        print(f"  {pista:11s} <- {original.name:34s} {duracion(destino):6.1f} s  "
              f"{peso / 1024 / 1024:4.1f} MB  (venía a {float(medida['input_i']):.1f} LUFS)")

    print(f"listo: {total / 1024 / 1024:.1f} MB en {DESTINO.relative_to(RAIZ)}")
    if faltan:
        print("sin original (suena el chiptune en su lugar): " + ", ".join(faltan))
    print("Recordá correr tools/actualizar_manifest.py para que el juego las cargue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
