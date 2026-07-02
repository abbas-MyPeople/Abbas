/* ==========================================================================
   Live market data, straight from the browser.
   Fetches Cboe's public delayed-quotes CDN (same source the CI snapshot job
   uses) so freshness never depends on GitHub Actions cron. Callers try this
   first and silently fall back to the committed JSON snapshot on any failure
   (CORS, offline, endpoint change) — the dashboard can only get fresher,
   never more broken. Feed itself is ~15-min delayed (free tier).
   ========================================================================== */

const CDN = 'https://cdn.cboe.com/api/global/delayed_quotes';

/* Fetch JSON with a hard timeout; if the direct call fails (CORS, network),
   retry once through a keyless CORS relay. Cache-busted per minute. */
async function get(url, ms) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), ms);
  try {
    const r = await fetch(url, { cache: 'no-store', signal: ctl.signal });
    if (!r.ok) throw new Error('http ' + r.status);
    return await r.json();
  } finally { clearTimeout(t); }
}
async function getJSON(path) {
  const url = `${CDN}/${path}?_=${Math.floor(Date.now() / 60000)}`;
  try { return await get(url, 7000); }
  catch (e) {
    return await get('https://api.allorigins.win/raw?url=' + encodeURIComponent(url), 10000);
  }
}

/* Cboe stamps ET wall-clock strings; convert to a real UTC instant so
   fmt.ago() math is honest. */
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

/* Full live pull: quote + near-dated chain in our snapshot schema. */
export async function fetchLiveMarket(symbol = 'SPY', maxDTE = 7) {
  const j = await getJSON(`options/${symbol}.json`);
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

  const quote = {
    symbol, asOf, price: spot,
    change: d.price_change, changePct: d.price_change_percent,
    open: d.open, dayHigh: d.high, dayLow: d.low,
    prevClose: d.prev_day_close, volume: d.volume,
    // iv30 is annualized %; per-day 1σ ≈ iv30 / √252
    dailyMovePct: d.iv30 ? d.iv30 / Math.sqrt(252) : undefined,
    source: 'live'
  };
  return { quote, chain: { symbol, asOf, spot, riskFree: 0.043, maxDTE, source: 'live', contracts } };
}

export async function fetchLiveQuote(symbol = 'SPY') {
  const { quote } = await fetchLiveMarket(symbol, -1); // skip contract collection
  return quote;
}

export async function fetchLiveVIX() {
  const d = (await getJSON('quotes/_VIX.json')).data || {};
  return { vix: d.current_price ?? d.close, vixChg: d.price_change };
}
