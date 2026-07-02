/* ==========================================================================
   Structure & levels engine.
   Pulls OHLC per timeframe (Yahoo chart API via the tiered fetcher), then:
   - finds swing highs/lows (fractal pivots), clusters them into levels,
     ranks by touches + recency → supports below / resistances above
   - classifies the forming shape from the slopes of recent swing highs vs
     swing lows (trend, coil, ascending/descending triangle, range, ...)
   - emits the concrete levels to watch, with distance from spot
   Results are cached ~4 min per (symbol, interval) so multiple cards can
   share one fetch. All model-derived — labeled as such in the UI.
   ========================================================================== */
import { getAny } from './cboe.js';
import { fmt } from './app.js';

const YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart';

export const TF_SETS = [
  { key: '15m', label: '15m', interval: '15m', range: '5d' },
  { key: '1h',  label: '1h',  interval: '60m', range: '1mo' },
  { key: '1d',  label: '1D',  interval: '1d',  range: '6mo' },
  { key: '1w',  label: '1W',  interval: '1wk', range: '2y' }
];

const cache = new Map(); // key -> {ts, data}

async function fetchOHLC(symbol, interval, range) {
  const k = `${symbol}|${interval}`;
  const hit = cache.get(k);
  if (hit && Date.now() - hit.ts < 240_000) return hit.data;
  const j = await getAny(`${YAHOO}/${encodeURIComponent(symbol)}?interval=${interval}&range=${range}&includePrePost=false`);
  const r = j.chart?.result?.[0];
  const q = r?.indicators?.quote?.[0] || {};
  const candles = (r?.timestamp || []).map((t, i) => ({
    t, o: q.open?.[i], h: q.high?.[i], l: q.low?.[i], c: q.close?.[i]
  })).filter(x => x.h != null && x.l != null && x.c != null);
  if (candles.length < 20) throw new Error('ohlc: too few candles');
  cache.set(k, { ts: Date.now(), data: candles });
  return candles;
}

/* Fractal swing points: high[i] strictly greatest of i±k, same for lows. */
function swings(candles, k = 2) {
  const highs = [], lows = [];
  for (let i = k; i < candles.length - k; i++) {
    let isH = true, isL = true;
    for (let j = 1; j <= k; j++) {
      if (candles[i].h < candles[i - j].h || candles[i].h < candles[i + j].h) isH = false;
      if (candles[i].l > candles[i - j].l || candles[i].l > candles[i + j].l) isL = false;
    }
    if (isH) highs.push({ i, p: candles[i].h });
    if (isL) lows.push({ i, p: candles[i].l });
  }
  return { highs, lows };
}

/* Cluster nearby swing prices into levels; strength = touches + recency. */
function clusterLevels(points, tolPct, lastIndex) {
  const sorted = [...points].sort((a, b) => a.p - b.p);
  const clusters = [];
  for (const pt of sorted) {
    const c = clusters[clusters.length - 1];
    if (c && Math.abs(pt.p - c.price) / c.price <= tolPct) {
      c.touches++;
      c.price = (c.price * (c.touches - 1) + pt.p) / c.touches;
      c.lastI = Math.max(c.lastI, pt.i);
    } else {
      clusters.push({ price: pt.p, touches: 1, lastI: pt.i });
    }
  }
  for (const c of clusters) {
    const recency = 1 - Math.min(1, (lastIndex - c.lastI) / lastIndex); // 0..1
    c.strength = c.touches + recency * 1.5;
  }
  return clusters;
}

/* Slope of a simple linear fit over swing points, as % of price per bar. */
function slopePctPerBar(points) {
  if (points.length < 2) return 0;
  const n = points.length;
  const mx = points.reduce((s, p) => s + p.i, 0) / n;
  const my = points.reduce((s, p) => s + p.p, 0) / n;
  let num = 0, den = 0;
  for (const p of points) { num += (p.i - mx) * (p.p - my); den += (p.i - mx) ** 2; }
  const slope = den ? num / den : 0;
  return (slope / my) * 100;
}

function classifyShape(hs, ls, rangePct) {
  // thresholds scale with the timeframe's typical bar range
  const th = Math.max(0.008, rangePct * 0.04);
  const up = (s) => s > th, dn = (s) => s < -th, flat = (s) => Math.abs(s) <= th;
  if (up(hs) && up(ls))   return { shape: 'Uptrend', desc: 'higher highs & higher lows', cls: 'up' };
  if (dn(hs) && dn(ls))   return { shape: 'Downtrend', desc: 'lower highs & lower lows', cls: 'down' };
  if (dn(hs) && up(ls))   return { shape: 'Coil / triangle', desc: 'range contracting — breakout building', cls: 'gold' };
  if (up(hs) && dn(ls))   return { shape: 'Expanding range', desc: 'widening swings — whipsaw risk', cls: 'down' };
  if (flat(hs) && up(ls)) return { shape: 'Ascending triangle', desc: 'flat ceiling, rising floor — bullish lean', cls: 'up' };
  if (dn(hs) && flat(ls)) return { shape: 'Descending triangle', desc: 'falling ceiling, flat floor — bearish lean', cls: 'down' };
  return { shape: 'Range', desc: 'sideways between the levels', cls: 'flat' };
}

