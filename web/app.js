(() => {
  const REFRESH_MS = 2000;
  const DEFAULT_STOCK = "nvidia";
  const DEFAULT_MARKET = "xetra";

  let stock = localStorage.getItem("monitor_stock") || DEFAULT_STOCK;
  let market = localStorage.getItem("monitor_market") || DEFAULT_MARKET;
  let stocksMeta = [];
  let timer = null;
  let lastPrice = null;

  const els = {
    body: document.body,
    stocks: document.getElementById("stocks"),
    livePill: document.getElementById("livePill"),
    liveText: document.getElementById("liveText"),
    brand: document.getElementById("brand"),
    marketName: document.getElementById("marketName"),
    price: document.getElementById("price"),
    change: document.getElementById("change"),
    tradeMeta: document.getElementById("tradeMeta"),
    markets: document.getElementById("markets"),
    bidAsk: document.getElementById("bidAsk"),
    open: document.getElementById("open"),
    high: document.getElementById("high"),
    low: document.getElementById("low"),
    volume: document.getElementById("volume"),
    source: document.getElementById("source"),
  };

  function money(value, currency) {
    if (value === null || value === undefined || Number.isNaN(value)) return "—";
    return `${Number(value).toLocaleString("it-IT", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} ${currency}`;
  }

  function volumeTxt(value) {
    if (value === null || value === undefined) return "—";
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
    return String(value);
  }

  function formatTime(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleTimeString("it-IT", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return "—";
    }
  }

  function currentStockMeta() {
    return stocksMeta.find((s) => s.id === stock) || null;
  }

  function applyTheme(meta) {
    const accent = meta?.accent || "#76b900";
    els.body.dataset.stock = stock;
    els.body.style.setProperty("--accent", accent);
    els.body.style.setProperty("--accent-soft", hexToRgba(accent, 0.18));
    els.body.style.setProperty("--accent-border", hexToRgba(accent, 0.35));
    els.brand.textContent = meta?.name || stock.toUpperCase();
    document.title = `${meta?.name || "Monitor"} — Tempo reale`;
  }

  function hexToRgba(hex, alpha) {
    const raw = (hex || "").replace("#", "");
    if (raw.length !== 6) return `rgba(118, 185, 0, ${alpha})`;
    const r = parseInt(raw.slice(0, 2), 16);
    const g = parseInt(raw.slice(2, 4), 16);
    const b = parseInt(raw.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function ensureMarketForStock() {
    const meta = currentStockMeta();
    if (!meta?.markets?.length) return;
    const exists = meta.markets.some((m) => m.id === market);
    if (!exists) {
      market = meta.markets[0].id;
      localStorage.setItem("monitor_market", market);
    }
  }

  function setStocks(list) {
    stocksMeta = list;
    els.stocks.innerHTML = "";
    list.forEach((s) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = s.name;
      btn.dataset.stock = s.id;
      if (s.id === stock) btn.classList.add("active");
      btn.addEventListener("click", () => {
        if (stock === s.id) return;
        stock = s.id;
        localStorage.setItem("monitor_stock", stock);
        lastPrice = null;
        ensureMarketForStock();
        applyTheme(currentStockMeta());
        [...els.stocks.children].forEach((el) =>
          el.classList.toggle("active", el.dataset.stock === stock)
        );
        setMarkets(currentStockMeta()?.markets || []);
        refresh();
      });
      els.stocks.appendChild(btn);
    });
  }

  function setMarkets(list) {
    els.markets.innerHTML = "";
    list.forEach((m) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = m.name;
      btn.dataset.market = m.id;
      if (m.id === market) btn.classList.add("active");
      btn.addEventListener("click", () => {
        market = m.id;
        localStorage.setItem("monitor_market", market);
        lastPrice = null;
        [...els.markets.children].forEach((el) =>
          el.classList.toggle("active", el.dataset.market === market)
        );
        refresh();
      });
      els.markets.appendChild(btn);
    });
  }

  function render(data) {
    const up = data.change >= 0;
    const sign = up ? "+" : "";

    els.brand.textContent = data.stock_name;
    els.marketName.textContent = `${data.market_name} · ${data.symbol}`;
    els.price.textContent = money(data.price, data.currency);
    els.change.textContent = `${up ? "▲" : "▼"} ${sign}${Number(data.change).toFixed(2)} (${sign}${Number(data.change_pct).toFixed(2)}%)`;
    els.change.className = `change ${up ? "up" : "down"}`;

    if (lastPrice !== null && data.price !== lastPrice) {
      const flashClass = data.price > lastPrice ? "flash-up" : "flash-down";
      els.price.classList.remove("flash-up", "flash-down");
      void els.price.offsetWidth;
      els.price.classList.add(flashClass);
      setTimeout(() => els.price.classList.remove(flashClass), 350);
    }
    lastPrice = data.price;

    const state = data.market_open ? "Mercato aperto" : "Mercato chiuso";
    els.tradeMeta.textContent = `Ultimo trade ${formatTime(data.last_trade_at)} · ${state}`;

    els.bidAsk.textContent = `${money(data.bid, data.currency)} / ${money(data.ask, data.currency)}`;
    els.open.textContent = money(data.open, data.currency);
    els.high.textContent = money(data.high, data.currency);
    els.low.textContent = money(data.low, data.currency);
    els.volume.textContent = volumeTxt(data.volume);
    els.source.textContent = data.source_label;

    if (data.realtime) {
      els.livePill.classList.remove("delayed");
      els.liveText.textContent = "TEMPO REALE";
    } else {
      els.livePill.classList.add("delayed");
      els.liveText.textContent = "DATI IN RITARDO";
    }
  }

  async function refresh() {
    try {
      const res = await fetch(
        `/api/quote?stock=${encodeURIComponent(stock)}&market=${encodeURIComponent(market)}`,
        { cache: "no-store" }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Errore rete");
      render(data);
    } catch (err) {
      els.tradeMeta.textContent = `Errore: ${err.message || err}`;
    }
  }

  async function boot() {
    try {
      const res = await fetch("/api/stocks", { cache: "no-store" });
      const data = await res.json();
      if (!data.stocks?.length) throw new Error("Nessun titolo");
      if (!data.stocks.some((s) => s.id === stock)) stock = data.stocks[0].id;
      setStocks(data.stocks);
      ensureMarketForStock();
      applyTheme(currentStockMeta());
      setMarkets(currentStockMeta()?.markets || []);
    } catch {
      setStocks([
        {
          id: "nvidia",
          name: "NVIDIA",
          accent: "#76b900",
          markets: [
            { id: "xetra", name: "Xetra (Europa)" },
            { id: "frankfurt", name: "Francoforte" },
            { id: "tradegate", name: "Tradegate (Europa)" },
            { id: "nasdaq", name: "NASDAQ (USA)" },
          ],
        },
        {
          id: "tesla",
          name: "Tesla",
          accent: "#cc0000",
          markets: [
            { id: "xetra", name: "Xetra (Europa)" },
            { id: "frankfurt", name: "Francoforte" },
            { id: "tradegate", name: "Tradegate (Europa)" },
            { id: "nasdaq", name: "NASDAQ (USA)" },
          ],
        },
        {
          id: "rheinmetall",
          name: "Rheinmetall",
          accent: "#1f6feb",
          markets: [
            { id: "xetra", name: "Xetra (Europa)" },
            { id: "frankfurt", name: "Francoforte" },
            { id: "tradegate", name: "Tradegate (Europa)" },
          ],
        },
      ]);
      ensureMarketForStock();
      applyTheme(currentStockMeta());
      setMarkets(currentStockMeta()?.markets || []);
    }
    await refresh();
    timer = setInterval(refresh, REFRESH_MS);
  }

  boot();
})();
