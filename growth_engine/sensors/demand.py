"""
growth_engine.sensors.demand — FREE demand-signal harvester (Google Autocomplete).

No API key, no cost: hits the public Google Suggest endpoint for our buyer topics and turns the real
"what people also type" expansions into findings — top demand signals + commercial-intent queries we may
not have a page for yet (content/A-B opportunities). Deterministic; network failure → clean no-op. This is
the demand half of making the loop data-driven (the AI-visibility half is sensors/ai_visibility.py; the
first-party half is GSC once the service account is granted Search Console access).
"""
from __future__ import annotations
import urllib.request, urllib.parse, json, os
from .. import model
from ..executors import REPO

# Buyer topics for the ideal customer (independent restaurant owners). Refined from research + real queries.
SEEDS = [
    "how to cut doordash fees", "best restaurant pos", "restaurant online ordering",
    "ai phone answering for restaurants", "how much does a restaurant pos cost",
    "should i leave doordash", "how to get more restaurant reviews", "restaurant loyalty program",
    "restaurant marketing", "how to reduce restaurant no shows", "restaurant catering software",
    "how to get my restaurant on google", "commission free online ordering", "toast vs",
]
_COMMERCIAL = ("cost", "price", "pricing", " vs ", "alternative", "best", "cheapest",
               "near me", "setup", "service", "software", "calculator", "how much")


def _suggest(term: str) -> list[str]:
    try:
        url = "https://suggestqueries.google.com/complete/search?client=firefox&q=" + urllib.parse.quote(term)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8", "replace"))
        return [s for s in d[1] if isinstance(s, str)]
    except Exception:
        return []


def _slugs() -> set[str]:
    try:
        return {p.lower() for p in os.listdir(REPO) if p.endswith(".html")}
    except Exception:
        return set()


def _covered(sugg: str, slugs: set[str]) -> bool:
    words = [w for w in sugg.lower().replace("?", "").replace("'", "").split() if len(w) > 3]
    if len(words) < 2:
        return True  # too generic to call a gap
    key = words[:2]
    return any(all(w in s for w in key) for s in slugs)


def sense(verbose: bool = True) -> dict:
    counts: dict[str, int] = {}
    for seed in SEEDS:
        for s in _suggest(seed):
            k = s.lower().strip()
            if k:
                counts[k] = counts.get(k, 0) + 1
    if not counts:
        if verbose:
            print("demand: no autocomplete data (network?) — skipping.")
        return {"available": False}

    model.signal("demand", "autocomplete_terms", "site", len(counts), unit="count", period="point",
                 meta={"top": sorted(counts, key=lambda k: -counts[k])[:20]})
    slugs = _slugs()
    commercial = [s for s in counts if any(k in s for k in _COMMERCIAL)]
    gaps = [s for s in commercial if not _covered(s, slugs)]
    top = sorted(counts, key=lambda k: -counts[k])[:8]

    model.finding("D1_demand", "site", "opportunity", "watch",
                  "Demand signals (real Google searches): " + "; ".join(top[:6]),
                  detail="What people actually type around our buyer topics (Google Autocomplete). "
                         "Use these to shape headlines, A/B copy, and the next content pages.")
    for g in gaps[:3]:
        model.finding("D2_gap", f"query:{g}", "opportunity", "watch",
                      f"Content gap — people search “{g}” and we may not cover it",
                      detail="Commercial-intent query with no obvious matching page — a candidate for a new "
                             "comparison / cost / how-to page or calculator.")
    if verbose:
        print(f"demand: {len(counts)} suggestions, {len(gaps)} commercial gaps. Top: {top[:4]}")
    return {"available": True, "count": len(counts), "gaps": gaps[:5]}
