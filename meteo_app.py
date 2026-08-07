#!/usr/bin/env python3
"""
Meteo Bordighera — app web con dati e previsioni.
Usa Open-Meteo (nessuna API key). Nessuna libreria da installare.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import ssl
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "meteo"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787

# Bordighera (IM), Liguria
LATITUDE = 43.7804
LONGITUDE = 7.6632
TIMEZONE = "Europe/Rome"
LOCATION = {
    "name": "Bordighera",
    "region": "Liguria, Italia",
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "timezone": TIMEZONE,
}

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
USER_AGENT = "MeteoBordighera/1.0 (+https://github.com/marcobalza64-netizen/marco)"


def _http_get_json(url: str, timeout: float = 20.0) -> dict:
    """Scarica JSON. Su Mac preferisce curl (certificati Apple), poi urllib."""
    errors: list[str] = []
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    try:
        completed = subprocess.run(
            [
                "curl",
                "-fsSL",
                "--max-time",
                str(int(timeout)),
                "-A",
                USER_AGENT,
                "-H",
                "Accept: application/json",
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

    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"urllib: {exc}")

    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"urllib-insecure: {exc}")

    raise RuntimeError(" | ".join(errors))


def fetch_weather() -> dict:
    forecast_params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timezone": TIMEZONE,
        "forecast_days": 14,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "is_day",
                "precipitation",
                "rain",
                "showers",
                "snowfall",
                "weather_code",
                "cloud_cover",
                "pressure_msl",
                "surface_pressure",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
                "uv_index",
                "visibility",
            ]
        ),
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation_probability",
                "precipitation",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
                "uv_index",
                "is_day",
            ]
        ),
        "daily": ",".join(
            [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "sunrise",
                "sunset",
                "uv_index_max",
                "precipitation_sum",
                "precipitation_probability_max",
                "rain_sum",
                "showers_sum",
                "snowfall_sum",
                "precipitation_hours",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "wind_direction_10m_dominant",
            ]
        ),
        "wind_speed_unit": "kmh",
    }
    forecast_url = f"{OPEN_METEO_URL}?{urllib.parse.urlencode(forecast_params)}"
    forecast = _http_get_json(forecast_url)

    marine = None
    marine_error = None
    try:
        marine_params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "timezone": TIMEZONE,
            "forecast_days": 7,
            "current": "sea_surface_temperature,wave_height,wave_direction,wave_period",
            "hourly": "sea_surface_temperature,wave_height,wave_direction,wave_period",
            "daily": "wave_height_max,wave_direction_dominant,wave_period_max",
        }
        marine_url = f"{MARINE_URL}?{urllib.parse.urlencode(marine_params)}"
        marine = _http_get_json(marine_url)
    except Exception as exc:  # noqa: BLE001
        marine_error = str(exc)

    now = datetime.now(ZoneInfo(TIMEZONE))
    return {
        "location": LOCATION,
        "fetched_at": now.isoformat(),
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "forecast": forecast,
        "marine": marine,
        "marine_error": marine_error,
        "units": {
            "temperature": "°C",
            "wind": "km/h",
            "precipitation": "mm",
            "pressure": "hPa",
            "visibility": "m",
            "wave_height": "m",
            "wave_period": "s",
        },
        "source": {
            "name": "Open-Meteo",
            "url": "https://open-meteo.com/",
            "license": "CC BY 4.0",
        },
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "MeteoBordighera/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in {"/", "/index.html"}:
            return self._serve_file(WEB_DIR / "index.html")

        if path == "/api/health":
            return self._send_json(
                200,
                {
                    "ok": True,
                    "location": LOCATION,
                    "time": datetime.now(ZoneInfo(TIMEZONE)).isoformat(),
                },
            )

        if path == "/api/weather":
            try:
                return self._send_json(200, fetch_weather())
            except urllib.error.HTTPError as exc:
                return self._send_json(502, {"error": f"Open-Meteo HTTP {exc.code}: {exc.reason}"})
            except urllib.error.URLError as exc:
                return self._send_json(502, {"error": f"Rete non disponibile: {exc.reason}"})
            except Exception as exc:  # noqa: BLE001
                return self._send_json(502, {"error": str(exc)})

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
    parser = argparse.ArgumentParser(description="Meteo Bordighera — web app")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Porta (default: 8787)")
    parser.add_argument("--no-browser", action="store_true", help="Non aprire il browser")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not WEB_DIR.is_dir():
        print(f"Cartella meteo non trovata: {WEB_DIR}")
        return 1

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print("=== Meteo Bordighera ===")
    print(f"Apri nel browser: {url}")
    print("Dati: Open-Meteo (attuale, oraria, giornaliera, mare)")
    print("Per uscire: Ctrl+C")
    print()

    if not args.no_browser:
        open_browser_later(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer interrotto.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
