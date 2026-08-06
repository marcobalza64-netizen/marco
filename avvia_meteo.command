#!/bin/bash
# Mac: doppio clic per aprire Meteo Bordighera nel browser
cd "$(dirname "$0")"

echo "=== Meteo Bordighera ==="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python non trovato sul Mac."
  echo "Scaricalo da: https://python.org/downloads/"
  echo
  read -r -p "Premi Invio per chiudere..."
  exit 1
fi

echo "Avvio server web locale..."
echo "Il browser si apre da solo su http://127.0.0.1:8787"
echo "Per uscire: Ctrl+C"
echo

python3 meteo_app.py

echo
read -r -p "Premi Invio per chiudere..."
