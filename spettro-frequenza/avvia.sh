#!/usr/bin/env bash
# Linux: avvia lo Spettro Frequenza
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Spettro Frequenza ==="
echo "Microfono → grafico frequenze colorato"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 non trovato. Installa python3 e python3-venv."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Prima esecuzione: preparo l'ambiente Python…"
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Controllo dipendenze…"
python -m pip install --upgrade pip >/dev/null 2>&1
python -m pip install -r requirements.txt

echo
echo "Avvio in corso…"
echo "Per uscire: chiudi la finestra del grafico."
echo

python spectrum_visualizer.py
