#!/usr/bin/env python3
"""
Monitor in tempo reale delle azioni NVIDIA sui mercati europei.
Simboli: Xetra (NVD.DE), Francoforte (NVD.F), NASDAQ (NVDA).
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

import yfinance as yf
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Riduce rumore di yfinance in console
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", category=FutureWarning)

# Mercati europei disponibili (Yahoo Finance)
MARKETS = {
    "xetra": {
        "symbol": "NVD.DE",
        "name": "Xetra (Francoforte)",
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

DEFAULT_MARKET = "xetra"
DEFAULT_INTERVAL_SEC = 5


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
    market_state: str
    fetched_at: datetime


def _safe_float(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: object) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def infer_market_state(market_key: str, reported: Optional[str]) -> str:
    """Usa lo stato Yahoo se disponibile, altrimenti stima dagli orari locali."""
    if reported and reported.upper() not in {"UNKNOWN", "NONE", ""}:
        return reported.upper()

    market = MARKETS[market_key]
    now = datetime.now(ZoneInfo(market["tz"]))
    # Sabato/Domenica chiuso
    if now.weekday() >= 5:
        return "CLOSED"

    minutes = now.hour * 60 + now.minute
    if market_key in {"xetra", "frankfurt"}:
        # Xetra: ~09:00–17:30 ora di Berlino
        if 9 * 60 <= minutes < 17 * 60 + 30:
            return "REGULAR"
        return "CLOSED"

    # NASDAQ: 09:30–16:00 ET
    if 9 * 60 + 30 <= minutes < 16 * 60:
        return "REGULAR"
    if 4 * 60 <= minutes < 9 * 60 + 30:
        return "PRE"
    if 16 * 60 <= minutes < 20 * 60:
        return "POST"
    return "CLOSED"


def fetch_quote(symbol: str, currency_hint: str, market_key: str) -> Quote:
    ticker = yf.Ticker(symbol)
    info = ticker.fast_info

    price = _safe_float(getattr(info, "last_price", None))
    previous_close = _safe_float(getattr(info, "previous_close", None))
    open_price = _safe_float(getattr(info, "open", None))
    high = _safe_float(getattr(info, "day_high", None))
    low = _safe_float(getattr(info, "day_low", None))
    volume = _safe_int(getattr(info, "last_volume", None))
    currency = getattr(info, "currency", None) or currency_hint
    reported_state = getattr(info, "market_state", None)
    market_state = infer_market_state(
        market_key, str(reported_state) if reported_state is not None else None
    )

    # Fallback su history recente se mancano dati OHLC
    if price is None or open_price is None or high is None or low is None:
        hist = ticker.history(period="5d", interval="1d")
        if not hist.empty:
            last = hist.iloc[-1]
            if price is None:
                price = _safe_float(last.get("Close"))
            if open_price is None:
                open_price = _safe_float(last.get("Open"))
            if high is None:
                high = _safe_float(last.get("High"))
            if low is None:
                low = _safe_float(last.get("Low"))
            if volume is None:
                volume = _safe_int(last.get("Volume"))
            if previous_close is None and len(hist) >= 2:
                previous_close = _safe_float(hist.iloc[-2].get("Close"))

    if price is None:
        raise RuntimeError(f"Nessun prezzo disponibile per {symbol}")

    if previous_close and previous_close != 0:
        change = price - previous_close
        change_pct = (change / previous_close) * 100
    else:
        change = 0.0
        change_pct = 0.0

    return Quote(
        symbol=symbol,
        price=price,
        currency=str(currency),
        change=change,
        change_pct=change_pct,
        open_price=open_price,
        high=high,
        low=low,
        previous_close=previous_close,
        volume=volume,
        market_state=market_state,
        fetched_at=datetime.now(timezone.utc),
    )


def format_money(value: Optional[float], currency: str) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} {currency}"


def format_volume(value: Optional[int]) -> str:
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def market_state_label(state: str) -> str:
    mapping = {
        "REGULAR": "Aperto",
        "PRE": "Pre-mercato",
        "PREPRE": "Pre-pre mercato",
        "POST": "After hours",
        "POSTPOST": "Post mercato",
        "CLOSED": "Chiuso",
        "UNKNOWN": "N/D",
    }
    return mapping.get(state.upper(), state)


def build_display(
    quote: Quote,
    market_key: str,
    interval: int,
    error: Optional[str] = None,
) -> Panel:
    market = MARKETS[market_key]
    local_tz = ZoneInfo(market["tz"])
    local_now = datetime.now(local_tz)

    title = Text()
    title.append("NVIDIA  ", style="bold green")
    title.append(market["name"], style="bold white")
    title.append(f"  ·  {quote.symbol}", style="dim")

    price_color = "green" if quote.change >= 0 else "red"
    arrow = "▲" if quote.change >= 0 else "▼"
    sign = "+" if quote.change >= 0 else ""

    price_line = Text()
    price_line.append(f"{quote.price:,.2f}", style=f"bold {price_color}")
    price_line.append(f" {quote.currency}  ", style="bold white")
    price_line.append(
        f"{arrow} {sign}{quote.change:,.2f} ({sign}{quote.change_pct:.2f}%)",
        style=price_color,
    )

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column(style="white")
    table.add_row("Apertura", format_money(quote.open_price, quote.currency))
    table.add_row("Massimo", format_money(quote.high, quote.currency))
    table.add_row("Minimo", format_money(quote.low, quote.currency))
    table.add_row("Chiusura prec.", format_money(quote.previous_close, quote.currency))
    table.add_row("Volume", format_volume(quote.volume))
    table.add_row("Stato mercato", market_state_label(quote.market_state))
    table.add_row(
        "Ora locale mercato",
        local_now.strftime("%d/%m/%Y %H:%M:%S %Z"),
    )
    table.add_row(
        "Ultimo aggiornamento",
        quote.fetched_at.astimezone(local_tz).strftime("%H:%M:%S"),
    )
    table.add_row("Intervallo refresh", f"{interval}s")

    body_parts = [price_line, Text(""), table]

    if error:
        body_parts.append(Text(""))
        body_parts.append(Text(f"Avviso: {error}", style="yellow"))

    body_parts.append(Text(""))
    body_parts.append(
        Text(
            "Ctrl+C per uscire  ·  Dati Yahoo Finance (near real-time)",
            style="dim",
        )
    )

    return Panel(
        Group(*body_parts),
        title=title,
        border_style="green" if quote.change >= 0 else "red",
        padding=(1, 2),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor in tempo reale azioni NVIDIA (mercati europei)"
    )
    parser.add_argument(
        "-m",
        "--market",
        choices=sorted(MARKETS.keys()),
        default=DEFAULT_MARKET,
        help="Mercato da monitorare (default: xetra)",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_SEC,
        help="Secondi tra un aggiornamento e l'altro (default: 5)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Mostra una sola quotazione e termina",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    market = MARKETS[args.market]
    console = Console()

    if args.interval < 2:
        console.print("[red]Intervallo minimo: 2 secondi[/red]")
        return 1

    console.print(
        f"[bold]Avvio monitor NVIDIA[/bold] su [cyan]{market['name']}[/cyan] "
        f"([white]{market['symbol']}[/white])…"
    )

    last_quote: Optional[Quote] = None
    last_error: Optional[str] = None

    def refresh() -> Panel:
        nonlocal last_quote, last_error
        try:
            last_quote = fetch_quote(
                market["symbol"], market["currency"], args.market
            )
            last_error = None
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            if last_quote is None:
                last_quote = Quote(
                    symbol=market["symbol"],
                    price=0.0,
                    currency=market["currency"],
                    change=0.0,
                    change_pct=0.0,
                    open_price=None,
                    high=None,
                    low=None,
                    previous_close=None,
                    volume=None,
                    market_state=infer_market_state(args.market, None),
                    fetched_at=datetime.now(timezone.utc),
                )
        return build_display(last_quote, args.market, args.interval, last_error)

    if args.once:
        console.print(refresh())
        return 0 if last_error is None else 1

    try:
        with Live(refresh(), console=console, refresh_per_second=4) as live:
            while True:
                time.sleep(args.interval)
                live.update(refresh())
    except KeyboardInterrupt:
        console.print("\n[dim]Monitor interrotto.[/dim]")
        return 0


if __name__ == "__main__":
    sys.exit(main())
