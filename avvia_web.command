#!/bin/bash
# Mac: tasto destro → Apri  (se dice "autore non identificato")
cd "$(dirname "$0")"

# Rimuove il blocco quarantena di macOS su questa cartella
xattr -cr . >/dev/null 2>&1 || true

echo "=== Monitor NVIDIA Web ==="
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
