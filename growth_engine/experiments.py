"""
growth_engine.experiments — the ENGINE-SIDE A/B experiment lifecycle (spec: research/ab-testing-engine-spec.md).

The site ships every copy/targeting change as an EXPERIMENT instead of a hard swap: the control (A) stays
live, a variant (B) runs on a slice of traffic, GA4 measures conversion (lead_submit + call_click +
finder_capture) per variant, and the engine keeps only what WINS — a self-improving optimization loop.

Lifecycle (spec §4):
    draft ──(owner approves in the daily brief)──▶ running
    running ──(GA4: enough samples + significant)──▶ shipped   (winner B baked into the page permanently)
    running ──(A wins, or max_days with no winner)──▶ reverted (control kept unchanged)

Division of labour (spec §8 guardrails):
  • PROPOSE (engine)   — `propose_from_finding` turns a lead-rate/copy finding into a DRAFT experiment.
  • START   (OWNER-gated) — `start` writes the experiment into repo-root `experiments.json` after validating
                           scope + selector + non-overlap + concurrency cap. Only runs on owner approval.
  • MEASURE (engine, deterministic) — `measure` reads GA4 per-variant (filtered on the reusable custom
                           dimensions `experiment_id` + `variant`). No LLM.
  • DECIDE  (engine, deterministic + honest stats) — `decide` is a two-proportion z-test with a min-sample
                           floor and a max-days stop. Auto promote/revert WITHOUT re-asking the owner —
                           the experiment was already approved; the DATA is the judge.
  • APPLY   (engine) — `apply_decision` bakes B permanently (validate_edit + scope fence + write) on promote,
                           or keeps control on revert; records `result`; logs the transition.

State/audit: every transition is appended to `state/experiments.jsonl` (git is the audit log). No LLM, no
secrets ever printed. Kill switch: ENGINE_DISABLED=1 → the cycle no-ops.
"""
from __future__ import annotations
import json, math, re, os, datetime
from pathlib import Path

from . import model
from .executors import (REPO, is_allowed_path, read_page, validate_edit,
                        ScopeError, ValidationError)

# repo-root experiments.json — lives next to index.html; the client runner reads the SAME file.
EXPERIMENTS_FILE = REPO / "experiments.json"
EXPERIMENTS_LOG = model.STATE / "experiments.jsonl"          # append-only transition audit

# ── lifecycle constants (spec §2 defaults + §5 decision rule) ───────────────────────────────────
CONV_EVENTS = ["lead_submit", "call_click", "finder_capture"]   # a "conversion" = any of these
MIN_SESSIONS_PER_VARIANT = 200      # no decision before this many sessions PER VARIANT (avoid false wins)
MAX_DAYS = 21                        # hard stop → decide or revert (inconclusive)
CONCURRENCY_CAP = 3                  # at most this many RUNNING experiments at once (spec §6)
SPLIT = 0.5                          # default share of visitors who see B
ALPHA = 0.05                         # significance threshold for the z-test
MIN_ABS_LIFT = 0.005                 # B must beat A by ≥0.5 percentage-points of conversion rate (guard trivial wins)

# rule_ids whose findings the engine turns into EXPERIMENTS rather than hard edits.
EXPERIMENT_RULES = {"G7_lead_rate"}


# ════════════════════════════════════════ store: experiments.json ═══════════════════════════════

def load() -> dict:
    """Read the repo-root experiments.json. Missing/corrupt → an empty, well-formed shell."""
    if not EXPERIMENTS_FILE.exists():
        return {"experiments": []}
    try:
        data = json.loads(EXPERIMENTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"experiments": []}
    if not isinstance(data, dict) or not isinstance(data.get("experiments"), list):
        return {"experiments": []}
    return data


def save(data: dict) -> None:
    """Write experiments.json (pretty, stable) so a diff is human-readable in the commit."""
    EXPERIMENTS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def _today() -> str:
    return datetime.date.today().isoformat()


def _log(event: str, exp: dict, extra: dict | None = None) -> None:
    """Append one lifecycle transition to state/experiments.jsonl (the audit log)."""
    rec = {"ts": model.now(), "event": event, "id": exp.get("id")}
    if extra:
        rec.update(extra)
    model._append(EXPERIMENTS_LOG, rec)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").strip().lower()).strip("-") or "exp"


