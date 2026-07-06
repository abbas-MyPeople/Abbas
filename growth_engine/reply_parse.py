"""
growth_engine.reply_parse — read the owner's email reply into per-item decisions (ported verbatim
from seo_engine.reply_parse; the deterministic layer is domain-agnostic).

Handles the common shapes ("approve all", "1 approve, 2 reject", "3 make it say X", bare per-line).
Anything it can't classify is returned as `ambiguous` — the runtime then asks Claude (actioner_llm) and,
if still unclear, re-asks the owner rather than guessing. SAFETY: only explicit approvals ship; unmentioned
items = no decision = roll over (never auto-reject, never auto-approve). Only "approve all" blanket-approves.
"""
from __future__ import annotations
import re

_APPROVE = {"approve", "approved", "approves", "yes", "y", "ok", "okay", "ship", "send", "go",
            "yep", "yeah", "sure", "lgtm", "good", "great", "fine"}
_REJECT = {"reject", "rejected", "no", "n", "skip", "drop", "nope", "kill", "remove", "pass", "nah"}
_ALL = {"all", "everything", "both", "them all"}

_QUOTE_MARKERS = re.compile(r"(^>.*$)|(^on .*wrote:.*$)|(^-+\s*original message)|(^from:.*$)",
                            re.I | re.M)


def _owner_text(raw: str) -> str:
    lines = []
    for ln in raw.splitlines():
        if _QUOTE_MARKERS.match(ln.strip()):
            break
        lines.append(ln)
    return "\n".join(lines).strip()


def _verb(word_set, text) -> bool:
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in word_set)


def parse(raw: str, num_items: int) -> dict:
    """Return {global_: 'approve_all'|'reject_all'|None, items:{n:{decision,instruction}}, ambiguous:[...]}."""
    text = _owner_text(raw)
    low = text.lower()
    out = {"global_": None, "items": {}, "ambiguous": []}
    if not text:
        return out

    if _verb(_APPROVE, low) and _verb(_ALL, low) and not re.search(r"\d", low):
        out["global_"] = "approve_all"
        for n in range(1, num_items + 1):
            out["items"][n] = {"decision": "approve", "instruction": None}
        return out
    if _verb(_REJECT, low) and _verb(_ALL, low) and not re.search(r"\d", low):
        out["global_"] = "reject_all"
        for n in range(1, num_items + 1):
            out["items"][n] = {"decision": "reject", "instruction": None}
        return out

    clauses = [c.strip() for c in re.split(r"[\n,;]+", text) if c.strip()]
    for c in clauses:
        m = re.search(r"\b(\d{1,2})\b", c)
        if not m:
            continue
        n = int(m.group(1))
        if not (1 <= n <= num_items):
            out["ambiguous"].append(c)
            continue
        rest = (c[:m.start()] + " " + c[m.end():]).strip(" :.-")
        rest_low = rest.lower()
        if _verb(_APPROVE, rest_low) and not _verb(_REJECT, rest_low):
            out["items"][n] = {"decision": "approve", "instruction": None}
        elif _verb(_REJECT, rest_low) and not _verb(_APPROVE, rest_low):
            out["items"][n] = {"decision": "reject", "instruction": None}
        elif rest:                                # a number + free text = an edit instruction
            out["items"][n] = {"decision": "instruct", "instruction": rest}
        else:
            out["ambiguous"].append(c)

    if not out["items"] and not out["ambiguous"]:
        if num_items == 1 and _verb(_APPROVE, low) and not _verb(_REJECT, low):
            out["items"][1] = {"decision": "approve", "instruction": None}
        elif num_items == 1 and _verb(_REJECT, low) and not _verb(_APPROVE, low):
            out["items"][1] = {"decision": "reject", "instruction": None}
        else:
            out["ambiguous"].append(text)          # → runtime asks Claude / re-asks owner
    return out


if __name__ == "__main__":
    cases = [
        ("approve all", 3, {1: "approve", 2: "approve", 3: "approve"}),
        ("1 approve, 2 reject, 3 approve", 3, {1: "approve", 2: "reject", 3: "approve"}),
        ("1 yes\n2 no", 2, {1: "approve", 2: "reject"}),
        ("2 make it say 'book a call today'", 3, {2: "instruct"}),
        ("reject everything", 2, {1: "reject", 2: "reject"}),
        ("approve", 1, {1: "approve"}),
        ("looks good", 1, {1: "approve"}),
        ("1 approve", 3, {1: "approve"}),
    ]
    ok = 0
    for raw, n, expect in cases:
        r = parse(raw, n)
        got = {k: v["decision"] for k, v in r["items"].items()}
        strict = all(got.get(k) == v for k, v in expect.items())
        ok += strict
        print(f"{'OK ' if strict else 'XX '} {raw!r:42} -> {got}  amb={r['ambiguous'] or ''}")
    print(f"\n{ok}/{len(cases)} parser cases pass")
