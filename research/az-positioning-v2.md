# AZ Positioning v2 — the FDE thesis (canonical strategy doc)

*The captured conclusion of a long working session (founder research on 56 restaurant-tech companies +
the flagship code audit + first-principles strategy). This is the foundation the v2 website and pitch
are built on. Internal document — plain-English owner-facing language is derived from it, not equal to
it.*

---

## 1. The identity: the Forward-Deployed Engineer for restaurants

AZ is not a "restaurant tech consultant." It is the **forward-deployed engineer (FDE) for independent
restaurants** — the person who comes in, builds and wires up the AI systems a restaurant could never
assemble itself, and *runs* them.

**Why this is grounded, not a leap:** the FDE model is the most-validated new business model of the
moment. Palantir built a multi-billion-dollar company on forward-deployed engineers; OpenAI, Anthropic
and every serious AI company are now racing to hire them — *because AI capability has outrun customers'
ability to integrate it themselves.* "The FDE for [vertical]" is the pattern of the decade. No one has
aimed it at restaurants. That resolves the earlier "is an integrated platform for indies grounded?"
worry: the precedent isn't "someone integrated for restaurants," it's "the FDE model is proven and
rising, and restaurants are an open lane."

## 2. The proof stack — why AZ does NOT need an external client first

Two proofs at opposite ends of the market, which together beat any single local logo:
- **Enterprise:** Abbas deployed **Hard Rock Cafe's first production AI agents (3), plus the
  observability stack, agent maintenance, and surrounding integration**, as a **Senior Solution
  Architect & Sales Engineer (WSO2).** → *"I built and shipped this for a global hospitality brand."*
- **Owner-operator:** he runs the same class of systems on **his own restaurant (Wok & Karahi)**. →
  *"And I run it on my own place — so I've made every mistake on mine, not yours."*

The one-liner: **"I did it for a global chain. I do it on my own restaurant. Now I do it for yours."**
> ⚠️ ACCURACY/BRANDING TO CONFIRM before public use: exact titles/dates/scope wording for Hard Rock &
> WSO2; logo-usage rights (Hard Rock is a trademark — use "worked with"/case-study framing unless
> permission exists); and reconcile the site's current "ex-Google engineer" claim with what is
> verifiable. The brand is honesty — every credential on the site must be exactly true and defensible.

## 3. The first-principles core — the one commonality under everything AZ does

Reduce a restaurant to its money equation and every AZ capability collapses to one thing:

> **Each product = one department of a big chain's corporate machine, delivered as an AI system by an
> FDE.** Chains have marketing, a call center, revenue management, CRM/loyalty, finance/BI, data
> science. AZ gives an *independent* all of them — as AI, built and run by one person. *That* is what
> "chain-grade at indie prices" actually means, with a mechanism.

### The money map (the 6 buckets)
| # | The job | Chain dept it replaces | AZ capabilities | Value type |
|---|---|---|---|---|
| 1 | Get Found | Marketing / SEO | AEO/SEO, Google profile, AI-answer optimization, local pages | Make money (demand) |
| 2 | Win the Order | Call center + web/app | AI phone agent, first-party ordering, website | Make money (convert) |
| 3 | Grow the Order | Revenue management | upsell, menu engineering, self-optimizing menu/pricing, catering | Make money (bigger) |
| 4 | Keep the Guest | CRM / loyalty | reviews engine, loyalty, win-back/SMS, guest identity (CDP), 3P→1P | Make money (repeat) |
| 5 | Keep the Money | Finance / procurement / ops | true-net P&L, tablet consolidation, labor/food cost, fee strategy | Save money (margin) |
| 6 | The Brain | Corporate HQ / data science | analytics, dollar-ranked judgment loop, growth engine, monitoring | Optimize + run 1–5 |

1–5 are the value chain (demand → order → bigger → repeat → margin); **6 is the operating layer that
runs and auto-optimizes the other five** — the frontier and the moat.

### The 5 invariants (the pattern under every capability — this is the brand)
1. **A chain department, not a tool** (replaces budget/headcount, not a SaaS feature).
2. **Delivered — built *and run* — by AI + an FDE**, not sold as software you operate.
3. **Grounded in your real dollars** (measured true-net, not vanity metrics).
4. **Owner-gated and safe** (nothing acts on your business without approval).
5. **One throat, fully integrated** (the systems talk to each other — the reason chains win).
No competitor satisfies all five: a tool vendor breaks 1/2/5, an agency breaks 2/3, a POS vendor
breaks 3/4. AZ is the only one — *because it's an operator-engineer running an FDE model.*

## 4. The moat (evolved, honest)
Not the tool list, not any feature (all copyable in days — the audit says so). The durable moat is the
combination: (a) the **dollar-grounded judgment layer** (24 months of real statements + POS fused into
a ranked, falsifiable model of where the next net dollar is); (b) the **safety/authority doctrine** for
letting AI act on a live business (forged through real incidents — "arguably AZ's real IP"); (c) the
**FDE delivery at AI-collapsed cost**; compounding into a (d) **cross-client learning flywheel** (every
restaurant onboarded makes the model + doctrine smarter/safer for the next). **Status: real but
LATENT** — today it's a bespoke single-tenant lab; the autonomous loop has never closed once. The one
move that converts latent→real: **extract the per-restaurant config layer (`client.yaml`)** so a second
restaurant is onboarding, not a rebuild. (See §7.)

## 5. Breadth verdict
**Asset — as long as you sell narrow.** Breadth of *delivery* is the cure for the owner's #1 pain
(fragmentation) and the moat. Breadth of *message* is the liability. Rule: **sell one number, deliver
the platform, become the operating system.** (Enter through one bucket's dollar wedge; reveal the whole
map only after.)

## 6. The language rule — internal frame vs. what the owner hears
The owner has never heard "FDE." Never say it to them. Translate everything into their worldview + dollars:

| Internal (this doc) | What the owner hears |
|---|---|
| Forward-deployed engineer | "I come in, set it all up, and run it for you." |
| Chain department as AI | "The stuff big chains have a whole team for — done for your place." |
| The judgment loop / true-net | "I'll show you which items and channels actually make you money." |
| Closed-loop growth engine | "I watch your numbers every week and keep making it better." |
| AEO / GEO | "So ChatGPT and Google send people to you." |
| CDP / guest identity | "Your own customer list — that you actually own, not the apps." |
| Platform / moat / operating system | (never said to the owner) |

**Entry wedge (recommended, still open):** lead with **#5 "see your true numbers"** (only an
operator-engineer can show an owner their real per-item/channel/daypart net) or the **AI phone agent**
(tangible, demoable). NOT delivery commissions (commodity, and — for Wok — intentional CAC). Decide the
one wedge before the site copy is finalized.

## 7. Honest guardrails (protect the trust that IS the brand)
Do not publish what the code can't back (the audit caught these): no "872 reviews" until verified; no
"AI answers your line today" until the main line is cut over; no "autonomous engine running" until one
full loop is recorded; "commission rescue" is a capability + the measured *drag*, not a *recovered*
result. **Hard Rock + Wok & Karahi are the real proof — lead with them.**

## 8. The path (latent → real)
1. Extract the **config layer** (`client.yaml`) → lab becomes deployable. *(highest leverage)*
2. **Close one autonomous loop** end-to-end and record it → the boldest claim becomes demonstrated.
3. Manufacture **real deltas** (review count, GBP post-launch, QR/direct + catering baselines run
   clean, voice-agent main-line cutover) → the case study gets hard numbers before the restaurant sale.
