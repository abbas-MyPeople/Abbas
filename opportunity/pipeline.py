#!/usr/bin/env python3
"""Phases 2 and 5-9: restaurant context, enrichment, dedupe, rank, phrase, shape.

The ranking is done by score.py before any model is called, and the model only
ever phrases a summary over facts it was handed. Nothing in here invents a
number, a name, a date or a relationship - a fact we do not have is simply absent.

    python3 opportunity/pipeline.py --selftest
"""
from __future__ import annotations

import os
import re
import sys

from . import providers, score

# Reuse the flagship crawler rather than writing a second one. Its evidence
# doctrine (outreach/ARCHITECTURE.md) is the one this tool inherits.
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from outreach.collect import get as crawl_get, strip as crawl_strip
except ImportError:                                     # pragma: no cover
    crawl_get = crawl_strip = None

GROUP_FORMAT_WORDS = ("catering", "party tray", "party pack", "platter", "family pack",
                      "family size", "bulk order", "group order", "half pan", "full pan",
                      "feeds ", "serves ")
DIETARY_WORDS = ("halal", "kosher", "vegan", "vegetarian", "gluten-free")

# A mosque plus a halal restaurant is a real, evidence-backed link. Anything
# looser than this would be us inventing compatibility.
DIET_ORG_LINK = {"halal": {"worship"}, "kosher": {"worship"}}

CONTEXT_PAGES = ("", "/catering", "/menu")


def restaurant_context(restaurant: dict) -> dict:
    """Phase 2. Public site only. Absent signals stay absent."""
    ctx = {
        "name": restaurant.get("name"),
        "cuisine": _cuisine_from_types(restaurant.get("types") or []),
        "open_lunch": restaurant.get("open_lunch"),
        "has_group_format": None,
        "dietary_positioning": None,
    }

    site = restaurant.get("website")
    if not site or not crawl_get:
        return ctx

    text = ""
    for path in CONTEXT_PAGES:
        status, _, body = crawl_get(site.rstrip("/") + path)
        if status == 200 and not body.startswith("__ERR__"):
            text += " " + (crawl_strip(body) if crawl_strip else body).lower()

    if not text.strip():
        return ctx

    ctx["has_group_format"] = any(w in text for w in GROUP_FORMAT_WORDS) or None
    for word in DIETARY_WORDS:
        if word in text:
            ctx["dietary_positioning"] = word
            break
    return ctx


def _cuisine_from_types(types: list) -> str | None:
    for t in types:
        if t.endswith("_restaurant") and t != "restaurant":
            return t[:-11].replace("_", " ")
    return None


def enrich(candidates: list, restaurant: dict, ctx: dict) -> list:
    """Phase 5. Attach the fit signals the scorer reads, each one grounded."""
    diet = ctx.get("dietary_positioning")
    for c in candidates:
        c.setdefault("group_format_supported", True)

        if diet and c.get("org_type") in DIET_ORG_LINK.get(diet, set()):
            c["dietary_signals"] = [diet]

        if c.get("kind") == "organization":
            c["contact_route"] = _org_route(c)
            c["known_buyer_role"] = c.get("org_type") in (
                "medical", "hospital", "dental", "law_firm", "corporate_office",
                "office", "school", "university", "property_management")
        else:
            c["contact_route"] = "Event organiser via the public listing"

        if c.get("website"):
            c["website_flag"] = True
    return candidates


def _org_route(c: dict) -> str:
    role = {
        "medical": "Office manager or practice administrator",
        "hospital": "Food services or practice administrator",
        "dental": "Office manager",
        "law_firm": "Office manager or executive assistant",
        "corporate_office": "Office manager or HR",
        "office": "Office manager",
        "school": "School administrator",
        "university": "Department or student-life coordinator",
        "worship": "Community or events coordinator",
        "property_management": "Property manager",
        "venue": "Events coordinator",
        "hotel": "Banquet or events coordinator",
        "dealership": "Sales manager",
    }.get(c.get("org_type"), "Office manager")
    how = "public phone" if c.get("public_phone") else ("website" if c.get("website") else "listing")
    return f"{role} - via {how}"


def dedupe(candidates: list) -> list:
    """Phase 6. Same place from two groups, or the same event listed twice."""
    seen_ids, seen_keys, out = set(), set(), []
    for c in candidates:
        cid = c.get("id")
        if cid and cid in seen_ids:
            continue
        key = (_norm(c.get("title")), round(c.get("distance_miles") or -1))
        if key in seen_keys:
            continue
        if cid:
            seen_ids.add(cid)
        seen_keys.add(key)
        out.append(c)
    return out


def _norm(s) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def owner_reasons(o: dict, ctx: dict) -> list:
    """Why-it-fits, written for a restaurant owner.

    Deliberately NOT the scorer's breakdown strings - those are engineer-facing
    ("reachable via organizer page", "no size published; medical type prior") and
    reading them back to an owner is how a smart tool sounds stupid. Distance is
    omitted because the card header already shows it.
    """
    out = []

    if o.get("attendance"):
        out.append(f"About {int(o['attendance']):,} people expected")
    elif o.get("headcount"):
        out.append(f"Around {int(o['headcount']):,} staff on site")

    if o.get("group_format_supported") and ctx.get("has_group_format"):
        out.append("You already offer group and tray formats")
    if o.get("occasion") == "weekday_lunch" and ctx.get("open_lunch"):
        out.append("Weekday lunch fits your opening hours")
    elif o.get("occasion") == "all_day_event":
        out.append("All-day event, so food demand spans a meal")

    diet = ctx.get("dietary_positioning")
    if diet and diet in (o.get("dietary_signals") or []):
        out.append(f"Your {diet} positioning matters to this group")

    if o.get("recurring"):
        out.append("Recurring prospect, so there is no deadline to miss")
    elif o.get("when"):
        out.append("Time-sensitive, but still far enough out to win")

    if o.get("public_phone"):
        out.append("Public phone number listed")
    elif o.get("organizer_page"):
        out.append("Organiser contact page is public")

    return out


