# Build Status Ledger — complete / incomplete / what's left

*Compiled from the independent flagship code audit (WokAndKarahiTexas.com, commit 624f946, 2026-07-11)
+ this AZ repo. Status vocabulary: **LIVE** (in production for its users) · **DEPLOYED-INTERNAL**
(running but gated/not on final channel) · **BUILT-NOT-DEPLOYED** · **SPEC/EARLY**. Statuses are from
the audit's own findings, not marketing copy. Use this to decide what to finish first.*

---

## A. Flagship (Wok & Karahi) systems — the proof engine
| System | What it does | Status | What's left to finish |
|---|---|---|---|
| **website-v2** (AEO site) | Public AI-readable site, static-rendered menu, schema, llms.txt | **LIVE** | Automated menu **price-sync** (menu.json is regenerated manually → prices can drift from Clover). |
| **growth_brain** | Daily whole-business advisor; top-3 money-ranked moves emailed 7am | **LIVE & PROVEN AUTONOMOUS** (3 bot commits, 29 caches, 3 real briefs) | Nothing critical — this is the one proven autonomous piece. |
| **reports / Daily reports** | Nightly sales email (channels, tenders, dayparts, 3P P&L, top items) | **LIVE** | None (Jul 2–8 outage root-caused, fixed, backfilled). |
| **analytics** (Control Plane) | BI: sales/kitchen/money/website, true-net reconciliation, Groq chat, /apps portal | **LIVE (internal, gated)** | Multitenant/config extraction (per-restaurant maps are code, not config). |
| **clover-analysis** | 90-day order deep-dive + fee model + books reconciliation | **BUILT & RUN** (one-shot, Jun 2026) | Complete for Wok; re-run per client at onboarding. |
| **voice-agent** ("Haniya") | ~28 Vapi tools, gated Clover order-writes, reservations, complaints, spam screen | **DEPLOYED-INTERNAL** (own Vapi #; orders OFF; main line not forwarded) | ① flip **main-line forwarding** (one KDS-staff confirmation away) ② turn **orders ON** ③ full **Urdu/Hindi** transcription (currently English-only) ④ fix 2 failing persona tests ⑤ start a **call ledger** (no metrics exist). |
| **rewards** (CDP + receipt-scan spin-wheel) | Guest identity/CDP, OTP, OCR receipt verify, guest-360, campaigns | **DEPLOYED, ZERO USAGE** | Activate the **QR faucet** (deferred ~Aug; QR currently points to Clover ordering); capture first members/spins data. |
| **seo_engine** (closed-loop "living website") | Sense → propose ≤3 → email/portal approve → auto-commit/merge | **DEPLOYED, PARTIALLY OPERATIONAL** | **Never completed one autonomous cycle.** ① build executors for more rules (2 of ~12 done) ② **close & record ONE full loop** ③ portal flow (email leg retired 07-10). |
| **operator** ("constitution" + ledger) | Authority tiers, playbooks, backlog, briefs, value model | **SPEC + SCAFFOLD** | Wire the automation (inbox cursor null; 1 brief; work was done in interactive sessions, not autonomous). |
| **admin** (Manager Agent over SMS) | Claude Code + repo shell via Twilio SMS | **BUILT-NOT-DEPLOYED** | Add one Anthropic API key + deploy (wok-admin on Fly). |
| **chat** | Owner mobile analytics chat over Clover | **DEPLOYED-INTERNAL** | Rotate weak default creds; otherwise done. |
| **employees** | Handbook portal + Q&A | **DEPLOYED-INTERNAL** | Minor; per-client data swap. |
| **recipes** | Recipe scaling + catering portion calculator | **DEPLOYED-INTERNAL** | Minor. |
| **mcp-server** | Menu/info/catering tools inside ChatGPT/Claude | **BUILT & PUBLISH-INTENT** | Static data only — no live ordering / hosted endpoint yet. |
| **email-campaign** | Bulk promo emailer + ~530 contacts | **BUILT (manual run)** | Schedule/automate if wanted; PII-custody plan. |
| **marketing** (print QR cards) | Spin & Win + review QR cards | **BUILT** | QR currently → Clover ordering; point to /game when the faucet opens. |
| **self-optimizing menu** | Dynamic pricing/deals from POS+search demand, owner-gated, A/B | **SPEC / EARLY BUILD** | The frontier SKU — build it; sell the direction, not a result yet. |

## B. AZ (this repo / azrestaurantpartners.com) systems
| System | Status | What's left |
|---|---|---|
| **Marketing site** (index/details/toolbox/guides + ~33 guides + 101 tool pages, calculators, glossary, comparison pages, case-study) | **LIVE** | **v2 redesign** around the FDE/money-map positioning (next deliverable). Fix overstated claims (872 reviews, bilingual-live, engine-running). |
| **growth_engine** (AZ port of seo_engine) | **BUILT, ARMED — no signal yet** | 2 owner steps: grant GA4 service-account access to the AZ property + add reused secrets. Then it produces findings. Same "close one loop" gap as flagship. |
| **command** center (dashboard, worklog, portfolio) | Exists | Living ops dashboard; keep updated. |
| **flagship/** bridge (capability ledger, case study, sync protocol) | Living | Reconcile ledger against the audit's real statuses (this doc). |
| **research/** corpus | Living | Where all strategy lives (founder playbook, moat, this ledger, positioning v2). |

## C. Cross-cutting — the things that aren't a single app (highest leverage)
| Item | Status | Why it matters |
|---|---|---|
| **Per-restaurant config layer (`client.yaml`)** | **NOT BUILT** | The single move that turns "bespoke lab" → "deploy to client #2." Consumed by rewards/analytics/voice/growth_brain. **#1 priority for the whole business.** |
| **Secrets rotation + history scrub** | **OPEN** (owner has a plan) | Repo tracks live Clover token/keys/PII in "full backup mode." |
| **Real deltas / proof numbers** | **PARTIAL** | Baselines are world-class; before/after is thin. Needs: Places API review count, GBP post-launch pull, QR/direct + catering baselines run clean, voice main-line cutover. Get these **before the restaurant sale**. |
| **Restaurant sale (~2 months)** | In motion | Kept as the AZ demo; compresses the window to capture live deltas. |

---

## D. Critical path — what to finish, in order
1. **Config layer (`client.yaml`)** — converts lab → product; unblocks every "deploy many" claim.
2. **Close ONE autonomous loop** (seo_engine or AZ growth_engine) and record it — turns the boldest claim from "armed" to "demonstrated." (AZ side needs the 2 GA4 owner-steps first.)
3. **Voice-agent main-line cutover** (one confirmation) → starts a real call ledger.
4. **Capture deltas** before the sale: review count, GBP delta, QR/direct + catering.
5. **AZ website v2** (positioning rebuild) — separate track, can run in parallel.
6. **Rewards/CDP faucet** activation + first usage data.

### Snapshot: what's DONE vs. LEFT
- ✅ **Done / live:** the AEO site, growth_brain (autonomous), daily reports, analytics control plane, clover-analysis, the AZ marketing site + content engine, the voice agent's *build*, the rewards *build*.
- 🟡 **Built, needs flipping on:** voice main line + orders, rewards QR faucet, admin (1 key), AZ growth_engine (2 owner steps).
- 🔴 **Not done / the real work:** the config layer, one closed autonomous loop, real deltas, the self-optimizing menu, the AZ v2 site.
