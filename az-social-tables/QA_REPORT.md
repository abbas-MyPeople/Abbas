# QA_REPORT — az-social-tables

*Run 2026-07-06 on Python 3.11.15 / Flask 3.1.3, in the session container.*

## Commands run

| Command | Result |
|---|---|
| `pip install -r requirements.txt` (flask; gunicorn listed for future deploy) | PASS |
| `python -m compileall -q .` (syntax check, all modules) | PASS |
| `python smoke_test.py` — 26 route/flow assertions | **PASS (26/26)** |
| `python app.py` + `curl /health` (real server boot) | PASS |
| Playwright (pre-installed Chromium): rendered `/`, `/events`, event detail, `/restaurants`, `/admin`, admin event page; screenshots reviewed | PASS — pages render as designed, brand consistent, forms visible |
| `git status` (repo root) | Only `az-social-tables/` added; **zero existing files modified** |

Lint/typecheck: **no linter or type-checker is configured anywhere in this repo**
(no ruff/flake8/mypy/eslint configs; the Abbas repo is a no-build static site).
`compileall` + the smoke test stand in. Tests: no existing test suite in the repo;
`smoke_test.py` was written for this project and covers: all public routes, seed
data, application submit (valid + invalid + consent enforcement), waitlist-on-full,
restaurant inquiry, admin auth (401/200), approve/confirm/seated flows, event
create/edit + draft hidden from public, ROI save + render, mock Clover adapter.

## What the smoke test proves

Full pilot loop works end-to-end: operator creates event → public page live →
consumer applies → operator approves → deposit confirmed → seated/no-show marked →
ROI entered → restaurant-net summary computed. Mock Clover numbers fill the ROI
panel when manual figures are missing and are clearly labeled as mock.

## Known issues / accepted trade-offs (all fine for a local pilot, listed honestly)

1. **JSON-file store, whole-file writes under a lock.** Fine for one operator and
   dozens of rows; not safe under multi-process gunicorn with concurrent writes.
   Run single-worker, or swap to SQLite (store.py is the seam) before real hosting.
2. **HTTP Basic auth with dev defaults (`admin`/`admin`).** Must set
   `AUTH_USER`/`AUTH_PASS` + `FLASK_SECRET_KEY` before exposing beyond localhost;
   Basic auth is only acceptable over HTTPS.
3. **No CSRF tokens** on forms. Low risk locally; add (Flask-WTF or a hand-rolled
   token) before public hosting of the admin.
4. **No rate-limiting/captcha** on the public application form — spam is possible
   once the URL is public. Manual review is the pilot backstop.
5. **No payments** — deposit language is placeholder by design; collected manually.
6. **No email/SMS automation** — confirmations are manual texts (templates in
   MARKETING_COPY). Deliberate: validate demand before building comms.
7. **Clover adapter is a mock** that raises loudly if switched to "real" — the
   real read-only client is a documented next step, not silently fake.
8. **Google Fonts loaded from CDN** on public pages — degrades gracefully to
   system serif offline.
9. Seed event dates are static (July/Aug 2026); operator should edit dates when
   the pilot actually schedules.

## Needs manual review by the owner

- Pricing placeholders: $6/seated-guest fee, $10–15 deposits, first-event-free.
- Seed copy claims (e.g. "rate highest in Spring") — consistent with the W&K
  repo's grounded claims, but owner should eyeball all public copy.
- Working name "Social Tables" — trademark collision with Cvent's product; fine
  for a pilot, check before spending on the name.
- Event dates vs. the JOB B slow-night analysis before locking week 1.

## Production readiness: **6 / 10**

Ready today for: local operation + a manually-run pilot (the actual goal).
Between it and public hosting: credentials, CSRF, rate-limiting, SQLite, HTTPS
host (the sibling apps' Render pattern fits: gunicorn single worker + persistent
disk). Nothing was deployed.
