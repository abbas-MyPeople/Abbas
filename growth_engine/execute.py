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
import os, subprocess, difflib, hashlib, json
from . import model, notify, actioner_llm, experiments
from .executors import EXECUTORS, apply_llm_plan, is_allowed_path, validate_edit, read_page, REPO, ScopeError, ValidationError

EXECUTED = model.STATE / "executed.jsonl"    # fingerprints of decisions already actioned (idempotency)


def _latest(path):
    rows = model.load(path)
    return rows[-1] if rows else None


def _decision_fp(dec) -> str:
    """Stable fingerprint of an owner decision — so a frequent schedule never re-applies or re-emails it."""
    payload = json.dumps({"b": dec.get("batch_id"), "g": dec.get("global"), "i": dec.get("items")}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def _already_executed(fp) -> bool:
    return any(r.get("fp") == fp for r in model.load(EXECUTED))


def _record_executed(fp, batch_id):
    EXECUTED.parent.mkdir(parents=True, exist_ok=True)
    with EXECUTED.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": model.now(), "fp": fp, "batch_id": batch_id}, sort_keys=True) + "\n")


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

        # ── A/B EXPERIMENTS: an experiment-type finding LAUNCHES an A/B test, not a hard edit (spec §4).
        # Approve/instruct route here first. An "instruct" carries the owner's angle → variant B is concrete,
        # so we queue an experiment_start plan (run() calls experiments.start on --apply). A bare "approve"
        # has no angle yet, so we DON'T launch a placeholder variant onto the live site — we ask for the copy.
        # TODO(integration): to auto-draft B from a freeform angle, run it through actioner_llm first; today
        # the instruction text is used verbatim as B's value (owner supplies exact copy).
        if s["rule_id"] in experiments.EXPERIMENT_RULES and decision in ("approve", "instruct"):
            angle = (d.get("instruction") or "").strip() if decision == "instruct" else ""
            draft = experiments.propose_from_finding(finding)
            if not draft:
                skipped.append(f"item {n} ({s['rule_id']}): not testable (selector missing / element overlap) — no experiment")
                continue
            if angle:
                draft["variants"]["B"]["value"] = angle
                plans.append({"kind": "experiment_start", "draft": draft,
                              "summary": f"start A/B experiment {draft['id']} on {draft['page']} · {draft['anchor']}",
                              "files": {}, "local_drafts": {}})
            else:
                sect = (finding.get("target") or {}).get("section", "hero")
                clarifications.append(f"Experiment {draft['id']} ({draft['anchor']}) is approved and ready. "
                                      f"Reply with the exact new {sect} copy (the audience/angle) and I'll launch the A/B test.")
            continue

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

    dec = _latest(model.STATE / "decisions.jsonl")
    if not dec:
        if verbose:
            print("execute: no owner decision yet — nothing to do.")
        return {"batch_id": None, "plans": [], "committed": []}
    dfp = _decision_fp(dec)   # decision fingerprint (NOT the drafts-loop `fp` below — keep distinct)
    if not dry and _already_executed(dfp):
        if verbose:
            print(f"execute: decision {dfp[:8]} already actioned — no-op (idempotent; safe to run often).")
        return {"batch_id": dec.get("batch_id"), "plans": [], "committed": [], "idempotent_skip": True}

    res = plan_from_decisions(verbose=verbose)
    plans = res["plans"]
    committed = []

    if verbose:
        print(f"execute · batch {res['batch_id']} · {len(plans)} edit-plan(s) · "
              f"{len(res['clarifications'])} clarification(s)")
        for s in res["skipped"]:
            print(f"  (skip) {s}")

    # ── read-receipt: reply to the owner with what we understood + what we'll do (once per decision) ──
    if not dry:
        batch = _latest(model.STATE / "batches.jsonl") or {}
        surf = {s["n"]: s for s in batch.get("surfaced", [])}
        understood, next_steps = [], []
        if dec.get("global"):
            understood.append(f"Overall: {dec['global']}.")
        for n_str, d in (dec.get("items") or {}).items():
            n = int(n_str); h = (surf.get(n) or {}).get("headline", f"item {n}"); deci = d.get("decision")
            if deci == "approve":
                understood.append(f"#{n} “{h}” — approved.")
            elif deci == "reject":
                understood.append(f"#{n} “{h}” — rejected (leaving as-is).")
            elif deci == "instruct":
                understood.append(f"#{n} “{h}” — your change: “{(d.get('instruction') or '').strip()[:140]}”.")
            else:
                understood.append(f"#{n} “{h}” — unclear, rolling over.")
        for p in plans:
            next_steps.append((f"Launch an A/B test: {p['summary']}" if p.get("kind") == "experiment_start"
                               else f"Apply: {p.get('summary','a change')}") + ".")
        for q in res["clarifications"]:
            next_steps.append(f"Ask you to clarify: {q[:140]}")
        if not plans and not res["clarifications"]:
            next_steps.append("Nothing to ship from this reply — recorded your decisions.")
        notify.send_ack(res["batch_id"], understood, next_steps, verbose=verbose)

    # ── render/apply each plan ──
    for p in plans:
        # A/B experiment start: owner-gated launch. run_cycle later measures/decides. ONE commit of
        # experiments.json (repo root) deploys the live split via GitHub Pages.
        if p.get("kind") == "experiment_start":
            draft = p["draft"]
            if verbose:
                print(f"  • {p['summary']}")
            if dry:
                if verbose:
                    print(f"      ↳ (dry-run) would launch experiment {draft['id']} — "
                          f"B[{draft['variants']['B'].get('selector')}] = {str(draft['variants']['B'].get('value',''))[:60]!r}")
                continue
            try:
                exp = experiments.start(draft)
            except (ScopeError, ValidationError) as e:
                print(f"      ✗ experiment start REJECTED: {e}")
                continue
            _sh("git", "config", "user.name", "growth-engine[bot]")
            _sh("git", "config", "user.email", "growth-engine@users.noreply.github.com")
            _sh("git", "add", "--", "experiments.json")
            msg = f"growth-engine: start A/B {exp['id']} (batch {res['batch_id']})"
            c = _sh("git", "commit", "-m", msg)
            if c.returncode == 0:
                committed.append("experiments.json")
                model.log_action("experiment_start", f"Started A/B test {exp['id']}", batch_id=res["batch_id"],
                                 target={"page_file": draft.get("page"), "section": draft.get("anchor")}, status="running")
                if verbose:
                    print(f"      ✓ committed: {msg}")
            else:
                print(f"      ✗ commit failed: {(c.stderr or c.stdout).strip()[:160]}")
            continue

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
                model.log_action("edit", p["summary"], batch_id=res["batch_id"],
                                 target={"page_file": path}, status="shipped")
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
    else:
        _record_executed(dfp, res.get("batch_id"))   # mark done → frequent re-runs are safe no-ops
    res["committed"] = committed
    return res


if __name__ == "__main__":
    run(dry=True)
