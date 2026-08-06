#!/usr/bin/env python3
"""
Monitor NVIDIA — mercati europei in tempo reale
Nessuna libreria da installare: usa solo Python standard.

Fonti:
- Xetra / Francoforte: API Börse Frankfurt (tempo reale)
- NASDAQ: Yahoo Finance (near real-time)
"""

from __future__ import annotations

import argparse
import json
import ssl
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

# ISIN NVIDIA
NVIDIA_ISIN = "US67066G1040"

MARKETS = {
    "xetra": {
        "symbol": "NVD.DE",
        "name": "Xetra (Europa)",
        "currency": "EUR",
        "tz": "Europe/Berlin",
        "source": "boerse",
        "mic": "XETR",
        "realtime": True,
    },
    "frankfurt": {
        "symbol": "NVD.F",
        "name": "Francoforte",
        "currency": "EUR",
        "tz": "Europe/Berlin",
        "source": "boerse",
        "mic": "XFRA",
        "realtime": True,
    },
    "tradegate": {
        "symbol": "NVD.TG",
        "name": "Tradegate (Europa)",
        "currency": "EUR",
        "tz": "Europe/Berlin",
        "source": "tradegate",
        "mic": None,
        "realtime": True,
    },
    "nasdaq": {
        "symbol": "NVDA",
        "name": "NASDAQ (USA)",
        "currency": "USD",
        "tz": "America/New_York",
        "source": "yahoo",
        "mic": None,
        "realtime": True,
    },
}

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Cache sessione Yahoo (crumb + cookie file)
_YAHOO_CRUMB: Optional[str] = None
_YAHOO_COOKIE_FILE = "/tmp/nvidia_monitor_yf.cookies"


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
    bid: Optional[float]
    ask: Optional[float]
    market_open: bool
    last_trade_at: Optional[datetime]
    fetched_at: datetime
    source_label: str
    realtime: bool


def clear() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def download_json(url: str, headers: Optional[dict[str, str]] = None, cookie_file: Optional[str] = None) -> dict:
    """Scarica JSON. Preferisce curl (certificati Mac), poi urllib."""
    errors: list[str] = []
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)

    curl_cmd = ["curl", "-fsSL", "--max-time", "15", "-A", UA]
    for key, value in hdrs.items():
        if key.lower() == "user-agent":
            continue
        curl_cmd.extend(["-H", f"{key}: {value}"])
    if cookie_file:
        curl_cmd.extend(["-b", cookie_file, "-c", cookie_file])
    curl_cmd.append(url)

    try:
        completed = subprocess.run(curl_cmd, capture_output=True, text=True, check=False)
        if completed.returncode == 0 and completed.stdout.strip():
            return json.loads(completed.stdout)
        err = (completed.stderr or completed.stdout or f"curl exit {completed.returncode}").strip()
        errors.append(f"curl: {err}")
    except FileNotFoundError:
        errors.append("curl: non trovato")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"curl: {exc}")

    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"urllib: {exc}")

    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"urllib-insecure: {exc}")

    raise RuntimeError(" | ".join(errors))


def parse_boerse_time(value: Optional[str], tz_name: str) -> Optional[datetime]:
    if not value:
        return None
    text = value.strip()
    # Esempi: 2026-08-06T14:32:48+02:00  oppure  ...Z
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(tz_name))
        return dt.astimezone(ZoneInfo(tz_name))
    except ValueError:
        return None


