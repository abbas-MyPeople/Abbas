#!/usr/bin/env python3
"""Fetch multi-timeframe OHLCV candles (Yahoo chart API) and write committed JSON.

Companion to fetch_market.py: where that script snapshots the *current* quote and
options chain, this one persists real candle history at every timeframe the desk
analyzes — 1m through monthly — so analysis can zoom gross → subtle from data, not
inference. Stdlib only; designed to run inside GitHub Actions (which has open
egress) and commit results for consumers that don't.

Outputs stocks/data/candles/<sym>_<interval>.json plus a manifest.json describing
what succeeded, so a remote reader can diagnose failures without job logs.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "candles")
ET = ZoneInfo("America/New_York")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0"}

# symbol -> list of (interval, range). Ranges chosen to stay well inside Yahoo's
# per-interval caps (1m:7d, 5m/15m:60d, 60m:730d) with margin for API drift.
PLAN = {
    "^GSPC": [("1m", "5d"), ("5m", "30d"), ("15m", "60d"), ("60m", "180d"),
              ("1d", "2y"), ("1wk", "5y"), ("1mo", "20y")],
    "SPY":   [("1m", "5d"), ("5m", "30d"), ("15m", "60d"), ("60m", "180d"), ("1d", "2y")],
    "^VIX":  [("60m", "30d"), ("1d", "1y")],
}


def http_json(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def fetch(symbol, interval, rng):
    from urllib.parse import quote
    last_err = None
    for host in ("query1", "query2"):
        for attempt in range(3):
            try:
                j = http_json(
                    f"https://{host}.finance.yahoo.com/v8/finance/chart/{quote(symbol)}"
                    f"?interval={interval}&range={rng}&includePrePost=false"
                )
                res = j["chart"]["result"][0]
                ts = res.get("timestamp") or []
                q = res["indicators"]["quote"][0]
                candles = []
                for i, t in enumerate(ts):
                    o, h, l, c = (q[k][i] for k in ("open", "high", "low", "close"))
                    if None in (o, h, l, c):
                        continue  # partial/halted bar
                    candles.append({
                        "t": t,
                        "et": datetime.fromtimestamp(t, ET).isoformat(),
                        "o": round(o, 2), "h": round(h, 2),
                        "l": round(l, 2), "c": round(c, 2),
                        "v": (q.get("volume") or [None] * len(ts))[i],
                    })
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "range": rng,
                    "fetchedAt": datetime.now(timezone.utc).isoformat(),
                    "exchangeTZ": res.get("meta", {}).get("exchangeTimezoneName"),
                    "count": len(candles),
                    "candles": candles,
                }
            except Exception as e:  # noqa: BLE001 - record and retry
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(last_err or "unknown fetch error")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = {"generatedAt": datetime.now(timezone.utc).isoformat(), "files": {}, "errors": {}}
    for symbol, specs in PLAN.items():
        slug = symbol.lstrip("^").lower()
        for interval, rng in specs:
            name = f"{slug}_{interval}.json"
            try:
                data = fetch(symbol, interval, rng)
                with open(os.path.join(OUT_DIR, name), "w") as f:
                    json.dump(data, f, separators=(",", ":"))
                manifest["files"][name] = data["count"]
                print(f"ok  {name}: {data['count']} candles")
            except Exception as e:  # noqa: BLE001 - keep going; manifest records it
                manifest["errors"][name] = str(e)
                print(f"ERR {name}: {e}", file=sys.stderr)
            time.sleep(1)  # gentle pacing
    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    # Exit zero even with partial errors: committing what we got beats nothing,
    # and manifest.json tells the reader exactly what's missing.
    print(json.dumps({"ok": len(manifest["files"]), "err": len(manifest["errors"])}))


if __name__ == "__main__":
    main()
