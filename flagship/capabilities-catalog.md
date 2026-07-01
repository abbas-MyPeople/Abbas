# AZ Restaurant Partners — Client Capabilities & Implementation Guide

> **Purpose:** turn everything proven on the Wok & Karahi flagship into a **productized menu of
> capabilities** AZ Restaurant Partners can sell and deliver to other restaurants, plus an
> implementation playbook for onboarding a new client. Meant to be fed to the AZ repo's chatbot as
> a knowledge base for scoping engagements and generating proposals.
>
> **Provenance:** derived from the full Wok & Karahi build (voice agent, website/AEO, Clover
> analytics) and the philosophy playbook in [`voice-agent-playbook.md`](voice-agent-playbook.md).
> **Now reconciled against the live AZ site** (this doc lives inside the AZ repo). The
> capability letters below (A–F) map to the site's named "plays" and published pricing — see the
> reconciliation table in §6 and the full mapping in [`CAPABILITY-LEDGER.md`](CAPABILITY-LEDGER.md),
> which is the source of truth for status. Where this catalog and the ledger disagree, the ledger wins.

---

## 1. The model
AZ Restaurant Partners does for other restaurants what we built for Wok & Karahi: **data-grounded,
human-feeling, business-goal-aligned technology across departments.** Each department is a productized
capability with the same DNA:
- **Grounded in the client's real data** (POS, reviews, search, sales).
- **Sounds/reads human and on-brand.**
- **Captures operational intelligence** back to the owner.
- **Aligned to the two money goals:** more **first-party orders** (off the ~30% third-party apps) and
  more **catering / retention**.
