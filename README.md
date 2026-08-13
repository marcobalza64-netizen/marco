# Spettro Frequenza (solo programma Python)

Visualizzatore scenografico dal microfono, con regolazione sensibilità e valori di frequenza in Hz.

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
- Slider **Sensibilità** = ampiezza dello spettro
- Tasti **+ / −** oppure frecce ↑ ↓
- In basso: **scala frequenze in Hz**
- In alto a destra: **frequenza dominante** in tempo reale
