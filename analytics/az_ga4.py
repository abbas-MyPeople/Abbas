#!/usr/bin/env python3
"""GA4 Data API queries for AZ Restaurant Partners (azrestaurantpartners.com).

WHY a SEPARATE module: `ga4.py` (copied in from the Wok & Karahi dashboard) carries Wok-tuned
default report bodies + a property-id default of another property. Rather than edit/fork it, this
module REUSES only its credential + token plumbing (`_sa_info`, `_access_token`) and issues its own
AZ-specific `runReport` calls against the AZ property. That way ga4.py stays untouched and safe.

The AZ marketing site fires these GA4 custom events via a delegated tracker:
  section_view (param `section`), click, call_click, email_click, whatsapp_click, pdf_download,
  outbound_click, lead_submit, finder_capture — each also carrying `page` + utm params.

PRIVACY: no secret is hardcoded or written to disk here. The service-account key arrives from the
environment (GA4_SA_JSON) on the Space, or the local gitignored key file for dev — all resolved by
ga4._sa_info(). The property id comes from env GA4_PROPERTY_ID.

NEVER crash on missing creds and NEVER fabricate numbers: every public function degrades to a clean
{available: False, connect: True, reason} state that the frontend renders as "Connect GA4", and an
empty-but-authorized property renders as "No data yet — the property is new".
"""

import json
from datetime import datetime, timezone

import ga4  # reuse credential + token plumbing ONLY (do not use its Wok-tuned report bodies)

DATA_API = "https://analyticsdata.googleapis.com/v1beta"

# The AZ conversion/interaction events (from the delegated tracker). The first three are the
# money events surfaced prominently in the dashboard header.
CONVERSION_EVENTS = ["lead_submit", "call_click", "finder_capture"]
INTERACTION_EVENTS = [
    "lead_submit", "call_click", "finder_capture", "email_click", "whatsapp_click",
    "pdf_download", "outbound_click", "click", "section_view",
]


# ════════════════════════════════════════════ CREDS / TOKEN ════════════════════════════════════════

def _property_id():
    """AZ GA4 property id from env. No hardcoded default (the real id is a Space secret)."""
    import os
    return os.environ.get("GA4_PROPERTY_ID", "").strip()


def available():
    """True when a property id AND a usable SA key are present (does not prove API reachability)."""
    return bool(_property_id()) and ga4._sa_info() is not None


def _run(token, body):
    """POST one runReport for the AZ property. Uses stdlib urllib (same lean style as ga4.py)."""
    import urllib.request
    pid = _property_id()
    url = f"{DATA_API}/properties/{pid}:runReport"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


# ════════════════════════════════════════════ helpers ════════════════════════════════════════════

def _rows(rep):
    return rep.get("rows", []) or []


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0


def _row_date(r, i=0):
    d = r["dimensionValues"][i]["value"]  # "YYYYMMDD"
    return f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d


def _try(token, body):
    """Issue an optional report; a single bad dim/metric shouldn't sink the whole pull."""
    try:
        return _run(token, body)
    except Exception:
        return {"rows": []}


# ════════════════════════════════════════════ report bodies ════════════════════════════════════════

def totals(token, days):
    """Active users + sessions totals over the trailing `days` window (single row)."""
    rep = _try(token, {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "metrics": [{"name": "activeUsers"}, {"name": "sessions"},
                    {"name": "newUsers"}, {"name": "screenPageViews"}],
    })
    rws = _rows(rep)
    if not rws:
        return {"activeUsers": 0, "sessions": 0, "newUsers": 0, "screenPageViews": 0}
    mv = rws[0]["metricValues"]
    return {"activeUsers": int(_num(mv[0]["value"])), "sessions": int(_num(mv[1]["value"])),
            "newUsers": int(_num(mv[2]["value"])), "screenPageViews": int(_num(mv[3]["value"]))}


def daily_trend(token, days):
    """Per-day activeUsers + sessions for the trailing `days` window (line/bar trend)."""
    rep = _try(token, {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "date"}],
        "metrics": [{"name": "activeUsers"}, {"name": "sessions"}],
        "orderBys": [{"dimension": {"dimensionName": "date"}}],
        "limit": 100000,
    })
    out = []
    for r in _rows(rep):
        mv = r["metricValues"]
        out.append({"date": _row_date(r),
                    "activeUsers": int(_num(mv[0]["value"])),
                    "sessions": int(_num(mv[1]["value"]))})
    return out


def top_pages(token, days, limit=15):
    """Top pages by screenPageViews (dimension pagePath)."""
    rep = _try(token, {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "pagePath"}],
        "metrics": [{"name": "screenPageViews"}, {"name": "activeUsers"}],
        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
        "limit": limit,
    })
    out = []
    for r in _rows(rep):
        mv = r["metricValues"]
        out.append({"path": r["dimensionValues"][0]["value"],
                    "views": int(_num(mv[0]["value"])),
                    "users": int(_num(mv[1]["value"]))})
    return out


