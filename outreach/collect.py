#!/usr/bin/env python3
"""Collector v1 - site crawl, menu teardown, catering state, crawler access.

Implements ARCHITECTURE.md sections 4 and 8. Every value carries its own
evidence envelope, because a field without provenance becomes a claim we make
to an owner as though we knew it.

Free and automatable only. Public records, reviews, journey and social are
separate collectors.

    python3 outreach/collect.py outreach/targets/cypress.json [--limit N]
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
NOW = datetime.now(timezone.utc)

PAGES = ["", "/menu", "/menus", "/food", "/order", "/order-online", "/catering",
         "/about", "/contact", "/hours", "/events", "/private-dining", "/specials"]

DIRECT = {"toasttab": "Toast", "clover.com": "Clover", "order.online": "Owner.com",
          "chownow": "ChowNow", "popmenu": "Popmenu", "menufy": "Menufy",
          "slicelife": "Slice", "olo.com": "Olo", "spoton": "SpotOn",
          "bentobox": "BentoBox", "square.site": "Square", "squareup": "Square",
          "gloriafood": "GloriaFood", "menusifu": "MenuSifu", "ordereze": "Ordereze",
          "hungerrush": "HungerRush", "menudrive": "MenuDrive"}
THIRD = {"doordash": "DoorDash", "ubereats": "Uber Eats", "grubhub": "Grubhub",
         "postmates": "Postmates", "seamless": "Seamless", "ezcater": "ezCater"}
AI_BOTS = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended",
           "anthropic-ai", "CCBot", "Applebot-Extended"]


def ev(value, tier, source, method, confidence=1.0, days=30, note=None):
    """The evidence envelope from ARCHITECTURE.md section 0."""
    e = {"value": value, "tier": tier, "source": source, "method": method,
         "observed_at": NOW.isoformat(timespec="seconds"),
         "confidence": confidence,
         "expires": (NOW + timedelta(days=days)).date().isoformat()}
    if note:
        e["note"] = note
    return e


def unknown(reason, source=None):
    return {"value": None, "tier": "UNKNOWN", "reason": reason, "source": source,
            "observed_at": NOW.isoformat(timespec="seconds")}


def get(url, timeout=18):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl(), r.read(600_000).decode("utf-8", "ignore")
    except Exception as e:
        return 0, url, f"__ERR__{type(e).__name__}"


def strip(html):
    html = re.sub(r"(?s)<(script|style|noscript).*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def classify(html, text, links):
    """DEAD / PARKED / JS_SHELL / STATIC - section 8."""
    if not html or html.startswith("__ERR__") or len(html) < 500:
        return "DEAD"
    low = html.lower()
    if any(k in low for k in ("domain is for sale", "buy this domain", "godaddy.com/forsale",
                              "coming soon", "under construction", "parked free")):
        return "PARKED"
    if len(text.split()) < 30 and links >= 3:
        return "JS_SHELL"
    if len(text.split()) < 30:
        return "PARKED"
    return "STATIC"


def render(url):
    """Headless render. A JS shell is not an absence of content."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            pg = b.new_page(user_agent=UA, viewport={"width": 390, "height": 844})
            pg.goto(url, wait_until="networkidle", timeout=25000)
            html, text = pg.content(), pg.inner_text("body")
            b.close()
            return html, re.sub(r"\s+", " ", text).strip()
    except Exception:
        return None, None


PRICE = re.compile(r"\$\s?(\d{1,3}(?:\.\d{2})?)")


