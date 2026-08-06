# Monitor NVIDIA — mercati europei

App Python in tempo reale per seguire il valore delle azioni **NVIDIA** sui mercati europei (Xetra / Francoforte).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

## Cosa fa

- Mostra prezzo, variazione, apertura, max/min, volume
- Aggiornamento automatico ogni pochi secondi
- Mercati: **Xetra** (default, EUR), Francoforte, oppure NASDAQ
- Interfaccia a terminale chiara (verde = rialzo, rosso = ribasso)

> I dati arrivano da Yahoo Finance (near real-time). Non sono un feed professionale di borsa.

## Come scaricarla da GitHub (Mac)

### Modo più semplice (consigliato)

1. Vai su https://github.com/marcobalza64-netizen/marco  
2. Clicca **Code → Download ZIP** ed estrai lo ZIP  
3. Apri la cartella `marco-main`  
4. **Doppio clic** sul file `avvia.command`  
5. Se il Mac blocca l’apertura: tasto destro → **Apri** → **Apri**

Lo script installa da solo `yfinance` e avvia il monitor.  
Per uscire: `Ctrl + C`.

### Da Terminale

Apri **Terminale** (`Applicazioni → Utility → Terminale`) e copia/incolla **tutto** questo blocco:

```bash
cd ~/Downloads/marco-main 2>/dev/null || cd ~/marco 2>/dev/null || cd marco
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python nvidia_monitor.py
```

> Importante: usa sempre `source .venv/bin/activate` **prima** di `python nvidia_monitor.py`,  
> altrimenti compare l’errore `No module named 'yfinance'`.

### Errore: `No module named 'yfinance'`

Nel Terminale, nella cartella del progetto, esegui:

```bash
cd ~/Downloads/marco-main
python3 -m pip install -r requirements.txt
python3 nvidia_monitor.py
```

Oppure (meglio, con ambiente virtuale):

```bash
cd ~/Downloads/marco-main
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python nvidia_monitor.py
```

### Se non hai Python sul Mac

```bash
# Installa Homebrew (se non ce l'hai)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installa Python
brew install python
```

Poi ripeti i passi 2–4 sopra.

### Se non hai git

Scarica lo ZIP da GitHub:

1. Vai su https://github.com/marcobalza64-netizen/marco
2. Clicca **Code → Download ZIP**
3. Estrai lo ZIP
4. Nel Terminale:

```bash
cd ~/Downloads/marco-main   # adatta il percorso se diverso
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python nvidia_monitor.py
```

## Opzioni

```bash
# Mercato Xetra (default, EUR)
python nvidia_monitor.py

# Francoforte
python nvidia_monitor.py -m frankfurt

# NASDAQ USA (USD)
python nvidia_monitor.py -m nasdaq

# Aggiorna ogni 10 secondi
python nvidia_monitor.py -i 10

# Una sola quotazione (senza loop)
python nvidia_monitor.py --once
```

| Opzione | Descrizione |
|--------|-------------|
| `-m xetra` | Xetra `NVD.DE` (EUR) — default |
| `-m frankfurt` | Francoforte `NVD.F` (EUR) |
| `-m nasdaq` | NASDAQ USA `NVDA` (USD) |
| `-i 5` | Intervallo refresh in secondi |
| `--once` | Stampa una volta e termina |

## Orari di mercato (Europa)

- **Xetra / Francoforte**: circa 09:00 – 17:30 (ora di Berlino), lun–ven
- Fuori orario lo stato risulta “Chiuso”; il prezzo mostrato è l’ultimo disponibile

## Requisiti

- macOS
- Python 3.10 o superiore
- Connessione internet

## Disclaimer

Questa app è solo a scopo informativo/didattico. Non costituisce consiglio finanziario.