def _unique_id(base: str, data: dict | None = None) -> str:
    data = data if data is not None else load()
    ids = {e.get("id") for e in data.get("experiments", [])}
    if base not in ids:
        return base
    i = 2
    while f"{base}-{i}" in ids:
        i += 1
    return f"{base}-{i}"


def _days_running(exp: dict) -> int:
    started = exp.get("started")
    if not started:
        return 0
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(started)).days
    except Exception:
        return 0


# ════════════════════════════════════════ selector locating / baking ════════════════════════════
# Static GitHub Pages: to PROMOTE a winner we must find the target element in the raw HTML and replace
# its innerHTML (or an attribute) deterministically — no DOM, no LLM. We locate the element by walking
# the CSS selector left→right (ancestor → … → target), requiring EXACTLY ONE match at every step. Any
# ambiguity (0 or >1) → refuse (safe: the promote simply doesn't happen and the experiment stays running).

def _parse_selector(selector: str) -> list[dict]:
    """A CSS selector → a list of simple parts (descendant combinator / whitespace only)."""
    parts = []
    for raw in (selector or "").split():
        tag, ids, classes = None, [], []
        for tok in re.findall(r"[#.]?[\w-]+", raw):
            if tok.startswith("#"):
                ids.append(tok[1:])
            elif tok.startswith("."):
                classes.append(tok[1:])
            else:
                tag = tok
        parts.append({"tag": tag, "ids": ids, "classes": classes})
    return parts


def _match_open_tags(html: str, simple: dict, lo: int, hi: int) -> list[re.Match]:
    """All opening tags in html[lo:hi] matching one simple selector (tag + required id/classes)."""
    tag = simple["tag"] or r"\w+"
    pat = re.compile(r"<(" + tag + r")\b([^>]*)>", re.I)
    out = []
    for m in pat.finditer(html, lo, hi):
        attrs = m.group(2)
        ok = True
        for _id in simple["ids"]:
            if not re.search(r'\bid\s*=\s*["\']' + re.escape(_id) + r'["\']', attrs, re.I):
                ok = False
                break
        for _cl in simple["classes"]:
            if ok and not re.search(r'\bclass\s*=\s*["\'][^"\']*\b' + re.escape(_cl) + r'\b[^"\']*["\']', attrs, re.I):
                ok = False
                break
        if ok:
            out.append(m)
    return out


def _match_close(html: str, tag: str, open_end: int) -> tuple[int, int] | None:
    """Position of the matching </tag> for an element whose opening tag ends at open_end (depth-aware)."""
    tok = re.compile(r"<(/?)" + re.escape(tag) + r"\b", re.I)
    depth = 1
    for m in tok.finditer(html, open_end):
        if m.group(1) == "/":                     # a closing tag
            depth -= 1
            if depth == 0:
                gt = html.find(">", m.end())
                if gt == -1:
                    return None
                return (m.start(), gt + 1)
        else:                                      # a nested opening tag of the same name
            depth += 1
    return None


def _find_element(html: str, selector: str) -> tuple[str, int, int, int, int] | None:
    """Locate the UNIQUE element a selector points at. Returns (tag, open_start, open_end, close_start,
    close_end) or None if it is not uniquely locatable (0 or >1 candidates at any step)."""
    parts = _parse_selector(selector)
    if not parts:
        return None
    lo, hi = 0, len(html)
    el = None
    for simple in parts:
        matches = _match_open_tags(html, simple, lo, hi)
        if len(matches) != 1:
            return None
        m = matches[0]
        tag = m.group(1)
        open_start, open_end = m.start(), m.end()
        close = _match_close(html, tag, open_end)
        if not close:
            return None
        close_start, close_end = close
        el = (tag, open_start, open_end, close_start, close_end)
        lo, hi = open_end, close_start            # descend into this element for the next part
    return el


def _selector_present(html: str, selector: str) -> bool:
    return _find_element(html, selector) is not None


