#!/bin/bash
# Mac: doppio clic per avviare lo Spettro Frequenza
cd "$(dirname "$0")"

echo "=== Spettro Frequenza ==="
echo "Microfono → grafico frequenze colorato"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python non trovato sul Mac."
  echo "Scaricalo da: https://www.python.org/downloads/"
  echo
  read -r -p "Premi Invio per chiudere..."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Prima esecuzione: preparo l'ambiente Python…"
  python3 -m venv .venv || {
    echo "Impossibile creare il virtualenv."
    read -r -p "Premi Invio per chiudere..."
    exit 1
  }
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Controllo dipendenze…"
python -m pip install --upgrade pip >/dev/null 2>&1
python -m pip install -r requirements.txt || {
  echo
  echo "Installazione dipendenze fallita."
  echo "Prova da Terminale:"
  echo "  cd \"$(pwd)\""
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -r requirements.txt"
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
