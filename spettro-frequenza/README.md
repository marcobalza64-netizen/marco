# Spettro Frequenza — solo programma Python

Questa cartella contiene **solo** l’app spettro audio (niente altre applicazioni).

## Download ZIP (solo questo programma)

Scarica **questo file** (non tutto il repository):

https://github.com/marcobalza64-netizen/marco/raw/cursor/spettro-frequenza-completo-9461/spettro-frequenza-completo.zip

Oppure usa il branch dedicato (ZIP pulito, solo spettro):

https://github.com/marcobalza64-netizen/marco/archive/refs/heads/cursor/spettro-solo-python-9461.zip

1. Estrai lo ZIP  
2. Avvia con `avvia.command` (Mac) o `avvia.bat` (Windows)  
3. Consenti il microfono

## Requisiti

- **Python 3.10+** — https://www.python.org/downloads/
- Microfono
- Permesso microfono dal sistema

## Avvio rapido

### Mac
Doppio clic su `avvia.command` (se blocca: tasto destro → Apri → Apri)

### Windows
Doppio clic su `avvia.bat`

### Linux
```bash
chmod +x avvia.sh
./avvia.sh
```

### Da Terminale
```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python spectrum_visualizer.py
```

## Opzioni
```bash
python spectrum_visualizer.py --list-devices
python spectrum_visualizer.py --device 1
```

## File inclusi
| File | Ruolo |
|------|--------|
| `spectrum_visualizer.py` | Programma |
| `requirements.txt` | Dipendenze |
| `avvia.command` | Launcher Mac |
| `avvia.bat` | Launcher Windows |
| `avvia.sh` | Launcher Linux |
