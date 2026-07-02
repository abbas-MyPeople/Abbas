/* ==========================================================================
   Market data tiers, fetched straight from the browser.

   Tier 1 — REAL-TIME price: Yahoo's chart API (real-time for US equities).
   Tier 2 — ~15-min delayed: Cboe public delayed-quotes CDN (quote + the full
            options chain; free real-time OPTIONS data does not exist).
   Tier 3 — committed JSON snapshot from CI (offline/last resort).

   Every fetch: direct first, then keyless CORS relays, all with hard
   timeouts. Callers merge tiers so the freshest field always wins and the
   UI labels what it's showing. Failure never breaks the page — it just
   falls down a tier.
   ========================================================================== */

const CDN = 'https://cdn.cboe.com/api/global/delayed_quotes';
const YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart';

async function get(url, ms) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), ms);
  try {
    const r = await fetch(url, { cache: 'no-store', signal: ctl.signal });
    if (!r.ok) throw new Error('http ' + r.status);
    return await r.json();
  } finally { clearTimeout(t); }
}

/* Direct → corsproxy.io → allorigins. Cache-busted per minute. */
async function getAny(url) {
  const busted = url + (url.includes('?') ? '&' : '?') + '_=' + Math.floor(Date.now() / 60000);
  try { return await get(busted, 6000); } catch (e) { /* next tier */ }
  try { return await get('https://corsproxy.io/?url=' + encodeURIComponent(busted), 8000); } catch (e) { /* next */ }
  return await get('https://api.allorigins.win/raw?url=' + encodeURIComponent(busted), 9000);
}

/* Drop undefined values so tier-merging via spread never clobbers a real
   field with an empty one. */
function clean(o) {
  const out = {};
  for (const k in o) if (o[k] !== undefined && o[k] !== null) out[k] = o[k];
  return out;
}

/* Cboe stamps ET wall-clock strings; convert to a real UTC instant. */
function etOffsetMs() {
  const nowEt = new Date().toLocaleString('sv-SE', { timeZone: 'America/New_York' });
  return Date.now() - Date.parse(nowEt.replace(' ', 'T') + 'Z');
}
export function etToISO(s) {
  if (!s) return null;
  const t = Date.parse(String(s).replace(' ', 'T') + 'Z');
  if (isNaN(t)) return null;
  return new Date(t + etOffsetMs()).toISOString().slice(0, 19) + 'Z';
}

function etToday() {
  return new Date().toLocaleString('sv-SE', { timeZone: 'America/New_York' }).slice(0, 10);
}

/* ---------- Tier 1: real-time quote (Yahoo) ---------- */
export async function fetchRealtimeQuote(symbol = 'SPY') {
  const j = await getAny(`${YAHOO}/${encodeURIComponent(symbol)}?interval=1m&range=1d&includePrePost=false`);
  const r = j.chart?.result?.[0];
  const m = r?.meta || {};
  const price = m.regularMarketPrice;
  if (price == null) throw new Error('yahoo: no price');
  const prev = m.chartPreviousClose ?? m.previousClose;
  const closes = (r.indicators?.quote?.[0]?.close || []).filter(v => v != null);
  return clean({
    symbol,
    asOf: new Date((m.regularMarketTime || Math.floor(Date.now() / 1000)) * 1000)
      .toISOString().slice(0, 19) + 'Z',
    price,
    prevClose: prev,
    change: prev != null ? price - prev : undefined,
    changePct: prev ? ((price - prev) / prev) * 100 : undefined,
    dayHigh: m.regularMarketDayHigh,
    dayLow: m.regularMarketDayLow,
    volume: m.regularMarketVolume,
    spark: closes.length > 10 ? closes.filter((_, i) => i % 5 === 0) : undefined,
    source: 'realtime'
  });
}

/* ---------- Tier 2: delayed quote + options chain (Cboe) ---------- */

