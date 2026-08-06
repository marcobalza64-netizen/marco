#!/usr/bin/env python3
"""
Monitor NVIDIA — mercati europei
Nessuna libreria da installare: usa solo Python standard.
"""

from __future__ import annotations

import argparse
import json
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

MARKETS = {
    "xetra": {
        "symbol": "NVD.DE",
        "name": "Xetra (Europa)",
        "currency": "EUR",
        "tz": "Europe/Berlin",
    },
    "frankfurt": {
        "symbol": "NVD.F",
        "name": "Francoforte",
        "currency": "EUR",
        "tz": "Europe/Berlin",
    },
    "nasdaq": {
        "symbol": "NVDA",
        "name": "NASDAQ (USA)",
        "currency": "USD",
        "tz": "America/New_York",
    },
}

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


@dataclass
class Quote:
    symbol: str
    price: float
    currency: str
    change: float
    change_pct: float
    open_price: Optional[float]
    high: Optional[float]
    low: Optional[float]
    previous_close: Optional[float]
    volume: Optional[int]
    market_open: bool
    fetched_at: datetime


def clear() -> None:
    # Pulisce il terminale (Mac / Linux / Windows)
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def download_json(url: str) -> dict:
    """Scarica JSON. Su Mac evita errori certificato SSL di Python."""
    errors: list[str] = []

    # 1) curl del sistema (sul Mac usa i certificati Apple → di solito funziona)
    try:
        completed = subprocess.run(
            [
                "curl",
                "-fsSL",
                "--max-time",
                "15",
                "-A",
                UA,
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            return json.loads(completed.stdout)
        err = (completed.stderr or completed.stdout or f"curl exit {completed.returncode}").strip()
        errors.append(f"curl: {err}")
    except FileNotFoundError:
        errors.append("curl: non trovato")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"curl: {exc}")

    # 2) urllib con certificati normali
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"urllib: {exc}")

    # 3) urllib senza verifica SSL (solo se i certificati Python sul Mac sono rotti)
    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"urllib-insecure: {exc}")

    raise RuntimeError(" | ".join(errors))


def fetch_quote(market_key: str) -> Quote:
    market = MARKETS[market_key]
    symbol = market["symbol"]
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{symbol}?interval=1d&range=5d"
    )
    data = download_json(url)

    result = data["chart"]["result"][0]
    meta = result["meta"]
    indicators = result["indicators"]["quote"][0]

    price = float(meta.get("regularMarketPrice") or meta.get("previousClose") or 0)
    currency = meta.get("currency") or market["currency"]

    # Ultimo giorno con dati validi
    opens = indicators.get("open") or []
    highs = indicators.get("high") or []
    lows = indicators.get("low") or []
    closes = indicators.get("close") or []
    volumes = indicators.get("volume") or []

    def last_valid(values):
        for value in reversed(values):
            if value is not None:
                return value
        return None

    def previous_valid(values):
        found_last = False
        for value in reversed(values):
            if value is None:
                continue
            if not found_last:
                found_last = True
                continue
            return value
        return None

    open_price = last_valid(opens)
    high = meta.get("regularMarketDayHigh")
    if high is None:
        high = last_valid(highs)
    low = meta.get("regularMarketDayLow")
    if low is None:
        low = last_valid(lows)
    volume = meta.get("regularMarketVolume")
    if volume is None:
        volume = last_valid(volumes)

    # Chiusura precedente = penultima chiusura giornaliera
    previous_close = previous_valid(closes)
    if previous_close is None:
        previous_close = meta.get("previousClose") or meta.get("chartPreviousClose")

    open_price = float(open_price) if open_price is not None else None
    high = float(high) if high is not None else None
    low = float(low) if low is not None else None
    volume = int(volume) if volume is not None else None
    previous_close = float(previous_close) if previous_close is not None else None

    if previous_close and previous_close != 0:
        change = price - previous_close
        change_pct = (change / previous_close) * 100
    else:
        change = 0.0
        change_pct = 0.0

    now = datetime.now(ZoneInfo(market["tz"]))
    market_open = is_market_open(market_key, now)

    return Quote(
        symbol=symbol,
        price=price,
        currency=currency,
        change=change,
        change_pct=change_pct,
        open_price=open_price,
        high=high,
        low=low,
        previous_close=previous_close,
        volume=volume,
        market_open=market_open,
        fetched_at=now,
    )


def is_market_open(market_key: str, now: datetime) -> bool:
    if now.weekday() >= 5:
        return False
    minutes = now.hour * 60 + now.minute
    if market_key in {"xetra", "frankfurt"}:
        return 9 * 60 <= minutes < 17 * 60 + 30
    return 9 * 60 + 30 <= minutes < 16 * 60


def money(value: Optional[float], currency: str) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} {currency}"


def volume_txt(value: Optional[int]) -> str:
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def render(quote: Quote, market_key: str, interval: int, error: Optional[str]) -> str:
    market = MARKETS[market_key]
    up = quote.change >= 0
    color = "\033[92m" if up else "\033[91m"
    reset = "\033[0m"
    bold = "\033[1m"
    dim = "\033[2m"
    arrow = "▲" if up else "▼"
    sign = "+" if up else ""

    lines = [
        f"{bold}NVIDIA — {market['name']}{reset}  {dim}({quote.symbol}){reset}",
        "",
        f"{color}{bold}{quote.price:,.2f} {quote.currency}{reset}  "
        f"{color}{arrow} {sign}{quote.change:,.2f} ({sign}{quote.change_pct:.2f}%){reset}",
        "",
        f"  Apertura         {money(quote.open_price, quote.currency)}",
        f"  Massimo          {money(quote.high, quote.currency)}",
        f"  Minimo           {money(quote.low, quote.currency)}",
        f"  Chiusura prec.   {money(quote.previous_close, quote.currency)}",
        f"  Volume           {volume_txt(quote.volume)}",
        f"  Stato mercato    {'Aperto' if quote.market_open else 'Chiuso'}",
        f"  Ora locale       {quote.fetched_at.strftime('%d/%m/%Y %H:%M:%S %Z')}",
        f"  Aggiornamento    ogni {interval}s",
        "",
    ]
    if error:
        lines.append(f"\033[93mAvviso: {error}{reset}")
        lines.append("")
    lines.append(f"{dim}Ctrl+C per uscire{reset}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor NVIDIA (Europa) — senza installazioni")
    parser.add_argument(
        "-m",
        "--market",
        choices=sorted(MARKETS.keys()),
        default="xetra",
        help="Mercato (default: xetra)",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=5,
        help="Secondi tra aggiornamenti (default: 5)",
    )
    parser.add_argument("--once", action="store_true", help="Una sola quotazione")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.interval < 2:
        print("Intervallo minimo: 2 secondi")
        return 1

    last_quote: Optional[Quote] = None
    last_error: Optional[str] = None

    def refresh() -> None:
        nonlocal last_quote, last_error
        try:
            last_quote = fetch_quote(args.market)
            last_error = None
        except Exception as exc:  # noqa: BLE001 - mostriamo qualsiasi errore rete/dati
            last_error = str(exc)

        if last_quote is None:
            print("Caricamento…")
            if last_error:
                print(f"Errore: {last_error}")
            return

        clear()
        print(render(last_quote, args.market, args.interval, last_error))

    if args.once:
        refresh()
        return 0 if last_error is None and last_quote is not None else 1

    print("Avvio monitor NVIDIA…")
    try:
        while True:
            refresh()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nMonitor interrotto.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
