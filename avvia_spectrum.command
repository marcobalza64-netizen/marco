#!/bin/bash
# Mac: doppio clic per avviare il visualizzatore spettro audio
cd "$(dirname "$0")"

echo "=== Spettro Audio ==="
echo "Microfono → grafico frequenze colorato"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python non trovato sul Mac."
  echo "Scaricalo da: https://www.python.org/downloads/"
  echo
  read -r -p "Premi Invio per chiudere..."
  exit 1
fi

# Crea un ambiente virtuale locale (una sola volta) e installa le dipendenze
if [ ! -d ".venv-spectrum" ]; then
  echo "Prima esecuzione: preparo l'ambiente Python…"
  python3 -m venv .venv-spectrum || {
    echo "Impossibile creare il virtualenv."
    read -r -p "Premi Invio per chiudere..."
    exit 1
  }
fi

# shellcheck disable=SC1091
source .venv-spectrum/bin/activate

echo "Controllo dipendenze…"
python -m pip install --upgrade pip >/dev/null 2>&1
python -m pip install -r requirements-spectrum.txt || {
  echo
  echo "Installazione dipendenze fallita."
  echo "Prova da Terminale:"
  echo "  cd \"$(pwd)\""
  echo "  python3 -m venv .venv-spectrum"
  echo "  source .venv-spectrum/bin/activate"
  echo "  pip install -r requirements-spectrum.txt"
  echo
  read -r -p "Premi Invio per chiudere..."
  exit 1
}

echo
echo "Avvio in corso…"
echo "Se il Mac chiede il microfono: premi OK / Consenti."
echo "Per uscire: chiudi la finestra del grafico."
echo

python spectrum_visualizer.py

echo
read -r -p "Premi Invio per chiudere..."