def fetch_boerse(market_key: str) -> Quote:
    market = MARKETS[market_key]
    mic = market["mic"]
    tz_name = market["tz"]

    price_url = (
        "https://api.boerse-frankfurt.de/v1/data/price_information/single"
        f"?isin={NVIDIA_ISIN}&mic={mic}"
    )
    box_url = (
        "https://api.boerse-frankfurt.de/v1/data/quote_box/single"
        f"?isin={NVIDIA_ISIN}&mic={mic}"
    )

    data = download_json(price_url)

    bid = ask = open_price = None
    box: dict = {}
    try:
        box = download_json(box_url)
        bid = float(box["bidLimit"]) if box.get("bidLimit") is not None else None
        ask = float(box["askLimit"]) if box.get("askLimit") is not None else None
        if box.get("open") is not None:
            open_price = float(box["open"])
    except Exception:  # noqa: BLE001
        pass

    currency_info = data.get("currency") or {}
    currency = currency_info.get("originalValue") or market["currency"]

    price = float(data["lastPrice"])
    previous_close = data.get("closingPricePrevTradingDay")
    previous_close = float(previous_close) if previous_close is not None else None
    change = float(data.get("changeToPrevDayAbsolute") or 0)
    change_pct = float(data.get("changeToPrevDayInPercent") or 0)
    high = float(data["dayHigh"]) if data.get("dayHigh") is not None else None
    low = float(data["dayLow"]) if data.get("dayLow") is not None else None
    volume = int(data["turnoverInPieces"]) if data.get("turnoverInPieces") is not None else None

    last_trade_at = parse_boerse_time(data.get("timestampLastPrice"), tz_name)
    now = datetime.now(ZoneInfo(tz_name))
    market_open = is_market_open(market_key, now)

    return Quote(
        symbol=market["symbol"],
        price=price,
        currency=str(currency),
        change=change,
        change_pct=change_pct,
        open_price=open_price,
        high=high,
        low=low,
        previous_close=previous_close,
        volume=volume,
        bid=bid,
        ask=ask,
        market_open=market_open,
        last_trade_at=last_trade_at,
        fetched_at=now,
        source_label="Börse Frankfurt (tempo reale)",
        realtime=True,
    )


