/* ==========================================================================
   Options analytics engine.
   Black-Scholes pricing + Greeks (so we can reprice "what-if" scenarios),
   plus a per-contract synthesis: how far & how fast price must move to pay,
   leverage, decay burn, probability, comparisons, and a recommendation score.
   All estimates are model-based and clearly labeled — education, not advice.
   ========================================================================== */
import { fmt } from './app.js';

/* ---------- Black-Scholes core ---------- */
export function normCDF(x) {
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989422804 * Math.exp(-x * x / 2);
  let p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return x > 0 ? 1 - p : p;
}
const normPDF = (x) => 0.3989422804 * Math.exp(-x * x / 2);

export function bsPrice(type, S, K, T, r, sig) {
  if (T <= 0 || sig <= 0) return Math.max(0, type === 'call' ? S - K : K - S);
  const d1 = (Math.log(S / K) + (r + sig * sig / 2) * T) / (sig * Math.sqrt(T));
  const d2 = d1 - sig * Math.sqrt(T);
  return type === 'call'
    ? S * normCDF(d1) - K * Math.exp(-r * T) * normCDF(d2)
    : K * Math.exp(-r * T) * normCDF(-d2) - S * normCDF(-d1);
}

export function bsGreeks(type, S, K, T, r, sig) {
  if (T <= 0 || sig <= 0) {
    const itm = type === 'call' ? S > K : S < K;
    return { delta: itm ? (type === 'call' ? 1 : -1) : 0, gamma: 0, theta: 0, vega: 0 };
  }
  const sqrtT = Math.sqrt(T);
  const d1 = (Math.log(S / K) + (r + sig * sig / 2) * T) / (sig * sqrtT);
  const d2 = d1 - sig * sqrtT;
  const pdf = normPDF(d1);
  const delta = type === 'call' ? normCDF(d1) : normCDF(d1) - 1;
  const gamma = pdf / (S * sig * sqrtT);
  const vega = S * pdf * sqrtT / 100; // per 1 vol point
  const theta = (type === 'call'
    ? (-(S * pdf * sig) / (2 * sqrtT) - r * K * Math.exp(-r * T) * normCDF(d2))
    : (-(S * pdf * sig) / (2 * sqrtT) + r * K * Math.exp(-r * T) * normCDF(-d2))) / 365;
  return { delta, gamma, theta, vega };
}

/* ---------- Enrich a raw contract into a full synthesis ---------- */
export function derive(c, spot, riskFree = 0.043) {
  const type = c.type;
  const K = c.strike;
  const dte = c.dte ?? 0;
  const T = Math.max(dte, 0.5) / 365; // floor so 0DTE stays finite
  const iv = c.iv && c.iv > 0 ? c.iv : 0.15;
  const mid = c.mid ?? ((c.bid != null && c.ask != null && c.ask > 0) ? (c.bid + c.ask) / 2 : c.last) ?? 0;
  const spreadPct = (c.ask && c.bid != null && mid > 0) ? (c.ask - c.bid) / mid : null;

  const g = (c.delta != null && c.theta != null)
    ? { delta: c.delta, gamma: c.gamma ?? 0, theta: c.theta, vega: c.vega ?? 0 }
    : bsGreeks(type, spot, K, T, riskFree, iv);

  const intrinsic = Math.max(0, type === 'call' ? spot - K : K - spot);
  const extrinsic = Math.max(0, mid - intrinsic);
  const breakeven = type === 'call' ? K + mid : K - mid;
  const moveToBE = breakeven - spot;                 // $ underlying must travel (signed toward profit)
  const movePctToBE = (moveToBE / spot) * 100;       // signed
  const absMovePctBE = Math.abs(movePctToBE);

  // 1σ expected move of the UNDERLYING over the life of the option
  const sigma$ = spot * iv * Math.sqrt(T);
  const emPct = (sigma$ / spot) * 100;

  // Probability price finishes past breakeven (normal-on-price approx)
  const z = (breakeven - spot) / (sigma$ || 1e-9);
  const probITM = Math.abs(g.delta) * 100;           // rough market-implied
  const probBE = type === 'call' ? (1 - normCDF(z)) * 100 : normCDF(z) * 100;

  // Leverage: $ of underlying exposure controlled per $ of premium
  const leverage = mid > 0 ? Math.abs(g.delta) * spot / mid : 0;
  // Decay burn: theta as a % of premium lost per day
  const thetaPct = mid > 0 ? (g.theta / mid) * 100 : 0;  // negative = losing
  const thetaDollars = g.theta * 100;                    // per contract (x100 multiplier)
  const daysToZeroExtrinsic = (g.theta < 0 && extrinsic > 0) ? extrinsic / Math.abs(g.theta) : null;

  // Scenario repricing: value & % return if underlying moves by X% (favorable dir)
  const scenario = (movePct) => {
    const S2 = spot * (1 + movePct / 100);
    const Tf = Math.max(T - 1 / 365, 0.5 / 365); // ~end of next session
    const v = bsPrice(type, S2, K, Tf, riskFree, iv);
    return mid > 0 ? { value: v, retPct: (v / mid - 1) * 100 } : { value: v, retPct: 0 };
  };
  const dir = type === 'call' ? 1 : -1;
  const retAtEM = scenario(dir * emPct).retPct;     // return if it moves 1σ favorably (by next session)
  const retAt1pct = scenario(dir * 1).retPct;        // return per +1% favorable underlying move
  const retToDouble = (() => {                        // how far underlying must move (favorable) to ~2x
    for (let m = 0.1; m <= 12; m += 0.1) {
      if (scenario(dir * m).retPct >= 100) return dir * m;
    }
    return null;
  })();

  // Liquidity 0..1
  const vol = c.volume ?? 0, oi = c.openInterest ?? 0;
  const liq = Math.max(0,
    Math.min(1, 0.4 * Math.min(1, vol / 3000) + 0.3 * Math.min(1, oi / 8000) +
      0.3 * (spreadPct == null ? 0.3 : Math.max(0, 1 - spreadPct / 0.15))));

  return {
    ...c, mid, spreadPct, intrinsic, extrinsic, breakeven, moveToBE, movePctToBE, absMovePctBE,
    iv, ...g, emPct, sigma$, probITM, probBE, leverage, thetaPct, thetaDollars, daysToZeroExtrinsic,
    retAtEM, retAt1pct, retToDouble, liq,
    moneyness: type === 'call' ? spot - K : K - spot
  };
}

