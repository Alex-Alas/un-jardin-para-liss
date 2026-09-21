#!/usr/bin/env bash
# Prepara un navegador headless y corre el QA de la partida completa.
#
#   tools/qa_navegador.sh
#
# No toca el sistema: crea un venv con playwright en un directorio temporal, usa el chromium
# ya descargado (o lo baja una vez) y, si al sistema le faltan librerías que chromium pide,
# las descarga como .deb y las extrae localmente para usarlas con LD_LIBRARY_PATH.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENTORNO="${QA_ENTORNO:-/tmp/qa-un-jardin}"
PUERTO="${QA_PUERTO:-8017}"
UV="${UV:-$HOME/.local/bin/uv}"

mkdir -p "$ENTORNO"
cd "$ENTORNO"

if [ ! -x "$ENTORNO/venv/bin/python" ]; then
  echo "· creando entorno de QA en $ENTORNO"
  "$UV" venv venv --python 3.11 >/dev/null
  "$UV" pip install -q --python venv/bin/python playwright >/dev/null
fi

if [ ! -d "$HOME/.cache/ms-playwright" ]; then
  echo "· descargando chromium"
  "$ENTORNO/venv/bin/playwright" install chromium
fi

# Del caché de playwright: preferir el headless shell (más liviano) y si no, el chromium completo.
CACHE="$HOME/.cache/ms-playwright"
EXE_COMPLETO="$(ls -d "$CACHE"/chromium-*/chrome-linux/chrome 2>/dev/null | head -1 || true)"
EXE_SHELL="$(ls -d "$CACHE"/chromium_headless_shell-*/chrome-headless-shell-linux-*/chrome-headless-shell 2>/dev/null | head -1 || true)"
export QA_CHROMIUM="${QA_CHROMIUM:-${EXE_SHELL:-$EXE_COMPLETO}}"

# Librerías del sistema que falten: se extraen .deb aquí, sin sudo.
LIBS="$ENTORNO/libs"
if [ -n "$QA_CHROMIUM" ] && ldd "$QA_CHROMIUM" 2>/dev/null | grep -q "not found"; then
  echo "· faltan librerías del sistema: se extraen .deb en $LIBS"
  mkdir -p "$LIBS/deb" "$LIBS/extract"
  (cd "$LIBS/deb" && apt-get download libnspr4 libnss3 libatk1.0-0 libatspi2.0-0 libxdamage1 >/dev/null 2>&1 || true)
  for deb in "$LIBS/deb"/*.deb; do dpkg -x "$deb" "$LIBS/extract" 2>/dev/null || true; done
fi
export LD_LIBRARY_PATH="$LIBS/extract/usr/lib/aarch64-linux-gnu:${LD_LIBRARY_PATH:-}"

echo "· sirviendo el juego en http://localhost:$PUERTO"
(cd "$RAIZ" && python3 -m http.server "$PUERTO" >/dev/null 2>&1) &
SERVIDOR=$!
trap 'kill $SERVIDOR 2>/dev/null || true' EXIT
sleep 1

echo "· jugando la partida completa con capturas"
"$ENTORNO/venv/bin/python" "$RAIZ/tools/qa_navegador.py" "http://localhost:$PUERTO" "${QA_SALIDA:-$ENTORNO/capturas}"

echo "· capturas en ${QA_SALIDA:-$ENTORNO/capturas}"
