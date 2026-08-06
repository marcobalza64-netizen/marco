#!/bin/bash
# Mac: tasto destro → Apri  (se dice "autore non identificato")
cd "$(dirname "$0")"

# Rimuove il blocco quarantena di macOS su questa cartella
xattr -cr . >/dev/null 2>&1 || true

echo "=== Monitor NVIDIA ==="
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
python3 nvidia_monitor.py

echo
read -r -p "Premi Invio per chiudere..."