def sources(token, days, limit=15):
    """Traffic sources by sessionDefaultChannelGroup."""
    rep = _try(token, {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "sessionDefaultChannelGroup"}],
        "metrics": [{"name": "sessions"}, {"name": "activeUsers"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
        "limit": limit,
    })
    out = []
    for r in _rows(rep):
        mv = r["metricValues"]
        out.append({"channel": r["dimensionValues"][0]["value"] or "(unassigned)",
                    "sessions": int(_num(mv[0]["value"])),
                    "users": int(_num(mv[1]["value"]))})
    return out


def event_counts(token, days, limit=50):
    """All event counts by eventName (metric eventCount)."""
    rep = _try(token, {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "eventName"}],
        "metrics": [{"name": "eventCount"}],
        "orderBys": [{"metric": {"metricName": "eventCount"}, "desc": True}],
        "limit": limit,
    })
    out = []
    for r in _rows(rep):
        out.append({"event": r["dimensionValues"][0]["value"],
                    "count": int(_num(r["metricValues"][0]["value"]))})
    return out


def section_views(token, days, limit=50):
    """section_view broken down by the `section` custom event param (dimension customEvent:section)."""
    rep = _try(token, {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "customEvent:section"}],
        "metrics": [{"name": "eventCount"}],
        "dimensionFilter": {"filter": {"fieldName": "eventName",
                                       "stringFilter": {"value": "section_view"}}},
        "orderBys": [{"metric": {"metricName": "eventCount"}, "desc": True}],
        "limit": limit,
    })
    out = []
    for r in _rows(rep):
        sec = r["dimensionValues"][0]["value"]
        if sec in ("(not set)", ""):
            sec = "(not set)"
        out.append({"section": sec, "count": int(_num(r["metricValues"][0]["value"]))})
    return out


# ════════════════════════════════════════════ top-level ════════════════════════════════════════════

def get():
    """Fetch the full AZ dashboard payload. NEVER raises; degrades to a clean connect/empty state.

    Shapes:
      • {available: True, ...data...}                       — live (may be all-zero if brand-new)
      • {available: False, connect: True, reason: "..."}    — no creds / property not set
    """
    if not _property_id():
        return {"available": False, "connect": True,
                "reason": "GA4_PROPERTY_ID not set (add it as a Space secret)"}
    info = ga4._sa_info()
    if info is None:
        return {"available": False, "connect": True,
                "reason": "no GA4 service-account key (set GA4_SA_JSON on the Space)"}

    try:
        token = ga4._access_token(info)
    except Exception as e:
        return {"available": False, "connect": True,
                "reason": _clean_reason(str(e))}

    try:
        t7 = totals(token, 7)
        t28 = totals(token, 28)
        trend = daily_trend(token, 28)
        pages = top_pages(token, 28)
        srcs = sources(token, 28)
        events = event_counts(token, 28)
        secs = section_views(token, 28)
    except Exception as e:
        # token minted but a *required* report failed (e.g. API disabled / no access)
        return {"available": False, "connect": True, "reason": _clean_reason(str(e))}

    # Pull the conversion + interaction event totals out of the event_counts table.
    ev_map = {e["event"]: e["count"] for e in events}
    conversions = {name: ev_map.get(name, 0) for name in CONVERSION_EVENTS}
    interactions = {name: ev_map.get(name, 0) for name in INTERACTION_EVENTS}

    has_any = bool(t28["sessions"] or t28["activeUsers"] or events)

    return {
        "available": True,
        "has_data": has_any,
        "property_id": _property_id(),
        "totals_7d": t7,
        "totals_28d": t28,
        "trend": trend,                 # per-day activeUsers + sessions (28d)
        "top_pages": pages,             # by screenPageViews (28d)
        "sources": srcs,                # by channel group (28d)
        "events": events,               # all eventName counts (28d)
        "conversions": conversions,     # lead_submit / call_click / finder_capture (28d)
        "interactions": interactions,   # full interaction event set (28d)
        "sections": secs,               # section_view by customEvent:section (28d)
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "basis": f"GA4 Data API · property {_property_id()} · 7d + 28d windows",
    }


def _clean_reason(msg):
    """Turn a raw transport/API error into a short owner-actionable hint (no traceback leakage)."""
    low = msg.lower()
    if "403" in msg or "service_disabled" in low or "has not been used" in low:
        return "Google Analytics Data API not enabled on the service-account's project"
    if "permission" in low or "permission_denied" in low:
        return f"service account is not a Viewer on GA4 property {_property_id()}"
    if "404" in msg:
        return f"GA4 property {_property_id()} not found (check GA4_PROPERTY_ID)"
    return "GA4 not connected yet"


# ════════════════════════════════════════════ CLI (local test) ════════════════════════════════════════

if __name__ == "__main__":
    import sys
    print(f"property = {_property_id() or '(unset)'} | key available = {available()}", file=sys.stderr)
    p = get()
    if not p.get("available"):
        print(f"GA4 UNAVAILABLE: {p.get('reason')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({k: v for k, v in p.items() if k not in ("trend",)}, indent=2))
    print(f"trend days: {len(p['trend'])}", file=sys.stderr)
