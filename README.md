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
3. Apri la cartella `marco-main`  
4. Avvia come sotto 👇

### Se il Mac dice “autore non identificato” / “non si può aprire”

È normale per i file scaricati da internet. **Non è un virus.**

**Modo A (più semplice)**  
1. Sul file `avvia_web.command` fai **tasto destro** (o Control + clic)  
2. Scegli **Apri**  
3. Nella finestra conferma di nuovo **Apri**

**Modo B (Impostazioni)**  
1. Prova ad aprirlo una volta (anche se si blocca)  
2. Vai su **Impostazioni di Sistema → Privacy e sicurezza**  
3. In basso trovi il messaggio sul file bloccato → clicca **Apri comunque**

**Modo C (sempre funziona — Terminale)**  
Apri **Terminale** e incolla:

```bash
cd ~/Downloads/marco-main
xattr -cr .
python3 web_app.py
```

Il browser si apre da solo su `http://127.0.0.1:8765`.  
Per uscire: `Ctrl + C`.

---

## Versione Terminale

Stesso discorso sul blocco Mac: **tasto destro → Apri** su `avvia.command`,  
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
Installa, poi riprova.

## Nota

Solo a scopo informativo, non è un consiglio finanziario.
