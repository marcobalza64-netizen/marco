# Meteo Bordighera

App web per vedere **tutti i dati meteo e le previsioni** di Bordighera (Liguria): condizioni attuali, prossime ore, 14 giorni e stato del mare.

**Non serve installare nulla** (niente pip): usa solo Python già presente sul Mac/PC.

> Nel ZIP del repository c’è anche l’app NVIDIA (`avvia_web.command`).  
> Per il **meteo** usa solo **`avvia_meteo.command`**.

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

## Avvio (meteo)

1. Scarica lo ZIP:  
   https://codeload.github.com/marcobalza64-netizen/marco/zip/refs/heads/cursor/meteo-bordighera-0955  
2. Estrai la cartella  
3. **Doppio clic** su `avvia_meteo.command`  
   (se il Mac blocca: tasto destro → **Apri** → **Apri**)

Si apre la pagina `http://127.0.0.1:8787`.  
Per uscire: nel Terminale premi `Ctrl + C`.

Oppure da Terminale:

```bash
cd ~/Downloads/marco-cursor-meteo-bordighera-0955
python3 meteo_app.py
```

### Se vedi la pagina ma senza dati
- Serve internet (i dati arrivano da Open-Meteo)
- Non aprire solo `meteo/index.html`: va avviato il server con `avvia_meteo.command`
- Premi **Aggiorna** nella pagina

## Nota

Solo a scopo informativo. I dati meteo possono variare rispetto ad altre fonti.
