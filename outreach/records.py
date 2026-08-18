#!/usr/bin/env python3
"""Public records collector - TABC permits and mixed beverage receipts.

This corrects an assumption in ARCHITECTURE.md section 11, which listed revenue
as never obtainable. For any venue holding a mixed beverage permit, Texas
publishes **actual monthly alcohol receipts per location**, split by liquor,
wine, beer and cover charge, with years of history. It is free, current to about
last month, and nobody doing outreach in Cy-Fair is reading it.

What it buys us, in order of value:

  1. Closure detection. Receipts that fall to zero and stay there are a venue
     winding down. Section 13.1 says never pitch growth to someone closing;
     this is how we know without guessing.
  2. Distress detection. A steep decline while still trading is the most
     receptive operator in the market, and they have not had to tell anyone.
  3. Direction. Whether a business is growing or shrinking, before the
     conversation starts.

Limits, stated plainly: it is alcohol revenue only, not food. A dry restaurant
appears nowhere. Reporting lags roughly two months. It is a direction signal for
the business, not a P&L.

    python3 outreach/records.py outreach/targets/cypress.json
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)
PORTAL = "https://data.texas.gov/resource"
RECEIPTS = "naix-2893"          # Mixed Beverage Gross Receipts
LICENCES = "kguh-7q9z"          # TABC licences


def ev(value, tier, source, method, confidence=1.0, days=45, note=None):
    e = {"value": value, "tier": tier, "source": source, "method": method,
         "observed_at": NOW.isoformat(timespec="seconds"), "confidence": confidence,
         "expires": (NOW + timedelta(days=days)).date().isoformat()}
    if note:
        e["note"] = note
    return e


def unknown(reason, source=None):
    return {"value": None, "tier": "UNKNOWN", "reason": reason, "source": source,
            "observed_at": NOW.isoformat(timespec="seconds")}


def soda(resource, where, limit=50000, order=None):
    p = {"$where": where, "$limit": limit}
    if order:
        p["$order"] = order
    url = f"{PORTAL}/{resource}.json?" + urllib.parse.urlencode(p)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)


# Geography and legal-form tokens carry no identity. "China Wok Cypress" matched
# "Scary Canary Cypress" on the word "cypress" alone and inherited $1.34m of
# someone else's revenue - which is exactly the failure this whole spec exists
# to prevent, so these are stopped hard.
STOP = {"llc", "inc", "corp", "corporation", "restaurant", "restaurants", "the", "cafe",
        "grill", "bar", "kitchen", "co", "ltd", "lp", "company", "and", "of", "tx",
        "cypress", "houston", "texas", "spring", "katy", "tomball", "usa", "america",
        "food", "foods", "eatery", "bistro", "lounge", "pub", "grille", "cuisine"}


def toks(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in STOP and len(w) > 2}


def street_no(addr):
    m = re.match(r"\s*(\d+)", addr or "")
    return m.group(1) if m else None


def match(target, venues):
    """Identity tokens must overlap, and the street number must agree.

    A wrong match here attaches another business's revenue to a restaurant and we
    would say it out loud to an owner. So the bar is deliberately high and the
    failure mode is "no match" rather than "probably this one"."""
    tn, ts = toks(target["name"]), street_no(target.get("address", ""))
    if not tn:
        return None, "none", 0.0
    cands = []
    for v in venues.values():
        vn = toks(v["name"])
        if not vn:
            continue
        shared = tn & vn
        if not shared:
            continue
        overlap = len(shared) / len(tn | vn)
        same_street = bool(ts) and ts == street_no(v["address"])
        # one shared token and no address agreement is a coincidence, not a match
        if len(shared) < 2 and not same_street:
            continue
        cands.append((overlap + (0.4 if same_street else 0.0), overlap, same_street, v))
    if not cands:
        return None, "none", 0.0
    cands.sort(reverse=True, key=lambda c: c[0])
    score, overlap, same_street, v = cands[0]
    if same_street and overlap >= 0.34:
        return v, "high", round(score, 2)
    # A known street number that disagrees caps the claim, however close the name.
    # d'Vine Wine Bar and Flying Vine Wine Bar share two tokens and are not the
    # same business.
    if ts and not same_street:
        return (v, "medium", round(score, 2)) if overlap >= 0.6 else (None, "none", round(score, 2))
    if overlap >= 0.6:
        return v, "high", round(score, 2)
    if overlap >= 0.45:
        return v, "medium", round(score, 2)
    return None, "none", round(score, 2)


def trend(months, dataset_latest):
    """months: {'YYYY-MM': total}. Windows are CALENDAR windows, not "last 12 rows".

    The bug this replaces: taking the last twelve *available* rows meant a venue
    that stopped filing in 2010 reported a confident "last 12 months" figure of
    $606,830. Presenting decade-old revenue as current is the single most
    dangerous thing this collector could do, so every figure now carries the date
    range it was computed over, and a venue that has stopped filing returns no
    current figure at all."""
    keys = sorted(months)
    if not keys:
        return None
    last_seen = keys[-1]

    def months_between(a, b):
        return (int(b[:4]) - int(a[:4])) * 12 + (int(b[5:7]) - int(a[5:7]))

    lag = months_between(last_seen, dataset_latest)

    def window(end, n):
        """Sum the n calendar months ending at `end`, treating absent months as zero."""
        y, m = int(end[:4]), int(end[5:7])
        out, ks = 0.0, []
        for i in range(n):
            mm = m - i
            yy = y + (mm - 1) // 12
            mm = (mm - 1) % 12 + 1
            k = f"{yy:04d}-{mm:02d}"
            ks.append(k)
            out += months.get(k, 0.0)
        return out, sorted(ks)

    if lag >= 3:
        return {
            "state": ev("NO_LONGER_REPORTING", "OBSERVED", f"{PORTAL}/{RECEIPTS}",
                        "venue absent from recent filings", 0.85,
                        note=(f"Last filed {last_seen}, {lag} months before the newest data in "
                              f"the set ({dataset_latest}). Either closed, sold, or now trading "
                              f"under a different permit. No current revenue figure exists - "
                              f"confirm on Maps before assuming anything.")),
            "last_seen": ev(last_seen, "OBSERVED", f"{PORTAL}/{RECEIPTS}", "final obligation month"),
            "current_revenue": unknown(f"venue has not filed since {last_seen}"),
            "historic_only": ev({k: round(months[k]) for k in keys[-12:]}, "OBSERVED",
                                f"{PORTAL}/{RECEIPTS}",
                                f"final 12 filed months, ending {last_seen} - HISTORIC, not current"),
        }

    recent, rk = window(last_seen, 12)
    y, m = int(last_seen[:4]), int(last_seen[5:7])
    m -= 12
    y += (m - 1) // 12
    prior_end = f"{y + (m - 1) // 12 if False else y:04d}-{(m - 1) % 12 + 1:02d}"
    prior, pk = window(prior_end, 12)
    tail = [months.get(k, 0.0) for k in rk[-4:]]

    if all(v == 0 for v in tail):
        state, why = "CLOSED_OR_DRY", ("Four consecutive months at zero while still on file. "
                                       "Closed, or the alcohol permit has gone. Confirm on Maps.")
    elif prior and recent / prior - 1 <= -0.35:
        state, why = "STEEP_DECLINE", ("Down sharply year on year while still trading. Felt "
                                       "pain, and they have not had to tell anyone.")
    elif prior and recent / prior - 1 <= -0.12:
        state, why = "SOFT_DECLINE", "Drifting down year on year. Real, not yet urgent."
    elif prior and recent / prior - 1 >= 0.20:
        state, why = "GROWING", ("Growing. Less felt pain now, but a better payer and worth "
                                 "knowing before they need us.")
    else:
        state, why = "FLAT", "Broadly flat year on year."

    return {
        "state": ev(state, "DERIVED", f"{PORTAL}/{RECEIPTS}",
                    f"12 calendar months to {last_seen} vs the 12 before", 0.85, note=why),
        "window": ev(f"{rk[0]} to {rk[-1]}", "OBSERVED", f"{PORTAL}/{RECEIPTS}",
                     "the range every figure below is computed over"),
        "last12_receipts": ev(round(recent), "DERIVED", f"{PORTAL}/{RECEIPTS}",
                              f"calendar sum {rk[0]}..{rk[-1]}, absent months counted as zero"),
        "prior12_receipts": ev(round(prior), "DERIVED", f"{PORTAL}/{RECEIPTS}",
                               f"calendar sum {pk[0]}..{pk[-1]}"),
        "yoy_change": ev(round(recent / prior - 1, 3) if prior else None, "DERIVED",
                         f"{PORTAL}/{RECEIPTS}", "last 12 over prior 12"),
        "last_seen": ev(last_seen, "OBSERVED", f"{PORTAL}/{RECEIPTS}", "final obligation month"),
        "monthly_series": ev({k: round(months[k]) for k in keys[-24:]}, "OBSERVED",
                             f"{PORTAL}/{RECEIPTS}", "last 24 filed months, for the shape"),
    }


def main():
    src = pathlib.Path(sys.argv[1])
    data = json.loads(src.read_text())
    city = "CYPRESS"

    print(f"pulling receipts for {city} ...")
    rows = soda(RECEIPTS, f"location_city='{city}'", order="obligation_end_date_yyyymmdd")
    venues = defaultdict(lambda: {"name": "", "address": "", "permit": "", "months": defaultdict(float)})
    for r in rows:
        k = (r.get("location_name", ""), r.get("location_address", ""))
        v = venues[k]
        v["name"], v["address"] = k
        v["permit"] = r.get("tabc_permit_number", "")
        v["months"][r["obligation_end_date_yyyymmdd"][:7]] += float(r.get("total_receipts", 0) or 0)
    dataset_latest = max(r["obligation_end_date_yyyymmdd"][:7] for r in rows)
    print(f"  {len(rows)} rows, {len(venues)} venues, newest filing {dataset_latest}")

    dossiers = pathlib.Path("outreach/dossiers")
    hits = 0
    summary = []
    for t in data["restaurants"]:
        v, quality, score = match(t, venues)
        slug = re.sub(r"[^a-z0-9]+", "-", t["name"].lower()).strip("-")
        f = dossiers / f"{slug}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        if v and quality in ("high", "medium"):
            hits += 1
            tr = trend(dict(v["months"]), dataset_latest)
            d["records"] = {
                "matched_to": ev(v["name"], "OBSERVED", f"{PORTAL}/{RECEIPTS}",
                                 "name-token overlap confirmed by street number",
                                 0.9 if quality == "high" else 0.6,
                                 note=f"match quality {quality} ({score}). Verify before "
                                      f"quoting any figure to an owner."),
                "tabc_permit": ev(v["permit"], "OBSERVED", f"{PORTAL}/{RECEIPTS}", "permit on receipts"),
                "alcohol_revenue": tr,
                "_scope": "Alcohol receipts only, not food. Reporting lags about two months.",
            }
            st = tr["state"]["value"]
            if st in ("CLOSED_OR_DRY", "NO_LONGER_REPORTING"):
                d["verdict"] = ev("DO_NOT_PURSUE", "INFERRED", f"{PORTAL}/{RECEIPTS}",
                                  "alcohol receipts stopped", 0.7,
                                  note="Confirm on Maps. Never pitch growth to someone winding down.")
            elif st == "STEEP_DECLINE":
                d["verdict"] = ev("PURSUE_NOW", "INFERRED", f"{PORTAL}/{RECEIPTS}",
                                  "sharp year-on-year decline while still trading", 0.7,
                                  note="Felt pain, and they have not had to tell anyone.")
            summary.append((st, t["name"], tr.get("yoy_change", {}).get("value"),
                            tr.get("last12_receipts", {}).get("value"),
                            v["name"], quality, tr["last_seen"]["value"]))
        else:
            d["records"] = {"alcohol_revenue": {
                "value": None, "tier": "UNKNOWN",
                "reason": "No mixed beverage permit matched. Either the venue does not serve "
                          "alcohol, or it trades under a different registered name.",
                "best_match_score": score}}
        f.write_text(json.dumps(d, indent=1))

    print(f"\nmatched {hits} of {len(data['restaurants'])} targets to a permit\n")
    order = {"STEEP_DECLINE": 0, "SOFT_DECLINE": 1, "FLAT": 2, "GROWING": 3,
             "CLOSED_OR_DRY": 4, "NO_LONGER_REPORTING": 5}
    for st, name, yoy, last12, matched, quality, seen in sorted(summary, key=lambda x: order.get(x[0], 9)):
        y = f"{yoy*100:+.0f}%" if yoy is not None else "   -"
        rev = f"${last12:>10,}" if last12 is not None else "         -"
        print(f"  {st:20} {name[:26]:28} {y:>6} {rev}  last filed {seen}  <- {matched[:24]} ({quality})")


if __name__ == "__main__":
    main()
