# Monitor NVIDIA (Europa)

App semplice per vedere il prezzo **NVIDIA** in tempo reale sul mercato europeo.

**Non serve installare nulla** (niente pip, niente yfinance): usa solo Python già presente sul Mac.

## Sul Mac — 2 passi

### 1) Scarica
1. Vai su: https://github.com/marcobalza64-netizen/marco  
2. Clicca **Code** → **Download ZIP**  
3. Doppio clic sullo ZIP per estrarlo  
4. Apri la cartella `marco-main`

### 2) Avvia
- **Doppio clic** sul file `avvia.command`  
- Se il Mac dice che non si può aprire: **tasto destro** → **Apri** → **Apri**

Vedrai il prezzo NVIDIA aggiornarsi da solo.  
Per uscire: `Ctrl + C`, poi Invio.

---

### In alternativa (Terminale)

```bash
cd ~/Downloads/marco-main
python3 nvidia_monitor.py
```

## Opzioni

```bash
python3 nvidia_monitor.py              # Xetra Europa (euro)
python3 nvidia_monitor.py -m frankfurt # Francoforte
python3 nvidia_monitor.py -m nasdaq    # USA (dollari)
python3 nvidia_monitor.py -i 10        # aggiorna ogni 10 secondi
```

## Se manca Python

Scarica Python da https://www.python.org/downloads/  
Installa, poi ripeti il doppio clic su `avvia.command`.

## Se compare "certificate verify failed"

Scarica di nuovo lo ZIP aggiornato da GitHub (dopo il merge di questa correzione) e riavvia.  
La nuova versione usa `curl` del Mac e non dipende più dai certificati rotti di Python.

## Nota

Dati da Yahoo Finance (near real-time). Solo a scopo informativo, non è un consiglio finanziario.
