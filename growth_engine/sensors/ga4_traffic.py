"""
growth_engine.sensors.ga4_traffic — the AZ MEASURE (replaces the restaurant's Clover momentum sensor).

Reads GA4 for azrestaurantpartners.com and emits DETERMINISTIC findings (NO LLM here):
  • traffic momentum   — sessions / users this window vs the prior equal window (up / down / flat)
  • page performance    — top pages, and "traffic-but-no-lead" underperformers
  • conversion trend    — lead_submit / call_click / finder_capture vs the prior window
  • funnel drop-off      — section_view counts that fall off a cliff deeper in the page
  • dead CTA             — a section seen a lot whose click event barely fires

It reuses the existing GA4 client at ../analytics/ga4.py (its SA-key + token + runReport plumbing) but
issues AZ-specific report bodies so it can read AZ's own events. Credential-guarded: no GA4 key / no
property → it emits an "unavailable" signal and cleanly no-ops (never blocks the run, never fabricates).
Read-only: GA4 Data API runReport GETs only.
"""
from __future__ import annotations
import os, sys, datetime
from pathlib import Path
from .. import model

# ../analytics relative to growth_engine (repo-root sibling); AZ_ANALYTICS_DIR overrides (tests/CI).
_ANALYTICS = Path(os.environ.get("AZ_ANALYTICS_DIR")
                  or Path(__file__).resolve().parent.parent.parent / "analytics")

# AZ on-site conversion events (the site's GA4 key events). Order = funnel intent → completion.
KEY_EVENTS = ["finder_capture", "call_click", "lead_submit"]
WINDOW_DAYS = 7                    # "this window" vs the immediately-prior equal window
UNDERPERF_MIN_VIEWS = 40          # a page must have real traffic before "no leads" is meaningful
DEAD_CTA_MIN_VIEWS = 60           # a section must be seen enough before "dead CTA" is meaningful
DEAD_CTA_MAX_RATIO = 0.02         # clicks/views below this on a well-seen section = dead CTA
DROPOFF_RATIO = 0.25              # a deep section under 25% of the top section's views = cliff


def _ga4():
    """Import the shared GA4 client (ga4.py) — it exposes the _sa_info/_access_token/_run_report
    primitives this sensor calls (az_ga4.py has a different high-level API). None if no key/dep."""
    try:
        if str(_ANALYTICS) not in sys.path:
            sys.path.insert(0, str(_ANALYTICS))
        import ga4 as g          # shared client: reads GA4_PROPERTY_ID + GA4_SA_JSON from env
        if g._sa_info() is None:            # no service-account key present
            return None
        return g
    except Exception:                        # never let a missing dep break the run
        return None


def _windows():
    today = datetime.date.today()
    cur_start = today - datetime.timedelta(days=WINDOW_DAYS - 1)
    prev_end = cur_start - datetime.timedelta(days=1)
    prev_start = prev_end - datetime.timedelta(days=WINDOW_DAYS - 1)
    return (cur_start.isoformat(), today.isoformat(),
            prev_start.isoformat(), prev_end.isoformat())


def _num(mv, i=0):
    try:
        return float(mv[i]["value"])
    except (TypeError, ValueError, IndexError, KeyError):
        return 0.0


def _delta_pct(cur, prev):
    if prev <= 0:
        return None
    return round((cur - prev) / prev * 100, 1)


def _page_file(path: str) -> str:
    """Map a GA4 pagePath to a repo page file (for a proposal's target)."""
    p = (path or "/").split("?")[0].split("#")[0]
    if p in ("", "/"):
        return "index.html"
    p = p.lstrip("/")
    if p.endswith("/"):
        return p + "index.html"
    if not p.endswith(".html"):
        return p + ".html"
    return p


# ── report helpers (each wrapped so one bad report never sinks the run) ──

def _traffic(g, token, start, end):
    try:
        rep = g._run_report(token, {
            "dateRanges": [{"startDate": start, "endDate": end}],
            "metrics": [{"name": "sessions"}, {"name": "totalUsers"},
                        {"name": "newUsers"}, {"name": "activeUsers"}],
        })
        rows = rep.get("rows") or []
        if not rows:
            return {"sessions": 0, "totalUsers": 0, "newUsers": 0, "activeUsers": 0}
        mv = rows[0]["metricValues"]
        return {"sessions": int(_num(mv, 0)), "totalUsers": int(_num(mv, 1)),
                "newUsers": int(_num(mv, 2)), "activeUsers": int(_num(mv, 3))}
    except Exception:
        return {"sessions": 0, "totalUsers": 0, "newUsers": 0, "activeUsers": 0}


