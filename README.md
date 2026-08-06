# Meteo Bordighera

App web per vedere **tutti i dati meteo e le previsioni** di Bordighera (Liguria): condizioni attuali, prossime ore, 14 giorni e stato del mare.

**Non serve installare nulla** (niente pip): usa solo Python già presente sul Mac/PC.

## Cosa mostra
- Temperatura, percepita, umidità, pressione, UV, visibilità
- Vento, raffiche e direzione
- Previsione oraria (24 ore)
- Previsione giornaliera (14 giorni)
- Mare: temperatura acqua, altezza e periodo onde
- Alba e tramonto

## Fonti dati
- [Open-Meteo](https://open-meteo.com/) (licenza CC BY 4.0)
- Coordinate: Bordighera · 43.78°N, 7.66°E · fuso `Europe/Rome`

---

## Avvio (consigliato)

1. Vai su: https://github.com/marcobalza64-netizen/marco  
2. **Code → Download ZIP** ed estrai  
3. **Doppio clic** su `avvia_meteo.command`  
   (se il Mac blocca: tasto destro → **Apri** → **Apri**)

Si apre la pagina `http://127.0.0.1:8787`.  
Per uscire: nel Terminale premi `Ctrl + C`.

Oppure da Terminale:

```bash
cd ~/Downloads/marco-main
python3 meteo_app.py
```

Opzioni:

```bash
python3 meteo_app.py --port 8787
python3 meteo_app.py --no-browser
```

---

## API locale

- `GET /api/health` — stato del server
- `GET /api/weather` — JSON completo (attuale, oraria, giornaliera, mare)

## Se manca Python

Scarica Python da https://www.python.org/downloads/  
Installa, poi ripeti il doppio clic su `avvia_meteo.command`.

## Nota

Solo a scopo informativo. I dati meteo possono variare rispetto ad altre fonti.
