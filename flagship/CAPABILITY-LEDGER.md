# Capability Ledger — the Wok & Karahi → AZ bridge

> **This is the single source of truth for "what have we proven, and is it productized yet?"**
> Every capability AZ Restaurant Partners sells should trace to something proven on the flagship
> (Wok & Karahi, Abbas's own restaurant / test business). When a capability ships or changes at the
> flagship, update the matching row here — that is how restaurant R&D becomes AZ product without
> anyone re-synthesizing it by hand. See [`SYNC-PROTOCOL.md`](SYNC-PROTOCOL.md) for the ritual.

**Legend — Flagship status:** 🟢 live · 🟡 built/deployed (non-public app) · 🔵 spec'd, build pending · ⚪ advisory only (not a flagship build).
**Legend — AZ status:** ✅ marketed as a named play + priced · 🟠 marketed but thin (no proof/case) · 🔴 proven at flagship but NOT yet a marketed AZ offering (**opportunity**) · ⚪ marketed with no flagship proof (**flag**).

Last reconciled: 2026-07-01 (from full audits of both repos).

---

## A. Capabilities proven at the flagship → mapped to AZ offerings

| # | Capability | Flagship proof (where it lives in the Wok repo) | Flagship status | AZ offering name (site) | AZ status | The gap / next move |
|---|---|---|---|---|---|---|
| 1 | **AI Phone Agent** (POS-integrated ordering, catering, upsell, multilingual, warm-transfer) | `voice-agent/` — live on Fly.io (`app=wok-voice`), 24 Vapi tools, English+Urdu/Hindi, gated Clover writes, 15-persona QA gate | 🟢 | "AI Phone Agent — answer every call, 24/7" | 🟠 | Named & priced, but **no proof/demo/case**. Highest-value needle: surface the live flagship agent as proof (recording/transcript/number). |
| 2 | **AEO/SEO website** (AI-crawler-readable, entity schema, static-rendered menu, local pages) | `website-v2/` — live at wokandkarahitexas.com; fixed the "403-to-bots" problem | 🟢 | "Get found by AI, not just Google" (local SEO + GEO) | 🟠 | Marketed; the flagship before/after (403 → AI-readable) is the perfect proof story and isn't shown. |
| 3 | **Sales analytics + true-net P&L** (conversational BI over POS, channel economics, menu engineering) | `analytics/` — live (HF Space); `docs/dashboard-v2/` true-net reconciliation spec | 🟢 | "See across all your locations" / dashboard-BI | 🟠 | The "true net vs card-only illusion" reconciliation is a differentiated SKU; not yet articulated as its own offer. |
| 4 | **Direct-ordering / commission rescue** (push demand off ~30% 3P, tracked links, attribution) | `website-v2/` order CTAs + voice steering + `clover-analysis/` fee model + **the physical "thank-you note in every bag" tactic, customized per order type** — the 3P note says *"Paying up to 50% extra?? Order on our website, save big"* (evidence: `assets/wok-3p-to-direct-thankyou-card.png`). Direct value stated on card: delivery within 5 mi for **$7.99**, no extra fees, cheaper prices, more deals. | 🟢 | "Commission Rescue" | ✅ | **Proven in the real world, not just online.** Strong AZ copy: the "up to 50% extra" framing + the order-type-customized insert is a turnkey, low-tech tactic any client can run day one. Quantify the direct-vs-3P shift once owner supplies it. |
| 5 | **Reviews / reputation engine** (positive-solicit + negative-intercept, in brand voice) | Real, live **two-track system at the flagship**: (a) a *"Scan me"* QR card brought to the table **only when a guest is visibly happy** (primed by reminding them of the experience → high scan rate); (b) if a guest is unhappy, the **owner's business card** is offered so they raise it directly with the owner — **intercepting the negative review before it posts**. | 🟢 | "More 5-star reviews the smart way" | 🟠→✅ | **Proven with hard numbers: reviews doubled ~400 → 800+ in ~1 year, and all-five-star since adopting it.** This is the flagship's best social-proof result. Package the *filter-and-intercept* method as the AZ reviews offer; a software layer (auto-solicit/respond) is the upsell on top. |
| 6 | **Retention / loyalty / win-back / SMS marketing** (returning-caller memory, consent-based SMS loyalty + win-back campaigns, "the usual") | `voice-agent/` loyalty + `caller_history` + `sms_notify` (SMS plumbing live); `email-campaign/` consent-aware sender. **SMS loyalty/win-back is in active build now — near-complete, one test send done; not yet fully rolled out.** | 🔵 (near-complete) | "Win back your regulars" (CRM) | 🟠 | Returning-caller memory + SMS plumbing are real. Owner is comfortable presenting this as a current capability given it's close to done — **but keep this ledger honest: it's rolling out, not fully live.** Surface as "available" on the site is the owner's call; don't publish a *result* until there is one. |
| 7 | **Catering / corporate-lunch engine** (portion sizing, quote routing, occasion pages) | `recipes/` portion tool (live, Render) + voice `catering.py` + `docs/07`,`docs/14` | 🟢 | "Catering & corporate lunches" | ✅ | Strong. The "how much food do I need?" engine is a concrete, demoable widget. |
| 8 | **MCP connector** (per-restaurant menu/hours/ordering natively inside Claude/ChatGPT) | `mcp-server/` — publishable to npm/Smithery, 6 tools | 🟡 | — | 🔴 | **OPPORTUNITY: proven, cheap, differentiated — not marketed at all.** Natural add to "Get found by AI." |
| 9 | **Closed-loop AEO/SEO growth engine** (MEASURE→DIAGNOSE→DECIDE→ACT→VERIFY, auto-PRs, ~$10–35/mo) | `docs/aeo-seo-engine/MASTER-PLAN.md` (+5 workstreams) | 🔵 | partially under "Get found" | 🔴 | **OPPORTUNITY: the strongest recurring-retainer product in the repo.** Package as a monthly "AI-visibility growth engine." |
| 10 | **Text / chat POS assistant** (customer/owner conversational layer over live POS, two-pass fetch) | `chat/` — deployed (Render), OpenRouter, 5-min Clover cache | 🟡 | — | 🔴 | OPPORTUNITY: the text sibling of the voice agent; low marginal cost to offer. |
| 11 | **Staff handbook / onboarding Q&A microapp** | `employees/` — deployed (Render), handbook search/Q&A | 🟡 | — | 🔴 | Minor SKU; easy re-skin per client. Optional add-on. |
| 12 | **Client-onboarding data pipeline** (pull a client's Clover catalog+orders, reconcile fees, build money model, auto-gen content) | `clover-analysis/` — offline toolkit | 🟡 | (internal delivery capability) | n/a | Not a customer-facing SKU — this is *how AZ onboards*. Keep internal; it makes every other SKU cheaper to deliver. |
| 13 | **Tablet consolidation** (3P delivery apps → the POS, so orders flow straight to the kitchen — no manual re-entry) | **Live at the flagship for 1+ year:** third-party orders now land directly in the **Clover POS** and print to the kitchen automatically. Before: staff had to manually accept on each delivery tablet then **re-key** the order into the POS to print a ticket — which, during rushes, caused **lost, late, and incorrect orders**. | 🟢 | "End the tablet chaos" | 🟠→✅ | **Corrected: this IS flagship-proven, 1+ year live** (was wrongly listed as advisory-only). The pain story — manual re-entry → lost/late/wrong orders in a rush → fixed — is exactly the buyer's daily headache. Add the flagship result as proof. |

| 15 | **Self-optimizing menu — intelligent understanding + dynamic pricing/deals** (fuse Clover orders + SEO search demand + timing + deal performance → an intelligence layer that writes back to the Clover menu with dynamic pricing & auto-generated deals, **owner-authorized first, with proof + A/B testing**) | New project in early build at the flagship; builds on `analytics/` + `docs/aeo-seo-engine/` (closed-loop MEASURE→DECIDE→ACT→VERIFY) + gated Clover writes proven in `voice-agent/clover_order.py`. | 🔵 (early build) | — | 🔴 | **The most differentiated future SKU in the whole portfolio** — a menu that prices and merchandises itself from real demand, gated by owner approval and validated by A/B tests. No competitor for independents does this. Frame as the "Optimize/Transform" tier's flagship offer. Honest status: just beginning — sell the *direction*, don't claim a delivered result yet. |
| 16 | **POS / order-flow efficiency** (table-level order attribution, phone capture at the table, spice-level & order-detail standardization) | Live at the flagship — orders tagged to the specific table, phone numbers captured, order details (e.g. spice) handled more consistently. | 🟢 | (part of ops/onboarding) | 🔴 | Small but real operational wins that compound. Bundle into the onboarding/optimization engagement rather than a standalone SKU. |

## B. AZ offerings marketed as a service (no flagship product artifact — fine, just label honestly)

| # | AZ offering name (site) | Backing | Status | Note |
|---|---|---|---|---|
| 14 | "Recover what the apps owe you" (chargeback/deduction recovery, 20–25% contingency) | Advisory / service motion | ⚪ | Real offer; no flagship artifact. Fine — label it a service, not a product. |

---

## C. How to read this for "shifting the needle"

- **🔴 rows are the growth list** — capabilities you've already *paid for* by building them at the flagship, but AZ isn't selling. Turning these into named offers is pure upside (no new build). Priority: #8 MCP connector and #9 AEO growth engine (recurring revenue), then #10 chat.
- **🟠 rows are the proof list** — marketed but thin. The fix isn't more building; it's *surfacing the flagship proof* (the live voice number, the 403→AI-readable before/after, the true-net reconciliation). This is the AZ site's own #1 conversion gap. See [`case-study-wok-and-karahi.md`](case-study-wok-and-karahi.md).
- **⚪ rows are the honesty list** — keep them, but never let the site imply flagship proof that doesn't exist.

## D. Cross-references
- Full offering catalog with reuse paths & onboarding playbook → [`capabilities-catalog.md`](capabilities-catalog.md)
- The voice-agent philosophy/engineering template → [`voice-agent-playbook.md`](voice-agent-playbook.md)
- The flagship case study (fills the proof gap) → [`case-study-wok-and-karahi.md`](case-study-wok-and-karahi.md)
- Live AZ pricing/plays → `../details.html`; private pricing model → `../research/pricing-strategy.md`