def _events(g, token, start, end):
    out = {e: 0 for e in KEY_EVENTS}
    try:
        rep = g._run_report(token, {
            "dateRanges": [{"startDate": start, "endDate": end}],
            "dimensions": [{"name": "eventName"}],
            "metrics": [{"name": "eventCount"}],
            "dimensionFilter": {"filter": {"fieldName": "eventName",
                                           "inListFilter": {"values": KEY_EVENTS}}},
        })
        for r in rep.get("rows") or []:
            name = r["dimensionValues"][0]["value"]
            if name in out:
                out[name] = int(_num(r["metricValues"], 0))
    except Exception:
        pass
    return out


def _pages(g, token, start, end):
    try:
        rep = g._run_report(token, {
            "dateRanges": [{"startDate": start, "endDate": end}],
            "dimensions": [{"name": "pagePath"}],
            "metrics": [{"name": "screenPageViews"}, {"name": "engagementRate"},
                        {"name": "keyEvents"}],
            "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
            "limit": 40,
        })
        out = []
        for r in rep.get("rows") or []:
            mv = r["metricValues"]
            out.append({"path": r["dimensionValues"][0]["value"],
                        "views": int(_num(mv, 0)),
                        "engagementRate": round(_num(mv, 1) * 100, 1),
                        "keyEvents": int(_num(mv, 2))})
        return out
    except Exception:
        return []


def _sections(g, token, start, end):
    """section_view + section-CTA clicks, grouped by a section label param. Best-effort: if the AZ
    site doesn't emit a labelled section_view custom dimension, this returns [] and the funnel/dead-CTA
    rules simply don't fire (no fabrication)."""
    try:
        rep = g._run_report(token, {
            "dateRanges": [{"startDate": start, "endDate": end}],
            "dimensions": [{"name": "eventName"}, {"name": "customEvent:section"}],
            "metrics": [{"name": "eventCount"}],
            "dimensionFilter": {"filter": {"fieldName": "eventName",
                                           "inListFilter": {"values": ["section_view", "cta_click"]}}},
            "limit": 200,
        })
        views, clicks, order = {}, {}, []
        for r in rep.get("rows") or []:
            ev = r["dimensionValues"][0]["value"]
            label = r["dimensionValues"][1]["value"]
            n = int(_num(r["metricValues"], 0))
            if not label or label == "(not set)":
                continue
            if ev == "section_view":
                if label not in views:
                    order.append(label)
                views[label] = views.get(label, 0) + n
            elif ev == "cta_click":
                clicks[label] = clicks.get(label, 0) + n
        return [{"label": s, "views": views[s], "clicks": clicks.get(s, 0)} for s in order]
    except Exception:
        return []


