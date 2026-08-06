# Monitor NVIDIA (Europa) — tempo reale

App semplice per vedere il prezzo **NVIDIA** in tempo reale sul mercato europeo.

**Non serve installare nulla** (niente pip): usa solo Python già presente sul Mac.

## Fonti dati
- **Xetra / Francoforte**: Börse Frankfurt → **tempo reale**
- **Tradegate**: mercato Europa retail → **tempo reale**
- **NASDAQ**: Yahoo Finance → near real-time

## Sul Mac — 2 passi

### 1) Scarica
1. Vai su: https://github.com/marcobalza64-netizen/marco  
2. Clicca **Code** → **Download ZIP**  
3. Doppio clic sullo ZIP per estrarlo  
4. Apri la cartella `marco-main`

### 2) Avvia
- **Doppio clic** sul file `avvia.command`  
- Se il Mac dice che non si può aprire: **tasto destro** → **Apri** → **Apri**

Vedrai il prezzo NVIDIA aggiornarsi ogni 2 secondi, con ora dell’ultimo trade.  
Per uscire: `Ctrl + C`, poi Invio.

---

### In alternativa (Terminale)

```bash
cd ~/Downloads/marco-main
python3 nvidia_monitor.py
```

## Opzioni

```bash
python3 nvidia_monitor.py              # Xetra Europa tempo reale (euro)
python3 nvidia_monitor.py -m frankfurt # Francoforte tempo reale
python3 nvidia_monitor.py -m tradegate # Tradegate tempo reale
python3 nvidia_monitor.py -m nasdaq    # USA (dollari)
python3 nvidia_monitor.py -i 1         # aggiorna ogni 1 secondo
```

## Se manca Python

Scarica Python da https://www.python.org/downloads/  
Installa, poi ripeti il doppio clic su `avvia.command`.

## Nota

Solo a scopo informativo, non è un consiglio finanziario.
