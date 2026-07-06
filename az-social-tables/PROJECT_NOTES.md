# PROJECT_NOTES — az-social-tables (Phase 1 discovery)

*Written 2026-07-06. Findings from inspecting both repos before building anything.*

## Where this project lives and why

- **Repo:** `abbas-MyPeople/Abbas` (AZ Restaurant Partners — "the product" repo).
  The sister repo `abbas-MyPeople/WokAndKarahiTexas.com` is "the lab" (the restaurant).
  This project is an AZ Restaurant Partners **product** with Wok & Karahi as its first
  pilot venue, so it belongs here — same pattern as everything else AZ sells: prove it
  at the restaurant, productize it here.
- **Isolation:** everything is inside `az-social-tables/`. Nothing outside this folder
  was modified. No existing backend, Clover code, or AZ site file was touched.

## Branch / git state at session start

- Both repos were checked out on the platform-created session branch
  `claude/az-social-tables-mvp-ypl8h9` (this remote Claude Code session's dedicated
  branch), not `main`. **Deliberate deviation from the "main only" instruction:** in
  both repos a push to `main` triggers GitHub Actions **live deploys**
  (azrestaurantpartners.com / wokandkarahitexas.com). Committing to the isolated
  session branch is the only way to satisfy "do not deploy / do not touch production"
  while not losing the work when the ephemeral container is reclaimed. Merging to
  `main` remains an owner decision.

## Stack & conventions found

### Abbas repo (this one)
- **Static HTML/CSS/JS site, no build step**, deployed via GitHub Pages
  (CNAME `azrestaurantpartners.com`). Edit → push `main` → live.
- Brand system in `styles.css`: warm cream paper (`#f4eee2`), warm ink (`#1b1a17`),
  ember/terracotta accent (`#c0492b`), fonts **Fraunces** (display) + **Inter** (body).
  → The MVP reuses this palette so it reads as an AZ Restaurant Partners product.
- `.github/workflows/` here only runs the `stocks/` cron jobs — nothing that would
  pick up this folder. Safe.
- `research/` holds the strategy docs (personas, pricing, GTM, catering market) —
  used as background for the product spec.
- No package.json / no Node toolchain / no linter configured in either repo.

### WokAndKarahiTexas.com repo (read-only reference)
- **Monorepo**: static site (`website-v2/`) + four **Python/Flask** apps deployed to
  Render via root `render.yaml`:
  - `analytics/` (wok-analytics → data.wokandkarahitexas.com), `employees/`,
    `recipes/`, `chat/` — each is a single-folder Flask app with `app.py` +
    `requirements.txt`, started with `gunicorn app:app`, admin protected with
    HTTP Basic auth from `AUTH_USER`/`AUTH_PASS` env vars (`sync: false` — set in
    the Render dashboard, never committed).
- **Clover integration patterns** (all read-only, all keyed from a gitignored
  repo-root `.env`):
  - `clover-analysis/clover_client.py` — stdlib-only (`urllib`) GET client against
    `https://api.clover.com/v3/merchants/{MID}`, retry with backoff, `get_all()`
    pagination over `elements`, env vars `CLOVER_API_TOKEN` + `CLOVER_MERCHANT_ID`.
  - `clover-analysis/fetch_sales.py` — pulls orders by `createdTime` window with
    `expand=lineItems,orderType,payments,customers`; this is exactly the call shape
    our future "event night vs baseline" revenue comparison needs.
  - `analytics/clover_api.py` uses `CLOVER_API_KEY` naming on Render.
- **Guardrails in AGENTS.md** honored here: stay in your lane (own folder only),
  never commit secrets (`.env.example` only), pushes to `main` deploy.

## Stack decision for the MVP

**Flask (Python) + JSON-file storage, single folder, zero build step.**

Why:
1. It matches the established convention — the owner already runs four Flask apps
   with identical shape (`app.py`, `requirements.txt`, gunicorn, Basic-auth admin).
   If the pilot works, this drops into `render.yaml` as a fifth service unchanged.
2. Python 3.11 is on the machine; the only dependency is Flask. No Node toolchain
   exists in either repo, so Next.js/Vite would introduce a foreign stack + lockfiles.
3. The MVP needs a real server anyway (applications must persist across visitors);
   a static page + localStorage can't do applicant management.
4. JSON file storage (`data/db.json`, gitignored) keeps it fully local — no
   production DB, trivially inspectable, good enough for a manual 30-day pilot at
   1–4 events. Migration path to SQLite/Postgres is documented in the spec.

## Commands (all local)

```bash
cd az-social-tables
pip install -r requirements.txt
python app.py                 # http://localhost:5100
# admin: http://localhost:5100/admin  (dev default admin/admin — override via env)
python -m compileall .        # syntax check (no linter configured in repo)
python smoke_test.py          # route-level smoke test, no deps beyond Flask
```

## Deployment pattern (documented, NOT executed)

Same as siblings: add a `web` service to a `render.yaml` (rootDir
`az-social-tables`, `gunicorn app:app`), set `AUTH_USER`/`AUTH_PASS` in the Render
dashboard, point a subdomain CNAME at it. **Nothing was deployed in this session.**
File storage on Render's free tier is ephemeral — before real deployment, move to
SQLite on a persistent disk or a managed DB (flagged in QA_REPORT).

## Existing research that shaped the spec (read, not modified)

- `research/customer-personas.md`, `research/pricing-strategy.md`,
  `research/go-to-market-strategy.md`, `research/catering-market-analysis.md`
- W&K `CLAUDE.md`: slow-window facts — Monday closed, kitchen closes 4–5 PM daily,
  Tue–Thu are the softest dinner nights; GBP (not the website) is the discovery
  front door; social media has been tried and deprioritized (so pilot demand-gen
  leans on GBP, WhatsApp/community groups, Eventbrite/Meetup — see MARKETING_COPY).
