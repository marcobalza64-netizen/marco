# Monitor titoli Europa — tempo reale

App web per vedere i prezzi di **NVIDIA**, **Tesla** e **Rheinmetall** in tempo reale sul mercato europeo.

**Non serve installare nulla** (niente pip): usa solo Python già presente sul Mac.

---

## Spettro Frequenza (Python completo)

Visualizzatore microfono → spettro frequenze in tempo reale.

Pacchetto completo nella cartella **`spettro-frequenza/`** (Mac / Windows / Linux):

1. Scarica il progetto: **Code → Download ZIP** ed estrai
2. Entra in `spettro-frequenza`
3. Avvia con `avvia.command` (Mac), `avvia.bat` (Windows) o `./avvia.sh` (Linux)

Istruzioni dettagliate: [`spettro-frequenza/README.md`](spettro-frequenza/README.md)

## Fonti dati
- **Xetra / Francoforte**: Börse Frankfurt → **tempo reale**
- **Tradegate**: mercato Europa retail → **tempo reale**
- **NASDAQ / Yahoo**: Yahoo Finance → near real-time

---

## Versione WEB (consigliata)

Si apre nel browser e si aggiorna **in automatico** ogni 2 secondi.  
Puoi cambiare titolo (NVIDIA / Tesla / Rheinmetall) e mercato dalla pagina.

1. Vai su: https://github.com/marcobalza64-netizen/marco  
2. **Code → Download ZIP** ed estrai  
3. **Doppio clic** su `avvia_web.command`  
   (se il Mac blocca: tasto destro → **Apri** → **Apri**)

Si apre la pagina `http://127.0.0.1:8765` con i prezzi live.  
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
python3 stock_monitor.py
```

### Opzioni terminale

```bash
python3 stock_monitor.py                       # NVIDIA Xetra (euro)
python3 stock_monitor.py -s tesla              # Tesla
python3 stock_monitor.py -s rheinmetall        # Rheinmetall
python3 stock_monitor.py -s tesla -m tradegate # Tesla su Tradegate
python3 stock_monitor.py -s nvidia -m nasdaq   # NVIDIA USA (dollari)
python3 stock_monitor.py -i 1                  # aggiorna ogni 1 secondo
```

## Se manca Python

Scarica Python da https://www.python.org/downloads/  
Installa, poi ripeti il doppio clic su `avvia_web.command`.

## Nota

Solo a scopo informativo, non è un consiglio finanziario.