/* OCC symbol: ROOT + YYMMDD + C/P + strike*1000 (8 digits) */
function parseOcc(sym) {
  const m = /^([A-Z]+)(\d{6})([CP])(\d{8})$/.exec(sym);
  if (!m) return null;
  return {
    expiry: `20${m[2].slice(0, 2)}-${m[2].slice(2, 4)}-${m[2].slice(4, 6)}`,
    type: m[3] === 'C' ? 'call' : 'put',
    strike: Number(m[4]) / 1000
  };
}

export async function fetchLiveMarket(symbol = 'SPY', maxDTE = 7) {
  const j = await getAny(`${CDN}/options/${symbol}.json`);
  const d = j.data || {};
  const spot = d.current_price ?? d.close;
  if (!spot) throw new Error('cboe: no price');
  const asOf = etToISO(j.timestamp || d.last_trade_time) || new Date().toISOString().slice(0, 19) + 'Z';

  const todayMs = Date.parse(etToday());
  const contracts = [];
  for (const o of d.options || []) {
    const p = parseOcc(o.option); if (!p) continue;
    const dte = Math.round((Date.parse(p.expiry) - todayMs) / 86400000);
    if (dte < 0 || dte > maxDTE) continue;
    contracts.push({
      ...p, dte,
      bid: o.bid, ask: o.ask,
      mid: (o.bid != null && o.ask > 0) ? (o.bid + o.ask) / 2 : o.last_trade_price,
      last: o.last_trade_price,
      iv: o.iv, delta: o.delta, gamma: o.gamma, theta: o.theta, vega: o.vega,
      volume: o.volume, openInterest: o.open_interest
    });
  }

  const quote = clean({
    symbol, asOf, price: spot,
    change: d.price_change, changePct: d.price_change_percent,
    open: d.open, dayHigh: d.high, dayLow: d.low,
    prevClose: d.prev_day_close, volume: d.volume,
    // iv30 is annualized %; per-day 1σ ≈ iv30 / √252
    dailyMovePct: d.iv30 ? d.iv30 / Math.sqrt(252) : undefined,
    source: 'delayed'
  });
  return { quote, chain: { symbol, asOf, spot, riskFree: 0.043, maxDTE, source: 'delayed', contracts } };
}

/* ---------- Best-available quote: merge real-time over delayed ---------- */
export async function fetchLiveQuote(symbol = 'SPY') {
  const [rt, dl] = await Promise.allSettled([
    fetchRealtimeQuote(symbol),
    fetchLiveMarket(symbol, -1).then(x => x.quote)
  ]);
  const delayed = dl.status === 'fulfilled' ? dl.value : null;
  const realtime = rt.status === 'fulfilled' ? rt.value : null;
  if (!delayed && !realtime) throw new Error('no live quote');
  // Real-time fields win; delayed fills gaps (open, iv30-derived move).
  return { ...(delayed || {}), ...(realtime || {}) };
}

/* ---------- VIX: Yahoo real-time first, Cboe delayed fallback ---------- */
export async function fetchLiveVIX() {
  try {
    const j = await getAny(`${YAHOO}/%5EVIX?interval=1m&range=1d`);
    const m = j.chart?.result?.[0]?.meta || {};
    if (m.regularMarketPrice != null) {
      const prev = m.chartPreviousClose ?? m.previousClose;
      return { vix: m.regularMarketPrice, vixChg: prev != null ? m.regularMarketPrice - prev : undefined };
    }
    throw new Error('yahoo vix empty');
  } catch (e) {
    const d = (await getAny(`${CDN}/quotes/_VIX.json`)).data || {};
    return { vix: d.current_price ?? d.close, vixChg: d.price_change };
  }
}

/* Human label for a quote source. */
export function sourceLabel(src) {
  return src === 'realtime' ? 'real-time'
    : src === 'delayed' || src === 'live' ? '~15 min delayed'
    : 'snapshot';
}