export async function analyzeTF(symbol, tf, spot) {
  const candles = await fetchOHLC(symbol, tf.interval, tf.range);
  const px = spot ?? candles[candles.length - 1].c;
  const { highs, lows } = swings(candles);
  const lastIndex = candles.length - 1;

  // typical bar range % (drives tolerances)
  const rangePct = candles.slice(-40).reduce((s, c) => s + (c.h - c.l) / c.c, 0) / Math.min(40, candles.length) * 100;
  const tol = Math.max(0.0012, rangePct / 100 * 0.35);

  const levels = clusterLevels([...highs, ...lows], tol, lastIndex)
    .filter(l => l.touches >= 2 || l.strength > 2);
  const supports = levels.filter(l => l.price < px).sort((a, b) => b.price - a.price).slice(0, 2);
  const resistances = levels.filter(l => l.price > px).sort((a, b) => a.price - b.price).slice(0, 2);

  const recentH = highs.slice(-6), recentL = lows.slice(-6);
  const { shape, desc, cls } = classifyShape(slopePctPerBar(recentH), slopePctPerBar(recentL), rangePct);

  const r1 = resistances[0], s1 = supports[0];
  const watch = r1 && s1
    ? `break ${fmt.usd(r1.price)} ↑ or lose ${fmt.usd(s1.price)} ↓`
    : r1 ? `break ${fmt.usd(r1.price)} ↑` : s1 ? `hold ${fmt.usd(s1.price)} ↓` : '—';

  return { tf: tf.label, key: tf.key, shape, desc, cls, supports, resistances, watch, px };
}

export async function analyzeAll(symbol, spot, tfs = TF_SETS) {
  const out = await Promise.allSettled(tfs.map(tf => analyzeTF(symbol, tf, spot)));
  return out.map((r, i) => r.status === 'fulfilled' ? r.value : { tf: tfs[i].label, failed: true });
}

const distPct = (px, p) => Math.abs(p - px) / px * 100;
const lvlSpan = (px, l, dir) =>
  `<span class="mono ${dir}">${fmt.usd(l.price)}</span> <span class="dim" style="font-size:11px">${distPct(px, l.price).toFixed(2)}% · ${l.touches}×</span>`;

/* Full-width panel: one row per timeframe. */
export function renderStructurePanel(el, analyses) {
  el.innerHTML = `
    <div class="card">
      <div class="card-head"><h3>Structure &amp; levels — what's forming, what to watch</h3>
        <span class="hint">model-derived from swing highs/lows · refreshes ~5 min</span></div>
      <div class="table-wrap"><table class="chain" style="font-size:12.5px">
        <thead><tr><th style="text-align:left">TF</th><th style="text-align:left">Shape forming</th>
          <th>Supports</th><th>Resistances</th><th style="text-align:left">Levels to watch</th></tr></thead>
        <tbody>
          ${analyses.map(a => a.failed
            ? `<tr><td style="text-align:left">${a.tf}</td><td colspan="4" class="dim" style="text-align:left">data unavailable</td></tr>`
            : `<tr>
              <td style="text-align:left;font-weight:700">${a.tf}</td>
              <td style="text-align:left"><span class="tag ${a.cls === 'up' ? 'call' : a.cls === 'down' ? 'put' : a.cls === 'gold' ? 'gold' : 'info'}">${a.shape}</span>
                <div class="dim" style="font-size:11px;font-family:var(--sans)">${a.desc}</div></td>
              <td>${a.supports.map(l => lvlSpan(a.px, l, 'up')).join('<br>') || '—'}</td>
              <td>${a.resistances.map(l => lvlSpan(a.px, l, 'down')).join('<br>') || '—'}</td>
              <td style="text-align:left;font-family:var(--sans);color:var(--text-2)">${a.watch}</td>
            </tr>`).join('')}
        </tbody>
      </table></div>
      <p class="note" style="margin-top:8px">Supports/resistances are clustered swing levels (price · distance · touch count). Heuristic read — confirm on the chart above.</p>
    </div>`;
}

/* Compact one-liner strip for the home featured card (1h + 1D). */
export function structureStrip(analyses) {
  const ok = analyses.filter(a => !a.failed);
  if (!ok.length) return '';
  return `<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:10px">
    ${ok.map(a => `<span class="note"><b>${a.tf}</b>
      <span class="tag ${a.cls === 'up' ? 'call' : a.cls === 'down' ? 'put' : a.cls === 'gold' ? 'gold' : 'info'}" style="margin:0 4px">${a.shape}</span>
      S <span class="mono up">${a.supports[0] ? fmt.usd(a.supports[0].price) : '—'}</span> ·
      R <span class="mono down">${a.resistances[0] ? fmt.usd(a.resistances[0].price) : '—'}</span></span>`).join('')}
  </div>`;
}
