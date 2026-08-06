# Meteo Bordighera

App web per vedere **meteo e previsioni** di Bordighera (Liguria): ora, prossime ore, 14 giorni e mare.

**Non serve installare librerie** (niente pip).

> Nel ZIP c’è anche l’app NVIDIA. Per il **meteo** usa solo i file `avvia_meteo.*`.

---

## Importante: come condividere

`http://127.0.0.1:8787` funziona **solo sul computer che ha avviato l’app**.  
Se lo invii a un’altra persona, vedrà **“non c’è indirizzo” / sito non raggiungibile**.

### Opzione A — Link pubblico (consigliata)
Dopo il deploy GitHub Pages, condividi questo indirizzo:

**https://marcobalza64-netizen.github.io/marco/**

(La prima volta su GitHub: **Settings → Pages → Source: GitHub Actions**, poi aspetta il deploy.)

### Opzione B — Invia lo ZIP (ognuno lo avvia sul proprio PC)

1. Scarica:  
   https://codeload.github.com/marcobalza64-netizen/marco/zip/refs/heads/cursor/meteo-bordighera-0955  
2. Invia lo ZIP alla persona  
3. Lei estrae e avvia:

| Sistema | File da aprire |
|--------|-----------------|
| **Windows** | doppio clic su `avvia_meteo.bat` |
| **Mac** | doppio clic su `avvia_meteo.command` |

Su Windows serve [Python](https://www.python.org/downloads/) con la spunta **Add python.exe to PATH**.

Si apre `http://127.0.0.1:8787` **sul suo** computer (non sul tuo).

---

## Cosa mostra
- Temperatura, percepita, umidità, pressione, UV, visibilità
- Vento e raffiche
- Previsione oraria (24 ore) e giornaliera (14 giorni)
- Mare: temperatura acqua e onde
- Alba e tramonto

Dati: [Open-Meteo](https://open-meteo.com/) (CC BY 4.0) · Bordighera 43.78°N, 7.66°E
