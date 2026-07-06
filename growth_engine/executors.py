"""
growth_engine.executors — turn an APPROVED / interpreted proposal into a concrete, revertible edit.

Two kinds of executor:
  • DETERMINISTIC note (note_draft) — a sensor proposal ("page X has traffic but no leads") approved with a
    bare "approve" has no concrete new copy yet, so we write an engine-LOCAL draft note (NOT committed, not
    deployed) describing the recommended change. Live copy edits come only from a freeform instruction.
  • apply_llm_plan — applies the bounded find/replace the LLM actioner produced to a real marketing page.

EVERY committed edit passes the SCOPE FENCE + validate_edit BEFORE it is written/committed:
  • SCOPE FENCE: only AZ marketing pages (root *.html + tools/*.html) may be edited. stocks/, command/,
    .github/, growth_engine/, analytics/, flagship/, research/ (and anything else) are REFUSED.
  • VALIDATION: the new HTML must parse; every <script type="application/ld+json"> block must be
    json.loads-clean; any changed .js must pass `node --check`. Any failure → reject (raise), no commit.
"""
from __future__ import annotations
import json, re, subprocess, tempfile, os, datetime
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent           # the AZ repo root (parent of growth_engine/)
DRAFTS = Path(__file__).resolve().parent / "drafts"      # engine-local (never committed)
_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)

# ── SCOPE FENCE ─────────────────────────────────────────────────────────────
FORBIDDEN_DIRS = {"stocks", "command", ".github", "growth_engine", "analytics",
                  "flagship", "research", "node_modules", ".git"}


class ScopeError(Exception):
    """Raised when an edit targets a path outside the allowed AZ marketing pages."""


class ValidationError(Exception):
    """Raised when a proposed edit fails HTML/JSON-LD/JS validation."""


def is_allowed_path(rel: str) -> bool:
    """True only for AZ marketing pages: root-level *.html, or tools/*.html. Everything else is refused."""
    if not rel:
        return False
    rel = rel.strip().replace("\\", "/").lstrip("./")
    parts = [p for p in rel.split("/") if p]
    if not parts or rel.startswith("/") or ".." in parts:
        return False
    if parts[0] in FORBIDDEN_DIRS:
        return False
    if len(parts) == 1:
        return parts[0].endswith(".html")
    if len(parts) == 2 and parts[0] == "tools":
        return parts[1].endswith(".html")
    return False


def read_page(page_file: str) -> str | None:
    """Read a marketing page's current text (fence-checked). None if missing/refused."""
    if not is_allowed_path(page_file):
        return None
    full = REPO / page_file
    if not full.exists():
        return None
    try:
        return full.read_text(encoding="utf-8")
    except Exception:
        return None


# ── VALIDATION ──────────────────────────────────────────────────────────────

class _Parser(HTMLParser):
    def error(self, message):            # py<3.10 compat: never let the parser raise/abort silently
        raise ValueError(message)


def _html_parses(content: str) -> tuple[bool, str]:
    try:
        _Parser(convert_charrefs=True).feed(content)
        return True, ""
    except Exception as e:
        return False, f"HTML did not parse: {type(e).__name__}: {e}"


def _jsonld_clean(content: str) -> tuple[bool, str]:
    for i, raw in enumerate(_LD_RE.findall(content)):
        try:
            json.loads(raw)
        except json.JSONDecodeError as e:
            return False, f"JSON-LD block #{i + 1} is not json.loads-clean: {e}"
    return True, ""


def _js_node_check(content: str) -> tuple[bool, str]:
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
            tf.write(content)
            tmp = tf.name
    except Exception as e:
        return False, f"could not stage JS for node --check: {e}"
    try:
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            errln = next((ln.strip() for ln in r.stderr.splitlines() if "Error" in ln), "")
            return False, "node --check failed: " + (errln or "syntax error")
        return True, ""
    except FileNotFoundError:
        return False, "node not available to validate the changed .js"
    except Exception as e:
        return False, f"node --check error: {type(e).__name__}: {e}"
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def validate_edit(path: str, old_content: str | None, new_content: str) -> tuple[bool, str]:
    """Gate an edit BEFORE it is written/committed. Returns (ok, reason)."""
    if not is_allowed_path(path):
        return False, f"scope fence: {path!r} is not an editable AZ marketing page"
    if path.endswith(".html"):
        ok, why = _html_parses(new_content)
        if not ok:
            return False, why
        ok, why = _jsonld_clean(new_content)
        if not ok:
            return False, why
        # truncation guard: don't let an edit drop the closing tag it started with
        if old_content and "</html>" in old_content.lower() and "</html>" not in new_content.lower():
            return False, "edit removed the closing </html> tag (truncation)"
    if path.endswith(".js"):
        ok, why = _js_node_check(new_content)
        if not ok:
            return False, why
    return True, ""


# ── DETERMINISTIC executor: an engine-local recommendation note (never committed) ──

def note_draft(finding) -> dict:
    """A sensor proposal approved with a bare 'approve' → a draft recommendation note (engine-local,
    NOT committed / NOT deployed). The owner turns it into a real edit via a freeform instruction."""
    tgt = finding.get("target") or {}
    subj = (finding.get("subject") or "note").replace(":", "-").replace(" ", "-").lower()
    stamp = datetime.date.today().isoformat()
    path = DRAFTS / f"note-{stamp}-{subj}.md"
    body = (f"# Recommendation — {finding.get('headline','')}\n\n"
            f"_Generated {stamp}. Engine-local draft; nothing on the site changed._\n\n"
            f"**Page:** {tgt.get('page_file','(unspecified)')}  \n"
            f"**Section:** {tgt.get('section','(unspecified)')}\n\n"
            f"{finding.get('detail','')}\n\n"
            f"To ship a change, reply to the daily brief with the exact new wording, e.g.:\n"
            f'`{finding.get("_n","1")} make the {tgt.get("section","hero")} say "…"` — '
            f"I'll interpret it into a surgical edit and commit it.\n")
    return {"summary": f"Draft recommendation note: {finding.get('headline','')}",
            "files": {}, "local_drafts": {str(path): body}}


# ── LLM-interpreted executor: apply a bounded find/replace to a real page ──

def apply_llm_plan(plan: dict) -> dict:
    """Apply an actioner_llm edit plan to a marketing page. Fence + validate BEFORE returning the edit."""
    page_file = plan.get("page_file", "")
    if not is_allowed_path(page_file):
        raise ScopeError(f"refused: {page_file!r} is outside the editable AZ marketing pages")
    html = read_page(page_file)
    if html is None:
        raise ScopeError(f"refused: {page_file!r} not found or not readable under the repo root")
    find, replace = plan.get("find", ""), plan.get("replace")
    if not find or replace is None:
        raise ValidationError("edit plan missing find/replace")
    if html.count(find) != 1:
        raise ValidationError(f"`find` snippet must occur exactly once in {page_file} "
                              f"(found {html.count(find)})")
    new = html.replace(find, replace, 1)
    if new == html:
        raise ValidationError("edit is a no-op")
    ok, why = validate_edit(page_file, html, new)
    if not ok:
        raise ValidationError(why)
    return {"summary": f"{page_file}: {plan.get('change_description','copy edit')}",
            "files": {page_file: new}, "local_drafts": {}}


# rule_id → deterministic executor (the safe, non-live default for a sensor proposal)
EXECUTORS = {
    "G3_underperf_page": note_draft,
    "G4_conversion": note_draft,
    "G5_funnel_dropoff": note_draft,
    "G6_dead_cta": note_draft,
}
