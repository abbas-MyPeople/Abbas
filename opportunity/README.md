# Local Large-Order Opportunity Finder

The free-tool funnel from `AZ_free_tool_funnel_handoff.md`. This note records what is
built, what is deliberately not built yet, and the two decisions that block the rest.

## What is built

- **`../find-large-orders.html`** — the front end. Site shell, tokens, mobile-first, staged
  progress, result cards with sources, the post-result bridge CTA, FAQ, schema, and the
  section-17 analytics events firing into the existing GA4 property (`G-3GEL1D477G`, loaded by
  `script.js`). Distinguishes every failure reason rather than calling them all "nothing found".
- **`score.py`** — the deterministic ranker. Section 8's six dimensions and weights, bands
  instead of fake precision, out-of-range and already-passed opportunities dropped. Pure
  functions, no network, no model call.
- **`providers.py`** — Google Places (Text + Nearby), Ticketmaster Discovery, Groq. Every one
  returns empty without its credential instead of raising.
- **`pipeline.py`** — restaurant context via the `outreach/` crawler, enrichment, dedupe,
  ranking, and owner-facing reasons. The model is called only to phrase one summary line over
  facts it was handed.
- **`budget.py`** — monthly per-SKU ceiling that fails closed, plus per-IP and global throttles.
- **`server.py`, `Dockerfile`, `fly.toml`, `requirements.txt`** — the deployable service.

All three self-tests pass:

```
python3 -m opportunity.score --selftest
python3 -m opportunity.budget --selftest
python3 -m opportunity.pipeline --selftest
```

Verified end to end in a browser against a stubbed service: cards, bands, sources, dates,
CORS preflight, origin rejection, query validation and the 429 after five requests.

The page ships safe today. With `ENDPOINT` empty it says the tool is not switched on and offers
a manual look — it never renders invented opportunities, per section 13.

## Deploying it

Everything below uses credentials that already exist except one.

```
fly apps create az-opportunity
fly volumes create opp_state --size 1 --region dfw -a az-opportunity

fly secrets set -a az-opportunity \
  PLACES_API_KEY=...        # the only NEW one - see below
  TICKETMASTER_API_KEY=...  # free, developer.ticketmaster.com
  GROQ_API_KEY=...          # reuse the existing key

fly deploy --config opportunity/fly.toml --dockerfile opportunity/Dockerfile --remote-only
```

Then set `ENDPOINT` at the top of the page script in `find-large-orders.html` to
`https://az-opportunity.fly.dev/find`, and add the page to `sitemap.xml` and the nav.

`PLACES_API_KEY` is the same key `docs/dashboard-v2/OWNER-ACTIONS.md` has been asking for in the
Wok repo, so creating it also lights up the Google-reviews panel that has been sitting deferred
there. Google Cloud, enable "Places API (New)", create a key, restrict it to that API.

Optional once traffic is real: set `CF_TURNSTILE_SECRET` and the bot check enforces itself.
Leave it unset and it is skipped.

## The credential position (checked across BOTH repos, 2026-08-19)

