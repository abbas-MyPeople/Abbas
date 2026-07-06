# AZ Social Tables

**A restaurant social dining demand engine.** Restaurants publish curated dinner
events for their slow hours (singles dinners, new-friends tables, chef's tastings,
community nights); local people book seats; the operator balances, hosts, and
measures every table. The restaurant pays per *seated* guest.

- Consumer promise: **"Meet real people over real food."**
- Restaurant promise: **"Fill slow restaurant nights with pre-booked local customers."**
- Not a dating app — dating is one of four event formats. The customer is the restaurant.

First pilot venue: **Wok & Karahi**, Spring TX (see `VALIDATION_PLAN.md`).

## Run locally

```bash
cd az-social-tables
pip install -r requirements.txt
python app.py
```

- Public site: http://localhost:5100
- Operator console: http://localhost:5100/admin — dev login `admin` / `admin`
  (override with `AUTH_USER` / `AUTH_PASS`; see `.env.example`)

First run seeds `data/db.json` (gitignored) with three Wok & Karahi pilot events.
Delete that file to reset to seeds.

## What's here

| Path | What |
|---|---|
| `app.py` | Flask app — public site + operator console |
| `store.py` | JSON-file storage + seed events (swap for SQLite when the pilot outgrows it) |
| `integrations/clover/` | **Mocked** read-only Clover adapter — the contract for automated event-night ROI (see its docstring) |
| `templates/`, `static/` | Server-rendered pages, AZ-brand styling |
| `smoke_test.py` | Route-level smoke test (`python smoke_test.py`) |
| `PROJECT_NOTES.md` | Phase-1 repo discovery + stack rationale |
| `PRODUCT_SPEC.md` | Personas, flows, scope, metrics, risks |
| `MARKETING_COPY.md` | Consumer + restaurant copy, ad hooks, DM/email scripts |
| `VALIDATION_PLAN.md` | 30-day Wok & Karahi pilot: gates, metrics, case-study recipe |
| `QA_REPORT.md` | What was checked, known issues, readiness score |

## Boundaries

Fully self-contained: no code outside this folder is imported, modified, or
required. No production DB, no live Clover calls, no payments (deposit language is
placeholder; pilot collects deposits manually). **Not deployed** — see QA_REPORT
before considering that.
