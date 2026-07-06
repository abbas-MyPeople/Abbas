#!/usr/bin/env python3
"""GA4 Data API — website traffic + conversion-event time series for the Growth funnel.

WHY: the dashboard's Growth section keeps a LEADING tier (website visits → "order online" clicks)
that, until now, only ever showed a tasteful "connect GA4" placeholder. This module pulls the real
numbers so that tier lights up with live data, while leaving the placeholder intact when GA4 isn't
reachable (no creds, API not enabled, egress blocked) — never a broken/fake state.

PRIVACY (same rules as money.py / engine_v2): analytics/ syncs to a PUBLIC Hugging Face Space, so
NO secret is ever hardcoded or written to disk in analytics/. The service-account key arrives only
from the environment on the Space (GA4_SA_JSON, base64 or raw JSON), falling back to the local
gitignored key file (credentials/ga4-reader-sa.json) for dev. The cache file holds only aggregate
counts (no PII) and lives in a writable temp dir, NEVER inside analytics/.

AUTH: prefers google-auth (service_account.Credentials) when installed; otherwise falls back to a
pure-stdlib RS256 JWT → OAuth2 token exchange (the same lean urllib style as engine_v2), so the
module works even if the Space image lacks google-auth. Both paths sign the SA's JWT for the
analytics.readonly scope and POST to the GA4 Data API runReport endpoint.

Units: GA4 returns integer counts (sessions / users / event counts). No cents/dollars here.
"""

import os, json, time, base64, tempfile, threading
from datetime import datetime, timedelta, timezone

SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
TOKEN_URI = "https://oauth2.googleapis.com/token"
DATA_API = "https://analyticsdata.googleapis.com/v1beta"

# The on-site conversion events the site fires (GA4 key events — see tools/ga4_keyevents.py).
# form_submit = the COMPLETED Web3Forms catering lead (catering_inquiry is the intent/click).
KEY_EVENTS = ["order_click", "catering_inquiry", "form_submit", "call_tap", "get_directions"]

LOOKBACK_DAYS = 90
LAUNCH_DATE = "2026-06-28"             # site went live (DNS cutover) — "since launch" anchor
CACHE_TTL = 3600                       # GA4 data moves slowly; an hour is plenty fresh
# Cache is keyed by window so 7d/28d/90d/since-launch each persist independently.
CACHE_FILE = os.path.join(tempfile.gettempdir(), "wok_ga4_cache.json")

_lock = threading.Lock()
# payload cache is now per-window: {window_key: {payload, fetched_at}}
_cache = {"by_window": {}, "error": None}


def _window_start(window):
    """Resolve a window token to a startDate. Accepts 7/28/90 (days), 'launch'/'since_launch',
    or an explicit YYYY-MM-DD."""
    if not window or window in ("90", "90d", None):
        return (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    w = str(window).lower().rstrip("d")
    if w in ("launch", "since_launch", "since-launch"):
        return LAUNCH_DATE
    if w.isdigit():
        return (datetime.now(timezone.utc) - timedelta(days=int(w))).strftime("%Y-%m-%d")
    # explicit date
    try:
        datetime.strptime(window, "%Y-%m-%d")
        return window
    except Exception:
        return (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")


# ════════════════════════════════════════════ CREDS ════════════════════════════════════════════

def _sa_info():
    """Service-account key dict from env (GA4_SA_JSON, base64 OR raw JSON) → local file fallback.
    Returns None when no key is available (caller degrades to the 'connect GA4' placeholder)."""
    raw = os.environ.get("GA4_SA_JSON")
    if raw:
        raw = raw.strip()
        # accept either raw JSON or base64-of-JSON
        if not raw.startswith("{"):
            try:
                raw = base64.b64decode(raw).decode("utf-8")
            except Exception:
                pass
        try:
            return json.loads(raw)
        except Exception:
            return None
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, "..", "credentials", "ga4-reader-sa.json"),
              os.path.join(here, "credentials", "ga4-reader-sa.json")):
        if os.path.exists(p):
            try:
                return json.load(open(p))
            except Exception:
                return None
    return None


def _property_id():
    return os.environ.get("GA4_PROPERTY_ID", "455917909")


