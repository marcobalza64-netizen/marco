# Monitor NVIDIA (Europa) — tempo reale

App per vedere il prezzo **NVIDIA** in tempo reale sul mercato europeo.

**Non serve installare nulla** (niente pip): usa solo Python già presente sul Mac.

## Fonti dati
- **Xetra / Francoforte**: Börse Frankfurt → **tempo reale**
- **Tradegate**: mercato Europa retail → **tempo reale**
- **NASDAQ**: Yahoo Finance → near real-time

---

## Versione WEB (consigliata)

Si apre nel browser e si aggiorna **in automatico** ogni 2 secondi.

1. Vai su: https://github.com/marcobalza64-netizen/marco  
2. **Code → Download ZIP** ed estrai  
3. **Doppio clic** su `avvia_web.command`  
   (se il Mac blocca: tasto destro → **Apri** → **Apri**)

Si apre la pagina `http://127.0.0.1:8765` con il prezzo live.  
Per uscire: nel Terminale premi `Ctrl + C`.

Oppure da Terminale:

```bash
cd ~/Downloads/marco-main
python3 web_app.py
```

---

## Versione Terminale

- **Doppio clic** su `avvia.command`  
  oppure:

```bash
cd ~/Downloads/marco-main
python3 nvidia_monitor.py
```

### Opzioni terminale

```bash
python3 nvidia_monitor.py              # Xetra Europa tempo reale (euro)
python3 nvidia_monitor.py -m frankfurt # Francoforte tempo reale
python3 nvidia_monitor.py -m tradegate # Tradegate tempo reale
python3 nvidia_monitor.py -m nasdaq    # USA (dollari)
python3 nvidia_monitor.py -i 1         # aggiorna ogni 1 secondo
```

## Se manca Python

Scarica Python da https://www.python.org/downloads/  
Installa, poi ripeti il doppio clic su `avvia_web.command`.

## Nota

Solo a scopo informativo, non è un consiglio finanziario.