def menu_teardown(text, html, substantive):
    """Section 4. Price architecture from what is actually published.

    Only runs on a substantive site. A parked page with a phone number in it will
    happily yield a "median price", which is worse than no answer at all.

    Prices are split into per-item and large-format, because a $150 number on a
    restaurant site is a catering tray, not a dish, and averaging them together
    produces a figure that is wrong in a way nobody can see."""
    if not substantive:
        return {"price_architecture": unknown(
            "site is dead, parked or too thin to carry a menu", "site")}
    found = [float(p) for p in PRICE.findall(text)]
    item = sorted(p for p in found if 3.0 <= p <= 80.0)
    large = sorted(p for p in found if 80.0 < p <= 1500.0)
    prices = item
    if not prices:
        return {"prices_found": ev(0, "OBSERVED", "site", "regex over rendered text"),
                "price_architecture": unknown("no prices published on the pages we could read")}
    prices.sort()
    n = len(prices)
    med = prices[n // 2]
    charm = sum(1 for p in prices if round(p % 1, 2) in (0.99, 0.95, 0.49, 0.89))
    round_p = sum(1 for p in prices if p == int(p))
    return {
        "prices_found": ev(n, "OBSERVED", "site", "regex over rendered text"),
        "price_min": ev(prices[0], "OBSERVED", "site", "min of parsed prices"),
        "price_median": ev(med, "DERIVED", "site", "median of parsed prices"),
        "price_max": ev(prices[-1], "OBSERVED", "site", "max of parsed prices"),
        "price_spread": ev(round(prices[-1] - prices[0], 2), "DERIVED", "site", "max minus min"),
        "charm_pricing_share": ev(round(charm / n, 2), "DERIVED", "site",
                                  "share ending .99/.95/.49/.89"),
        "round_pricing_share": ev(round(round_p / n, 2), "DERIVED", "site",
                                  "share at whole dollars"),
        "pricing_style": ev(
            "charm" if charm / n > 0.5 else "round" if round_p / n > 0.5 else "mixed",
            "INFERRED", "site", "dominant ending across parsed prices", 0.7,
            note="mixed usually means prices were set item by item rather than to a policy"),
        "dollar_signs_used": ev("$" in text, "OBSERVED", "site", "literal scan"),
        "large_format_prices": ev(large, "OBSERVED", "site",
                                  "$80-1500, read as catering trays or party packages "
                                  "rather than dishes"),
        "price_deciles": ev([prices[int(n * (len(prices) - 1) / 10)] for n in range(11)],
                            "DERIVED", "site", "so the distribution can be sanity-checked "
                            "rather than trusted on a single median"),
        "_caveat": "Prices are parsed from unstructured page text, not a menu API. Treat the "
                   "shape as indicative and confirm any number before quoting it to an owner.",
    }


def catering_state(text, pages_seen):
    """Four states, section 4.5 - the pitch differs completely between them."""
    low = text.lower()
    mentioned = "catering" in low or "cater " in low
    has_page = any("/catering" in u for u in pages_seen)
    orderable = bool(re.search(r"catering[^.]{0,120}(order|request|enquir|inquir|quote|form)", low))
    priced = bool(re.search(r"catering[^.]{0,160}\$\s?\d", low)) or \
             bool(re.search(r"per (person|head)", low))
    if not mentioned:
        s, why = "ABSENT", ("No mention anywhere we could read. Capability unknown, and usually "
                            "means it has never been considered as a channel.")
    elif mentioned and not (has_page or orderable):
        s, why = "MENTIONED_ONLY", ("Named but with no way to order or price it. Demand may "
                                    "exist; the channel does not.")
    elif (has_page or orderable) and not priced:
        s, why = "PAGE_NO_PRICING", ("There is a catering page but no minimums or per-head "
                                     "pricing, so every enquiry becomes a manual conversation.")
    else:
        s, why = "OPERATIONAL", ("Catering has a real path. Look for volume levers rather "
                                 "than setup.")
    return {"state": ev(s, "OBSERVED" if not mentioned else "INFERRED", "site crawl",
                        "keyword and path analysis", 0.9 if not mentioned else 0.7, note=why),
            "has_catering_page": ev(has_page, "OBSERVED", "site crawl", "path scan"),
            "priced": ev(priced, "OBSERVED", "site crawl", "per-head or catering-adjacent price")}


def crawler_access(root):
    """AEO component: are the AI crawlers allowed. Many sites block them by accident."""
    st, _, body = get(urllib.parse.urljoin(root, "/robots.txt"), timeout=10)
    if st != 200 or body.startswith("__ERR__"):
        return {"robots_txt": ev(False, "OBSERVED", root + "/robots.txt", "fetch"),
                "ai_crawlers_blocked": ev([], "DERIVED", root + "/robots.txt",
                                          "no robots.txt means nothing is blocked")}
    blocked = []
    for bot in AI_BOTS:
        m = re.search(rf"user-agent:\s*{re.escape(bot)}(.*?)(?=user-agent:|$)",
                      body, re.I | re.S)
        if m and re.search(r"disallow:\s*/\s*$", m.group(1), re.I | re.M):
            blocked.append(bot)
    return {"robots_txt": ev(True, "OBSERVED", root + "/robots.txt", "fetch"),
            "ai_crawlers_blocked": ev(blocked, "OBSERVED", root + "/robots.txt",
                                      "per-agent disallow scan"),
            "llms_txt": ev(get(urllib.parse.urljoin(root, "/llms.txt"))[0] == 200,
                           "OBSERVED", root + "/llms.txt", "fetch")}


def first_gift(d):
    """Section 13.8 - one thing we can do or show before they owe us anything."""
    o = []
    if d["site"]["status"]["value"] in ("DEAD", "PARKED"):
        o.append("Show them what a guest sees today when they search the restaurant: nothing. "
                 "No access needed, and it is the whole pitch in one screen.")
    if d["site"]["status"]["value"] == "JS_SHELL":
        o.append("Show them their own site with JavaScript off, which is roughly what a "
                 "crawler and an AI assistant see. Costs nothing and lands hard.")
    if not d["discovery"]["restaurant_schema"]["value"]:
        o.append("Write their structured data and hand it over as a file. Twenty minutes, "
                 "needs no login, and their web person can paste it in.")
    if d["catering"]["state"]["value"] in ("ABSENT", "MENTIONED_ONLY"):
        o.append("Draft a one-page catering sheet with minimums and lead time. They can use "
                 "it whether or not they ever work with us.")
    if d["discovery"]["ai_crawlers_blocked"]["value"]:
        o.append("Tell them their robots.txt is blocking the AI crawlers, probably by "
                 "template accident. One-line fix, and nobody else will have told them.")
    return o or ["Run the five standard AI prompts and show them the verbatim answer they get."]


def collect(t):
    name, site = t["name"], t.get("site")
    if not site:
        return {"restaurant": t, "collected_at": NOW.isoformat(timespec="seconds"),
                "site": {"status": ev("NO_SITE_LISTED", "UNKNOWN", None, "directory had none")},
                "verdict": ev("VERIFY_FIRST", "INFERRED", "directory", "no site listed", 0.5,
                              note="confirm still trading before any approach"),
                "first_gift": ["Show them that searching their name returns no website at all."]}

    st, final, html = get(site)
    text = strip(html)
    links = len(set(re.findall(r'href="(/[^"#]*|https?://[^"]*)"', html)))
    status = classify(html, text, links)
    rendered = False

    if status == "JS_SHELL":
        rhtml, rtext = render(final)
        if rtext and len(rtext.split()) > len(text.split()):
            html, text, rendered = rhtml, rtext, True
            status = "STATIC_AFTER_RENDER"

    pages_seen, all_text = [final], text
    if status in ("STATIC", "STATIC_AFTER_RENDER"):
        root = f"{urllib.parse.urlparse(final).scheme}://{urllib.parse.urlparse(final).netloc}"
        for path in PAGES[1:]:
            u = root + path
            s2, f2, h2 = get(u, timeout=12)
            if s2 == 200 and not h2.startswith("__ERR__") and len(h2) > 800:
                t2 = strip(h2)
                if len(t2.split()) > 40:
                    pages_seen.append(f2)
                    all_text += " " + t2
                    html += h2

    low = html.lower()
    hosts = set(re.findall(r"https?://([a-z0-9.\-]+)", low))
    direct = sorted({v for k, v in DIRECT.items() if any(k in h for h in hosts) or k in low})
    third = sorted({v for k, v in THIRD.items() if any(k in h for h in hosts)})

    schema = []
    for blob in re.findall(r'<script[^>]+ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            j = json.loads(blob)
        except Exception:
            continue
        for node in (j.get("@graph") if isinstance(j, dict) and "@graph" in j
                     else j if isinstance(j, list) else [j]):
            if isinstance(node, dict) and node.get("@type"):
                ty = node["@type"]
                schema += ty if isinstance(ty, list) else [ty]

    root = f"{urllib.parse.urlparse(final).scheme}://{urllib.parse.urlparse(final).netloc}"
    d = {
        "restaurant": t,
        "collected_at": NOW.isoformat(timespec="seconds"),
        "site": {
            "status": ev(status, "OBSERVED", final, "fetch, classify, render fallback"),
            "rendered_with_browser": ev(rendered, "OBSERVED", final, "playwright chromium"),
            "final_url": ev(final, "OBSERVED", site, "redirect chain"),
            "https": ev(final.startswith("https://"), "OBSERVED", final, "scheme"),
            "words": ev(len(all_text.split()), "OBSERVED", final, "text after tag strip"),
            "pages_crawled": ev(len(pages_seen), "OBSERVED", final, "path probe", days=30),
            "substantive": ev(len(all_text.split()) >= 150 and links >= 3,
                              "DERIVED", final, "section 8 substance test"),
        },
        "discovery": {
            "restaurant_schema": ev(any(x in schema for x in
                                        ("Restaurant", "LocalBusiness", "FoodEstablishment")),
                                    "OBSERVED", final, "ld+json parse"),
            "schema_types": ev(sorted(set(schema)), "OBSERVED", final, "ld+json parse"),
            "mobile_viewport": ev('name="viewport"' in low, "OBSERVED", final, "meta scan"),
            "tel_link": ev('href="tel:' in low, "OBSERVED", final, "link scan"),
            "menu_is_pdf": ev(bool(re.search(r'href="[^"]+\.pdf', low)) and "menu" in low,
                              "OBSERVED", final, "link scan"),
            **crawler_access(root),
        },
        "ordering": {
            "direct_platforms": ev(direct, "OBSERVED", final, "link and fingerprint scan"),
            "third_party": ev(third, "OBSERVED", final, "link scan"),
            "channel_state": ev(
                "third-party only" if third and not direct else
                "direct only" if direct and not third else
                "both" if direct and third else "none online",
                "DERIVED", final, "from platforms found"),
        },
        # gate on classification, not word count: a parked page can carry 150 words
        # of registrar boilerplate and will happily yield a "median price"
        "menu": menu_teardown(all_text, html,
                              status in ("STATIC", "STATIC_AFTER_RENDER")
                              and len(all_text.split()) >= 150 and links >= 3),
        "catering": catering_state(all_text, pages_seen),
    }
    d["first_gift"] = first_gift(d)
    d["verdict"] = ev("PURSUE_NOW" if d["site"]["substantive"]["value"] else "VERIFY_FIRST",
                      "INFERRED", "collector", "site substance only - winnability needs "
                      "public records and a human read", 0.4,
                      note="provisional. section 13.1 verdict needs the records collector")
    return d


def main():
    src = pathlib.Path(sys.argv[1])
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    targets = json.loads(src.read_text())["restaurants"][:limit]
    outdir = src.parent.parent / "dossiers"
    outdir.mkdir(exist_ok=True)

    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(collect, targets))

    for r in results:
        slug = re.sub(r"[^a-z0-9]+", "-", r["restaurant"]["name"].lower()).strip("-")
        (outdir / f"{slug}.json").write_text(json.dumps(r, indent=1))
        s = r["site"]["status"]["value"]
        extra = ""
        if r.get("menu", {}).get("price_median", {}).get("value"):
            extra = f" median ${r['menu']['price_median']['value']:.2f}"
        cat = r.get("catering", {}).get("state", {}).get("value", "")
        print(f"  {r['restaurant']['name'][:30]:32} {s:20}{extra:16} catering={cat}")
    print(f"\n{len(results)} dossiers -> {outdir}")


if __name__ == "__main__":
    main()
