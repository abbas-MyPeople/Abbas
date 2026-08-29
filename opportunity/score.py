#!/usr/bin/env python3
"""Deterministic opportunity scorer.

The ranking is the product. Section 8 of the funnel brief is explicit that the
LLM must not decide this from scratch - it scores structured evidence, and the
model is only allowed to explain the result afterwards. So the whole scorer
lives here as pure functions with no network and no model call, which also
means it can be tested.

Every sub-score returns a value in 0..1 alongside the reason it landed there,
because a rank the owner cannot interrogate is a rank he will not trust. A
missing signal scores 0 and says so - it never silently becomes an average.

    python3 opportunity/score.py --selftest
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timezone

# Section 8. These are a starting heuristic, not a scientific claim.
WEIGHTS = {
    "order_size": 0.25,
    "restaurant_fit": 0.20,
    "timing": 0.15,
    "distance": 0.15,
    "reachability": 0.15,
    "confidence": 0.10,
}

# Headcount / attendance -> 0..1. Deliberately coarse: the underlying evidence
# is rarely precise enough to justify a finer curve.
SIZE_BANDS = [(500, 1.0), (200, 0.85), (100, 0.7), (50, 0.55), (25, 0.4), (10, 0.25)]

# Organisation types that plausibly buy group food, and how strongly.
ORG_PRIORS = {
    "hospital": 0.8, "medical": 0.7, "clinic": 0.65, "dental": 0.5,
    "law_firm": 0.7, "corporate_office": 0.7, "corporate_campus": 0.85,
    "school": 0.65, "college": 0.7, "university": 0.75,
    "worship": 0.6, "hotel": 0.55, "venue": 0.65,
    "property_management": 0.5, "dealership": 0.5, "office": 0.45,
}


def _band(value, bands):
    for threshold, score in bands:
        if value >= threshold:
            return score
    return 0.15


def score_order_size(ev: dict) -> tuple[float, str]:
    """Attendance for an event, headcount for an organisation, else the type prior."""
    attendance = ev.get("attendance")
    if isinstance(attendance, (int, float)) and attendance > 0:
        return _band(attendance, SIZE_BANDS), f"{int(attendance)} attending (sourced)"

    headcount = ev.get("headcount")
    if isinstance(headcount, (int, float)) and headcount > 0:
        return _band(headcount, SIZE_BANDS), f"~{int(headcount)} staff (sourced)"

    org_type = ev.get("org_type")
    if org_type in ORG_PRIORS:
        # A type prior is weaker than a counted head, so cap it well below 1.
        return ORG_PRIORS[org_type] * 0.6, f"no size published; {org_type} type prior"

    return 0.0, "no size signal"


def score_restaurant_fit(ev: dict, restaurant: dict) -> tuple[float, str]:
    """Cuisine, dietary, format and occasion alignment. All evidence-gated."""
    score, reasons = 0.0, []

    if ev.get("group_format_supported") and restaurant.get("has_group_format"):
        score += 0.35
        reasons.append("restaurant offers group/tray formats")

    occasion = ev.get("occasion")
    if occasion in ("weekday_lunch", "all_day_event") and restaurant.get("open_lunch"):
        score += 0.25
        reasons.append(f"{occasion.replace('_', ' ')} matches opening hours")

    # Dietary only counts when the restaurant's positioning is publicly explicit
    # and the opportunity actually signals the need. Never inferred.
    diet = restaurant.get("dietary_positioning")
    if diet and diet in (ev.get("dietary_signals") or []):
        score += 0.25
        reasons.append(f"{diet} positioning matches a stated requirement")

    if ev.get("cuisine_affinity"):
        score += 0.15
        reasons.append("cuisine suits the occasion")

    return min(score, 1.0), "; ".join(reasons) or "no positive fit signal"


def score_timing(ev: dict, today: date | None = None) -> tuple[float, str]:
    """Sooner is worth more, but not yet passed and not so soon it is unwinnable."""
    today = today or datetime.now(timezone.utc).date()

    if ev.get("recurring"):
        return 0.6, "recurring prospect - no deadline, always actionable"

    event_date = ev.get("event_date")
    if not event_date:
        return 0.0, "no date"

    if isinstance(event_date, str):
        try:
            event_date = date.fromisoformat(event_date)
        except ValueError:
            return 0.0, "unparseable date"

    days = (event_date - today).days
    if days < 0:
        return 0.0, "already passed"
    if days <= 2:
        return 0.5, f"in {days}d - very short notice"
    if days <= 10:
        return 1.0, f"in {days}d - time-sensitive, still winnable"
    if days <= 21:
        return 0.8, f"in {days}d"
    if days <= 45:
        return 0.5, f"in {days}d"
    return 0.25, f"in {days}d - far out"


def score_distance(ev: dict, max_miles: float = 12.0) -> tuple[float, str]:
    """Linear decay to the delivery ceiling, then nothing."""
    miles = ev.get("distance_miles")
    if miles is None:
        return 0.0, "distance unknown"
    if miles > max_miles:
        return 0.0, f"{miles:.1f} mi - outside practical range"
    return round(1.0 - (miles / max_miles), 3), f"{miles:.1f} mi"


def score_reachability(ev: dict) -> tuple[float, str]:
    """Can the owner actually act on this in the next 30 minutes?"""
    routes = {
        "organizer_page": 0.35, "public_phone": 0.3, "contact_form": 0.2,
        "public_email": 0.25, "known_buyer_role": 0.2, "website": 0.1,
    }
    found = [r for r in routes if ev.get(r)]
    if not found:
        return 0.0, "no public contact route found"
    total = min(sum(routes[r] for r in found), 1.0)
    return total, "reachable via " + ", ".join(r.replace("_", " ") for r in found)


def score_confidence(ev: dict, today: date | None = None) -> tuple[float, str]:
    """Freshness and source quality. Inferred size is worth less than a counted one."""
    today = today or datetime.now(timezone.utc).date()
    sources = ev.get("sources") or []
    if not sources:
        return 0.0, "no sources"

    score = min(0.4 + 0.2 * len(sources), 0.8)
    detail = [f"{len(sources)} source{'s' if len(sources) > 1 else ''}"]

    if ev.get("size_is_explicit"):
        score += 0.2
        detail.append("size explicitly stated")
    else:
        detail.append("size inferred")

    retrieved = ev.get("retrieved_at")
    if retrieved:
        try:
            age = (today - date.fromisoformat(str(retrieved)[:10])).days
            if age > 30:
                score *= 0.7
                detail.append(f"{age}d old")
        except ValueError:
            pass

    return min(score, 1.0), "; ".join(detail)


def score_opportunity(ev: dict, restaurant: dict, today: date | None = None) -> dict:
    """Run every dimension and combine. Returns the breakdown, not just a number."""
    parts = {
        "order_size": score_order_size(ev),
        "restaurant_fit": score_restaurant_fit(ev, restaurant),
        "timing": score_timing(ev, today),
        "distance": score_distance(ev),
        "reachability": score_reachability(ev),
        "confidence": score_confidence(ev, today),
    }

    total = sum(WEIGHTS[k] * v[0] for k, v in parts.items())
    return {
        "score": round(total * 100, 1),
        "band": band_for(parts, total),
        "breakdown": {k: {"score": round(v[0], 3), "why": v[1]} for k, v in parts.items()},
    }


def band_for(parts: dict, total: float) -> str:
    """Human-readable bands. Section 8 forbids fake precision like '82.37% likely'."""
    timing = parts["timing"][0]
    size = parts["order_size"][0]

    if timing >= 0.8 and not parts["timing"][1].startswith("recurring"):
        return "Time-sensitive"
    if size >= 0.7:
        return "Large potential"
    if total >= 0.6:
        return "Strong fit"
    if parts["timing"][1].startswith("recurring") and total >= 0.4:
        return "Nearby recurring prospect"
    return "Worth contacting"


def rank(opportunities: list, restaurant: dict, limit: int = 12, today=None) -> list:
    """Score, sort, cut. Five strong beats fifty weak - section 22."""
    scored = []
    for ev in opportunities:
        result = score_opportunity(ev, restaurant, today)
        # Nothing outside delivery range or already passed should ever surface.
        if result["breakdown"]["distance"]["score"] == 0 and ev.get("distance_miles") is not None:
            continue
        if result["breakdown"]["timing"]["why"] == "already passed":
            continue
        scored.append({**ev, **result})

    scored.sort(key=lambda o: o["score"], reverse=True)
    return scored[:limit]


def _selftest() -> int:
    today = date(2026, 8, 19)
    restaurant = {
        "has_group_format": True, "open_lunch": True,
        "dietary_positioning": "halal", "name": "Wok & Karahi",
    }

    tournament = {
        "title": "Spring Youth Soccer Invitational", "attendance": 420,
        "event_date": "2026-08-24", "distance_miles": 1.8,
        "group_format_supported": True, "occasion": "all_day_event",
        "cuisine_affinity": True, "organizer_page": True,
        "sources": ["https://example.org/schedule"], "size_is_explicit": True,
        "retrieved_at": "2026-08-19",
    }
    clinic = {
        "title": "ABC Medical Center", "org_type": "medical", "recurring": True,
        "distance_miles": 1.3, "group_format_supported": True,
        "occasion": "weekday_lunch", "public_phone": True, "known_buyer_role": True,
        "sources": ["https://example.com"], "retrieved_at": "2026-08-19",
    }
    too_far = {"title": "Far Expo", "attendance": 900, "event_date": "2026-09-01",
               "distance_miles": 40.0, "sources": ["https://x.test"]}
    stale = {"title": "Last Week", "attendance": 300, "event_date": "2026-08-10",
             "distance_miles": 2.0, "sources": ["https://x.test"]}

    failures = []

    t = score_opportunity(tournament, restaurant, today)
    if t["band"] != "Time-sensitive":
        failures.append(f"tournament band was {t['band']}, expected Time-sensitive")
    if not t["score"] > 60:
        failures.append(f"tournament scored {t['score']}, expected > 60")

    c = score_opportunity(clinic, restaurant, today)
    if "recurring" not in c["breakdown"]["timing"]["why"]:
        failures.append("clinic should read as recurring")

    ranked = rank([tournament, clinic, too_far, stale], restaurant, today=today)
    titles = [o["title"] for o in ranked]
    if "Far Expo" in titles:
        failures.append("out-of-range opportunity was not filtered")
    if "Last Week" in titles:
        failures.append("passed event was not filtered")
    if titles and titles[0] != "Spring Youth Soccer Invitational":
        failures.append(f"expected the tournament to rank first, got {titles[0]}")

    # A missing signal must score zero and say why, never quietly average.
    empty = score_opportunity({"title": "Nothing known"}, restaurant, today)
    if empty["breakdown"]["order_size"]["score"] != 0.0:
        failures.append("unknown size did not score 0")
    if empty["breakdown"]["confidence"]["why"] != "no sources":
        failures.append("missing sources did not report 'no sources'")

    for f in failures:
        print(f"FAIL: {f}")
    if not failures:
        print(f"ok - {len(ranked)} ranked, top: {titles[0]} ({ranked[0]['score']})")
    return 1 if failures else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