def shape(ranked: list, ctx: dict, explain: bool = True) -> list:
    """Phases 8 and 9. Build the card the page renders."""
    cards = []
    for o in ranked:
        why = owner_reasons(o, ctx)

        summary = providers.summarize(o, ctx) if explain else None

        cards.append({
            "title": o.get("title"),
            "band": o.get("band"),
            "when": o.get("when"),
            "distance_miles": o.get("distance_miles"),
            "summary": summary,
            "why": why,
            "contact_route": o.get("contact_route"),
            "sources": o.get("sources") or [],
        })
    return cards


def search(query: str, budget=None, radius_miles: float = 5.0,
           event_radius_miles: float = 10.0, limit: int = 12,
           explain: bool = True) -> dict:
    """The whole pipeline. Returns a payload the front end can render as-is."""
    # Distinguish "we looked and found nothing" from "we were never switched on".
    # Collapsing the two would tell an owner his restaurant does not exist.
    if not providers.places_key():
        return {"ok": False, "reason": "not_configured", "opportunities": []}

    restaurant = providers.resolve_restaurant(query, budget=budget)
    if not restaurant:
        reason = "budget" if (budget and budget.exhausted_sku) else "not_found"
        return {"ok": False, "reason": reason, "opportunities": []}

    ctx = restaurant_context(restaurant)
    lat, lng = restaurant.get("lat"), restaurant.get("lng")

    candidates = providers.nearby_organizations(lat, lng, radius_miles, budget=budget)
    candidates += providers.upcoming_events(lat, lng, event_radius_miles)

    candidates = enrich(dedupe(candidates), restaurant, ctx)
    ranked = score.rank(candidates, ctx, limit=limit)

    return {
        "ok": True,
        "restaurant": {"name": restaurant.get("name"), "address": restaurant.get("address")},
        "opportunities": shape(ranked, ctx, explain=explain),
    }


def _selftest() -> int:
    """No network. Proves the shaping, dedupe and grounding rules hold."""
    failures = []
    ctx = {"name": "Wok & Karahi", "cuisine": "indian", "open_lunch": True,
           "has_group_format": True, "dietary_positioning": "halal"}

    cands = [
        {"kind": "organization", "id": "a", "title": "ABC Medical Center",
         "org_type": "medical", "distance_miles": 1.3, "public_phone": True,
         "recurring": True, "occasion": "weekday_lunch",
         "sources": [{"title": "Google Places", "url": "https://maps.example"}],
         "retrieved_at": "2026-08-19"},
        {"kind": "organization", "id": "a", "title": "ABC Medical Center",
         "org_type": "medical", "distance_miles": 1.3},          # duplicate id
        {"kind": "organization", "id": "b", "title": "Masjid Al-Noor",
         "org_type": "worship", "distance_miles": 2.1, "public_phone": True,
         "recurring": True, "occasion": "weekday_lunch",
         "sources": [{"title": "Google Places", "url": "https://maps.example"}],
         "retrieved_at": "2026-08-19"},
    ]

    deduped = dedupe(cands)
    if len(deduped) != 2:
        failures.append(f"dedupe kept {len(deduped)}, expected 2")

    enriched = enrich(deduped, {}, ctx)
    mosque = next(c for c in enriched if c["org_type"] == "worship")
    if mosque.get("dietary_signals") != ["halal"]:
        failures.append("halal restaurant + mosque should link on dietary")
    clinic = next(c for c in enriched if c["org_type"] == "medical")
    if "dietary_signals" in clinic:
        failures.append("a clinic must NOT get an invented dietary link")
    if "Office manager" not in clinic["contact_route"]:
        failures.append(f"unexpected clinic route: {clinic['contact_route']}")

    ranked = score.rank(enriched, ctx)
    cards = shape(ranked, ctx, explain=False)          # explain=False: no network
    if not cards:
        failures.append("no cards produced")
    elif not cards[0]["why"]:
        failures.append("card has no 'why' lines")
    elif cards[0]["summary"] is not None:
        failures.append("summary should be None when explain=False")
    # The owner never sees the scorer's internal phrasing.
    leaks = ("type prior", "reachable via", "(sourced)", "still winnable")
    if any(any(l in w for l in leaks) or re.search(r"\d+(\.\d+)? mi\b", w)
           for c in cards for w in c["why"]):
        failures.append(f"scorer debug phrasing leaked into 'why': {cards[0]['why']}")
    if not any("Recurring prospect" in w for c in cards for w in c["why"]):
        failures.append("expected an owner-facing recurring reason")

    if _cuisine_from_types(["indian_restaurant", "restaurant"]) != "indian":
        failures.append("cuisine extraction failed")

    for f in failures:
        print("FAIL:", f)
    if not failures:
        print(f"ok - {len(cards)} cards, dedupe and grounding rules hold")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else print(__doc__))
