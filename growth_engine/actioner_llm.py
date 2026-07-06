"""
growth_engine.actioner_llm — THE NEW PIECE.

When the owner's reply is NOT a clean approve/reject but a freeform instruction ("make the hero say X",
"move the pricing up", "tighten the case-study intro"), this asks Claude to interpret it into a BOUNDED,
surgical edit plan:  {page_file, section, change_description, find, replace}.

HARD GUARDRAILS
  • Only a NAMED page that EXISTS and passes the scope fence (executors.is_allowed_path) is eligible.
  • The plan must be a surgical find/replace where `find` is an EXACT existing snippet (verified to occur
    exactly once in the file). No whole-file rewrites, no invented anchors.
  • If the instruction is ambiguous or out-of-scope, Claude MUST return {"action":"clarify", ...} — we do
    NOT guess; execute.py then queues a short clarifying email back to the owner.
  • LLM COST GUARD: at most MAX_LLM_CALLS Claude calls per run; short max_tokens.
  • Kill switch (ENGINE_DISABLED=1) and missing ANTHROPIC_API_KEY → no call; returns a 'skip'/'clarify'.
  • Never prints secret values.

Used for REPLY INTERPRETATION ONLY. The actual file write + validation is executors.apply_llm_plan.
"""
from __future__ import annotations
import os, json, urllib.request
from . import executors

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-opus-4-8"
FALLBACK_MODEL = "claude-3-5-haiku-latest"
MAX_LLM_CALLS = 5
MAX_TOKENS = 900
PAGE_CHAR_CAP = 16000            # bound the context we send (cost guard)


class Budget:
    """Per-run cap on Claude calls."""
    def __init__(self, limit: int = MAX_LLM_CALLS):
        self.limit = limit
        self.used = 0

    def take(self) -> bool:
        if self.used >= self.limit:
            return False
        self.used += 1
        return True


_SYSTEM = (
    "You convert a restaurant-tech marketing site owner's short reply into ONE surgical HTML edit, or you "
    "ask for clarification. You are given: the proposal the reply refers to, the target page file, and that "
    "page's current HTML. Rules: (1) Output STRICT JSON only, no prose. (2) The edit MUST be a find/replace "
    "where `find` is copied VERBATIM from the provided HTML and occurs there exactly once; keep it short "
    "(a single tag/line/phrase). (3) Only change copy/text or attributes the instruction clearly asks for — "
    "never restructure the page. (4) If the instruction is vague, refers to a section/page you cannot locate "
    "in the given HTML, or asks for anything outside a simple copy/attribute edit, return action 'clarify' "
    "with a one-sentence question. Never invent content the owner didn't ask for."
)

_SCHEMA_HINT = (
    'Return JSON: {"action":"edit","section":"<short label>","change_description":"<what changed>",'
    '"find":"<exact existing snippet>","replace":"<new snippet>"}  '
    'OR  {"action":"clarify","question":"<one sentence>"}'
)


def _call(api_key: str, model: str, system: str, user: str) -> str:
    body = json.dumps({
        "model": model, "max_tokens": MAX_TOKENS, "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    parts = data.get("content") or []
    return "".join(p.get("text", "") for p in parts if p.get("type") == "text").strip()


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except Exception:
        i, j = text.find("{"), text.rfind("}")
        if 0 <= i < j:
            try:
                return json.loads(text[i:j + 1])
            except Exception:
                return None
    return None


def interpret(instruction: str, item: dict, budget: Budget, verbose: bool = True) -> dict:
    """Interpret a freeform instruction into a bounded edit plan.
    Returns one of:
      {"kind":"edit", "plan": {...}}      — a validated-shape surgical edit (executors will re-validate)
      {"kind":"clarify", "question": ...} — ambiguous/out-of-scope → queue a clarifying email
      {"kind":"skip", "reason": ...}      — no key / budget exhausted / kill switch
    """
    if os.environ.get("ENGINE_DISABLED") == "1":
        return {"kind": "skip", "reason": "ENGINE_DISABLED=1"}
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"kind": "clarify",
                "question": f'I can\'t auto-interpret "{instruction}" (no LLM configured). '
                            f"Please reply with the exact page + section and the new text."}

    # Resolve the target page from the proposal, if it named one.
    target = (item or {}).get("target") or {}
    page_file = target.get("page_file")
    section_hint = target.get("section", "")

    if not page_file:
        return {"kind": "clarify",
                "question": f'"{instruction}" — which page should I change (e.g. index.html, '
                            f"case-study.html, tools/…)? I won't guess."}
    if not executors.is_allowed_path(page_file):
        return {"kind": "clarify",
                "question": f'"{page_file}" is outside the pages I\'m allowed to edit. '
                            f"Name one of the marketing pages and I'll do it."}
    html = executors.read_page(page_file)
    if html is None:
        return {"kind": "clarify",
                "question": f"I couldn't find {page_file} in the repo. Which page did you mean?"}

    if not budget.take():
        return {"kind": "skip", "reason": "LLM call budget exhausted this run"}

    user = (
        f"PROPOSAL: {item.get('headline','(freeform)')}\n"
        f"TARGET PAGE FILE: {page_file}\n"
        f"TARGET SECTION HINT: {section_hint or '(none)'}\n"
        f"OWNER INSTRUCTION: {instruction}\n\n"
        f"{_SCHEMA_HINT}\n\n"
        f"--- CURRENT HTML OF {page_file} (verbatim; copy `find` from here) ---\n"
        f"{html[:PAGE_CHAR_CAP]}"
    )

    raw = ""
    for model in (MODEL, FALLBACK_MODEL):
        try:
            raw = _call(api_key, model, _SYSTEM, user)
            if raw:
                break
        except Exception as e:
            if verbose:
                print(f"actioner_llm: {model} call failed ({type(e).__name__}); trying fallback.")
            continue
    obj = _extract_json(raw) if raw else None
    if not obj:
        return {"kind": "clarify",
                "question": f'I couldn\'t confidently interpret "{instruction}". '
                            f"Please give the exact section and the new wording."}

    if obj.get("action") == "clarify":
        return {"kind": "clarify", "question": obj.get("question") or
                f'Can you clarify "{instruction}"? I need the exact section and new text.'}

    if obj.get("action") == "edit":
        find = obj.get("find") or ""
        replace = obj.get("replace")
        # Basic shape checks here; executors.apply_llm_plan does the load-bearing validation + fence.
        if not find or replace is None or find not in html:
            return {"kind": "clarify",
                    "question": f'I mapped "{instruction}" to {page_file} but couldn\'t pin an exact '
                                f"spot to change safely. Can you quote the current text and the new text?"}
        if html.count(find) != 1:
            return {"kind": "clarify",
                    "question": f'The text I\'d change on {page_file} appears more than once — '
                                f"can you give me a longer, unique quote of it plus the replacement?"}
        plan = {"page_file": page_file,
                "section": obj.get("section") or section_hint or "",
                "change_description": obj.get("change_description") or instruction,
                "find": find, "replace": replace}
        return {"kind": "edit", "plan": plan}

    return {"kind": "clarify",
            "question": f'I couldn\'t interpret "{instruction}" into a safe edit. '
                        f"Please name the page, the exact current text, and the new text."}
