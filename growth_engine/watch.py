"""
growth_engine.watch — the read-only heartbeat (ported from seo_engine.watch).

Runs the AZ live-site guard (checks/site.py), records every check as a `signal`, and raises a
`finding(severity=alert)` for any CRITICAL guard that fails (proof-bar numbers changed, platform
section vanished, canonical dropped, JSON-LD broke). $0, no secrets, no outward action.
"""
from __future__ import annotations
import sys
from . import model
from .checks import site


def run_watch(verbose: bool = True) -> dict:
    res = site.run()
    checks = res["checks"]
    critical = res.get("critical", set())
    failed = []

    for c in checks:
        model.signal(source="site", metric=c["metric"], subject="home",
                     value=1 if c["ok"] else 0, unit="bool", period="point",
                     meta={"raw": c["value"], "note": c["note"]})
        if not c["ok"]:
            failed.append(c)

    critical_fails = [c for c in failed if c["metric"] in critical]
    for c in critical_fails:
        model.finding(
            rule_id="G0_site_guard", subject=f"home:{c['metric']}", severity="alert", read="bad",
            headline=f"Site guard failed: {c['metric']}",
            detail=(c["note"] or f"{c['metric']} is no longer true on the live home page "
                    f"(value={c['value']!r}). A shipped change may have regressed."))

    ok_n = sum(1 for c in checks if c["ok"])
    summary = {"total": len(checks), "ok": ok_n, "failed": len(failed),
               "critical_fails": [c["metric"] for c in critical_fails]}

    if verbose:
        print(f"WATCH · {res['url']} · HTTP {res['status']} · {ok_n}/{len(checks)} checks OK")
        for c in checks:
            crit = " (CRITICAL)" if (not c["ok"] and c["metric"] in critical) else ""
            print(f"  {'OK ' if c['ok'] else 'XX '}{c['metric']:20} = {c['value']!r}{crit}  {c['note']}")
        print("\n" + ("All critical guards pass — shipped wins holding."
                      if not critical_fails else
                      f"!! {len(critical_fails)} CRITICAL regression(s) — findings written."))
    return summary


if __name__ == "__main__":
    s = run_watch()
    sys.exit(1 if s["critical_fails"] else 0)
