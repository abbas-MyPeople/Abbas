"""
growth_engine.run — the entry point the GitHub Actions cron calls (ported from seo_engine.run).

  python -m growth_engine.run --mode sense      # MEASURE: read GA4 → deterministic findings
  python -m growth_engine.run --mode watch      # read-only live-site guard (proof bar / platform / JSON-LD)
  python -m growth_engine.run --mode propose     # compose the daily brief (prints; no send)
  python -m growth_engine.run --mode send        # send the brief (dry-runs without the WK_ENGINE_* secret)
  python -m growth_engine.run --mode read        # read owner reply → parse approve/reject/instructions
  python -m growth_engine.run --mode execute      # apply approved/interpreted edits + commit to main (--dry default)
  python -m growth_engine.run --mode experiments  # A/B lifecycle: measure running experiments → decide → promote/revert (--dry default)

Kill switch: ENGINE_DISABLED=1 → every mode no-ops. Orchestration stays tiny; logic lives in the modules.
"""
from __future__ import annotations
import argparse, os, sys


def _disabled() -> bool:
    return os.environ.get("ENGINE_DISABLED") == "1"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AZ Restaurant Partners growth engine")
    ap.add_argument("--mode", choices=["sense", "watch", "propose", "send", "read", "execute", "experiments", "aivis"],
                    default="watch")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--dry", action="store_true", default=True, help="execute: plan/diff only (default)")
    ap.add_argument("--apply", dest="dry", action="store_false", help="execute: really write + commit")
    ap.add_argument("--force", action="store_true", help="aivis: ignore the weekly cadence gate")
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
        from .sensors import ga4_traffic, demand
        ga4_traffic.sense(verbose=v)
        try:
            demand.sense(verbose=v)          # free Google-Autocomplete demand signals (best-effort)
        except Exception as e:
            if v:
                print(f"demand: skipped ({type(e).__name__})")
        try:
            from .sensors import ai_visibility   # opt-in + weekly + cost-capped; self-no-ops otherwise
            ai_visibility.run(verbose=v)
        except Exception as e:
            if v:
                print(f"ai_visibility: skipped ({type(e).__name__})")
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
        from . import inbox, reply_parse, actioner_llm
        reply = inbox.fetch_reply(verbose=v)
        if not reply:
            return 0
        batch = inbox._latest_batch() or {}
        surfaced = batch.get("surfaced", [])
        num = min(3, int((batch.get("counts") or {}).get("proposals", 0)))
        parsed = reply_parse.parse(reply["text"], num)
        # The deterministic parser only handles replies phrased against the numbered proposals.
        # If the reply is freeform/ambiguous (or matched nothing), read the WHOLE reply with the LLM
        # so we always understand it, capture general directives, and can send a non-empty ack.
        understanding = None
        if parsed.get("ambiguous") or not parsed.get("items"):
            understanding = actioner_llm.understand_reply(reply["text"], surfaced, verbose=v)
            for n, d in (understanding.get("items") or {}).items():
                parsed.setdefault("items", {}).setdefault(n, d)   # don't override an explicit parse
        inbox.record_decisions(reply["batch_id"], parsed, understanding)
        if v:
            decisions = {k: x["decision"] for k, x in parsed["items"].items()}
            print(f"read: decisions = {decisions or 'none clear'}")
            if understanding:
                print(f"  understood: {understanding.get('summary','')}")
                if understanding.get("directives"):
                    print(f"  directives: {understanding['directives']}")
        return 0

    if args.mode == "execute":
        from . import execute
        execute.run(dry=args.dry, verbose=v)
        return 0

    if args.mode == "experiments":
        # A/B lifecycle: measure every running experiment, decide (deterministic z-test), and — on --apply —
        # promote (bake the winner into the page) / revert. run_cycle writes the page + experiments.json;
        # here we make the ONE revertible commit for the changed files (deploys via GitHub Pages).
        from . import experiments, execute
        s = experiments.run_cycle(verbose=v, apply=not args.dry)
        changed = s.get("changed_files") or []
        if not args.dry and changed:
            execute._sh("git", "config", "user.name", "growth-engine[bot]")
            execute._sh("git", "config", "user.email", "growth-engine@users.noreply.github.com")
            for path in changed:
                execute._sh("git", "add", "--", path)
            msg = "growth-engine: experiment " + ", ".join(s.get("commit_tags") or ["update"])
            c = execute._sh("git", "commit", "-m", msg)
            if c.returncode == 0:
                pu = execute._sh("git", "push", "origin", "HEAD:main")
                if v:
                    print(f"experiments: committed + {'pushed' if pu.returncode == 0 else 'push FAILED'} — {msg}")
            elif v:
                print(f"experiments: commit failed: {(c.stderr or c.stdout).strip()[:160]}")
        elif args.dry and changed and v:
            print(f"experiments: [dry-run] would commit {changed}")
        return 0

    if args.mode == "aivis":
        from .sensors import ai_visibility   # opt-in AI-recommendation rank tracker (AI_VISIBILITY_ENABLED=1)
        ai_visibility.run(verbose=v, force=args.force)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
