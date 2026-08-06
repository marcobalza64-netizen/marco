#!/bin/bash
# Doppio clic su questo file (Mac) oppure: ./avvia.command
set -e
cd "$(dirname "$0")"

echo "=== Monitor NVIDIA ==="
echo "Cartella: $(pwd)"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERRORE: Python3 non trovato."
  echo "Installa Python da https://www.python.org/downloads/ oppure con:"
  echo "  brew install python"
  read -r -p "Premi Invio per chiudere..."
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Creo ambiente virtuale..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installo/aggiorno dipendenze (yfinance, rich)..."
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt

echo
echo "Avvio monitor... (Ctrl+C per uscire)"
echo
python nvidia_monitor.py

echo
read -r -p "Premi Invio per chiudere..."
