#!/usr/bin/env python3
"""App web per sommare numeri — solo libreria standard Python."""

from __future__ import annotations

import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8765

HTML = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Somma Numeri</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg-1: #0f2a24;
      --bg-2: #1a4a3c;
      --ink: #f4f7f5;
      --muted: #b7c9c1;
      --accent: #3ecf8e;
      --accent-ink: #062418;
      --line: rgba(244, 247, 245, 0.14);
      --danger: #ff8a7a;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "DM Sans", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(ellipse 80% 50% at 10% 0%, rgba(62, 207, 142, 0.22), transparent 55%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(26, 74, 60, 0.9), transparent 50%),
        linear-gradient(160deg, var(--bg-1), var(--bg-2));
      display: grid;
      place-items: center;
      padding: 1.5rem;
    }

    main {
      width: min(100%, 420px);
    }

    h1 {
      font-family: "Fraunces", serif;
      font-size: clamp(2rem, 6vw, 2.6rem);
      font-weight: 700;
      margin: 0 0 0.35rem;
      letter-spacing: -0.02em;
    }

    .lead {
      margin: 0 0 1.75rem;
      color: var(--muted);
      line-height: 1.45;
    }

    form {
      display: grid;
      gap: 0.75rem;
    }

    label {
      font-size: 0.85rem;
      color: var(--muted);
    }

    .row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 0.6rem;
    }

    input[type="text"] {
      width: 100%;
      border: 1px solid var(--line);
      background: rgba(0, 0, 0, 0.25);
      color: var(--ink);
      border-radius: 10px;
      padding: 0.85rem 1rem;
      font: inherit;
      font-size: 1.05rem;
      outline: none;
    }

    input[type="text"]:focus {
      border-color: var(--accent);
    }

    button {
      border: 0;
      border-radius: 10px;
      padding: 0.85rem 1.1rem;
      font: inherit;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }

    button:hover { transform: translateY(-1px); }
    button:active { transform: translateY(0); }

    .add {
      background: var(--accent);
      color: var(--accent-ink);
    }

    .actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.6rem;
      margin-top: 0.5rem;
    }

    .sum {
      background: rgba(244, 247, 245, 0.1);
      color: var(--ink);
      border: 1px solid var(--line);
    }

    .clear {
      background: transparent;
      color: var(--muted);
      border: 1px solid var(--line);
    }

    .error {
      min-height: 1.25rem;
      color: var(--danger);
      font-size: 0.9rem;
      margin: 0.35rem 0 0;
    }

    .list {
      margin: 1.5rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.4rem;
    }

    .list li {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.55rem 0;
      border-bottom: 1px solid var(--line);
      animation: fadeIn 0.25s ease;
    }

    .list button {
      background: transparent;
      color: var(--muted);
      padding: 0.2rem 0.45rem;
      font-size: 0.85rem;
      font-weight: 400;
    }

    .result {
      margin-top: 1.5rem;
      padding-top: 1.25rem;
      border-top: 1px solid var(--line);
    }

    .result span {
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 0.25rem;
    }

    .result strong {
      font-family: "Fraunces", serif;
      font-size: clamp(2.2rem, 8vw, 3rem);
      font-weight: 700;
      color: var(--accent);
      letter-spacing: -0.03em;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <main>
    <h1>Somma Numeri</h1>
    <p class="lead">Aggiungi i numeri e calcola subito il totale.</p>

    <form id="form">
      <label for="numero">Numero</label>
      <div class="row">
        <input id="numero" type="text" inputmode="decimal" placeholder="es. 12,5" autocomplete="off" autofocus />
        <button class="add" type="submit">Aggiungi</button>
      </div>
      <p class="error" id="errore" aria-live="polite"></p>
      <div class="actions">
        <button class="sum" type="button" id="calcola">Calcola somma</button>
        <button class="clear" type="button" id="reset">Svuota</button>
      </div>
    </form>

    <ul class="list" id="lista"></ul>

    <div class="result">
      <span>Totale</span>
      <strong id="totale">0</strong>
    </div>
  </main>

  <script>
    const numeri = [];
    const input = document.getElementById("numero");
    const lista = document.getElementById("lista");
    const totaleEl = document.getElementById("totale");
    const errore = document.getElementById("errore");

    function format(n) {
      return Number.isInteger(n) ? String(n) : String(n);
    }

    function render(somma = null) {
      lista.innerHTML = numeri.map((n, i) =>
        `<li><span>${format(n)}</span><button type="button" data-i="${i}" aria-label="Rimuovi">rimuovi</button></li>`
      ).join("");
      if (somma !== null) {
        totaleEl.textContent = format(somma);
      }
    }

    async function sommaServer() {
      const res = await fetch("/api/somma", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ numeri }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.errore || "Errore");
      return data.somma;
    }

    document.getElementById("form").addEventListener("submit", (e) => {
      e.preventDefault();
      errore.textContent = "";
      const raw = input.value.trim().replace(",", ".");
      if (!raw) {
        errore.textContent = "Inserisci un numero.";
        return;
      }
      const n = Number(raw);
      if (!Number.isFinite(n)) {
        errore.textContent = "Valore non valido.";
        return;
      }
      numeri.push(n);
      input.value = "";
      input.focus();
      render(numeri.reduce((a, b) => a + b, 0));
    });

    lista.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-i]");
      if (!btn) return;
      numeri.splice(Number(btn.dataset.i), 1);
      render(numeri.reduce((a, b) => a + b, 0));
    });

    document.getElementById("calcola").addEventListener("click", async () => {
      errore.textContent = "";
      try {
        const somma = await sommaServer();
        render(somma);
      } catch (err) {
        errore.textContent = err.message || "Impossibile calcolare.";
      }
    });

    document.getElementById("reset").addEventListener("click", () => {
      numeri.length = 0;
      errore.textContent = "";
      render(0);
      input.focus();
    });
  </script>
</body>
</html>
"""


def somma(numeri: list[float]) -> float:
    return float(sum(numeri))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        print(f"[{self.log_date_time_string()}] {args[0]}")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/somma":
            self._send(404, b'{"errore":"Not found"}', "application/json; charset=utf-8")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
            valori = payload.get("numeri", [])
            if not isinstance(valori, list):
                raise ValueError("Lista numeri non valida")
            numeri = [float(x) for x in valori]
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            body = json.dumps({"errore": str(exc)}).encode("utf-8")
            self._send(400, body, "application/json; charset=utf-8")
            return

        risultato = somma(numeri)
        # Evita 1.0 se intero
        if risultato == int(risultato):
            out: float | int = int(risultato)
        else:
            out = risultato
        body = json.dumps({"somma": out, "numeri": numeri}).encode("utf-8")
        self._send(200, body, "application/json; charset=utf-8")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print("=== Somma Numeri ===")
    print(f"Apri il browser su: {url}")
    print("Premi Ctrl+C per uscire.\n")
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nApp chiusa.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
