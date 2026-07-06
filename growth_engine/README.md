# growth_engine — the AZ closed-loop growth engine

A self-running engine that keeps **azrestaurantpartners.com** performing: it MEASURES the site with GA4,
DIAGNOSES what's working / leaking, PROPOSES up to 3 concrete changes in one daily email, and — only for
what the owner approves — APPLIES the edit and commits it to `main` (GitHub Pages deploys it). Ported from
the Wok & Karahi `seo_engine` (same append-only signal/finding spine + email approve→execute loop),
retargeted to the AZ marketing site.

## The loop
`sense (GA4) → watch (site guard) → compose → send (email) → owner replies approve/reject/instruct → read → parse → execute (commit to main)`

## Layout
```
growth_engine/
  model.py            append-only fct_signal + finding spine (state/*.jsonl; refuses money units)
  run.py              entry point: --mode {sense|watch|propose|send|read|execute}
  watch.py            read-only heartbeat over the live-site guard
  compose.py          the DAILY brief: "how the site performed" + ≤3 concrete proposals
  notify.py           Gmail SMTP send (send-to-self) + clarifying-question sender; dry-runs w/o creds
  inbox.py            IMAP read of the reply; FAIL-CLOSED sender allowlist (azoeb27@gmail.com only)
  reply_parse.py      deterministic approve / reject / instruction parser
  actioner_llm.py     NEW — Claude interprets a freeform instruction into a BOUNDED find/replace edit plan
  executors.py        scope fence + validation + deterministic note drafts + apply the LLM edit plan
  execute.py          apply approved/interpreted edits → one revertible commit each to main (--dry default)
  sensors/ga4_traffic.py   the AZ MEASURE: GA4 traffic + conversion → deterministic findings
  checks/site.py           live-homepage invariants (proof bar, platform section, canonical, JSON-LD)
  state/*.jsonl            fct_signal / findings / batches / decisions (git = the DB + audit log)
  drafts/                 engine-local recommendation notes (NEVER committed/deployed)
```

## Run
```bash
python -m growth_engine.run --mode sense       # GA4 → findings (deterministic, no LLM)
python -m growth_engine.run --mode watch       # live-site guard ($0, no secrets)
python -m growth_engine.run --mode propose     # print the daily brief (no send)
python -m growth_engine.run --mode send        # send it (dry-runs without WK_ENGINE_* creds)
python -m growth_engine.run --mode read        # read + parse the owner's reply → decisions.jsonl
python -m growth_engine.run --mode execute            # DRY by default: prints unified diffs, writes nothing
python -m growth_engine.run --mode execute --apply    # really write + commit approved/interpreted edits
```

## Environment
| Var | Purpose |
|---|---|
| `GA4_PROPERTY_ID`, `GA4_SA_JSON` | GA4 read (via `../analytics/ga4.py`). Missing → sense no-ops cleanly. |
| `WK_ENGINE_EMAIL`, `WK_ENGINE_APP_PASSWORD` | Gmail SMTP/IMAP. Missing → send/read dry-run/no-op. |
| `WK_ENGINE_TO` | delivery inbox (defaults to `WK_ENGINE_EMAIL`). |
| `ANTHROPIC_API_KEY` | the LLM reply-actioner (Claude `claude-opus-4-8`). Missing → freeform → clarify. |
| `ENGINE_DISABLED=1` | **kill switch** — every mode no-ops. |

## Guardrails (load-bearing — "nothing breaks")
- **Dry-run is the default** everywhere; real writes need `--mode execute --apply` (or `send`/`read` with creds).
- **Only approved / interpreted items act**; unmentioned items roll over (never auto-approve/reject).
- **Fail-closed sender allowlist**: only `azoeb27@gmail.com` can approve; anyone else → ignored + alert.
- **Scope fence**: the executor may edit ONLY AZ marketing pages (root `*.html` + `tools/*.html`). It REFUSES
  `stocks/`, `command/`, `.github/`, `growth_engine/`, `analytics/`, `flagship/`, `research/`, anything else.
- **Validation before every commit**: HTML parses, every JSON-LD block is `json.loads`-clean, changed `.js`
  passes `node --check`. Any failure → reject + log, no commit.
- **LLM cost guard**: ≤5 Claude calls/run, short `max_tokens`, temperature 0, reply-interpretation only.
- **Secrets never printed**; `model.py` refuses money units; drafts/ is engine-local (never deployed).
- Every applied change is one commit → `git revert` undoes it.
```
