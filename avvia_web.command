#!/bin/bash
# Mac: doppio clic per aprire il monitor titoli nel browser
cd "$(dirname "$0")"

echo "=== Monitor Titoli Web ==="
echo "NVIDIA · Tesla · Rheinmetall"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python non trovato sul Mac."
  echo "Scaricalo da: https://www.python.org/downloads/"
  echo
  read -r -p "Premi Invio per chiudere..."
  exit 1
fi

echo "Avvio server web locale..."
echo "Il browser si apre da solo."
echo "Per uscire: Ctrl+C"
echo

python3 web_app.py

echo
read -r -p "Premi Invio per chiudere..."
