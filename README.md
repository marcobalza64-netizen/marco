# Spettro Frequenza (solo programma Python)

Visualizzatore scenografico dal microfono, con regolazione sensibilità.

## Avvio
1. Estrai lo ZIP
2. Mac: doppio clic `avvia.command`
   Windows: doppio clic `avvia.bat`
   Linux: `chmod +x avvia.sh && ./avvia.sh`

Oppure:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python spectrum_visualizer.py
```

## Controlli
- Slider **Sensibilità** in basso = ampiezza dello spettro
- Tasti **+ / −** oppure frecce ↑ ↓
- Chiudi la finestra per uscire