- **Reusable architecture; per-client is data + config** (see the playbook's "generalizes vs per-client").

---

## 2. Capability catalog (what we can sell)

### A. Voice / AI Phone Agent  — *built & live (flagship)*
Answers every call, takes orders into the POS, handles catering, upsells, remembers regulars, handles
complaints with real empathy + triage, and captures feedback. Bilingual-capable.
- **Proof:** Wok & Karahi — Vapi + a self-hosted tool server + Clover, grounded menu, returning-caller
  "the usual?", severity-based escalation, feedback log, dry-run→gated-live order writes.
- **Reusable:** the entire architecture and every flow. Per-client: POS creds, menu/best-sellers,
  brand voice, escalation tree, hours/order-types.
- **Client value:** stop missing calls; cut order errors; capture demand after hours; free up staff;
  push customers to direct ordering; a listening post for complaints/feedback.
- **Modules to price separately:** FAQ+transfer (entry), full ordering, catering sizing, returning-
  caller memory ("your usual?"), **preference memory** (learns your usual spice/protein/add-ons),
  **reservations** (with email + real seating rules), complaint/escalation + **feedback capture**
  (owner-reviewable log → FAQ), **item-knowledge layer** (describe/recommend any dish from real data),
  **context-aware promotions** (right offer at the right time), **honest ready-time** (real ETA from live
  kitchen load + a weather-timed-hot pickup offer), **SMS updates + loyalty/marketing** (auto-texts every
  order's details; soft opt-in with STOP-to-quit honored + recorded; tailored *presence-aware* campaigns —
  their usual + weather/day — gated like order writes), **live availability** (mirrors what the manager
  sets in the POS/Clover, auto-refreshed 2×/day, plus a manual 86 override; re-checked at order time so we
  never sell what the kitchen can't make and offer a real alternative),
  **presence/human-connection layer** (weather/day warmth, read desires/aversions), graceful silence
  handling, multilingual.
- **Owner intelligence digest** (owner-cool; also feeds capability D): the phone turned into a weekly
  read — complaints, feedback themes, upcoming reservations, new vs returning callers. `GET /digest`.
- **Reliability posture (sell this):** no silent failures — failed actions never falsely confirm and stay
  retryable; every error is logged + surfaced (/health, /errors); scenario-gated QA (25+ caller states);
  and irreversible writes are dry-run → gated-live. This is the difference between a demo and production.

### B. Reviews & Reputation Management
Monitor and respond to reviews (Google/Yelp/etc.) in the brand's human voice; sentiment + theme
mining; proactively solicit reviews from happy customers; route serious issues to the owner.
- **Reuse from voice:** the *genuine-empathy* complaint philosophy and the *structured feedback log*
  transfer directly — same "acknowledge → understand → capture → triage" pattern, async instead of live.
- **Client value:** higher rating and volume (the real front door — GBP drives most restaurant
  discovery), faster response, and a feed of what customers actually say.

### C. SEO / AEO / Web  — *built & live*
A fast, code-built, AI-crawler-readable site: entity/Restaurant/Menu/FAQ schema, statically-rendered
menu grounded in the POS, local + occasion landing pages, blog/content, robots/llms, internal linking.
- **Proof:** Wok & Karahi site live, full AEO build + audit; fixed the "403 to bots" problem so AI
  assistants can actually read the menu/hours.
- **Client value:** discoverability in both classic search and AI answers (the zero-click / AI-overview
  shift); a site that converts to direct orders instead of leaking to a third-party URL.

### D. Analytics & Business Intelligence  — *built*
POS integration → deep sales analysis: best/worst sellers by item/category/cuisine, channel economics
(dine-in vs takeout vs delivery vs 3P commission drag), dayparts, catering signals, AOV, top modifiers,
trends. Conversational dashboard.
- **Proof:** Wok & Karahi Clover analysis (90-day, 1,504-order deep dive); it directly powered the
  voice agent's smart defaults (popular protein/spice, attach rates).
- **Client value:** know what sells and when; price/menu decisions; the same data makes *every other*
  capability smarter (recommendations, upsell, content).

### E. Direct-Ordering & Margin Engine
Push demand to first-party ordering and quantify the win (third-party apps take ~30% + fees). Tracked
ordering links, attribution, and every touchpoint (voice, web, reviews) nudging to direct.
- **Client value:** margin recovery — the highest-ROI story for most restaurants.

### F. Retention / Lifecycle
Returning-customer recognition (from the voice history + POS), lightweight newsletter/loyalty, "the
usual" convenience, win-back. Corporate/recurring catering pipeline.
- **Reuse from voice:** the returning-caller memory is the seed of a cross-channel customer profile.

---

## 3. The cross-department thread (why this compounds)
The client's **real data is the shared substrate**. Analytics (D) produces the truth that makes the
Voice agent (A) recommend the right things, the Web/AEO (C) rank for the right dishes, Reviews (B) reply
with context, and Retention (F) target the right regulars. Sell one, and each additional department
gets cheaper to deliver and better because the data and the brand voice are already modeled. **Lead
with the highest-visible-pain capability (usually Voice or Reviews), then expand.**

---

## 4. Implementation playbook (onboarding a new client)

**Phase 0 — Discovery & grounding**
- Inventory: POS (Clover/Toast/Square/etc.), menu, hours/holidays/order types, delivery radius/fees,
  brand identity, escalation contacts, languages, the two money goals for *this* client.
- Pull the real data: POS catalog (with IDs) + N-day order history. Mine best-sellers, popular
  modifiers/spice, channel economics, attach rates. **This dataset powers every capability.**

**Phase 1 — Pick the entry capability & stand up the architecture**
- Usually Voice (missed calls) or Reviews (reputation). Deploy the reusable stack; swap in client data.
- Choose a **brand-fit voice and lock it**; wire the escalation tree; set hours/order-types.

**Phase 2 — Build the flows on the client's data**
- Grounded menu resolver + smart defaults from *their* sales; upsell pairings from *their* attach data;
  complaint/feedback capture; returning-caller memory; guardrails.

**Phase 3 — Dry-run → verified-live rollout**
- Keep irreversible actions gated (order writes dry-run; log the exact payload). Verify end-to-end on a
  real line/channel. Flip to live only after one verified transaction. Double-gate live writes.

**Phase 4 — Expand & compound**
- Add the next department reusing the same data + brand model. Feed captured feedback into the FAQ,
  the review replies, and menu/content decisions.

**Reusable assets to templatize:**
- The voice tool-server + Vapi config-as-code (model/prompt/voice/tools/transfer).
- The persistence pattern (volume-backed caller history + feedback log).
- The POS-grounded menu resolver + modifier validation + dry-run→gated write.
- The AEO site scaffold (schema, static menu, local/occasion pages).
- The analytics engine (POS → item/channel/daypart/catering insights).
- Discovery questionnaire + a per-department config schema.

---

## 5. Positioning one-liner (for proposals)
**"We give your restaurant a front-of-house that never sleeps, a website AI assistants can read, and a
brain that knows what sells — all grounded in your real numbers, all pushing customers to order direct.
Proven on our flagship; configured for you."**

---

## 6. Reconciliation with the live AZ site (done 2026-07-01)

The catalog letters map to the site's marketed "plays" and its published pricing as follows. Full
status (live / built / spec / advisory) is tracked in [`CAPABILITY-LEDGER.md`](CAPABILITY-LEDGER.md).

| Catalog capability | Live AZ "play" name | Where on the site | Flagship-backed? |
|---|---|---|---|
| A. Voice / AI Phone Agent | "AI Phone Agent — answer every call, 24/7" | index / details / onepager | ✅ live on Fly.io |
| B. Reviews & Reputation | "More 5-star reviews the smart way" | details / guides | method proven; no standalone app |
| C. SEO / AEO / Web | "Get found by AI, not just Google" | index / details / guides | ✅ site live |
| D. Analytics & BI | "See across all your locations" / dashboard | details | ✅ live (HF Space) |
| E. Direct-Ordering & Margin | "Commission Rescue" | index / details / onepager | ✅ live |
| F. Retention / Lifecycle | "Win back your regulars" (CRM + loyalty) | index / details | partly built |
| (E, applied to catering) | "Catering & corporate lunches" | details / guides | ✅ recipes tool live |

**Site plays NOT yet in this catalog as their own capability** (add reuse paths as they mature):
- "End the tablet chaos" (3P apps → POS consolidation) — **flagship-proven, live 1+ year** (ledger #13);
  add as its own capability.
- "More 5-star reviews" — **flagship-proven with numbers** (~400→800+ reviews, all 5★ in ~1 yr; ledger #5).
- "Recover what the apps owe you" (chargeback/deduction recovery, contingency) — service motion, no flagship build.

**Flagship capabilities NOT yet marketed at AZ** (the growth list — see ledger rows #8–#11):
- MCP "get-cited-by-AI" connector · closed-loop AEO growth engine (retainer) · text/chat POS assistant ·
  staff handbook microapp. These are proven/available but have no named AZ offer — pure upside.

**Published pricing (as of 2026-07-01, `details.html`):** Starter **$149/mo** (Founding-5 from $79) ·
Growth **$349/mo per location** (Founding-5 $199) · Multi-unit **$299/mo per location** (Founding-5 $179).
Public floor line: "Plans from $99/mo." The private à-la-carte model (setup fees, savings guarantee,
20–25% recovery contingency) lives in `../research/pricing-strategy.md` and stays off the public site.