/* ---------- Score & label a contract ---------- */
export function score(d) {
  const reasons = [];
  let s = 0;

  // Value: expected move should comfortably clear the breakeven distance
  const cushion = d.emPct > 0 ? (d.emPct - d.absMovePctBE) / d.emPct : -1; // >0 = EM clears BE
  if (cushion > 0.25) { s += 26; reasons.push(`1σ move (~${fmt.pct(d.emPct, 1)}) clears breakeven with room`); }
  else if (cushion > 0) { s += 16; reasons.push('expected move just reaches breakeven'); }
  else if (cushion > -0.4) { s += 6; reasons.push('needs an above-average move to pay'); }
  else { reasons.push('needs a large move relative to what\'s priced'); }

  // Probability sweet spot (avoid lottery tickets & deep-ITM proxies)
  if (d.probBE >= 40 && d.probBE <= 68) { s += 20; reasons.push(`balanced odds (~${Math.round(d.probBE)}% past BE)`); }
  else if (d.probBE > 68) { s += 10; reasons.push('high odds but limited upside (deep ITM)'); }
  else if (d.probBE >= 28) { s += 12; reasons.push('lower-odds, higher-payoff'); }
  else { s += 3; reasons.push('long-shot payoff profile'); }

  // Convexity: gamma vs theta — reward move-sensitivity per unit decay
  const conv = Math.abs(d.theta) > 0 ? (d.gamma * d.mid) / Math.abs(d.theta) : 0;
  if (conv > 6) { s += 16; reasons.push('strong convexity vs decay'); }
  else if (conv > 2.5) { s += 10; reasons.push('healthy gamma/theta'); }
  else { s += 3; }

  // Leverage sweet band (5x–25x notional)
  if (d.leverage >= 5 && d.leverage <= 25) { s += 12; reasons.push(`efficient leverage (~${Math.round(d.leverage)}x notional)`); }
  else if (d.leverage > 25) { s += 5; reasons.push('very high leverage — fragile'); }
  else { s += 4; }

  // Liquidity
  s += Math.round(d.liq * 18);
  if (d.liq > 0.7) reasons.push('deep liquidity, tight spread');
  else if (d.liq < 0.35) reasons.push('thin — mind the spread/fills');

  // Decay penalty for very fast burn on cheap extrinsic
  if (d.thetaPct < -12) { s -= 8; reasons.push('heavy daily theta burn'); }

  // Deep ITM acts like a stock proxy — little convexity, lots of capital at risk
  const absDelta = Math.abs(d.delta);
  if (absDelta > 0.82) { s -= 10; reasons.push('deep ITM — behaves like a stock proxy, little convexity'); }

  s = Math.max(0, Math.min(100, Math.round(s)));
  // A true standout is a liquid, convex directional bet the priced move can pay —
  // not a delta-1 proxy and not a far-OTM lottery ticket.
  const standout = s >= 72 && d.liq > 0.55 && cushion > 0.15 &&
    absDelta >= 0.25 && absDelta <= 0.72 && (d.spreadPct == null || d.spreadPct < 0.08);
  return { score: s, reasons, convexity: conv, cushion, standout };
}

/* ---------- Verdict label ---------- */
export function verdict(s) {
  if (s >= 78) return { txt: 'Prime', cls: 'high' };
  if (s >= 62) return { txt: 'Strong', cls: 'high' };
  if (s >= 46) return { txt: 'Balanced', cls: 'med' };
  if (s >= 30) return { txt: 'Speculative', cls: 'low' };
  return { txt: 'Lottery', cls: 'low' };
}
