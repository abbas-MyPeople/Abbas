"""
growth_engine.checks.site — the AZ live-site guard (ported from seo_engine.checks.entity/schema).

Fetches the LIVE azrestaurantpartners.com homepage and asserts the shipped invariants still hold:
the proof-bar stat numbers, the platform section, the canonical link, and that every
<script type="application/ld+json"> block parses. A regressed shipped-change → a critical finding.

Pure stdlib (urllib + json + re): ZERO dependencies, ZERO secrets, read-only.
"""
from __future__ import annotations
import json, re, urllib.request

HOME = "https://azrestaurantpartners.com/"
UA = "az-growth-engine/0.1 (+https://azrestaurantpartners.com; monitoring)"
_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)

# The canonical invariants the live home page must reflect (grounded in the live page 2026-07-06).
CANONICAL_FRAG = 'rel="canonical"'
PLATFORM_MARKER = 'class="section platform"'          # the platform section
PROOF_MARKER = 'class="section proof"'                # the proof bar
PROOF_STATS = ["~400 → 872", "3 tablets → 1 POS", "Up to 50%", "Found by AI"]

# Which guards, if they fail, mean a deliberately-shipped thing regressed (→ alert).
_CRITICAL = {"site_reachable", "jsonld_valid", "canonical_present",
             "platform_section", "proof_bar", "proof_stats"}


def fetch(url: str = HOME, timeout: int = 20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read().decode("utf-8", "replace")
    except Exception as e:                    # the guard must never crash the run
        return 0, f"{type(e).__name__}: {e}"


def _ld_invalid(html: str) -> tuple[int, int]:
    """Return (n_blocks, n_invalid) for the JSON-LD on the page."""
    blocks = _LD_RE.findall(html)
    invalid = 0
    for raw in blocks:
        try:
            json.loads(raw)
        except json.JSONDecodeError:
            invalid += 1
    return len(blocks), invalid


def run(url: str = HOME) -> dict:
    status, html = fetch(url)
    checks: list[dict] = []

    def add(metric, ok, value, note=""):
        checks.append({"metric": metric, "ok": bool(ok), "value": value, "note": note})

    add("site_reachable", status == 200, status, "" if status == 200 else html[:120])
    if status != 200:
        return {"url": url, "status": status, "checks": checks, "html_len": 0}

    n_ld, n_invalid = _ld_invalid(html)
    add("jsonld_present", n_ld > 0, n_ld)
    add("jsonld_valid", n_invalid == 0, n_invalid, f"{n_invalid} invalid block(s)" if n_invalid else "")

    add("canonical_present", CANONICAL_FRAG in html, CANONICAL_FRAG)
    add("platform_section", PLATFORM_MARKER in html, PLATFORM_MARKER)
    add("proof_bar", PROOF_MARKER in html, PROOF_MARKER)

    present = [s for s in PROOF_STATS if s in html]
    add("proof_stats", len(present) == len(PROOF_STATS), f"{len(present)}/{len(PROOF_STATS)}",
        "a proof-bar stat number changed or vanished" if len(present) != len(PROOF_STATS) else "")

    return {"url": url, "status": status, "checks": checks, "html_len": len(html), "critical": _CRITICAL}


if __name__ == "__main__":
    res = run()
    print(f"SITE · {res['url']} · HTTP {res['status']}")
    for c in res["checks"]:
        print(f"  {'OK ' if c['ok'] else 'XX '}{c['metric']:20} = {c['value']!r}  {c['note']}")
