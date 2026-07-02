#!/usr/bin/env python3
"""
Fetch SPY spot + options chain from CBOE's free delayed-quotes feed and write:
  stocks/data/spy/quote/latest.json
  stocks/data/spy/options/latest.json

CBOE delayed quotes include Greeks + IV already (~15 min delayed, no key).
VIX is pulled from Yahoo's public chart endpoint (best effort).
Stdlib only — no pip install needed in CI.

Swap SOURCE later for a real-time keyed provider without touching the frontend:
the frontend only reads the JSON files this script produces.
"""
import json, os, sys, math, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> stocks/
SYMBOL = "SPY"
MAX_DTE = 7
RISK_FREE = 0.043
UA = {"User-Agent": "Mozilla/5.0 (compatible; abbas-stocks-dashboard/1.0)"}

def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def now_et():
    # CI runs in UTC; approximate ET as UTC-4 (EDT). Good enough for DTE/labels.
    return datetime.datetime.utcnow() - datetime.timedelta(hours=4)

def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def bs_greeks(kind, S, K, T, r, sig):
    if T <= 0 or sig <= 0 or S <= 0 or K <= 0:
        itm = (S > K) if kind == "call" else (S < K)
        return {"delta": (1.0 if kind == "call" else -1.0) if itm else 0.0,
                "gamma": 0.0, "theta": 0.0, "vega": 0.0}
    sq = math.sqrt(T)
    d1 = (math.log(S / K) + (r + sig * sig / 2) * T) / (sig * sq)
    d2 = d1 - sig * sq
    pdf = math.exp(-d1 * d1 / 2) / math.sqrt(2 * math.pi)
    if kind == "call":
        delta = norm_cdf(d1)
        theta = (-(S * pdf * sig) / (2 * sq) - r * K * math.exp(-r * T) * norm_cdf(d2)) / 365
    else:
        delta = norm_cdf(d1) - 1
        theta = (-(S * pdf * sig) / (2 * sq) + r * K * math.exp(-r * T) * norm_cdf(-d2)) / 365
    gamma = pdf / (S * sig * sq)
    vega = S * pdf * sq / 100
    return {"delta": delta, "gamma": gamma, "theta": theta, "vega": vega}

def parse_occ(sym):
    """SPY260703C00620000 -> (expiry 'YYYY-MM-DD', 'call'/'put', strike float)."""
    root = sym[:len(sym) - 15]  # last 15 chars are date(6)+cp(1)+strike(8)
    tail = sym[len(root):]
    yy, mm, dd = tail[0:2], tail[2:4], tail[4:6]
    cp = tail[6]
    strike = int(tail[7:15]) / 1000.0
    expiry = f"20{yy}-{mm}-{dd}"
    return expiry, ("call" if cp == "C" else "put"), strike

def fetch_vix():
    try:
        j = http_json("https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=5d")
        res = j["chart"]["result"][0]
        meta = res["meta"]
        price = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        return price, (price - prev if price and prev else None)
    except Exception as e:
        print("VIX fetch failed:", e, file=sys.stderr)
        return None, None

def fetch_spark():
    try:
        j = http_json("https://query1.finance.yahoo.com/v8/finance/chart/SPY?interval=5m&range=1d")
        closes = j["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        return [round(c, 2) for c in closes if c is not None][-60:]
    except Exception as e:
        print("spark fetch failed:", e, file=sys.stderr)
        return None

def main():
    cboe = http_json(f"https://cdn.cboe.com/api/global/delayed_quotes/options/{SYMBOL}.json")
    data = cboe["data"]
    spot = data.get("current_price") or data.get("close")
    prev = data.get("prev_day_close")
    ts = cboe.get("timestamp") or now_et().isoformat()
    # True UTC — the frontend's "as of / ago" math parses this as an instant.
    as_of = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    today = now_et().date()
    contracts = []
    atm_iv_by_exp = {}
    for o in data.get("options", []):
        try:
            expiry, kind, strike = parse_occ(o["option"])
        except Exception:
            continue
        edate = datetime.date.fromisoformat(expiry)
        dte = (edate - today).days
        if dte < 0 or dte > MAX_DTE:
            continue
        iv = o.get("iv") or 0.0
        bid, ask = o.get("bid") or 0.0, o.get("ask") or 0.0
        last = o.get("last_trade_price") or 0.0
        mid = (bid + ask) / 2 if (bid and ask) else last
        delta, gamma = o.get("delta"), o.get("gamma")
        theta, vega = o.get("theta"), o.get("vega")
        if delta is None or theta is None:  # fill any gaps with our own BS
            g = bs_greeks(kind, spot, strike, max(dte, 0.5) / 365, RISK_FREE, iv or 0.15)
            delta = delta if delta is not None else g["delta"]
            gamma = gamma if gamma is not None else g["gamma"]
            theta = theta if theta is not None else g["theta"]
            vega = vega if vega is not None else g["vega"]
        contracts.append({
            "type": kind, "expiry": expiry, "dte": dte, "strike": strike,
            "bid": round(bid, 2), "ask": round(ask, 2), "last": round(last, 2), "mid": round(mid, 2),
            "iv": round(iv, 4), "delta": round(delta, 4), "gamma": round(gamma, 6),
            "theta": round(theta, 4), "vega": round(vega, 4),
            "volume": o.get("volume") or 0, "openInterest": o.get("open_interest") or 0,
        })
        # track ATM iv (closest strike to spot) per expiry
        d = abs(strike - spot)
        if expiry not in atm_iv_by_exp or d < atm_iv_by_exp[expiry][0]:
            atm_iv_by_exp[expiry] = (d, iv)

    contracts.sort(key=lambda c: (c["expiry"], c["type"], c["strike"]))

    # nearest-expiry ATM IV -> implied daily move
    near_iv = None
    if atm_iv_by_exp:
        near_exp = min(atm_iv_by_exp.keys())
        near_iv = atm_iv_by_exp[near_exp][1]
    daily_move_pct = round(near_iv * math.sqrt(1 / 365) * 100, 3) if near_iv else None

    vix, vix_chg = fetch_vix()
    spark = fetch_spark()

    change = (spot - prev) if (spot and prev) else None
    change_pct = (change / prev * 100) if (change and prev) else None

    quote = {
        "symbol": SYMBOL, "asOf": as_of, "price": round(spot, 2) if spot else None,
        "prevClose": round(prev, 2) if prev else None,
        "change": round(change, 2) if change is not None else None,
        "changePct": round(change_pct, 3) if change_pct is not None else None,
        "open": round(data["open"], 2) if data.get("open") else None,
        "dayHigh": round(data["high"], 2) if data.get("high") else None,
        "dayLow": round(data["low"], 2) if data.get("low") else None,
        "volume": data.get("volume"),
        "vix": round(vix, 2) if vix else None,
        "dailyMovePct": daily_move_pct,
        "spark": spark,
    }
    options = {
        "symbol": SYMBOL, "asOf": as_of, "spot": round(spot, 2) if spot else None,
        "riskFree": RISK_FREE, "maxDTE": MAX_DTE, "source": "CBOE delayed (~15m)",
        "expirations": sorted(atm_iv_by_exp.keys()), "contracts": contracts,
    }

    write(os.path.join(ROOT, "data", "spy", "quote", "latest.json"), quote)
    write(os.path.join(ROOT, "data", "spy", "options", "latest.json"), options)
    print(f"OK: {len(contracts)} contracts <= {MAX_DTE}DTE, spot={spot}, dailyMove={daily_move_pct}%")

def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

if __name__ == "__main__":
    main()
