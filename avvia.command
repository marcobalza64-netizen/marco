#!/bin/bash
# Mac: doppio clic su questo file per avviare il monitor titoli
cd "$(dirname "$0")"

echo "=== Monitor Titoli ==="
echo "NVIDIA · Tesla · Rheinmetall"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python non trovato sul Mac."
  echo "Scaricalo da: https://www.python.org/downloads/"
  echo "(spunta 'Add Python to PATH' / installa normalmente)"
  echo
  read -r -p "Premi Invio per chiudere..."
  exit 1
fi

echo "Avvio in corso… (per uscire: Ctrl+C)"
echo
python3 stock_monitor.py

echo
read -r -p "Premi Invio per chiudere..."
