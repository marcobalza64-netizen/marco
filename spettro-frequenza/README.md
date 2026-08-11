# Spettro Frequenza — Visualizzatore audio Python

Applicazione Python completa: ascolta il **microfono** e mostra lo **spettro delle frequenze** in tempo reale (barre colorate).

Funziona su **Mac**, **Windows** e **Linux**.

---

## Come scaricare

1. Apri il repository: https://github.com/marcobalza64-netizen/marco
2. Vai nella cartella **`spettro-frequenza`**
3. Oppure scarica tutto il progetto: **Code → Download ZIP**, estrai, poi entra in `spettro-frequenza`

---

## Requisiti

- **Python 3.10+** — https://www.python.org/downloads/
- Microfono collegato / integrato
- Permesso microfono dal sistema operativo

---

## Avvio rapido

### Mac

1. Doppio clic su `avvia.command`  
   (se macOS blocca: tasto destro → **Apri** → **Apri**)
2. Alla prima esecuzione crea da solo l’ambiente e installa le librerie
3. Se chiede il microfono → **Consenti**
4. Per uscire: chiudi la finestra del grafico

### Windows

1. Doppio clic su `avvia.bat`
2. Alla prima esecuzione installa le dipendenze
3. Se Windows chiede il microfono → **Consenti**
4. Per uscire: chiudi la finestra del grafico

### Linux

```bash
cd spettro-frequenza
chmod +x avvia.sh
./avvia.sh
```

Su Debian/Ubuntu, se manca PortAudio:

```bash
sudo apt install libportaudio2 portaudio19-dev python3-venv
```

---

## Avvio da Terminale (tutti i sistemi)

```bash
cd spettro-frequenza
python3 -m venv .venv
```

**Mac / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
python spectrum_visualizer.py
```

**Windows (Prompt dei comandi):**

```bat
.venv\Scripts\activate
pip install -r requirements.txt
python spectrum_visualizer.py
```

---

## Opzioni utili

```bash
python spectrum_visualizer.py --list-devices   # elenca microfoni
python spectrum_visualizer.py --device 1       # scegli un microfono
```

---

## Contenuto del pacchetto

| File | Descrizione |
|------|-------------|
| `spectrum_visualizer.py` | Programma principale (FFT + grafico) |
| `requirements.txt` | Dipendenze Python (`numpy`, `sounddevice`, `matplotlib`) |
| `avvia.command` | Launcher Mac (doppio clic) |
| `avvia.bat` | Launcher Windows (doppio clic) |
| `avvia.sh` | Launcher Linux |
| `README.md` | Queste istruzioni |

---

## Problemi comuni

**Non sente il microfono (Mac)**  
Impostazioni di Sistema → Privacy e sicurezza → Microfono → abilita Terminal / Python.

**PortAudio non trovato (Linux)**  
`sudo apt install libportaudio2 portaudio19-dev`

**Finestra non si apre**  
Serve un display grafico (sul Mac/Windows ok; su server Linux senza GUI non funziona).

---

## Cosa fa

1. Cattura audio dal microfono (44.1 kHz)
2. Calcola lo spettro con FFT
3. Mostra barre su scala logaritmica (40 Hz – 16 kHz)
4. Aggiorna il grafico in tempo reale