def available():
    """True when a property id and a usable SA key are present (does not prove API reachability)."""
    return bool(_property_id()) and _sa_info() is not None


# ════════════════════════════════════════════ TOKEN ════════════════════════════════════════════

def _token_via_google_auth(info):
    from google.oauth2 import service_account
    import google.auth.transport.requests as gar
    creds = service_account.Credentials.from_service_account_info(info, scopes=[SCOPE])
    creds.refresh(gar.Request())
    return creds.token


def _b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=")


def _token_via_stdlib(info):
    """Pure-stdlib SA JWT → OAuth2 access token (RS256). Used when google-auth isn't installed.
    Requires `cryptography` for RSA signing; if absent, raises (caller falls back to google-auth
    or reports unavailable)."""
    import urllib.request, urllib.parse
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claim = {
        "iss": info["client_email"], "scope": SCOPE, "aud": TOKEN_URI,
        "iat": now, "exp": now + 3600,
    }
    signing_input = _b64url(json.dumps(header).encode()) + b"." + _b64url(json.dumps(claim).encode())
    key = serialization.load_pem_private_key(info["private_key"].encode(), password=None)
    sig = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    assertion = (signing_input + b"." + _b64url(sig)).decode()

    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion,
    }).encode()
    req = urllib.request.Request(TOKEN_URI, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())["access_token"]


def _access_token(info):
    """Get an access token, preferring google-auth, falling back to the stdlib JWT signer."""
    try:
        return _token_via_google_auth(info)
    except ImportError:
        return _token_via_stdlib(info)


# ════════════════════════════════════════════ FETCH ════════════════════════════════════════════

def _run_report(token, body):
    import urllib.request
    url = f"{DATA_API}/properties/{_property_id()}:runReport"
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def _row_date(r, i=0):
    d = r["dimensionValues"][i]["value"]                # "YYYYMMDD"
    return f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0


def _rows(rep):
    return rep.get("rows", []) or []