The Wok & Karahi repo carries far more than this one. Provisioned there as GitHub secrets:
`SERPAPI_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `FLY_API_TOKEN`,
`HF_TOKEN`, Clover, Twilio, Vapi, GA4, GSC and Sheets service accounts.

**Places is already written, just not switched on.** `analytics/reviews.py`, `analytics/market.py`
and `analytics/app_v2.py` all read `PLACES_API_KEY` + `GOOGLE_PLACE_ID` and no-op cleanly without
them. `docs/dashboard-v2/OWNER-ACTIONS.md` has the setup line, and the decision log lists it as a
deferred owner one-timer. So the integration is not work that needs doing — the key is.

**Do not use `SERPAPI_KEY` for this.** `seo_engine/brain/gaps.py` states its ~40-search budget
"keeps a run well under the ~100/mo free tier". The account is on SerpApi's free plan and the SEO
engine already claims most of it. One search per public submission would exhaust the month in days
and starve gap discovery. `seo_engine/checks/billing.py` already alarms at 25 remaining searches.

Phase 2 (restaurant context) needs no credential at all. `outreach/collect.py` already crawls a
restaurant's site, tears down the menu and detects catering state.

## Additional cost: zero, if built this way

Verified against Google Maps Platform pricing, Fly.io pricing and the Ticketmaster developer
portal on 2026-08-19.

- **Nearby organizations + restaurant resolution — $0.** Google's free tier is per SKU per month:
  10K calls for Essentials, 5K for Pro, 1K for Enterprise. Places Nearby Search and Text Search
  are Pro, so 5,000 free calls each per month. At roughly one Text Search plus four to six Nearby
  Searches per run, Nearby is the binding SKU and that is about 800 free runs a month. Google
  requires a billing account on file even inside the free tier, so the hard cap below is not
  optional.
- **Events — $0.** Ticketmaster's Discovery API is free at 5,000 calls/day and 5 requests/second,
  which covers the venue, concert and sports class. It does not cover youth tournaments or school
  calendars; those come from direct crawls using the `outreach/` crawler, also free.
- **Explanation LLM — $0.** `GROQ_API_KEY` is provisioned and on the free tier. Phase 8 only writes
  short prose over structured evidence, so the token volume is small.
- **Hosting — cents.** `FLY_API_TOKEN` is already a secret and flyctl is authed. Note both existing
  fly.toml files deliberately set `auto_stop_machines = false` with `min_machines_running = 1`,
  because they answer calls and texts. This service has no such requirement, so it runs with
  auto-stop on: a shared-cpu-1x 256MB machine is about $2.02/month while running, and a stopped
  machine bills only rootfs at about $0.15 per GB per 30 days.

The one thing that must be built rather than assumed is the spend ceiling. Google bills real money
past the free tier, so the service needs a monthly call counter that fails closed, per-IP and global
rate limits, and Cloudflare Turnstile in front. When the ceiling is hit the page should say the tool
is resting until the first of the month, not throw an error.

If putting a card on Google Cloud is unwanted, the no-card fallback is OpenStreetMap: Overpass for
nearby organizations by category and Nominatim for geocoding, both free and keyless. Coverage and
category quality are meaningfully worse than Places, so this is a fallback, not the plan.

## Reuse `outreach/`, do not reinvent it

`outreach/ARCHITECTURE.md` opens with its one rule: every value carries its own evidence
envelope. `collect.py` implements exactly the shape section 14 asks for —
`value / tier / source / method / observed_at / confidence / expires`, with an explicit
`unknown(reason)` instead of a silent null. That is the grounding doctrine this tool needs,
already written and already in use. A second, parallel evidence scheme would be a mistake.

## The problem the brief under-specifies

A public page with no signup, no email and no card, doing paid Places lookups plus web search
plus an LLM call on every submission, promoted for SEO. Section 20 asks for caching and
throttling, which helps with repeat traffic but not with the structural exposure: anyone can
hit the endpoint, every hit costs real money, and search visibility guarantees bots find it.

Before this goes live it needs a hard monthly spend ceiling that fails closed, per-IP and
global rate limits, and a bot check that is not a signup — Cloudflare Turnstile is invisible
to real owners and keeps section 16's "no gate before the value" promise intact. Worth
deciding the ceiling up front, because the honest failure mode is the tool going quiet for the
rest of the month, and the page should say that rather than error.

## Pipeline, once the above is settled

1. Resolve restaurant → canonical place, lat/lng, website *(needs places key)*
2. Restaurant context → cuisine, dietary, hours, catering formats *(reuse `outreach/collect.py`)*
3. Nearby candidates by category within a bounded radius *(needs places key)*
4. Upcoming events over a bounded horizon *(web search)*
5. Enrich → distance, size evidence, contact route, recency
6. Deduplicate across sources
7. Score with `score.py` — deterministic, no model
8. Explain with Claude, given only the structured evidence and forbidden to add facts
9. Return cards + sources in the shape `find-large-orders.html` already renders

The response shape the page expects:

```json
{
  "restaurant": { "name": "Wok & Karahi" },
  "opportunities": [{
    "title": "Spring Youth Soccer Invitational",
    "band": "Time-sensitive",
    "when": "Saturday",
    "distance_miles": 1.8,
    "summary": "26 teams listed across the tournament schedule.",
    "why": ["full-day event", "family group food demand", "within delivery range"],
    "contact_route": "Tournament organizer / event contact",
    "sources": [{ "title": "Official schedule", "url": "https://..." }]
  }]
}
```

Set `ENDPOINT` at the top of the page script once the service is live.