def _bake(html: str, variant: dict) -> str:
    """Apply variant B permanently to the raw HTML. innerHTML/textContent → replace inner content;
    any other `attr` → set that attribute on the opening tag. Refuses if the element isn't unique."""
    el = _find_element(html, variant.get("selector", ""))
    if not el:
        raise ValidationError(f"promote: selector {variant.get('selector')!r} is not uniquely locatable")
    tag, os_, oe, cs, ce = el
    attr = variant.get("attr") or "innerHTML"
    val = variant.get("value") or ""
    if attr in ("innerHTML", "innerText", "textContent"):
        return html[:oe] + val + html[cs:]
    open_tag = html[os_:oe]
    if re.search(r"\b" + re.escape(attr) + r'\s*=\s*["\']', open_tag, re.I):
        new_open = re.sub(r'(\b' + re.escape(attr) + r'\s*=\s*["\'])[^"\']*(["\'])',
                          lambda m: m.group(1) + val + m.group(2), open_tag, count=1)
    else:
        new_open = open_tag[:-1] + f' {attr}="{val}">'
    return html[:os_] + new_open + html[oe:]


# ════════════════════════════════════════ PROPOSE (engine) ══════════════════════════════════════

# logical section → a concrete, high-leverage selector on the AZ homepage (the surfaces spec §6 favours).
_SECTION_SELECTORS = {
    "hero": {"selector": ".hero__title", "attr": "innerHTML"},
    "primary cta": {"selector": ".hero__cta .btn--primary", "attr": "innerHTML"},
}
_PLACEHOLDER = "{{OWNER_ANGLE — the new copy the Claude actioner fills in on approval}}"


def _section_selector(section: str) -> dict | None:
    s = (section or "hero").lower()
    if s in _SECTION_SELECTORS:
        return dict(_SECTION_SELECTORS[s])
    if "cta" in s or "button" in s:
        return dict(_SECTION_SELECTORS["primary cta"])
    if "hero" in s or "headline" in s or "title" in s:
        return dict(_SECTION_SELECTORS["hero"])
    # fall back to an id named after the section slug (validated for real presence below)
    return {"selector": f"#{_slug(section)}", "attr": "innerHTML"}


def propose_from_finding(finding: dict) -> dict | None:
    """Turn a copy/targeting finding (esp. G7_lead_rate) into a DRAFT experiment, or None if it can't be
    tested. Validated: the page is in scope, the target selector is a real UNIQUE element, and no RUNNING
    experiment already targets that element (non-overlap). B's value is a placeholder the actioner fills
    on approval when the owner supplies the angle."""
    rule = finding.get("rule_id")
    if rule not in EXPERIMENT_RULES:
        return None
    tgt = finding.get("target") or {}
    page = tgt.get("page_file") or "index.html"
    section = tgt.get("section") or "hero"
    if not is_allowed_path(page):
        return None
    html = read_page(page)
    if html is None:
        return None
    sel = _section_selector(section)
    if not sel or not _selector_present(html, sel["selector"]):
        return None
    # non-overlap: no running experiment already tests this element on this page
    for e in load().get("experiments", []):
        if (e.get("status") == "running" and e.get("page") == page
                and (e.get("variants", {}).get("B", {}) or {}).get("selector") == sel["selector"]):
            return None

    anchor = _slug(section)
    eid = _unique_id(f"{anchor}-{datetime.date.today():%Y-%m}")
    hypothesis = (finding.get("headline")
                  or f"An audience-fit {section} lifts the lead rate (share of visits that convert)")
    return {
        "id": eid,
        "status": "draft",
        "page": page,
        "anchor": anchor,
        "hypothesis": hypothesis,
        "metric": "conversion",                       # lead_submit + call_click + finder_capture
        "split": SPLIT,
        "variants": {
            "A": {"label": "control"},
            "B": {"selector": sel["selector"], "attr": sel["attr"], "value": _PLACEHOLDER},
        },
        "started": None,
        "min_sessions_per_variant": MIN_SESSIONS_PER_VARIANT,
        "max_days": MAX_DAYS,
        "result": None,
    }


# ════════════════════════════════════════ START (owner-gated) ═══════════════════════════════════