def _pull(info, window=None):
    """Issue the full Site-Performance report set for the given window. R1/R2 stay (widened);
    R3–R10 add channels, seo_trend, top_pages, devices, geo, landing, new-vs-returning, and the
    window-quality summary. Each report → its own payload key. Raises on transport/API errors so
    the caller can degrade. Reuses ONE token for all reports."""
    token = _access_token(info)
    start = _window_start(window)
    date_range = [{"startDate": start, "endDate": "today"}]

    # R1 — traffic by day (+ newUsers, activeUsers)
    traffic = _run_report(token, {
        "dateRanges": date_range,
        "dimensions": [{"name": "date"}],
        "metrics": [{"name": "sessions"}, {"name": "totalUsers"},
                    {"name": "newUsers"}, {"name": "activeUsers"}],
        "orderBys": [{"dimension": {"dimensionName": "date"}}],
        "limit": 100000,
    })

    # R2 — key-event counts by day (+ form_submit in KEY_EVENTS, + eventCountPerUser)
    events = _run_report(token, {
        "dateRanges": date_range,
        "dimensions": [{"name": "date"}, {"name": "eventName"}],
        "metrics": [{"name": "eventCount"}, {"name": "eventCountPerUser"}],
        "dimensionFilter": {"filter": {"fieldName": "eventName",
                                       "inListFilter": {"values": KEY_EVENTS}}},
        "orderBys": [{"dimension": {"dimensionName": "date"}}],
        "limit": 100000,
    })

    # ── R1/R2 → daily series keyed by date ──
    by_date = {}
    for r in _rows(traffic):
        d = _row_date(r); mv = r["metricValues"]
        by_date.setdefault(d, {"date": d, "sessions": 0, "totalUsers": 0, "newUsers": 0,
                               "activeUsers": 0, **{e: 0 for e in KEY_EVENTS}})
        by_date[d].update(sessions=int(_num(mv[0]["value"])), totalUsers=int(_num(mv[1]["value"])),
                          newUsers=int(_num(mv[2]["value"])), activeUsers=int(_num(mv[3]["value"])))
    for r in _rows(events):
        d = _row_date(r); ev = r["dimensionValues"][1]["value"]
        cnt = int(_num(r["metricValues"][0]["value"]))
        row = by_date.setdefault(d, {"date": d, "sessions": 0, "totalUsers": 0, "newUsers": 0,
                                     "activeUsers": 0, **{e: 0 for e in KEY_EVENTS}})
        if ev in KEY_EVENTS:
            row[ev] = row.get(ev, 0) + cnt
    series = [by_date[d] for d in sorted(by_date)]

    summary = {"sessions": 0, "totalUsers": 0, "newUsers": 0, "activeUsers": 0, **{e: 0 for e in KEY_EVENTS}}
    for row in series:
        for k in summary:
            summary[k] += row.get(k, 0)
    sessions = summary["sessions"] or 0
    # conversion rate (event ÷ sessions × 100) for EVERY action
    for e in KEY_EVENTS:
        summary[f"{e}_rate"] = round(summary[e] / sessions * 100, 2) if sessions else None

    # ── helper to safely issue an optional report (a single bad dim shouldn't sink the whole pull) ──
    def _try(body):
        try:
            return _run_report(token, body)
        except Exception:
            return {"rows": []}

    # R4 — channels / sources
    r4 = _try({"dateRanges": date_range,
               "dimensions": [{"name": "sessionDefaultChannelGroup"}, {"name": "sessionSource"}],
               "metrics": [{"name": "sessions"}, {"name": "totalUsers"},
                           {"name": "engagedSessions"}, {"name": "keyEvents"}],
               "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 25})
    channels = []
    for r in _rows(r4):
        mv = r["metricValues"]
        channels.append({"channel": r["dimensionValues"][0]["value"],
                         "source": r["dimensionValues"][1]["value"],
                         "sessions": int(_num(mv[0]["value"])), "users": int(_num(mv[1]["value"])),
                         "engagedSessions": int(_num(mv[2]["value"])), "keyEvents": int(_num(mv[3]["value"]))})

    # R5 — SEO since launch (organic channel per day)
    r5 = _try({"dateRanges": date_range,
               "dimensions": [{"name": "date"}, {"name": "sessionDefaultChannelGroup"}],
               "metrics": [{"name": "sessions"}],
               "orderBys": [{"dimension": {"dimensionName": "date"}}], "limit": 100000})
    seo_trend = []
    for r in _rows(r5):
        seo_trend.append({"date": _row_date(r), "channel": r["dimensionValues"][1]["value"],
                          "sessions": int(_num(r["metricValues"][0]["value"]))})

    # R6 — top pages
    r6 = _try({"dateRanges": date_range,
               "dimensions": [{"name": "pagePath"}, {"name": "pageTitle"}],
               "metrics": [{"name": "screenPageViews"}, {"name": "sessions"}, {"name": "engagedSessions"},
                           {"name": "userEngagementDuration"}, {"name": "averageSessionDuration"},
                           {"name": "bounceRate"}, {"name": "keyEvents"}],
               "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}], "limit": 50})
    top_pages = []
    for r in _rows(r6):
        mv = r["metricValues"]
        top_pages.append({"path": r["dimensionValues"][0]["value"], "title": r["dimensionValues"][1]["value"],
                          "views": int(_num(mv[0]["value"])), "sessions": int(_num(mv[1]["value"])),
                          "engagedSessions": int(_num(mv[2]["value"])),
                          "userEngagementDuration": round(_num(mv[3]["value"])),
                          "avgSessionDuration": round(_num(mv[4]["value"]), 1),
                          "bounceRate": round(_num(mv[5]["value"]) * 100, 1),
                          "keyEvents": int(_num(mv[6]["value"]))})

    # R7 — devices by day
    r7 = _try({"dateRanges": date_range,
               "dimensions": [{"name": "date"}, {"name": "deviceCategory"}],
               "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "averageSessionDuration"}],
               "orderBys": [{"dimension": {"dimensionName": "date"}}], "limit": 100000})
    devices = []
    for r in _rows(r7):
        mv = r["metricValues"]
        devices.append({"date": _row_date(r), "device": r["dimensionValues"][1]["value"],
                        "sessions": int(_num(mv[0]["value"])), "engagedSessions": int(_num(mv[1]["value"])),
                        "avgSessionDuration": round(_num(mv[2]["value"]), 1)})

    # R8 — geo (US region/city)
    r8 = _try({"dateRanges": date_range,
               "dimensions": [{"name": "region"}, {"name": "city"}],
               "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "keyEvents"}],
               "dimensionFilter": {"filter": {"fieldName": "country",
                                              "stringFilter": {"value": "United States"}}},
               "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 25})
    geo = []
    for r in _rows(r8):
        mv = r["metricValues"]
        geo.append({"region": r["dimensionValues"][0]["value"], "city": r["dimensionValues"][1]["value"],
                    "sessions": int(_num(mv[0]["value"])), "engagedSessions": int(_num(mv[1]["value"])),
                    "keyEvents": int(_num(mv[2]["value"]))})

    # R9 — landing pages
    r9 = _try({"dateRanges": date_range,
               "dimensions": [{"name": "landingPage"}],
               "metrics": [{"name": "sessions"}, {"name": "engagedSessions"},
                           {"name": "engagementRate"}, {"name": "keyEvents"}],
               "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 25})
    landing = []
    for r in _rows(r9):
        mv = r["metricValues"]
        landing.append({"landingPage": r["dimensionValues"][0]["value"],
                        "sessions": int(_num(mv[0]["value"])), "engagedSessions": int(_num(mv[1]["value"])),
                        "engagementRate": round(_num(mv[2]["value"]) * 100, 1),
                        "keyEvents": int(_num(mv[3]["value"]))})

    # R3 — new vs returning by day
    r3 = _try({"dateRanges": date_range,
               "dimensions": [{"name": "date"}, {"name": "newVsReturning"}],
               "metrics": [{"name": "sessions"}, {"name": "activeUsers"}],
               "orderBys": [{"dimension": {"dimensionName": "date"}}], "limit": 100000})
    nvr = []
    for r in _rows(r3):
        mv = r["metricValues"]
        nvr.append({"date": _row_date(r), "type": r["dimensionValues"][1]["value"] or "(unknown)",
                    "sessions": int(_num(mv[0]["value"])), "activeUsers": int(_num(mv[1]["value"]))})

    # R10 — window quality totals (single-row, no dims)
    r10 = _try({"dateRanges": date_range,
                "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "engagementRate"},
                            {"name": "averageSessionDuration"}, {"name": "userEngagementDuration"},
                            {"name": "bounceRate"}, {"name": "screenPageViewsPerSession"},
                            {"name": "keyEvents"}, {"name": "totalUsers"}, {"name": "newUsers"}]})
    quality = {}
    qrows = _rows(r10)
    if qrows:
        mv = qrows[0]["metricValues"]
        quality = {"sessions": int(_num(mv[0]["value"])), "engagedSessions": int(_num(mv[1]["value"])),
                   "engagementRate": round(_num(mv[2]["value"]) * 100, 1),
                   "avgSessionDuration": round(_num(mv[3]["value"]), 1),
                   "userEngagementDuration": round(_num(mv[4]["value"])),
                   "bounceRate": round(_num(mv[5]["value"]) * 100, 1),
                   "pagesPerSession": round(_num(mv[6]["value"]), 2),
                   "keyEvents": int(_num(mv[7]["value"])), "totalUsers": int(_num(mv[8]["value"])),
                   "newUsers": int(_num(mv[9]["value"]))}

    return {
        "available": True,
        "property_id": _property_id(),
        "window": str(window) if window else "90d",
        "lookback_days": LOOKBACK_DAYS,
        "launch_date": LAUNCH_DATE,
        "start_date": start,
        "key_events": KEY_EVENTS,
        "series": series,                  # per-day sessions/users(+new/active) + event counts
        "summary": summary,                # window totals + per-event rates
        "channels": channels,              # R4
        "seo_trend": seo_trend,            # R5
        "top_pages": top_pages,            # R6
        "devices": devices,                # R7
        "geo": geo,                        # R8
        "landing": landing,                # R9
        "nvr": nvr,                        # R3
        "quality": quality,                # R10
        "row_count": len(series),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "basis": f"GA4 Data API · property {_property_id()} · since {start} · "
                 "traffic + channels + pages + device/geo/landing + actions",
    }


# ════════════════════════════════════════════ CACHE ════════════════════════════════════════════

def _norm_window(window):
    return str(window).lower() if window else "90d"


def _restore_all():
    if os.path.exists(CACHE_FILE):
        try:
            return json.load(open(CACHE_FILE)).get("by_window", {})
        except Exception:
            return {}
    return {}


def _persist():
    try:
        json.dump({"by_window": _cache["by_window"]}, open(CACHE_FILE, "w"))
    except Exception:
        pass  # best-effort; never fatal


def get(force=False, window=None):
    """Return the GA4 payload for `window` (cached per-window, TTL-refreshed). Graceful empty when
    unavailable. window ∈ {7,28,90,'launch', YYYY-MM-DD} (default 90d).

    Shapes:
      • {available: True, series, summary, channels, top_pages, ...}  — live data present
      • {available: False, reason: "...", connect: True}              — degrade to the placeholder
    Never raises: any error becomes an {available: False, reason} so /api/data stays up."""
    info = _sa_info()
    if info is None:
        return {"available": False, "connect": True,
                "reason": "no GA4 service-account key (set GA4_SA_JSON on the Space)"}

    wkey = _norm_window(window)
    now = time.time()
    with _lock:
        bw = _cache["by_window"]
        ent = bw.get(wkey)
        if not force and ent and (now - ent.get("fetched_at", 0)) < CACHE_TTL:
            return ent["payload"]
        # cold start: hydrate from the persisted file if memory is empty
        if not bw:
            _cache["by_window"] = _restore_all()
            ent = _cache["by_window"].get(wkey)
            if ent and not force and (now - ent.get("fetched_at", 0)) < CACHE_TTL:
                return ent["payload"]

    try:
        payload = _pull(info, window=window)
        with _lock:
            _cache["by_window"][wkey] = {"payload": payload, "fetched_at": time.time()}
            _cache["error"] = None
        _persist()
        return payload
    except Exception as e:
        msg = str(e)
        # Enabled-API hint: a 403 SERVICE_DISABLED means the Data API isn't on for the project.
        hint = ""
        if "403" in msg or "SERVICE_DISABLED" in msg or "has not been used" in msg:
            hint = " — owner: enable the Google Analytics Data API on project ga4-reader-500818"
        elif "permission" in msg.lower() or "PERMISSION_DENIED" in msg:
            hint = " — owner: add the SA as a Viewer on GA4 property " + _property_id()
        with _lock:
            _cache["error"] = msg
            ent = _cache["by_window"].get(wkey)
            stale = ent["payload"] if ent else None
        if stale:                          # serve last-known-good rather than nothing
            out = dict(stale)
            out["stale"] = True
            out["last_error"] = msg + hint
            return out
        return {"available": False, "connect": True, "reason": msg + hint}


def summary(window=None):
    """Just the window summary (or None) — for folding into /api/data without the full series."""
    p = get(window=window)
    return p.get("summary") if p.get("available") else None


# ════════════════════════════════════════════ CLI (local test) ════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    print(f"property = {_property_id()} | key available = {available()}", file=sys.stderr)
    p = get(force=True)
    if not p.get("available"):
        print(f"GA4 UNAVAILABLE: {p.get('reason')}", file=sys.stderr)
        sys.exit(1)
    s = p["summary"]
    print(f"window {p['start_date']} → today  ({p['row_count']} days)")
    print(f"  sessions      {s['sessions']:,}   newUsers {s.get('newUsers',0):,}  activeUsers {s.get('activeUsers',0):,}")
    print(f"  totalUsers    {s['totalUsers']:,}")
    for e in KEY_EVENTS:
        print(f"  {e:18s}{s[e]:,}   ({s.get(e+'_rate')}% of sessions)")
    print(f"  channels {len(p.get('channels',[]))} · top_pages {len(p.get('top_pages',[]))} · "
          f"geo {len(p.get('geo',[]))} · landing {len(p.get('landing',[]))}")
    print(f"  quality: {p.get('quality')}")
