(() => {
  "use strict";

  const WMO = {
    0: { label: "Sereno", icon: "sole" },
    1: { label: "Prevalentemente sereno", icon: "sole" },
    2: { label: "Parzialmente nuvoloso", icon: "nuvoloso" },
    3: { label: "Coperto", icon: "coperto" },
    45: { label: "Nebbia", icon: "nebbia" },
    48: { label: "Nebbia con brina", icon: "nebbia" },
    51: { label: "Pioviggine leggera", icon: "pioggia" },
    53: { label: "Pioviggine", icon: "pioggia" },
    55: { label: "Pioviggine intensa", icon: "pioggia" },
    56: { label: "Pioviggine gelata leggera", icon: "pioggia" },
    57: { label: "Pioviggine gelata", icon: "pioggia" },
    61: { label: "Pioggia debole", icon: "pioggia" },
    63: { label: "Pioggia", icon: "pioggia" },
    65: { label: "Pioggia forte", icon: "pioggia" },
    66: { label: "Pioggia gelata leggera", icon: "pioggia" },
    67: { label: "Pioggia gelata", icon: "pioggia" },
    71: { label: "Neve debole", icon: "neve" },
    73: { label: "Neve", icon: "neve" },
    75: { label: "Neve intensa", icon: "neve" },
    77: { label: "Granelli di neve", icon: "neve" },
    80: { label: "Rovesci deboli", icon: "rovescio" },
    81: { label: "Rovesci", icon: "rovescio" },
    82: { label: "Rovesci violenti", icon: "rovescio" },
    85: { label: "Rovesci di neve deboli", icon: "neve" },
    86: { label: "Rovesci di neve", icon: "neve" },
    95: { label: "Temporale", icon: "temporale" },
    96: { label: "Temporale con grandine", icon: "temporale" },
    99: { label: "Temporale forte con grandine", icon: "temporale" },
  };

  const els = {
    status: document.getElementById("status"),
    statusText: document.getElementById("statusText"),
    refreshBtn: document.getElementById("refreshBtn"),
    placeLine: document.getElementById("placeLine"),
    headline: document.getElementById("headline"),
    temp: document.getElementById("temp"),
    condition: document.getElementById("condition"),
    feels: document.getElementById("feels"),
    updatedAt: document.getElementById("updatedAt"),
    metrics: document.getElementById("metrics"),
    hourly: document.getElementById("hourly"),
    daily: document.getElementById("daily"),
    marine: document.getElementById("marine"),
    sun: document.getElementById("sun"),
    coords: document.getElementById("coords"),
  };

  const REFRESH_MS = 10 * 60 * 1000;
  let timer = null;

  function weatherLabel(code) {
    return (WMO[code] && WMO[code].label) || `Codice meteo ${code}`;
  }

  function fmtTemp(v) {
    if (v == null || Number.isNaN(Number(v))) return "—";
    return `${Math.round(Number(v))}°`;
  }

  function fmtNum(v, digits = 0, suffix = "") {
    if (v == null || Number.isNaN(Number(v))) return "—";
    return `${Number(v).toFixed(digits)}${suffix}`;
  }

  function windDir(deg) {
    if (deg == null || Number.isNaN(Number(deg))) return "—";
    const dirs = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"];
    const i = Math.round(((Number(deg) % 360) / 45)) % 8;
    return `${dirs[i]} (${Math.round(Number(deg))}°)`;
  }

  function visibilityKm(m) {
    if (m == null || Number.isNaN(Number(m))) return "—";
    return `${(Number(m) / 1000).toFixed(1)} km`;
  }

  const TZ = "Europe/Rome";

  /** Open-Meteo returns wall-clock times in Europe/Rome without an offset. */
  function parseRome(iso) {
    if (!iso) return null;
    if (/[zZ]|[+-]\d{2}:?\d{2}$/.test(iso)) return new Date(iso);

    const m = iso.match(
      /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2}))?)?/
    );
    if (!m) return new Date(iso);

    const year = Number(m[1]);
    const month = Number(m[2]);
    const day = Number(m[3]);
    const hour = Number(m[4] || 12);
    const minute = Number(m[5] || 0);
    const second = Number(m[6] || 0);

    // Find the UTC instant whose Rome wall-clock matches this local time.
    let guess = Date.UTC(year, month - 1, day, hour, minute, second);
    for (let i = 0; i < 3; i += 1) {
      const parts = romeParts(new Date(guess));
      const asUtc = Date.UTC(
        parts.year,
        parts.month - 1,
        parts.day,
        parts.hour,
        parts.minute,
        parts.second
      );
      const target = Date.UTC(year, month - 1, day, hour, minute, second);
      guess += target - asUtc;
    }
    return new Date(guess);
  }

  function romeParts(date) {
    const parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: TZ,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hourCycle: "h23",
    }).formatToParts(date);
    const get = (type) => parts.find((p) => p.type === type)?.value;
    return {
      year: Number(get("year")),
      month: Number(get("month")),
      day: Number(get("day")),
      hour: Number(get("hour")),
      minute: Number(get("minute")),
      second: Number(get("second")),
    };
  }

  function formatClock(date) {
    if (!date) return "—";
    return date.toLocaleTimeString("it-IT", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: TZ,
    });
  }

  function formatDayName(date, index) {
    if (!date) return "—";
    if (index === 0) return "Oggi";
    if (index === 1) return "Domani";
    const name = date.toLocaleDateString("it-IT", {
      weekday: "long",
      day: "numeric",
      month: "short",
      timeZone: TZ,
    });
    return name.charAt(0).toUpperCase() + name.slice(1);
  }

  function formatHourLabel(date, isNow) {
    if (!date) return "—";
    if (isNow) return "Ora";
    return date.toLocaleTimeString("it-IT", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: TZ,
    });
  }

  function setStatus(ok, text) {
    els.status.classList.toggle("is-error", !ok);
    els.statusText.textContent = text;
  }

  function metric(label, value) {
    return `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function renderCurrent(data) {
    const cur = data.forecast.current || {};
    const daily = data.forecast.daily || {};
    const code = cur.weather_code;
    const isDay = cur.is_day === 1;

    els.placeLine.textContent = `${data.location.region}`;
    els.headline.textContent = isDay
      ? "Meteo e previsioni sulla costa"
      : "Notte sulla Riviera dei Fiori";
    els.temp.textContent = fmtTemp(cur.temperature_2m);
    els.condition.textContent = weatherLabel(code);
    els.feels.textContent = `Percepita ${fmtTemp(cur.apparent_temperature)} · Umidità ${fmtNum(cur.relative_humidity_2m, 0, "%")}`;

    const fetched = parseRome(data.fetched_at);
    els.updatedAt.textContent = fetched
      ? `Aggiornato alle ${formatClock(fetched)} · fonte Open-Meteo`
      : "Dati aggiornati";

    els.coords.textContent = `${data.location.latitude.toFixed(2)}°N · ${data.location.longitude.toFixed(2)}°E · ${data.location.timezone}`;

    els.metrics.innerHTML = [
      metric("Vento", `${fmtNum(cur.wind_speed_10m, 0, " km/h")} ${windDir(cur.wind_direction_10m)}`),
      metric("Raffiche", fmtNum(cur.wind_gusts_10m, 0, " km/h")),
      metric("Precipitazioni", fmtNum(cur.precipitation, 1, " mm")),
      metric("Nuvolosità", fmtNum(cur.cloud_cover, 0, "%")),
      metric("Pressione", fmtNum(cur.pressure_msl, 0, " hPa")),
      metric("UV", fmtNum(cur.uv_index, 1)),
      metric("Visibilità", visibilityKm(cur.visibility)),
      metric("Pioggia ora", fmtNum(cur.rain, 1, " mm")),
    ].join("");

    const sunrise = daily.sunrise && daily.sunrise[0] ? parseRome(daily.sunrise[0]) : null;
    const sunset = daily.sunset && daily.sunset[0] ? parseRome(daily.sunset[0]) : null;
    els.sun.innerHTML = [
      metric("Alba", formatClock(sunrise)),
      metric("Tramonto", formatClock(sunset)),
      metric("UV max oggi", fmtNum(daily.uv_index_max && daily.uv_index_max[0], 1)),
      metric("Pioggia oggi", fmtNum(daily.precipitation_sum && daily.precipitation_sum[0], 1, " mm")),
    ].join("");
  }

  function renderHourly(data) {
    const h = data.forecast.hourly || {};
    const times = h.time || [];
    const now = Date.now();
    let start = times.findIndex((t) => {
      const dt = parseRome(t);
      return dt && dt.getTime() >= now - 30 * 60 * 1000;
    });
    if (start < 0) start = 0;
    const end = Math.min(start + 24, times.length);

    const chunks = [];
    for (let i = start; i < end; i += 1) {
      const date = parseRome(times[i]);
      const isNow = i === start;
      chunks.push(`
        <article class="hour">
          <span class="when">${formatHourLabel(date, isNow)}</span>
          <span class="deg">${fmtTemp(h.temperature_2m[i])}</span>
          <span class="label">${weatherLabel(h.weather_code[i])}</span>
          <span class="rain">${fmtNum(h.precipitation_probability[i], 0, "%")} pioggia · ${fmtNum(h.wind_speed_10m[i], 0, " km/h")}</span>
        </article>
      `);
    }
    els.hourly.innerHTML = chunks.join("") || `<p class="note">Nessuna previsione oraria disponibile.</p>`;
  }

  function renderDaily(data) {
    const d = data.forecast.daily || {};
    const times = d.time || [];
    const rows = times.map((t, i) => {
      const date = parseRome(t);
      return `
        <article class="day">
          <div class="name">${formatDayName(date, i)}</div>
          <div class="desc">${weatherLabel(d.weather_code[i])}</div>
          <div class="temps">${fmtTemp(d.temperature_2m_max[i])}<small>${fmtTemp(d.temperature_2m_min[i])}</small></div>
          <div class="extra">${fmtNum(d.precipitation_probability_max[i], 0, "%")} pioggia · ${fmtNum(d.precipitation_sum[i], 1, " mm")}<br />vento ${fmtNum(d.wind_speed_10m_max[i], 0, " km/h")} ${windDir(d.wind_direction_10m_dominant[i])}</div>
        </article>
      `;
    });
    els.daily.innerHTML = rows.join("") || `<p class="note">Nessuna previsione giornaliera disponibile.</p>`;
  }

  function renderMarine(data) {
    if (!data.marine || !data.marine.current) {
      els.marine.innerHTML = `<p class="note">${data.marine_error ? `Mare non disponibile: ${data.marine_error}` : "Dati marini temporaneamente non disponibili."}</p>`;
      return;
    }
    const m = data.marine.current;
    const daily = data.marine.daily || {};
    els.marine.innerHTML = [
      metric("Temp. mare", fmtTemp(m.sea_surface_temperature)),
      metric("Altezza onde", fmtNum(m.wave_height, 1, " m")),
      metric("Periodo onde", fmtNum(m.wave_period, 0, " s")),
      metric("Direzione onde", windDir(m.wave_direction)),
      metric("Onde max (oggi)", fmtNum(daily.wave_height_max && daily.wave_height_max[0], 1, " m")),
      metric("Periodo max (oggi)", fmtNum(daily.wave_period_max && daily.wave_period_max[0], 0, " s")),
    ].join("");
  }

  async function loadWeather() {
    document.body.classList.add("is-loading");
    els.refreshBtn.disabled = true;
    setStatus(true, "Aggiornamento…");

    try {
      const res = await fetch(`/api/weather?t=${Date.now()}`, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || `Errore ${res.status}`);

      renderCurrent(data);
      renderHourly(data);
      renderDaily(data);
      renderMarine(data);
      setStatus(true, "Live");
    } catch (err) {
      console.error(err);
      setStatus(false, "Errore");
      els.updatedAt.textContent = err.message || "Impossibile caricare i dati meteo.";
    } finally {
      document.body.classList.remove("is-loading");
      els.refreshBtn.disabled = false;
    }
  }

  function schedule() {
    if (timer) clearInterval(timer);
    timer = setInterval(loadWeather, REFRESH_MS);
  }

  els.refreshBtn.addEventListener("click", () => {
    loadWeather();
    schedule();
  });

  loadWeather();
  schedule();
})();