def start(exp: dict) -> dict:
    """Validate + activate a DRAFT experiment: scope fence, selector present/unique, non-overlap,
    concurrency cap. Sets status 'running' + started date, appends to experiments.json, logs the
    transition. Raises ScopeError/ValidationError on any guardrail failure (nothing is written)."""
    page = exp.get("page") or ""
    if not is_allowed_path(page):
        raise ScopeError(f"start refused: {page!r} is not an editable AZ marketing page (scope fence)")
    html = read_page(page)
    if html is None:
        raise ScopeError(f"start refused: {page!r} not found/readable under the repo root")
    b = (exp.get("variants") or {}).get("B") or {}
    selector = b.get("selector") or ""
    if not _selector_present(html, selector):
        raise ValidationError(f"start refused: selector {selector!r} is not a unique element in {page}")

    data = load()
    running = [e for e in data["experiments"] if e.get("status") == "running"]
    if len(running) >= CONCURRENCY_CAP:
        raise ValidationError(f"start refused: concurrency cap ({CONCURRENCY_CAP}) reached — "
                              f"{len(running)} experiment(s) already running")
    for e in running:
        if e.get("page") == page and (e.get("variants", {}).get("B", {}) or {}).get("selector") == selector:
            raise ValidationError(f"start refused: {selector!r} on {page} is already under test (non-overlap)")

    if any(e.get("id") == exp.get("id") for e in data["experiments"]):
        exp["id"] = _unique_id(exp.get("id") or _slug(exp.get("anchor", "exp")), data)

    exp["status"] = "running"
    exp["started"] = _today()
    exp.setdefault("split", SPLIT)
    exp.setdefault("metric", "conversion")
    exp.setdefault("min_sessions_per_variant", MIN_SESSIONS_PER_VARIANT)
    exp.setdefault("max_days", MAX_DAYS)
    exp.setdefault("result", None)
    data["experiments"].append(exp)
    save(data)
    _log("start", exp, {"page": page, "selector": selector, "started": exp["started"]})
    return exp


def start_from_surfaced(surfaced: dict, value: str | None = None) -> dict | None:
    """Convenience for the approval path: build a draft from a surfaced brief item and START it. Returns
    the running experiment, or None if the item isn't experiment-type / not testable. If the owner gave a
    concrete angle, pass it as `value` to bake straight into variant B."""
    finding = {"rule_id": surfaced.get("rule_id"), "subject": surfaced.get("subject"),
               "headline": surfaced.get("headline", ""), "detail": surfaced.get("detail", ""),
               "target": surfaced.get("target") or {}}
    draft = propose_from_finding(finding)
    if not draft:
        return None
    if value:
        draft["variants"]["B"]["value"] = value
    return start(draft)


# ════════════════════════════════════════ MEASURE (deterministic GA4) ═══════════════════════════

def _num(mv, i=0):
    try:
        return float(mv[i]["value"])
    except (TypeError, ValueError, IndexError, KeyError):
        return 0.0


def _variant_filter(exp_id: str, variant: str, extra_events: list[str] | None = None) -> dict:
    """AND-group: customEvent:experiment_id == exp_id  AND  customEvent:variant == A|B  (+ optional
    eventName inList for the conversion read). Reuses the two reusable custom dimensions (spec §7)."""
    exprs = [
        {"filter": {"fieldName": "customEvent:experiment_id", "stringFilter": {"value": exp_id}}},
        {"filter": {"fieldName": "customEvent:variant", "stringFilter": {"value": variant}}},
    ]
    if extra_events:
        exprs.append({"filter": {"fieldName": "eventName", "inListFilter": {"values": extra_events}}})
    return {"andGroup": {"expressions": exprs}}


