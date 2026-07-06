"""
growth_engine.run — the entry point the GitHub Actions cron calls (ported from seo_engine.run).

  python -m growth_engine.run --mode sense      # MEASURE: read GA4 → deterministic findings
  python -m growth_engine.run --mode watch      # read-only live-site guard (proof bar / platform / JSON-LD)
  python -m growth_engine.run --mode propose     # compose the daily brief (prints; no send)
  python -m growth_engine.run --mode send        # send the brief (dry-runs without the WK_ENGINE_* secret)
  python -m growth_engine.run --mode read        # read owner reply → parse approve/reject/instructions
  python -m growth_engine.run --mode execute      # apply approved/interpreted edits + commit to main (--dry default)

Kill switch: ENGINE_DISABLED=1 → every mode no-ops. Orchestration stays tiny; logic lives in the modules.
"""
from __future__ import annotations
import argparse, os, sys


def _disabled() -> bool:
    return os.environ.get("ENGINE_DISABLED") == "1"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AZ Restaurant Partners growth engine")
    ap.add_argument("--mode", choices=["sense", "watch", "propose", "send", "read", "execute"],
                    default="watch")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--dry", action="store_true", default=True, help="execute: plan/diff only (default)")
    ap.add_argument("--apply", dest="dry", action="store_false", help="execute: really write + commit")
    args = ap.parse_args(argv)
    v = not args.quiet

    if _disabled():
        if v:
            print(f"[{args.mode}] ENGINE_DISABLED=1 — no-op.")
        return 0

    if args.mode == "watch":
        from . import watch
        s = watch.run_watch(verbose=v)
        return 1 if s["critical_fails"] else 0

    if args.mode == "sense":
        from .sensors import ga4_traffic
        ga4_traffic.sense(verbose=v)
        return 0

    if args.mode == "propose":
        from . import compose
        e = compose.from_state()
        print("SUBJECT:", e["subject"])
        print("=" * 64)
        print(e["body"])
        return 0

    if args.mode == "send":
        from . import notify
        notify.send_daily(verbose=v)
        return 0

    if args.mode == "read":
        from . import inbox, reply_parse
        reply = inbox.fetch_reply(verbose=v)
        if not reply:
            return 0
        batch = inbox._latest_batch() or {}
        num = min(3, int((batch.get("counts") or {}).get("proposals", 0)))
        parsed = reply_parse.parse(reply["text"], num)
        inbox.record_decisions(reply["batch_id"], parsed)
        if v:
            decisions = {k: x["decision"] for k, x in parsed["items"].items()}
            print(f"read: decisions = {decisions or 'none clear'}")
            if parsed["ambiguous"]:
                print(f"  ambiguous (→ LLM actioner / re-ask at execute): {parsed['ambiguous']}")
        return 0

    if args.mode == "execute":
        from . import execute
        execute.run(dry=args.dry, verbose=v)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