def sense(verbose: bool = True) -> dict:
    g = _ga4()
    if g is None:
        model.signal("ga4", "traffic_available", "site", 0, unit="bool", period="point")
        if verbose:
            print("ga4_traffic: GA4 not configured (no GA4_SA_JSON / property) — skipping "
                  "(activates in the Action once the SA key is present).")
        return {"available": False}

    try:
        info = g._sa_info()
        token = g._access_token(info)
    except Exception as e:
        model.signal("ga4", "traffic_available", "site", 0, unit="bool", period="point")
        if verbose:
            print(f"ga4_traffic: auth failed ({type(e).__name__}) — skipping.")
        return {"available": False}

    cs, ce, ps, pe = _windows()
    cur_t = _traffic(g, token, cs, ce)
    prev_t = _traffic(g, token, ps, pe)
    cur_e = _events(g, token, cs, ce)
    prev_e = _events(g, token, ps, pe)
    pages = _pages(g, token, cs, ce)
    sections = _sections(g, token, cs, ce)

    has_data = (cur_t["sessions"] or prev_t["sessions"] or pages)
    model.signal("ga4", "traffic_available", "site", 1 if has_data else 0,
                 unit="bool", period="point", meta={"window_days": WINDOW_DAYS})
    if not has_data:
        if verbose:
            print("ga4_traffic: GA4 reachable but no rows yet (new property) — brief will say 'no data'.")
        return {"available": True, "empty": True}

    # ── 1. traffic momentum ──────────────────────────────────────────────
    s_delta = _delta_pct(cur_t["sessions"], prev_t["sessions"])
    u_delta = _delta_pct(cur_t["totalUsers"], prev_t["totalUsers"])
    model.signal("ga4", "sessions_delta_pct", "site", s_delta, unit="pct", period=f"{WINDOW_DAYS}d",
                 meta={"cur": cur_t["sessions"], "prev": prev_t["sessions"]})
    model.signal("ga4", "users_delta_pct", "site", u_delta, unit="pct", period=f"{WINDOW_DAYS}d",
                 meta={"cur": cur_t["totalUsers"], "prev": prev_t["totalUsers"]})
    if s_delta is not None and s_delta <= -20:
        model.finding("G1_traffic", "site", "alert", "bad",
                      f"Traffic down {abs(s_delta):.0f}% week-over-week",
                      detail=(f"Sessions {prev_t['sessions']}→{cur_t['sessions']} "
                              f"({WINDOW_DAYS}d vs prior {WINDOW_DAYS}d). Worth a look before proposing changes."))
    else:
        # momentum is informational (→ ALSO rollup), never a proposal slot — proposals are actionable edits.
        arrow = "up" if (s_delta or 0) > 0 else ("down" if (s_delta or 0) < 0 else "flat")
        model.finding("G1_traffic", "site", "opportunity", "watch",
                      f"Traffic {arrow}: {cur_t['sessions']} sessions this {WINDOW_DAYS}d"
                      + (f" ({s_delta:+.0f}% WoW)" if s_delta is not None else ""),
                      detail=f"Users {prev_t['totalUsers']}→{cur_t['totalUsers']}, "
                             f"new {cur_t['newUsers']}. Baseline for this week's read.")

    # ── 2. page performance: top + "traffic but no lead" ─────────────────
    if pages:
        top3 = pages[:3]
        model.finding("G2_top_pages", "site", "opportunity", "watch",
                      "Top pages: " + ", ".join(f"{p['path']} ({p['views']})" for p in top3),
                      detail="Where attention actually landed this week.")
        for p in pages:
            if p["views"] >= UNDERPERF_MIN_VIEWS and p["keyEvents"] == 0:
                pf = _page_file(p["path"])
                model.signal("ga4", "page_no_lead_views", p["path"], p["views"], unit="count",
                             period=f"{WINDOW_DAYS}d")
                model.finding("G3_underperf_page", f"page:{p['path']}", "opportunity", "good",
                              f"{p['path']} got {p['views']} views but 0 conversions — strengthen its CTA",
                              detail=(f"Real traffic ({p['views']} views, engagement {p['engagementRate']}%) "
                                      f"with no lead_submit/call_click/finder_capture. The page ({pf}) needs a "
                                      f"clearer, higher-contrast call-to-action or a lead capture above the fold."),
                              target={"page_file": pf, "section": "primary CTA"})
                break   # surface the single worst offender, not a wall of them

    # ── 3. conversion trend ──────────────────────────────────────────────
    cur_total = sum(cur_e.values()); prev_total = sum(prev_e.values())
    c_delta = _delta_pct(cur_total, prev_total)
    for e in KEY_EVENTS:
        model.signal("ga4", f"conv_{e}", "site", cur_e[e], unit="count", period=f"{WINDOW_DAYS}d",
                     meta={"prev": prev_e[e], "delta_pct": _delta_pct(cur_e[e], prev_e[e])})
    model.signal("ga4", "conv_total_delta_pct", "site", c_delta, unit="pct", period=f"{WINDOW_DAYS}d",
                 meta={"cur": cur_total, "prev": prev_total})
    if c_delta is not None and c_delta <= -25 and prev_total >= 3:
        model.finding("G4_conversion", "site", "alert", "bad",
                      f"Conversions down {abs(c_delta):.0f}% WoW ({prev_total}→{cur_total})",
                      detail="lead_submit + call_click + finder_capture combined dropped — check recent changes.")
    elif cur_t["sessions"] >= 50 and cur_total == 0:
        model.finding("G4_conversion", "site", "opportunity", "good",
                      f"{cur_t['sessions']} sessions but 0 conversions this week — add a primary lead CTA",
                      detail="Healthy traffic, nothing captured. Propose a prominent 'Book a call' / lead form "
                             "on the homepage hero.",
                      target={"page_file": "index.html", "section": "hero"})
    else:
        model.finding("G4_conversion", "site", "opportunity", "watch",
                      f"Conversions this week: {cur_total}"
                      + (f" ({c_delta:+.0f}% WoW)" if c_delta is not None else ""),
                      detail="; ".join(f"{e}={cur_e[e]}" for e in KEY_EVENTS))

    # ── 3b. LEAD RATE (leads per 100 visits) — THE objective: grow leads faster than traffic ─────
    # We don't just want more visits; we want a higher share of the RIGHT visitors converting.
    cur_rate = (cur_total / cur_t["sessions"] * 100) if cur_t["sessions"] else None
    prev_rate = (prev_total / prev_t["sessions"] * 100) if prev_t["sessions"] else None
    rate_delta = _delta_pct(cur_rate, prev_rate) if (cur_rate is not None and prev_rate is not None) else None
    if cur_rate is not None:
        model.signal("ga4", "lead_rate_per_100", "site", round(cur_rate, 2), unit="rate", period=f"{WINDOW_DAYS}d",
                     meta={"cur": round(cur_rate, 2), "prev": None if prev_rate is None else round(prev_rate, 2),
                           "delta_pct": rate_delta, "leads": cur_total, "sessions": cur_t["sessions"]})
    # Traffic climbing but the RATIO flat/down = more visits, not more of the right ones → fix targeting/clarity.
    if (s_delta is not None and s_delta >= 10 and cur_t["sessions"] >= 50
            and (rate_delta is None or rate_delta <= 0)):
        model.finding("G7_lead_rate", "site", "opportunity", "good",
                      f"Traffic up {s_delta:+.0f}% but the lead rate isn't"
                      + (f" ({cur_rate:.1f} leads/100 visits)" if cur_rate is not None else ""),
                      detail=("More visits aren't turning into more of the RIGHT visitors. Sharpen who the homepage "
                              "speaks to (an audience-fit headline + subhead), make the value obvious in the first "
                              "screen, and lead with one clear primary CTA — so a higher SHARE of traffic converts, "
                              "not just more traffic. Reply with the audience/angle to target and I'll draft it."),
                      target={"page_file": "index.html", "section": "hero"})

    # ── 4. funnel drop-off + 5. dead CTA (only if the site emits labelled sections) ──
    if len(sections) >= 2:
        top_views = max(s["views"] for s in sections)
        for i, s in enumerate(sections):
            if i >= 1 and top_views and s["views"] <= top_views * DROPOFF_RATIO:
                model.finding("G5_funnel_dropoff", f"section:{s['label']}", "opportunity", "good",
                              f"Section '{s['label']}' loses most visitors (only {s['views']} of {top_views} reach it)",
                              detail=("Steep drop-off deeper in the page. Propose moving this section higher or "
                                      "tightening the copy above it so more visitors reach the offer."),
                              target={"page_file": "index.html", "section": s["label"]})
                break
        for s in sections:
            ratio = (s["clicks"] / s["views"]) if s["views"] else 0
            if s["views"] >= DEAD_CTA_MIN_VIEWS and ratio < DEAD_CTA_MAX_RATIO:
                model.finding("G6_dead_cta", f"section:{s['label']}", "opportunity", "good",
                              f"Dead CTA in '{s['label']}': seen {s['views']}× but only {s['clicks']} clicks",
                              detail=("A well-seen section whose CTA barely converts. Propose rewording the button, "
                                      "raising its contrast, or moving it in-view."),
                              target={"page_file": "index.html", "section": s["label"]})
                break

    if verbose:
        print(f"ga4_traffic: sessions {prev_t['sessions']}→{cur_t['sessions']} "
              f"({'n/a' if s_delta is None else f'{s_delta:+.0f}%'}), conversions {prev_total}→{cur_total}, "
              f"{len(pages)} pages, {len(sections)} labelled sections.")
    return {"available": True, "sessions": cur_t["sessions"], "conversions": cur_total,
            "pages": len(pages), "sections": len(sections)}


if __name__ == "__main__":
    sense()
