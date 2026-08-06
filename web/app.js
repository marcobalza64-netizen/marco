(() => {
  const REFRESH_MS = 2000;
  let market = localStorage.getItem("nvidia_market") || "xetra";
  let timer = null;
  let lastPrice = null;

  const els = {
    livePill: document.getElementById("livePill"),
    liveText: document.getElementById("liveText"),
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
        localStorage.setItem("nvidia_market", market);
        [...els.markets.children].forEach((el) => el.classList.toggle("active", el.dataset.market === market));
        refresh();
      });
      els.markets.appendChild(btn);
    });
  }

  function render(data) {
    const up = data.change >= 0;
    const sign = up ? "+" : "";

    els.marketName.textContent = `${data.market_name} · ${data.symbol}`;
    els.price.textContent = money(data.price, data.currency);
    els.change.textContent = `${up ? "▲" : "▼"} ${sign}${Number(data.change).toFixed(2)} (${sign}${Number(data.change_pct).toFixed(2)}%)`;
    els.change.className = `change ${up ? "up" : "down"}`;

    if (lastPrice !== null && data.price !== lastPrice) {
      const flashClass = data.price > lastPrice ? "flash-up" : "flash-down";
      els.price.classList.remove("flash-up", "flash-down");
      // force reflow for restart animation
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
      const res = await fetch(`/api/quote?market=${encodeURIComponent(market)}`, {
        cache: "no-store",
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Errore rete");
      render(data);
    } catch (err) {
      els.tradeMeta.textContent = `Errore: ${err.message || err}`;
    }
  }

  async function boot() {
    try {
      const res = await fetch("/api/markets", { cache: "no-store" });
      const data = await res.json();
      if (data.markets?.length) setMarkets(data.markets);
    } catch {
      setMarkets([
        { id: "xetra", name: "Xetra (Europa)" },
        { id: "frankfurt", name: "Francoforte" },
        { id: "tradegate", name: "Tradegate (Europa)" },
        { id: "nasdaq", name: "NASDAQ (USA)" },
      ]);
    }
    await refresh();
    timer = setInterval(refresh, REFRESH_MS);
  }

  boot();
})();
