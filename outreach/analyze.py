#!/usr/bin/env python3
"""Read a restaurant's public web presence and score where it is losing money.

Everything here comes from what the restaurant publishes to the open web: their
own site, and the platform links on it. Nothing private, nothing scraped from
behind a login, no personal data — this is the same read a guest performs in
five seconds, done consistently.

The output is not a lead score. It is a per-restaurant map of which of the six
jobs is visibly broken, so the first sentence of any approach is about them
rather than about us.

    python3 outreach/analyze.py targets/cypress.json
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151 Safari/537.36"

# Direct-ordering platforms. Presence means they already keep the money on at
# least some orders; absence with delivery links present is the expensive case.
DIRECT = {
    "toasttab.com": "Toast", "order.toasttab.com": "Toast",
    "clover.com": "Clover", "order.online": "Owner.com", "owner.com": "Owner.com",
    "chownow.com": "ChowNow", "popmenu.com": "Popmenu", "menufy.com": "Menufy",
    "slicelife.com": "Slice", "olo.com": "Olo", "spoton.com": "SpotOn",
    "bentobox": "BentoBox", "square.site": "Square", "squareup.com": "Square",
    "toast.com": "Toast", "gloriafood": "GloriaFood", "menusifu": "MenuSifu",
}
THIRD_PARTY = {"doordash.com": "DoorDash", "ubereats.com": "Uber Eats",
               "grubhub.com": "Grubhub", "postmates.com": "Postmates",
               "seamless.com": "Seamless", "slicelife.com/delivery": "Slice"}
SOCIAL = {"facebook.com": "Facebook", "instagram.com": "Instagram",
          "tiktok.com": "TikTok", "twitter.com": "X", "x.com": "X",
          "yelp.com": "Yelp"}


def fetch(url: str, timeout: int = 20) -> tuple[int, str, str]:
    """(status, final_url, body). Never raises — an unreachable site is a finding."""
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl(), r.read(400_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:                                    # DNS, TLS, timeout
        return 0, url, f"__ERROR__{type(e).__name__}"


def analyse(site: str) -> dict:
    status, final, html = fetch(site)
    if status == 0 or not html or html.startswith("__ERROR__"):
        return {"reachable": False, "status": status,
                "error": html.replace("__ERROR__", "") if html else "no response"}

    low = html.lower()
    hosts = set(re.findall(r"https?://([a-z0-9.\-]+)", low))

    direct = sorted({v for k, v in DIRECT.items() if any(k in h for h in hosts) or k in low})
    third = sorted({v for k, v in THIRD_PARTY.items() if any(k in h for h in hosts)})
    social = sorted({v for k, v in SOCIAL.items() if any(k in h for h in hosts)})

    schema_types: list[str] = []
    for blob in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(blob)
        except Exception:
            continue
        for node in (d.get("@graph") if isinstance(d, dict) and "@graph" in d
                     else d if isinstance(d, list) else [d]):
            if isinstance(node, dict) and node.get("@type"):
                t = node["@type"]
                schema_types += t if isinstance(t, list) else [t]

    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\s*(20\d\d)", low)]

    return {
        "reachable": True,
        "status": status,
        "final_url": final,
        "https": final.startswith("https://"),
        "mobile_ready": 'name="viewport"' in low,
        "bytes": len(html),
        "schema": sorted(set(schema_types)),
        "has_restaurant_schema": any(t in schema_types for t in
                                     ("Restaurant", "LocalBusiness", "FoodEstablishment")),
        "direct_ordering": direct,
        "third_party": third,
        "social": social,
        "menu_is_pdf": bool(re.search(r'href="[^"]+\.pdf', low)) and "menu" in low,
        "copyright_year": max(years) if years else None,
        "phone_on_page": bool(re.search(r'href="tel:', low)),
    }


def findings(name: str, a: dict) -> list[dict]:
    """Observable gaps, each mapped to the job it belongs to. Angle, not score."""
    out = []
    if not a.get("reachable"):
        out.append({"job": "Getting found", "severity": "high",
                    "gap": "No working website",
                    "why": "A guest deciding right now has nothing to look at, and an AI "
                           "assistant has nothing to read. Everything else is downstream of this."})
        return out

    if not a["https"]:
        out.append({"job": "Getting found", "severity": "high", "gap": "No HTTPS",
                    "why": "Browsers warn on it and search treats it as a negative signal."})
    if not a["mobile_ready"]:
        out.append({"job": "Getting found", "severity": "high", "gap": "Not built for phones",
                    "why": "Almost every restaurant decision is made on a phone."})
    if not a["has_restaurant_schema"]:
        out.append({"job": "Getting found", "severity": "medium",
                    "gap": "No Restaurant structured data",
                    "why": "Search and AI assistants read structured data first. Without it they "
                           "guess the cuisine, hours and menu — or skip the restaurant."})
    if a["menu_is_pdf"]:
        out.append({"job": "Getting found", "severity": "medium", "gap": "Menu is a PDF",
                    "why": "A PDF menu is close to unreadable on a phone and largely invisible "
                           "to the assistants people now ask."})
    if a["copyright_year"] and a["copyright_year"] < datetime.now().year - 1:
        out.append({"job": "Getting found", "severity": "low",
                    "gap": f"Site looks unmaintained (© {a['copyright_year']})",
                    "why": "Stale signals suggest stale hours and a stale menu."})

    if a["third_party"] and not a["direct_ordering"]:
        out.append({"job": "Winning the order", "severity": "high",
                    "gap": f"Only third-party ordering ({', '.join(a['third_party'])})",
                    "why": "Every order pays a commission, including from guests who already "
                           "knew the name. This is usually the single largest recoverable leak."})
    elif not a["direct_ordering"] and not a["third_party"]:
        out.append({"job": "Winning the order", "severity": "high",
                    "gap": "No online ordering at all",
                    "why": "Orders are limited to whoever gets through on the phone."})
    if not a["phone_on_page"]:
        out.append({"job": "Winning the order", "severity": "low",
                    "gap": "No tap-to-call number",
                    "why": "On a phone, a number that is not a link is a number not dialled."})
    if not a["social"]:
        out.append({"job": "Keeping the guest", "severity": "low",
                    "gap": "No social presence linked",
                    "why": "Nothing to bring a past guest back with."})
    return out


def main() -> None:
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "outreach/targets/cypress.json")
    targets = json.loads(src.read_text())

    def one(t):
        site = t.get("site")
        a = analyse(site) if site else {"reachable": False, "error": "no website listed"}
        f = findings(t["name"], a)
        return {**t, "analysis": a, "findings": f,
                "high": sum(1 for x in f if x["severity"] == "high")}

    # 86 sites at up to 20s each is 28 minutes serially; these are independent reads.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(one, targets["restaurants"]))
    for r in results:
        print(f"  {r['name'][:34]:36} {'ok  ' if r['analysis'].get('reachable') else 'DOWN'} "
              f"{len(r['findings'])} gaps {'!' * r['high']}")

    results.sort(key=lambda r: (-r["high"], -len(r["findings"])))
    out = src.parent.parent / f"analysis-{src.stem}.json"
    out.write_text(json.dumps({"area": targets.get("area"), "generated": datetime.now().isoformat(timespec="seconds"),
                               "restaurants": results}, indent=1))
    print(f"\n{len(results)} analysed -> {out}")


if __name__ == "__main__":
    main()
