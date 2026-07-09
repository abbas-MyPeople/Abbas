#!/usr/bin/env python3
"""Fetch multi-timeframe OHLCV candles from several free sources; write committed JSON.

Companion to fetch_market.py: persists real candle history at every timeframe the
desk analyzes (1m -> monthly) so analysis zooms gross -> subtle from data, not
inference. Stdlib only; runs inside GitHub Actions (open egress) and commits for
consumers that don't have it.

Sources, most-reliable first (each independent; partial success still commits):
- Stooq CSV      : daily/weekly/monthly OHLCV, deep history, no rate limits.
- CBOE cdn       : delayed intraday chart bars for _SPX/SPY (same host the
                   options snapshot already uses successfully from Actions).
- Yahoo chart API: intraday history (1m/5m/15m/60m) — rate-limits shared runner
                   IPs, so it's tried last with backoff; a 429 costs nothing.

Outputs stocks/data/candles/* plus manifest.json describing what succeeded.
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
UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Accept": "text/csv,application/json;q=0.9,*/*;q=0.8",
}
manifest = {"generatedAt": datetime.now(timezone.utc).isoformat(), "files": {}, "errors": {}}


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def save(name, payload, count):
    with open(os.path.join(OUT_DIR, name), "w") as f:
        f.write(payload)
    manifest["files"][name] = count
    print(f"ok  {name}: {count}")


def attempt(name, fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001 - record and continue; manifest tells the reader
        manifest["errors"][name] = f"{type(e).__name__}: {e}"
        print(f"ERR {name}: {e}", file=sys.stderr)


# ---------- Stooq: daily / weekly / monthly OHLCV ----------
def stooq(symbol, slug, interval, d1):
    def go():
        url = (f"https://stooq.com/q/d/l/?s={symbol}&i={interval}"
               f"&d1={d1}&d2={datetime.now(ET).strftime('%Y%m%d')}")
        body = http_get(url)
        rows = [r for r in body.strip().splitlines() if r]
        if len(rows) < 2 or not rows[0].lower().startswith("date"):
            raise ValueError(f"unexpected response: {body[:120]!r}")
        save(f"{slug}_{interval}_stooq.csv", body, len(rows) - 1)
    attempt(f"{slug}_{interval}_stooq.csv", go)


# ---------- CBOE: delayed intraday chart bars ----------
def cboe(symbol, slug):
    def go():
        url = f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{symbol}.json"
        body = http_get(url)
        j = json.loads(body)  # validate; commit raw for local parsing
        n = len(j.get("data") or [])
        save(f"{slug}_intraday_cboe.json", body, n)
    attempt(f"{slug}_intraday_cboe.json", go)


# ---------- Yahoo: intraday history (best effort, backoff on 429) ----------
def yahoo(symbol, slug, interval, rng):
    def go():
        from urllib.parse import quote
        last = None
        for i, host in enumerate(("query1", "query2", "query1", "query2")):
            try:
                body = http_get(
                    f"https://{host}.finance.yahoo.com/v8/finance/chart/{quote(symbol)}"
                    f"?interval={interval}&range={rng}&includePrePost=false")
                res = json.loads(body)["chart"]["result"][0]
                ts = res.get("timestamp") or []
                q = res["indicators"]["quote"][0]
                candles = [
                    {"t": t, "et": datetime.fromtimestamp(t, ET).isoformat(),
                     "o": round(q["open"][k], 2), "h": round(q["high"][k], 2),
                     "l": round(q["low"][k], 2), "c": round(q["close"][k], 2),
                     "v": (q.get("volume") or [None] * len(ts))[k]}
                    for k, t in enumerate(ts)
                    if None not in (q["open"][k], q["high"][k], q["low"][k], q["close"][k])
                ]
                out = {"symbol": symbol, "interval": interval, "range": rng,
                       "fetchedAt": datetime.now(timezone.utc).isoformat(),
                       "count": len(candles), "candles": candles}
                save(f"{slug}_{interval}.json", json.dumps(out, separators=(",", ":")),
                     len(candles))
                return
            except Exception as e:  # noqa: BLE001 - retry with backoff (429s often clear)
                last = e
                time.sleep(20 * (i + 1))
        raise last
    attempt(f"{slug}_{interval}.json", go)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Reliable sources first, so a Yahoo rate-limit can't block them.
    stooq("%5Espx", "gspc", "d", "20240101")
    stooq("%5Espx", "gspc", "w", "20200101")
    stooq("%5Espx", "gspc", "m", "20100101")
    stooq("spy.us", "spy", "d", "20240101")
    stooq("%5Evix", "vix", "d", "20250101")
    cboe("_SPX", "gspc")
    cboe("SPY", "spy")

    for sym, slug in (("^GSPC", "gspc"), ("SPY", "spy")):
        for interval, rng in (("1m", "5d"), ("5m", "30d"), ("15m", "60d"), ("60m", "180d")):
            yahoo(sym, slug, interval, rng)
            time.sleep(5)

    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    # Exit zero even on partial failure: committing what we got beats nothing.
    print(json.dumps({"ok": len(manifest["files"]), "err": len(manifest["errors"])}))


if __name__ == "__main__":
    main()
