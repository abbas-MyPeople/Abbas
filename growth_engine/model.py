"""
growth_engine.model — the MEASURE spine + the finding object (ported from seo_engine.model).

One append-only time-series (`fct_signal`) is the shared spine: every source's number is stored
the same way (source × metric × subject × period), so deltas are queried uniformly. On top sits
`finding` (DIAGNOSE/DECIDE). Decisions/batches/actions are recorded by the notify/inbox/execute
modules. State is plain JSONL under `growth_engine/state/` — git is the database + the audit log.

PRIVACY: AZ Restaurant Partners is a B2B consulting site — we store only counts, percentages,
shares, ranks, and booleans here. No money, no PII (same guard the restaurant engine uses).
"""
from __future__ import annotations
import json, datetime
from pathlib import Path

STATE = Path(__file__).resolve().parent / "state"
SIGNALS = STATE / "fct_signal.jsonl"
FINDINGS = STATE / "findings.jsonl"

# Units that are ALWAYS forbidden here (money / PII). A cheap guard against accidental leakage.
_FORBIDDEN_UNITS = {"usd", "cents", "dollars", "$"}


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def signal(source: str, metric: str, subject: str, value, unit: str = "count",
           period: str = "point", meta: dict | None = None) -> dict:
    """Record one measurement. Refuses money units by design."""
    if unit.lower() in _FORBIDDEN_UNITS:
        raise ValueError(f"growth_engine stores no money — refused unit {unit!r} for {metric!r}")
    rec = {"ts": now(), "source": source, "metric": metric, "subject": subject,
           "value": value, "unit": unit, "period": period, "meta": meta or {}}
    _append(SIGNALS, rec)
    return rec


def finding(rule_id: str, subject: str, severity: str, read: str, headline: str,
            detail: str = "", signal_refs: list | None = None, verify_at: str | None = None,
            target: dict | None = None) -> dict:
    """Record a DIAGNOSE result. severity: gate|alert|opportunity. read: good|watch|bad.
    `target` (optional) names the exact page/section a proposal touches: {page_file, section}."""
    rec = {"ts": now(), "rule_id": rule_id, "subject": subject, "severity": severity,
           "read": read, "headline": headline, "detail": detail,
           "signal_refs": signal_refs or [], "dedupe_key": f"{rule_id}:{subject}",
           "status": "open", "verify_at": verify_at, "target": target or {}}
    _append(FINDINGS, rec)
    return rec


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


ACTIONS = STATE / "actions.jsonl"


def log_action(kind: str, summary: str, batch_id: str | None = None, status: str = "done",
               target: dict | None = None, result: str | None = None) -> dict:
    """Record a material action taken on the owner's behalf — feeds the 'Since last time' brief section."""
    rec = {"ts": now(), "kind": kind, "summary": summary, "batch_id": batch_id,
           "status": status, "target": target or {}, "result": result}
    _append(ACTIONS, rec)
    return rec


def load_actions() -> list[dict]:
    return load(ACTIONS)


def load_signals() -> list[dict]:
    return load(SIGNALS)


def load_findings() -> list[dict]:
    return load(FINDINGS)


def latest(signals: list[dict], metric: str, subject: str | None = None):
    """Most recent value for a metric (optionally a subject). None if never measured."""
    hits = [s for s in signals if s["metric"] == metric and (subject is None or s["subject"] == subject)]
    return hits[-1] if hits else None
