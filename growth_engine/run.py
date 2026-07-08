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
    ap.add_argument("--mode", choices=["sense", "watch", "propose", "send", "read", "execute", "experiments",
                                       "aivis", "agent", "merge"],
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

    if args.mode == "agent":
        # Build the next QUEUED reply-task on a throwaway branch, open a PR, email the owner the link.
        # Nothing reaches the live site until the owner replies "merge" (--mode merge). One task per run.
        from . import tasks, reply_agent, execute, notify

        def _git(*a):
            return execute._sh("git", *a)

        def _commit_queue(msg):
            _git("add", "--", "command/reply-tasks.json")
            c = _git("commit", "-m", msg)
            if c.returncode == 0:
                _git("push", "origin", "HEAD:main")

        t = tasks.next_queued()
        if not t:
            if v:
                print("agent: no queued reply-tasks.")
            return 0
        tid, branch = t["id"], f"reply/{t['id']}"
        if args.dry:      # true no-op preview — mutate/commit nothing
            if v:
                print(f"agent: [dry-run] would build task {tid}: {t['directive'][:80]}")
            return 0
        _git("config", "user.name", "growth-engine[bot]")
        _git("config", "user.email", "growth-engine@users.noreply.github.com")
        _git("fetch", "origin", "main")
        # 1) mark building on main + push (durable; prevents double-processing)
        tasks.update(tid, status="building", branch=branch)
        _commit_queue(f"reply-agent: start {tid}")
        # 2) build on a fresh branch off latest main
        _git("checkout", "-B", branch, "origin/main")
        res = reply_agent.build(t["directive"], verbose=v)
        changed = res.get("changed_files") or []
        if not changed:
            _git("checkout", "main"); _git("reset", "--hard", "origin/main")
            tasks.update(tid, status="failed", summary=res.get("summary", "no changes produced"))
            _commit_queue(f"reply-agent: {tid} produced no changes")
            if v:
                print(f"agent: {tid} produced no changes — marked failed.")
            return 0
        for f in changed:
            _git("add", "--", f)
        _git("commit", "-m", f"reply-agent: {t['directive'][:60]} ({tid})")
        _git("push", "-u", "origin", branch)
        # 3) open the PR (gh CLI; GH_TOKEN provided by the workflow)
        pr = execute._sh("gh", "pr", "create", "--base", "main", "--head", branch,
                         "--title", f"[reply-agent] {t['directive'][:60]}",
                         "--body", (f"Auto-built from your email reply — review before it ships.\n\n"
                                    f"**You asked:** {t['directive']}\n\n**What I did:** {res.get('summary','')}\n\n"
                                    f"Reply **\"merge\"** to the engine email to ship this to the live site."))
        pr_url = ""
        if pr.returncode == 0 and pr.stdout:
            pr_url = pr.stdout.strip().splitlines()[-1]
        elif v:
            print(f"agent: gh pr create failed: {(pr.stderr or pr.stdout).strip()[:160]}")
        num = pr_url.rstrip("/").split("/")[-1] if pr_url else ""
        # 4) record pr_open on main + notify the owner
        _git("checkout", "main"); _git("reset", "--hard", "origin/main")
        tasks.update(tid, status="pr_open", pr_url=(pr_url or None),
                     pr_number=(int(num) if num.isdigit() else None), summary=res.get("summary"))
        _commit_queue(f"reply-agent: opened PR for {tid}")
        notify.send_task_done(t, pr_url, res.get("summary", ""), verbose=v)
        if v:
            print(f"agent: built {tid} → {pr_url or '(PR create failed)'}")
        return 0

    if args.mode == "merge":
        # Owner replied "merge" → merge the newest open reply-agent PR (fail-closed on sender via inbox).
        from . import inbox, tasks, execute, notify
        execute._sh("git", "config", "user.name", "growth-engine[bot]")
        execute._sh("git", "config", "user.email", "growth-engine@users.noreply.github.com")
        reply = inbox.fetch_reply(verbose=v)
        if not reply:
            return 0
        low = (reply["text"] or "").lower()
        if not any(w in low for w in ("merge", "ship it", "go live", "publish it", "ship this")):
            if v:
                print("merge: no merge intent in the latest reply.")
            return 0
        prs = tasks.open_prs()
        if not prs:
            if v:
                print("merge: no open reply-agent PRs to merge.")
            return 0
        t = prs[-1]     # newest open PR
        r = execute._sh("gh", "pr", "merge", str(t["pr_number"]), "--squash", "--delete-branch")
        if r.returncode == 0:
            execute._sh("git", "fetch", "origin", "main")
            execute._sh("git", "checkout", "main")
            execute._sh("git", "reset", "--hard", "origin/main")
            tasks.update(t["id"], status="merged")
            execute._sh("git", "add", "--", "command/reply-tasks.json")
            c = execute._sh("git", "commit", "-m", f"reply-agent: merged {t['id']}")
            if c.returncode == 0:
                execute._sh("git", "push", "origin", "HEAD:main")
            notify.send_merged(t, verbose=v)
            if v:
                print(f"merge: merged PR #{t['pr_number']} ({t['id']}).")
        elif v:
            print(f"merge: gh merge failed: {(r.stderr or r.stdout).strip()[:160]}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