def _variant_read(ga4, token, exp_id: str, variant: str, start: str) -> dict:
    """sessions + conversions for one variant over [started..today]. Any GA4 hiccup → zeros (never fabricate)."""
    date_range = [{"startDate": start or "2020-01-01", "endDate": "today"}]
    sessions = 0
    try:
        rep = ga4._run_report(token, {
            "dateRanges": date_range, "metrics": [{"name": "sessions"}],
            "dimensionFilter": _variant_filter(exp_id, variant)})
        rows = rep.get("rows") or []
        if rows:
            sessions = int(_num(rows[0]["metricValues"], 0))
    except Exception:
        sessions = 0
    conv = 0
    try:
        rep = ga4._run_report(token, {
            "dateRanges": date_range, "metrics": [{"name": "eventCount"}],
            "dimensionFilter": _variant_filter(exp_id, variant, CONV_EVENTS)})
        rows = rep.get("rows") or []
        if rows:
            conv = int(_num(rows[0]["metricValues"], 0))
    except Exception:
        conv = 0
    rate = (conv / sessions) if sessions else 0.0
    return {"sessions": sessions, "conv": conv, "rate": rate}


def measure(exp: dict, ga4, token: str) -> dict:
    """Per-variant GA4 read → {A:{sessions,conv,rate}, B:{sessions,conv,rate}}. rate = conversions/sessions."""
    start = exp.get("started")
    return {"A": _variant_read(ga4, token, exp["id"], "A", start),
            "B": _variant_read(ga4, token, exp["id"], "B", start)}


# ════════════════════════════════════════ DECIDE (deterministic stats) ══════════════════════════

