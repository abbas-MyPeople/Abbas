#!/usr/bin/env python3
"""External data providers, each behind a small interface.

Every provider returns [] or None when its credential is missing rather than
raising, so the pipeline degrades instead of failing. Nothing here fabricates a
value: a field that is not published comes back absent, never guessed.

Chosen so the whole tool runs inside free tiers (see README):
  - Google Places API (New) - Text Search + Nearby Search, Pro SKUs, 5k free/mo each
  - Ticketmaster Discovery  - 5k calls/day free
  - Groq                    - free tier, used only to phrase a summary line
"""
from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

PLACES_BASE = "https://places.googleapis.com/v1"
TICKETMASTER_BASE = "https://app.ticketmaster.com/discovery/v2/events.json"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.environ.get("OPP_GROQ_MODEL", "llama-3.3-70b-versatile")

UA = "AZRestaurantPartners-OpportunityFinder/1.0 (+https://azrestaurantpartners.com)"


def _post(url: str, payload: dict, headers: dict, timeout: int = 20):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": UA, **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return None


def _get(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return None


def haversine_miles(a: tuple, b: tuple) -> float:
    """Straight-line distance. Honest about being straight-line, not drive time."""
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return round(2 * 3958.8 * math.asin(math.sqrt(h)), 2)


# ── Google Places ─────────────────────────────────────────────────────────────

def places_key() -> str | None:
    return os.environ.get("PLACES_API_KEY") or None


# Grouped so each group is ONE Nearby call. Places caps results at 20 per call,
# so grouping by buying occasion gives better coverage than one giant request.
NEARBY_GROUPS = {
    "medical": ["hospital", "doctor", "dental_clinic", "medical_lab", "physiotherapist"],
    "education_worship": ["school", "primary_school", "secondary_school", "university",
                          "church", "mosque", "synagogue", "hindu_temple"],
    "corporate": ["corporate_office", "lawyer", "insurance_agency", "real_estate_agency",
                  "accounting", "car_dealer"],
    "venue_hospitality": ["event_venue", "hotel", "banquet_hall", "convention_center",
                          "community_center"],
}

# Which of our internal org_type values each group maps to, for the scorer.
GROUP_ORG_TYPE = {
    "medical": "medical", "education_worship": "school",
    "corporate": "corporate_office", "venue_hospitality": "venue",
}

TYPE_TO_ORG = {
    "hospital": "hospital", "doctor": "medical", "dental_clinic": "dental",
    "school": "school", "primary_school": "school", "secondary_school": "school",
    "university": "university", "church": "worship", "mosque": "worship",
    "synagogue": "worship", "hindu_temple": "worship",
    "corporate_office": "corporate_office", "lawyer": "law_firm",
    "insurance_agency": "office", "real_estate_agency": "property_management",
    "accounting": "office", "car_dealer": "dealership",
    "event_venue": "venue", "hotel": "hotel", "banquet_hall": "venue",
    "convention_center": "venue", "community_center": "venue",
}


def resolve_restaurant(query: str, budget=None) -> dict | None:
    """Phase 1. One Text Search call. Returns None if the key is missing or nothing matched."""
    key = places_key()
    if not key:
        return None
    if budget and not budget.spend("places_text", 1):
        return None

    data = _post(
        f"{PLACES_BASE}/places:searchText",
        {"textQuery": query, "maxResultCount": 1, "includedType": "restaurant"},
        {"X-Goog-Api-Key": key,
         "X-Goog-FieldMask": ("places.id,places.displayName,places.formattedAddress,"
                              "places.location,places.websiteUri,places.primaryType,"
                              "places.types,places.regularOpeningHours")},
    )
    places = (data or {}).get("places") or []
    if not places:
        return None

    p = places[0]
    loc = p.get("location") or {}
    hours = ((p.get("regularOpeningHours") or {}).get("weekdayDescriptions")) or []
    return {
        "place_id": p.get("id"),
        "name": (p.get("displayName") or {}).get("text"),
        "address": p.get("formattedAddress"),
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
        "website": p.get("websiteUri"),
        "types": p.get("types") or [],
        "hours": hours,
        # Lunch service is inferred from published hours only, never assumed.
        "open_lunch": any(":" in h and ("11" in h or "12" in h) for h in hours) or None,
    }


def nearby_organizations(lat: float, lng: float, radius_miles: float = 5.0,
                         budget=None) -> list[dict]:
    """Phase 3. One Nearby call per group. Returns [] without a key."""
    key = places_key()
    if not key or lat is None or lng is None:
        return []

    out, origin = [], (lat, lng)
    for group, types in NEARBY_GROUPS.items():
        if budget and not budget.spend("places_nearby", 1):
            break
        data = _post(
            f"{PLACES_BASE}/places:searchNearby",
            {"includedTypes": types, "maxResultCount": 20,
             "locationRestriction": {"circle": {
                 "center": {"latitude": lat, "longitude": lng},
                 "radius": min(radius_miles * 1609.34, 50000)}}},
            {"X-Goog-Api-Key": key,
             "X-Goog-FieldMask": ("places.id,places.displayName,places.location,"
                                  "places.primaryType,places.types,places.websiteUri,"
                                  "places.nationalPhoneNumber,places.businessStatus")},
        )
        for p in (data or {}).get("places") or []:
            if p.get("businessStatus") not in (None, "OPERATIONAL"):
                continue
            loc = p.get("location") or {}
            if loc.get("latitude") is None:
                continue
            primary = p.get("primaryType")
            out.append({
                "kind": "organization",
                "id": p.get("id"),
                "title": (p.get("displayName") or {}).get("text"),
                "org_type": TYPE_TO_ORG.get(primary, GROUP_ORG_TYPE.get(group, "office")),
                "distance_miles": haversine_miles(origin, (loc["latitude"], loc["longitude"])),
                "website": p.get("websiteUri"),
                "public_phone": bool(p.get("nationalPhoneNumber")),
                "phone": p.get("nationalPhoneNumber"),
                "recurring": True,
                "occasion": "weekday_lunch",
                "sources": [{"title": "Google Places",
                             "url": f"https://www.google.com/maps/place/?q=place_id:{p.get('id')}"}],
                "retrieved_at": datetime.now(timezone.utc).date().isoformat(),
            })
    return out


# ── Ticketmaster Discovery ────────────────────────────────────────────────────

def upcoming_events(lat: float, lng: float, radius_miles: float = 10.0,
                    horizon_days: int = 30) -> list[dict]:
    """Phase 4. Free tier, 5k/day. Covers venue/concert/sports, not school calendars."""
    key = os.environ.get("TICKETMASTER_API_KEY")
    if not key or lat is None or lng is None:
        return []

    now = datetime.now(timezone.utc)
    params = {
        "apikey": key, "latlong": f"{lat},{lng}",
        "radius": int(radius_miles), "unit": "miles",
        "startDateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": (now + timedelta(days=horizon_days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size": 50, "sort": "date,asc",
    }
    data = _get(f"{TICKETMASTER_BASE}?{urllib.parse.urlencode(params)}")
    events = ((data or {}).get("_embedded") or {}).get("events") or []

    out, origin = [], (lat, lng)
    for e in events:
        start = ((e.get("dates") or {}).get("start") or {}).get("localDate")
        if not start:
            continue
        venues = ((e.get("_embedded") or {}).get("venues") or [])
        venue = venues[0] if venues else {}
        vloc = venue.get("location") or {}
        try:
            miles = haversine_miles(origin, (float(vloc["latitude"]), float(vloc["longitude"])))
        except (KeyError, TypeError, ValueError):
            miles = None

        # Capacity is only used when the venue actually publishes it.
        cap = venue.get("capacity")
        out.append({
            "kind": "event",
            "id": e.get("id"),
            "title": e.get("name"),
            "event_date": start,
            "when": start,
            "distance_miles": miles,
            "venue": venue.get("name"),
            "attendance": int(cap) if isinstance(cap, (int, float)) and cap else None,
            "size_is_explicit": bool(cap),
            "organizer_page": bool(e.get("url")),
            "occasion": "all_day_event",
            "group_format_supported": True,
            "sources": [s for s in [
                {"title": "Ticketmaster listing", "url": e.get("url")} if e.get("url") else None,
            ] if s],
            "retrieved_at": now.date().isoformat(),
        })
    return out


# ── Groq: phrasing only ───────────────────────────────────────────────────────

SUMMARY_SYSTEM = (
    "You write one plain sentence about a sales opportunity for a restaurant owner. "
    "You are given structured facts. Use ONLY those facts. Never invent attendance, "
    "headcount, names, dates, or relationships. If a fact is absent, do not mention it. "
    "No marketing adjectives. No exclamation marks. One sentence, under 25 words."
)


def summarize(opportunity: dict, restaurant: dict) -> str | None:
    """Phase 8. Phrasing only - the model receives evidence and may not add to it."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None

    facts = {k: opportunity.get(k) for k in
             ("title", "kind", "org_type", "venue", "event_date", "distance_miles",
              "attendance", "occasion") if opportunity.get(k) is not None}
    facts["restaurant_cuisine"] = restaurant.get("cuisine")

    data = _post(GROQ_URL, {
        "model": GROQ_MODEL, "max_tokens": 60, "temperature": 0.2,
        "messages": [{"role": "system", "content": SUMMARY_SYSTEM},
                     {"role": "user", "content": json.dumps(facts)}],
    }, {"Authorization": f"Bearer {key}"})

    try:
        return data["choices"][0]["message"]["content"].strip() or None
    except (KeyError, IndexError, TypeError):
        return None
