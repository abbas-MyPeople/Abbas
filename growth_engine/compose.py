"""
growth_engine.compose — build the DAILY brief email (ported from seo_engine.compose, retargeted to AZ).

Two parts:
  1. "HOW THE SITE PERFORMED" — a short, honest read from the latest GA4 signals (traffic + conversion).
  2. up to 3 concrete PROPOSALS — each with WHY, the exact PAGE/SECTION it touches, and a reply handle.

Verdict-first, phone-skimmable, plain reply protocol. COMPOSE only — sending is notify.py. A quiet day
produces an honest short "nothing to change, here's what I'm watching" note. Even with GA4 empty (brand-new
property, no rows) it renders a valid brief.
"""
from __future__ import annotations
from . import model

FROM_NAME = "AZ site growth engine"
# rule_id → the single KPI each proposal is trying to move (keeps IMPACT honest + specific).
_IMPACT = {
    "G3_underperf_page": "turn page traffic into leads (lead_submit / call_click)",
    "G4_conversion": "primary conversions (book-a-call / lead form)",
    "G5_funnel_dropoff": "keep visitors reaching the offer",
    "G6_dead_cta": "CTA click-through",
    "G0_site_guard": "site integrity → AI/organic discovery",
}
_DEFAULT_IMPACT = "leads + discovery"


def _dedupe(findings):
    latest = {}
    for f in findings:
        key = f.get("dedupe_key") or f"{f.get('rule_id')}:{f.get('subject')}"
        latest[key] = f              # later record wins (most recent run)
    return list(latest.values())


def _blocks(findings):
    findings = _dedupe(findings)
    alerts = [f for f in findings if f.get("severity") == "alert"]
    proposals = [f for f in findings if f.get("severity") == "opportunity" and f.get("read") == "good"]
    watching = [f for f in findings if f.get("severity") == "opportunity" and f.get("read") == "watch"]
    return alerts, proposals, watching


def _fmt_pct(v):
    return "n/a" if v is None else f"{v:+.0f}%"


def _performance(signals) -> list[str]:
    """The 'how the site performed' summary, read straight from the newest GA4 signals."""
    if not model.latest(signals, "traffic_available", "site"):
        return []
    avail = model.latest(signals, "traffic_available", "site")
    if not avail or not avail.get("value"):
        return ["• GA4 is connected but has no rows yet — the property is still gathering data."]
    lines = []
    sd = model.latest(signals, "sessions_delta_pct", "site")
    if sd:
        m = sd.get("meta", {})
        lines.append(f"• Traffic: {m.get('prev','?')} → {m.get('cur','?')} sessions "
                     f"({_fmt_pct(sd.get('value'))} vs the prior week).")
    ct = model.latest(signals, "conv_total_delta_pct", "site")
    if ct:
        m = ct.get("meta", {})
        parts = []
        for e in ("finder_capture", "call_click", "lead_submit"):
            s = model.latest(signals, f"conv_{e}", "site")
            if s:
                parts.append(f"{e}={s.get('value')}")
        lines.append(f"• Conversions: {m.get('prev','?')} → {m.get('cur','?')} "
                     f"({_fmt_pct(ct.get('value'))} WoW)" + (" — " + ", ".join(parts) if parts else "") + ".")
    return lines


def render_email(findings, signals=None) -> dict:
    signals = signals if signals is not None else []
    alerts, proposals, watching = _blocks(findings)
    surface = proposals[:3]
    overflow = proposals[3:]
    perf = _performance(signals)

    lines = []
    # ── verdict line ──
    if alerts:
        verdict = f"⚠ {len(alerts)} thing(s) need a look, plus {len(surface)} proposed change(s)."
    elif surface:
        verdict = f"{len(surface)} proposed change(s) for the site today — reply to approve."
    else:
        verdict = "Nothing needs changing today. Here's how the site did + what I'm watching."
    lines.append(verdict)
    lines.append("")

    # ── how the site performed ──
    if perf:
        lines.append("═══ HOW THE SITE PERFORMED ═══")
        lines.extend(perf)
        lines.append("")

    # ── alerts first ──
    if alerts:
        lines.append("═══ NEEDS ATTENTION ═══")
        for a in alerts:
            lines.append(f"• {a['headline']}")
            if a.get("detail"):
                lines.append(f"  {a['detail']}")
        lines.append("")

    # ── the numbered proposals ──
    if surface:
        lines.append("═══ PROPOSED CHANGES (reply to approve) ═══")
        lines.append("")
        for i, p in enumerate(surface, 1):
            impact = _IMPACT.get(p.get("rule_id"), _DEFAULT_IMPACT)
            tgt = p.get("target") or {}
            where = ""
            if tgt.get("page_file"):
                where = f"{tgt['page_file']}" + (f" · {tgt['section']}" if tgt.get("section") else "")
            lines.append(f"{i}) {p['headline']}")
            if p.get("detail"):
                lines.append(f"   Why:    {p['detail']}")
            if where:
                lines.append(f"   Where:  {where}")
            lines.append(f"   Impact: {impact}")
            lines.append(f'   Reply:  "{i} approve"  ·  "{i} reject"  ·  "{i} <your exact instruction>"')
            lines.append("")

    # ── status rollup ──
    also = []
    for w in watching:
        also.append(f"• {w['headline']}")
    for o in overflow:
        also.append(f"• (queued) {o['headline']}")
    if not surface and not alerts:
        also.append("• Live-site guard (proof bar, platform section, canonical, JSON-LD): all holding.")
    if also:
        lines.append("═══ ALSO TODAY (no action needed) ═══")
        lines.extend(also)
        lines.append("")

    # ── protocol footer ──
    lines.append("──")
    if surface:
        lines.append('Reply "approve all" to ship everything, or per-item as shown. Freeform tweaks OK '
                     '("1 make the hero say …") — I\'ll interpret and confirm before anything ships.')
    lines.append("Nothing changes on the site until you reply.")
    lines.append(f"— {FROM_NAME}")

    subj_tag = f"{len(surface)} proposed change(s)" if surface else "all holding"
    if alerts:
        subj_tag = f"{len(alerts)} to review · " + subj_tag
    subject = f"AZ Restaurant Partners — daily site check: {subj_tag}"

    surfaced = [{"n": i + 1, "rule_id": p.get("rule_id"), "subject": p.get("subject"),
                 "headline": p.get("headline"), "target": p.get("target") or {}}
                for i, p in enumerate(surface)]
    return {"subject": subject, "body": "\n".join(lines), "surfaced": surfaced,
            "counts": {"alerts": len(alerts), "proposals": len(proposals), "watching": len(watching)}}


def from_state() -> dict:
    return render_email(model.load_findings(), model.load_signals())


if __name__ == "__main__":
    e = from_state()
    print("SUBJECT:", e["subject"])
    print("=" * 64)
    print(e["body"])