def _norm_cdf(z: float) -> float:
    """Standard-normal CDF via math.erf (no scipy)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def two_proportion_z(c_a: int, n_a: int, c_b: int, n_b: int) -> tuple[float | None, float | None]:
    """Two-proportion z-test on conversion rate (B vs A). Returns (z, two-sided p). Pure python."""
    if n_a <= 0 or n_b <= 0:
        return None, None
    p_a, p_b = c_a / n_a, c_b / n_b
    p_pool = (c_a + c_b) / (n_a + n_b)
    if p_pool <= 0 or p_pool >= 1:
        return 0.0, 1.0                              # no variance → no signal
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return 0.0, 1.0
    z = (p_b - p_a) / se
    p = 2.0 * (1.0 - _norm_cdf(abs(z)))
    return z, max(0.0, min(1.0, p))


def _result(action, winner, lift_pct, p, n_a, n_b, reason):
    return {"action": action, "winner": winner, "lift_pct": lift_pct, "p": p,
            "n_a": n_a, "n_b": n_b, "reason": reason}


def decide(exp: dict, m: dict) -> dict:
    """The deterministic decision rule (spec §5). Requires BOTH variants ≥ min_sessions AND ≥1 conversion
    total before any significance call; then a two-proportion z-test. Returns a decision dict with
    action ∈ {promote, revert, continue}."""
    a, b = m["A"], m["B"]
    n_a, n_b, c_a, c_b = a["sessions"], b["sessions"], a["conv"], b["conv"]
    r_a, r_b = a["rate"], b["rate"]
    min_s = int(exp.get("min_sessions_per_variant", MIN_SESSIONS_PER_VARIANT))
    max_d = int(exp.get("max_days", MAX_DAYS))
    days = _days_running(exp)
    lift_pct = round((r_b - r_a) / r_a * 100, 1) if r_a > 0 else None
    winner_lean = "B" if r_b > r_a else ("A" if r_a > r_b else None)

    enough = (n_a >= min_s and n_b >= min_s and (c_a + c_b) >= 1)
    if not enough:
        if days >= max_d:
            return _result("revert", None, lift_pct, None, n_a, n_b,
                           f"max_days ({max_d}) reached without minimum samples "
                           f"(A {n_a}/{min_s}, B {n_b}/{min_s}, {c_a + c_b} conv) — reverting (inconclusive)")
        return _result("continue", winner_lean, lift_pct, None, n_a, n_b,
                       f"gathering data — A {n_a}/{min_s}, B {n_b}/{min_s} sessions, {c_a + c_b} conversion(s)")

    z, p = two_proportion_z(c_a, n_a, c_b, n_b)
    p_round = None if p is None else round(p, 4)
    if p is not None and p < ALPHA and r_b >= r_a + MIN_ABS_LIFT:
        return _result("promote", "B", lift_pct, p_round, n_a, n_b,
                       f"B wins — {r_b * 100:.2f} vs {r_a * 100:.2f} leads/100 sessions, p={p:.4f} (<{ALPHA})")
    if p is not None and p < ALPHA and r_a >= r_b + MIN_ABS_LIFT:
        return _result("revert", "A", lift_pct, p_round, n_a, n_b,
                       f"A (control) wins — {r_a * 100:.2f} vs {r_b * 100:.2f} leads/100, p={p:.4f} — reverting")
    if days >= max_d:
        return _result("revert", winner_lean, lift_pct, p_round, n_a, n_b,
                       f"max_days ({max_d}) reached, no significant winner "
                       f"(p={'n/a' if p is None else f'{p:.3f}'}) — reverting to control")
    return _result("continue", winner_lean, lift_pct, p_round, n_a, n_b,
                   f"not yet significant (p={'n/a' if p is None else f'{p:.3f}'}) — continuing")


# ════════════════════════════════════════ APPLY (promote / revert) ══════════════════════════════

def _save_updated(exp: dict) -> None:
    """Replace the experiment entry (matched by id) in experiments.json with `exp`."""
    data = load()
    for i, e in enumerate(data["experiments"]):
        if e.get("id") == exp.get("id"):
            data["experiments"][i] = exp
            break
    else:
        data["experiments"].append(exp)
    save(data)


def apply_decision(exp: dict, decision: dict) -> dict:
    """Enact a decision. promote → bake B into the page (validate_edit + scope fence + write), status
    'shipped'. revert → status 'reverted' (control untouched). Records `result`, logs the transition,
    writes experiments.json. Returns {"changed": [repo-relative files that changed]} so the caller commits."""
    action = decision.get("action")
    changed: list[str] = []
    if action == "promote":
        page = exp["page"]
        html = read_page(page)
        if html is None:
            raise ScopeError(f"promote refused: {page!r} not readable (scope fence)")
        b = exp["variants"]["B"]
        if "{{" in (b.get("value") or ""):
            raise ValidationError("promote refused: variant B value is still a placeholder (needs the owner's angle)")
        new = _bake(html, b)
        if new == html:
            raise ValidationError("promote is a no-op: baked value already matches the page")
        ok, why = validate_edit(page, html, new)          # HTML/JSON-LD parse + scope fence + truncation guard
        if not ok:
            raise ValidationError(f"promote rejected by validate_edit: {why}")
        (REPO / page).write_text(new, encoding="utf-8")
        exp["status"] = "shipped"
        changed.append(page)
    elif action == "revert":
        exp["status"] = "reverted"
    else:
        return {"changed": []}                             # continue → nothing to apply

    exp["result"] = {"winner": decision.get("winner"), "lift_pct": decision.get("lift_pct"),
                     "p": decision.get("p"), "n_a": decision.get("n_a"), "n_b": decision.get("n_b"),
                     "reason": decision.get("reason"), "decided": _today()}
    _save_updated(exp)
    changed.append("experiments.json")
    _log("decision", exp, {**decision, "applied": True, "status": exp["status"]})
    return {"changed": changed}


# ════════════════════════════════════════ run_cycle (orchestration) ═════════════════════════════

def _ga4():
    """Reuse the sensor's GA4 bootstrap (shared analytics/ga4.py client). None if no key/dep."""
    try:
        from .sensors.ga4_traffic import _ga4 as sensor_ga4
        return sensor_ga4()
    except Exception:
        return None


