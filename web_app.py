#!/usr/bin/env python3
"""
Monitor NVIDIA — versione web in tempo reale.
Apre il browser e aggiorna il prezzo in automatico.
Nessuna libreria da installare.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from nvidia_monitor import MARKETS, fetch_quote

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def quote_to_dict(market_key: str) -> dict:
    q = fetch_quote(market_key)
    market = MARKETS[market_key]
    return {
        "market": market_key,
        "market_name": market["name"],
        "symbol": q.symbol,
        "price": q.price,
        "currency": q.currency,
        "change": q.change,
        "change_pct": q.change_pct,
        "open": q.open_price,
        "high": q.high,
        "low": q.low,
        "previous_close": q.previous_close,
        "volume": q.volume,
        "bid": q.bid,
        "ask": q.ask,
        "market_open": q.market_open,
        "last_trade_at": q.last_trade_at.isoformat() if q.last_trade_at else None,
        "fetched_at": q.fetched_at.isoformat(),
        "source_label": q.source_label,
        "realtime": q.realtime,
        "server_time": datetime.now().astimezone().isoformat(),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "NvidiaMonitorWeb/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path in {"/", "/index.html"}:
            return self._serve_file(WEB_DIR / "index.html")

        if path == "/api/markets":
            markets = [
                {
                    "id": key,
                    "name": meta["name"],
                    "symbol": meta["symbol"],
                    "currency": meta["currency"],
                    "realtime": bool(meta.get("realtime")),
                }
                for key, meta in MARKETS.items()
            ]
            return self._send_json(200, {"markets": markets})

        if path == "/api/quote":
            qs = parse_qs(parsed.query)
            market = (qs.get("market") or ["xetra"])[0]
            if market not in MARKETS:
                return self._send_json(400, {"error": f"Mercato non valido: {market}"})
            try:
                return self._send_json(200, quote_to_dict(market))
            except Exception as exc:  # noqa: BLE001
                return self._send_json(502, {"error": str(exc)})

        # Static files under /web or direct names
        candidate = WEB_DIR / path.lstrip("/")
        if candidate.is_file() and WEB_DIR in candidate.resolve().parents:
            return self._serve_file(candidate)

        self._send_json(404, {"error": "Non trovato"})

    def _serve_file(self, file_path: Path) -> None:
        if not file_path.is_file():
            self._send_json(404, {"error": "File non trovato"})
            return
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
        }:
            content_type = f"{content_type}; charset=utf-8"
        body = file_path.read_bytes()
        self._send(200, body, content_type)


def open_browser_later(url: str, delay: float = 0.8) -> None:
    def _open() -> None:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass

    timer = threading.Timer(delay, _open)
    timer.daemon = True
    timer.start()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor NVIDIA web (tempo reale)")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Porta (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Non aprire il browser")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not WEB_DIR.is_dir():
        print(f"Cartella web non trovata: {WEB_DIR}")
        return 1

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print("=== Monitor NVIDIA Web ===")
    print(f"Apri nel browser: {url}")
    print("Aggiornamento automatico ogni 2 secondi.")
    print("Per uscire: Ctrl+C")
    print()

    if not args.no_browser:
        open_browser_later(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer web interrotto.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