def parse_eu_number(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def fetch_tradegate(market_key: str) -> Quote:
    market = MARKETS[market_key]
    tz_name = market["tz"]
    url = f"https://www.tradegate.de/refresh.php?isin={NVIDIA_ISIN}"
    data = download_json(url)

    price = parse_eu_number(data.get("last"))
    if price is None:
        raise RuntimeError("Tradegate: prezzo mancante")

    previous_close = parse_eu_number(data.get("close"))
    high = parse_eu_number(data.get("high"))
    low = parse_eu_number(data.get("low"))
    bid = parse_eu_number(data.get("bid"))
    ask = parse_eu_number(data.get("ask"))
    volume = None
    if data.get("stueck") is not None:
        try:
            volume = int(data["stueck"])
        except (TypeError, ValueError):
            volume = None

    if previous_close and previous_close != 0:
        change = price - previous_close
        change_pct = (change / previous_close) * 100
    else:
        # delta a volte è già la variazione assoluta
        change = parse_eu_number(data.get("delta")) or 0.0
        change_pct = (change / price) * 100 if price else 0.0

    now = datetime.now(ZoneInfo(tz_name))
    return Quote(
        symbol=market["symbol"],
        price=price,
        currency=market["currency"],
        change=change,
        change_pct=change_pct,
        open_price=None,
        high=high,
        low=low,
        previous_close=previous_close,
        volume=volume,
        bid=bid,
        ask=ask,
        market_open=is_market_open(market_key, now),
        last_trade_at=now,  # Tradegate non espone timestamp nel JSON refresh
        fetched_at=now,
        source_label="Tradegate (tempo reale)",
        realtime=True,
    )


def ensure_yahoo_crumb() -> str:
    global _YAHOO_CRUMB
    if _YAHOO_CRUMB:
        return _YAHOO_CRUMB

    # Inizializza cookie + crumb (necessari per quote Yahoo)
    subprocess.run(
        ["curl", "-sS", "-c", _YAHOO_COOKIE_FILE, "-b", _YAHOO_COOKIE_FILE, "-A", UA, "https://fc.yahoo.com"],
        capture_output=True,
        text=True,
        check=False,
    )
    completed = subprocess.run(
        [
            "curl",
            "-sS",
            "-b",
            _YAHOO_COOKIE_FILE,
            "-c",
            _YAHOO_COOKIE_FILE,
            "-A",
            UA,
            "https://query1.finance.yahoo.com/v1/test/getcrumb",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    crumb = (completed.stdout or "").strip()
    if (
        not crumb
        or completed.returncode != 0
        or " " in crumb
        or "Too Many" in crumb
        or "<" in crumb
    ):
        raise RuntimeError("Impossibile ottenere sessione Yahoo Finance")
    _YAHOO_CRUMB = crumb
    return crumb


def fetch_yahoo_chart(market_key: str) -> Quote:
    """Fallback Yahoo chart 1m se la quote API non è disponibile."""
    market = MARKETS[market_key]
    symbol = market["symbol"]
    tz_name = market["tz"]
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{symbol}?interval=1m&range=1d"
    )
    data = download_json(url)
    result = data["chart"]["result"][0]
    meta = result["meta"]
    quote_ind = result["indicators"]["quote"][0]
    closes = quote_ind.get("close") or []
    volumes = quote_ind.get("volume") or []
    timestamps = result.get("timestamp") or []

    price = float(meta.get("regularMarketPrice") or 0)
    # Preferisci ultimo close al minuto se più recente
    for close in reversed(closes):
        if close is not None:
            price = float(close)
            break

    previous_close = meta.get("previousClose") or meta.get("chartPreviousClose")
    previous_close = float(previous_close) if previous_close is not None else None
    if previous_close and previous_close != 0:
        change = price - previous_close
        change_pct = (change / previous_close) * 100
    else:
        change = 0.0
        change_pct = 0.0

    high = meta.get("regularMarketDayHigh")
    low = meta.get("regularMarketDayLow")
    volume = meta.get("regularMarketVolume")
    high = float(high) if high is not None else None
    low = float(low) if low is not None else None
    volume = int(volume) if volume is not None else None

    last_trade_at = None
    if timestamps:
        last_trade_at = datetime.fromtimestamp(int(timestamps[-1]), ZoneInfo(tz_name))
    elif meta.get("regularMarketTime"):
        last_trade_at = datetime.fromtimestamp(int(meta["regularMarketTime"]), ZoneInfo(tz_name))

    now = datetime.now(ZoneInfo(tz_name))
    return Quote(
        symbol=symbol,
        price=price,
        currency=str(meta.get("currency") or market["currency"]),
        change=change,
        change_pct=change_pct,
        open_price=None,
        high=high,
        low=low,
        previous_close=previous_close,
        volume=volume,
        bid=None,
        ask=None,
        market_open=is_market_open(market_key, now),
        last_trade_at=last_trade_at,
        fetched_at=now,
        source_label="Yahoo Finance (intraday 1m)",
        realtime=False,
    )


def fetch_yahoo(market_key: str) -> Quote:
    try:
        market = MARKETS[market_key]
        symbol = market["symbol"]
        tz_name = market["tz"]
        crumb = ensure_yahoo_crumb()
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}&crumb={crumb}"
        data = download_json(url, cookie_file=_YAHOO_COOKIE_FILE)
        results = (data.get("quoteResponse") or {}).get("result") or []
        if not results:
            raise RuntimeError(f"Nessuna quotazione Yahoo per {symbol}")
        q = results[0]

        price = float(q.get("regularMarketPrice") or 0)
        previous_close = q.get("regularMarketPreviousClose")
        previous_close = float(previous_close) if previous_close is not None else None
        change = float(q.get("regularMarketChange") or 0)
        change_pct = float(q.get("regularMarketChangePercent") or 0)
        open_price = q.get("regularMarketOpen")
        open_price = float(open_price) if open_price is not None else None
        high = q.get("regularMarketDayHigh")
        high = float(high) if high is not None else None
        low = q.get("regularMarketDayLow")
        low = float(low) if low is not None else None
        volume = q.get("regularMarketVolume")
        volume = int(volume) if volume is not None else None
        currency = q.get("currency") or market["currency"]

        last_trade_at = None
        ts = q.get("regularMarketTime")
        if ts:
            last_trade_at = datetime.fromtimestamp(int(ts), ZoneInfo(tz_name))

        delayed_by = int(q.get("exchangeDataDelayedBy") or 0)
        realtime = delayed_by == 0
        source_label = (
            "Yahoo Finance (tempo reale)"
            if realtime
            else f"Yahoo Finance (ritardo ~{delayed_by} min)"
        )

        now = datetime.now(ZoneInfo(tz_name))
        state = str(q.get("marketState") or "").upper()
        market_open = state in {"REGULAR", "PRE", "POST"} or is_market_open(market_key, now)

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
            bid=None,
            ask=None,
            market_open=market_open,
            last_trade_at=last_trade_at,
            fetched_at=now,
            source_label=source_label,
            realtime=realtime,
        )
    except Exception:
        return fetch_yahoo_chart(market_key)


