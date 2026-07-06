"""
growth_engine.execute — apply APPROVED / interpreted items, then commit to `main` (ported + retargeted).

GitHub Pages serves the AZ repo root on `main`, so a commit to main deploys. Each applied change is ONE
revertible commit: `growth-engine: <summary> (batch <id>)`. Freeform "instruct" items are interpreted by
the LLM actioner into a bounded edit; ambiguous/out-of-scope ones queue a clarifying email instead of
guessing. `--dry` (DEFAULT) logs the exact unified diff and writes/commits NOTHING.

GUARDRAILS enforced here (defense in depth):
  • ENGINE_DISABLED=1 → no-op.
  • Only 'approve'/'instruct' items act; unmentioned items roll over.
  • SCOPE FENCE + validate_edit re-checked on every file right before commit; a failure → reject + log.
  • One commit per change (revert = git revert that commit).
"""
from __future__ import annotations
import os, subprocess, difflib
from . import model, notify, actioner_llm
from .executors import EXECUTORS, apply_llm_plan, is_allowed_path, validate_edit, read_page, REPO, ScopeError, ValidationError


def _latest(path):
    rows = model.load(path)
    return rows[-1] if rows else None


def _findings_by_key():
    out = {}
    for f in model.load_findings():
        out[f.get("dedupe_key") or f"{f.get('rule_id')}:{f.get('subject')}"] = f
    return out


def plan_from_decisions(verbose: bool = True) -> dict:
    """Return {batch_id, plans:[...], clarifications:[...], skipped:[...]}."""
    dec = _latest(model.STATE / "decisions.jsonl")
    batch = _latest(model.STATE / "batches.jsonl")
    if not dec or not batch:
        return {"batch_id": None, "plans": [], "clarifications": [], "skipped": ["no decisions/batch yet"]}

    surfaced = {s["n"]: s for s in batch.get("surfaced", [])}
    fbk = _findings_by_key()
    budget = actioner_llm.Budget()
    plans, clarifications, skipped = [], [], []

    for n_str, d in (dec.get("items") or {}).items():
        n = int(n_str)
        s = surfaced.get(n)
        if not s:
            skipped.append(f"item {n}: not in the sent batch")
            continue
        decision = d.get("decision")
        finding = fbk.get(f"{s['rule_id']}:{s['subject']}", s)
        finding = {**finding, "target": finding.get("target") or s.get("target") or {}, "_n": n}

        if decision == "approve":
            ex = EXECUTORS.get(s["rule_id"])
            if not ex:
                skipped.append(f"item {n} ({s['rule_id']}): no deterministic executor — needs a freeform instruction")
                continue
            try:
                p = ex(finding)
            except Exception as e:
                skipped.append(f"item {n} ({s['rule_id']}): executor error {type(e).__name__}: {e}")
                continue
            if p:
                plans.append(p)

        elif decision == "instruct":
            instruction = d.get("instruction") or ""
            res = actioner_llm.interpret(instruction, {**s, "target": finding.get("target")}, budget, verbose=verbose)
            if res["kind"] == "edit":
                try:
                    plans.append(apply_llm_plan(res["plan"]))
                except (ScopeError, ValidationError) as e:
                    skipped.append(f"item {n}: LLM edit REJECTED ({type(e).__name__}: {e})")
                    clarifications.append(f"For item {n}, I couldn't safely apply that: {e}. "
                                          f"Please quote the exact current text + the new text.")
            elif res["kind"] == "clarify":
                clarifications.append(res["question"])
            else:
                skipped.append(f"item {n}: {res.get('reason','skipped')}")

        elif decision == "reject":
            skipped.append(f"item {n}: rejected by owner")
        else:
            skipped.append(f"item {n}: no clear decision — rolled over")

    return {"batch_id": dec.get("batch_id"), "plans": plans,
            "clarifications": clarifications, "skipped": skipped}


def _sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def _diff(path, old, new):
    return "".join(difflib.unified_diff((old or "").splitlines(keepends=True),
                                        new.splitlines(keepends=True),
                                        fromfile=f"a/{path}", tofile=f"b/{path}"))


def run(dry: bool = True, verbose: bool = True) -> dict:
    if os.environ.get("ENGINE_DISABLED") == "1":
        if verbose:
            print("execute: ENGINE_DISABLED=1 — no-op.")
        return {"disabled": True}

    res = plan_from_decisions(verbose=verbose)
    plans = res["plans"]
    committed = []

    if verbose:
        print(f"execute · batch {res['batch_id']} · {len(plans)} edit-plan(s) · "
              f"{len(res['clarifications'])} clarification(s)")
        for s in res["skipped"]:
            print(f"  (skip) {s}")

    # ── render/apply each plan ──
    for p in plans:
        files = p.get("files", {})
        drafts = p.get("local_drafts", {})
        if verbose:
            print(f"  • {p['summary']}")

        # engine-local drafts: written on real runs, NEVER git-added / committed.
        if not dry:
            for dpath, content in drafts.items():
                fp = REPO / dpath if not os.path.isabs(dpath) else __import__("pathlib").Path(dpath)
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text(content, encoding="utf-8")
        elif drafts and verbose:
            for dpath in drafts:
                print(f"      ↳ (engine-local draft, not committed) {dpath}")

        # marketing-page edits: fence + validate, then ONE commit each.
        for path, new in files.items():
            old = read_page(path) or ""
            if not is_allowed_path(path):
                print(f"      ✗ REFUSED (scope fence): {path}")
                continue
            ok, why = validate_edit(path, old, new)
            if not ok:
                print(f"      ✗ REJECTED (validation): {path} — {why}")
                continue
            if verbose:
                print(f"      ↳ {path}")
            if dry:
                print(_diff(path, old, new) or "      (no textual diff)")
                continue
            (REPO / path).write_text(new, encoding="utf-8")
            _sh("git", "config", "user.name", "growth-engine[bot]")
            _sh("git", "config", "user.email", "growth-engine@users.noreply.github.com")
            _sh("git", "add", "--", path)
            msg = f"growth-engine: {p['summary']} (batch {res['batch_id']})"
            c = _sh("git", "commit", "-m", msg)
            if c.returncode == 0:
                committed.append(path)
                if verbose:
                    print(f"      ✓ committed: {msg}")
            else:
                print(f"      ✗ commit failed: {(c.stderr or c.stdout).strip()[:160]}")

    # ── push committed changes to main (deploys via GitHub Pages) ──
    if not dry and committed:
        pu = _sh("git", "push", "origin", "HEAD:main")
        if verbose:
            print("execute: pushed to main." if pu.returncode == 0
                  else f"execute: push failed: {(pu.stderr or pu.stdout).strip()[:160]}")

    # ── clarifications: ask the owner rather than guess ──
    for q in res["clarifications"]:
        if dry:
            if verbose:
                print(f"  [dry-run] would ask owner: {q}")
        else:
            notify.queue_clarification(res["batch_id"], q, verbose=verbose)

    if dry and verbose:
        print("  [dry-run] nothing written, nothing committed.")
    res["committed"] = committed
    return res


if __name__ == "__main__":
    run(dry=True)
