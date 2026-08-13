# Spettro Frequenza — solo programma Python

Visualizzatore **scenografico** del microfono in tempo reale, con **regolazione sensibilità**.

## Download ZIP (solo questo programma)

https://github.com/marcobalza64-netizen/marco/raw/cursor/spettro-frequenza-completo-9461/spettro-frequenza-completo.zip

Oppure branch pulito:

https://github.com/marcobalza64-netizen/marco/archive/refs/heads/cursor/spettro-solo-python-9461.zip

## Avvio (Python 3 già installato)

1. Estrai lo ZIP  
2. **Mac:** doppio clic su `avvia.command`  
   **Windows:** doppio clic su `avvia.bat`  
   **Linux:** `chmod +x avvia.sh && ./avvia.sh`  
3. Consenti il microfono  

Alla prima esecuzione installa da solo le librerie.

### Da Terminale
```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python spectrum_visualizer.py
```

## Controlli
- **Slider “Sensibilità”** in basso → regola l’ampiezza dello spettro  
- Tasti **+ / −** (o frecce ↑ ↓) → stessa regolazione  
- Chiudi la finestra per uscire  

```bash
python spectrum_visualizer.py --sensitivity 2.0
python spectrum_visualizer.py --list-devices
python spectrum_visualizer.py --device 1
```

## Cosa vedi
- **Scala frequenze in Hz** sotto lo spettro (40 Hz … 16 kHz)  
- **Frequenza dominante** in tempo reale (numero grande + linea sul picco)  
- Barre a **specchio** con bagliore  
- Forma d’onda in alto  
- Slider sensibilità / ampiezza  

## File
| File | Ruolo |
|------|--------|
| `spectrum_visualizer.py` | Programma |
| `requirements.txt` | Dipendenze |
| `avvia.command` | Launcher Mac |
| `avvia.bat` | Launcher Windows |
| `avvia.sh` | Launcher Linux |