def run_cycle(verbose: bool = True, apply: bool = False) -> dict:
    """For every RUNNING experiment: measure → decide → (apply). Deterministic; no LLM. GA4 read reuses
    the sensor's client. With apply=False (dry) it measures + decides but writes NOTHING. With apply=True it
    promotes/reverts (writing the page + experiments.json) and returns the changed files for the caller to
    commit. A summary feeds the daily brief."""
    summary = {"available": False, "running": [], "decisions": [], "changed_files": [], "commit_tags": []}
    if os.environ.get("ENGINE_DISABLED") == "1":
        if verbose:
            print("experiments: ENGINE_DISABLED=1 — no-op.")
        summary["disabled"] = True
        return summary

    data = load()
    running = [e for e in data["experiments"] if e.get("status") == "running"]
    if not running:
        if verbose:
            print("experiments: no running experiments — nothing to measure.")
        return summary

    ga4 = _ga4()
    if ga4 is None:
        if verbose:
            print(f"experiments: {len(running)} running, but GA4 not configured — can't measure/decide "
                  "(data-gated; will decide once the SA key is present).")
        for exp in running:
            summary["running"].append({"id": exp["id"], "page": exp.get("page"),
                                       "days": _days_running(exp), "measured": False})
        return summary

    try:
        token = ga4._access_token(ga4._sa_info())
    except Exception as e:
        if verbose:
            print(f"experiments: GA4 auth failed ({type(e).__name__}) — skipping (no decision).")
        for exp in running:
            summary["running"].append({"id": exp["id"], "page": exp.get("page"),
                                       "days": _days_running(exp), "measured": False})
        return summary

    summary["available"] = True
    for exp in running:
        m = measure(exp, ga4, token)
        _log("measure", exp, {"a": m["A"], "b": m["B"]})
        d = decide(exp, m)
        summary["running"].append({
            "id": exp["id"], "page": exp.get("page"), "anchor": exp.get("anchor"),
            "days": _days_running(exp), "max_days": exp.get("max_days", MAX_DAYS), "measured": True,
            "a_sessions": m["A"]["sessions"], "b_sessions": m["B"]["sessions"],
            "a_rate": round(m["A"]["rate"] * 100, 2), "b_rate": round(m["B"]["rate"] * 100, 2),
            "action": d["action"], "reason": d["reason"]})
        if verbose:
            print(f"  · {exp['id']}: A {m['A']['conv']}/{m['A']['sessions']} vs "
                  f"B {m['B']['conv']}/{m['B']['sessions']} → {d['action']} ({d['reason']})")

        if d["action"] in ("promote", "revert"):
            entry = {"id": exp["id"], **d}
            if apply:
                try:
                    res = apply_decision(exp, d)
                    summary["changed_files"].extend(res["changed"])
                    summary["commit_tags"].append(f"{exp['id']}:{d['action']}")
                    entry["applied"] = True
                    entry["status"] = exp["status"]
                except (ScopeError, ValidationError) as e:
                    entry["applied"] = False
                    entry["error"] = str(e)
                    _log("error", exp, {"action": d["action"], "error": str(e)})
                    if verbose:
                        print(f"      ✗ apply rejected: {e}")
            else:
                entry["applied"] = False
            summary["decisions"].append(entry)

    summary["changed_files"] = sorted(set(summary["changed_files"]))
    return summary


# ════════════════════════════════════════ brief_data (for compose) ══════════════════════════════

def brief_data() -> dict:
    """Deterministic read of experiments.json + state/experiments.jsonl for the daily brief. Returns the
    running experiments (id/page/days + latest per-variant lead-rate) and any decisions applied TODAY."""
    data = load()
    logs = model.load(EXPERIMENTS_LOG)
    latest_measure: dict[str, dict] = {}
    for l in logs:
        if l.get("event") == "measure" and l.get("id"):
            latest_measure[l["id"]] = l

    running = []
    for e in data.get("experiments", []):
        if e.get("status") != "running":
            continue
        mm = latest_measure.get(e["id"], {})
        a, b = mm.get("a") or {}, mm.get("b") or {}
        running.append({
            "id": e["id"], "page": e.get("page"), "anchor": e.get("anchor"),
            "days": _days_running(e), "max_days": e.get("max_days", MAX_DAYS),
            "a_rate": round((a.get("rate") or 0) * 100, 2) if a else None,
            "b_rate": round((b.get("rate") or 0) * 100, 2) if b else None,
            "a_sessions": a.get("sessions"), "b_sessions": b.get("sessions")})

    today = _today()
    decisions_today = []
    for l in logs:
        if (l.get("event") == "decision" and l.get("applied")
                and str(l.get("ts", "")).startswith(today)):
            decisions_today.append({
                "id": l.get("id"), "action": l.get("action"), "winner": l.get("winner"),
                "lift_pct": l.get("lift_pct"), "p": l.get("p"), "status": l.get("status"),
                "reason": l.get("reason")})
    return {"running": running, "decisions_today": decisions_today}


if __name__ == "__main__":
    s = run_cycle(apply=False)
    print(json.dumps(s, indent=2))
