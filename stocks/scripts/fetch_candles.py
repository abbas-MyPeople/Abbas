#!/usr/bin/env python3
"""Fetch multi-timeframe S&P 500 candles from several free sources; write committed JSON/CSV.

Persists real candle history at every timeframe the desk analyzes (1m -> monthly)
so analysis zooms gross -> subtle from data, not inference. Stdlib only; runs in
GitHub Actions (open egress) and commits for consumers that don't have it.

Sources (each independent; partial success still commits, manifest records the rest):
- FRED CSV        : SP500 daily closes, trailing 10y. Boring and reliable.
- Stooq CSV       : deep daily/weekly/monthly OHLCV — needs a cookie handshake and
                    is download-limited per IP, so treated as opportunistic.
- MarketWatch CSV : dot-com-era daily OHLC, fetched year-by-year.
- Yahoo chart API : intraday history (1m/5m/15m/60m) with the fc.yahoo.com
                    cookie + getcrumb handshake that clears datacenter 429s.
"""
import http.cookiejar
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "candles")
ET = ZoneInfo("America/New_York")
BASE_HEADERS = [
    ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0"),
    ("Accept", "text/csv,application/json;q=0.9,*/*;q=0.8"),
    ("Accept-Language", "en-US,en;q=0.9"),
]
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = BASE_HEADERS
manifest = {"generatedAt": datetime.now(timezone.utc).isoformat(), "files": {}, "errors": {}}


def http_get(url, timeout=30):
    with opener.open(url, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def save(name, payload, count):
    with open(os.path.join(OUT_DIR, name), "w") as f:
        f.write(payload)
    manifest["files"][name] = count
    print(f"ok  {name}: {count}")


def attempt(name, fn):
    try:
        fn()
        return True
    except Exception as e:  # noqa: BLE001 - record and continue
        manifest["errors"][name] = f"{type(e).__name__}: {str(e)[:180]}"
        print(f"ERR {name}: {e}", file=sys.stderr)
        return False


def csv_rows(body):
    rows = [r for r in body.strip().splitlines() if r]
    if len(rows) < 2 or "<" in rows[0]:
        raise ValueError(f"unexpected response: {body[:100]!r}")
    return rows


# ---------- FRED: daily closes, trailing decade ----------
def fred():
    body = http_get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500")
    save("gspc_daily_close_fred.csv", body, len(csv_rows(body)) - 1)


# ---------- Stooq: deep OHLCV (cookie handshake, opportunistic) ----------
def stooq(symbol, slug, interval, d1):
    def go():
        try:
            http_get(f"https://stooq.com/q/?s={symbol}")  # set cookies
        except Exception:  # noqa: BLE001 - handshake best-effort
            pass
        url = (f"https://stooq.com/q/d/l/?s={symbol}&i={interval}"
               f"&d1={d1}&d2={datetime.now(ET).strftime('%Y%m%d')}")
        body = http_get(url)
        save(f"{slug}_{interval}_stooq.csv", body, len(csv_rows(body)) - 1)
    attempt(f"{slug}_{interval}_stooq.csv", go)


# ---------- MarketWatch: historical daily OHLC by year ----------
def marketwatch(slug, year_from, year_to):
    # year-by-year pull; header kept from first chunk only
    def go():
        chunks, total = [], 0
        for y in range(year_from, year_to + 1):
            url = ("https://www.marketwatch.com/investing/index/spx/downloaddatapartial"
                   f"?startdate=01/01/{y}%2000:00:00&enddate=12/31/{y}%2000:00:00"
                   "&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false")
            rows = csv_rows(http_get(url))
            chunks.append("\n".join(rows if not chunks else rows[1:]))
            total += len(rows) - 1
            time.sleep(2)
        save(f"{slug}_daily_mw_{year_from}_{year_to}.csv", "\n".join(chunks), total)
    attempt(f"{slug}_daily_mw_{year_from}_{year_to}.csv", go)


# ---------- Yahoo: intraday history with cookie + crumb ----------
_crumb = None


def yahoo_crumb():
    global _crumb
    if _crumb is None:
        try:
            http_get("https://fc.yahoo.com")  # sets session cookie (404 is fine)
        except Exception:  # noqa: BLE001
            pass
        _crumb = http_get("https://query1.finance.yahoo.com/v1/test/getcrumb").strip()
    return _crumb


def yahoo(symbol, slug, interval, rng):
    def go():
        from urllib.parse import quote
        last = None
        for i, host in enumerate(("query1", "query2", "query1")):
            try:
                crumb = ""
                try:
                    crumb = "&crumb=" + quote(yahoo_crumb())
                except Exception:  # noqa: BLE001 - crumb is best-effort
                    pass
                body = http_get(
                    f"https://{host}.finance.yahoo.com/v8/finance/chart/{quote(symbol)}"
                    f"?interval={interval}&range={rng}&includePrePost=false{crumb}")
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
            except Exception as e:  # noqa: BLE001 - space out retries; 429s decay
                last = e
                time.sleep(25 * (i + 1))
        raise last
    attempt(f"{slug}_{interval}.json", go)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    attempt("gspc_daily_close_fred.csv", fred)
    stooq("%5Espx", "gspc", "d", "19950101")
    stooq("%5Espx", "gspc", "w", "19950101")
    stooq("%5Espx", "gspc", "m", "19500101")
    stooq("%5Evix", "vix", "d", "20150101")
    marketwatch("gspc", 1998, 2003)   # dot-com era daily OHLC
    marketwatch("gspc", 2025, 2026)   # current regime daily OHLC

    for sym, slug, specs in (
        ("^GSPC", "gspc", (("1m", "5d"), ("5m", "30d"), ("15m", "60d"), ("60m", "730d"))),
        ("SPY", "spy", (("1m", "5d"),)),
    ):
        for interval, rng in specs:
            yahoo(sym, slug, interval, rng)
            time.sleep(10)

    with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(json.dumps({"ok": len(manifest["files"]), "err": len(manifest["errors"])}))


if __name__ == "__main__":
    main()