def fetch_quote(market_key: str) -> Quote:
    market = MARKETS[market_key]
    if market["source"] == "boerse":
        return fetch_boerse(market_key)
    if market["source"] == "tradegate":
        return fetch_tradegate(market_key)
    return fetch_yahoo(market_key)


def is_market_open(market_key: str, now: datetime) -> bool:
    if now.weekday() >= 5:
        return False
    minutes = now.hour * 60 + now.minute
    if market_key in {"xetra", "frankfurt", "tradegate"}:
        # Europa: trading esteso circa 08:00–22:00 ora di Berlino
        return 8 * 60 <= minutes < 22 * 60
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
    live = "TEMPO REALE" if quote.realtime else "DATI IN RITARDO"

    trade_time = (
        quote.last_trade_at.strftime("%H:%M:%S %Z")
        if quote.last_trade_at
        else "—"
    )

    lines = [
        f"{bold}NVIDIA — {market['name']}{reset}  {dim}({quote.symbol}){reset}",
        f"{dim}{quote.source_label}  ·  {live}{reset}",
        "",
        f"{color}{bold}{quote.price:,.2f} {quote.currency}{reset}  "
        f"{color}{arrow} {sign}{quote.change:,.2f} ({sign}{quote.change_pct:.2f}%){reset}",
        "",
        f"  Ultimo trade     {trade_time}",
        f"  Bid / Ask        {money(quote.bid, quote.currency)} / {money(quote.ask, quote.currency)}",
        f"  Apertura         {money(quote.open_price, quote.currency)}",
        f"  Massimo          {money(quote.high, quote.currency)}",
        f"  Minimo           {money(quote.low, quote.currency)}",
        f"  Chiusura prec.   {money(quote.previous_close, quote.currency)}",
        f"  Volume           {volume_txt(quote.volume)}",
        f"  Stato mercato    {'Aperto' if quote.market_open else 'Chiuso'}",
        f"  Refresh          ogni {interval}s  ({quote.fetched_at.strftime('%H:%M:%S')})",
        "",
    ]
    if error:
        lines.append(f"\033[93mAvviso: {error}{reset}")
        lines.append("")
    lines.append(f"{dim}Ctrl+C per uscire{reset}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor NVIDIA Europa in tempo reale")
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
        default=2,
        help="Secondi tra aggiornamenti (default: 2)",
    )
    parser.add_argument("--once", action="store_true", help="Una sola quotazione")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.interval < 1:
        print("Intervallo minimo: 1 secondo")
        return 1

    last_quote: Optional[Quote] = None
    last_error: Optional[str] = None

    def refresh() -> None:
        nonlocal last_quote, last_error
        try:
            last_quote = fetch_quote(args.market)
            last_error = None
        except Exception as exc:  # noqa: BLE001
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

    print("Avvio monitor NVIDIA in tempo reale…")
    try:
        while True:
            refresh()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nMonitor interrotto.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
