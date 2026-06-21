# Wok & Karahi — AI Agentic Commerce Readiness Playbook

**For:** the owner of Wok & Karahi · 3422 FM 2920 Unit #120, Spring, TX 77388 · (281) 362-5354
**Prepared:** June 21, 2026
**Status:** Side-quest deliverable — practical implementation guide for the restaurant (separate from AZ strategy research)

> Reliability tags: **[IND]** independent/press · **[VENDOR]** company · **[SOFT]** SEO/marketing blog. Percentage-uplift figures from [SOFT] sources are directional, not guarantees.

---

## Read this first (the honest 60-second version)

1. **Full "AI agent checkout" is NOT something a single independent restaurant can plug into directly today.** OpenAI's Agentic Commerce Protocol (ACP), Google's AP2, Visa Intelligent Commerce, and Mastercard Agent Pay are all real and live — but they reach restaurants **through your POS/online-ordering vendor**, not via a one-restaurant signup. OpenAI even *scaled back* its direct-merchant checkout in early 2026 after only a handful of merchants went live. Nobody is "missing the boat" by not coding an ACP server. [VENDOR][IND]

2. **The realistic wins you can capture RIGHT NOW are three:**
   - **AI discoverability** — being the restaurant ChatGPT/Gemini/Perplexity *names* for "best halal Chinese near Spring TX." Mostly free, mostly DIY.
   - **AI voice phone ordering** — an AI that answers your phone 24/7. ~30% of restaurant calls go unanswered; the single most concrete "agentic" revenue win for an independent today.
   - **POS choice** — picking an ordering/POS platform *already wired into* the agent rails, so when ChatGPT ordering scales to your area you're in automatically.

3. **Most urgent technical problem found:** your website **wokandkarahitexas.com blocks automated visitors** — every read returned `HTTP 403 host_not_allowed`. If a bot/crawler can't read your site, **AI assistants literally cannot see your menu, hours, or address from your own site.** Fix this first.

Everything below is sequenced: **this week → this month → this quarter.**

---

## Where you stand today

- **You exist and you're well-reviewed.** ~61 Yelp reviews, "Best Halal Chinese Indo-Pak in Houston 2024," listed on Yelp, DoorDash, Instagram, Facebook, Zabihah, Novacircle, Wheree. [IND]
- **NAP:** Wok & Karahi · 3422 FM 2920 Unit #120, Spring, TX 77388 · (281) 362-5354 — make this *exact format* identical everywhere.
- **Hours** (verify current everywhere): Mon closed; Tue–Thu 11:30–4, 5–9; Fri–Sat 12:30–4, 5–10; Sun 12:30–4, 5–9.
- **Website blocks bots** (403) — platform unconfirmed because of it. *You need to tell us whether it's Wix, Squarespace, WordPress, GoDaddy, etc.* — the exact menu-markup steps depend on it.
- **On DoorDash** (commissions up to ~30%) — fine as a channel, not where you keep the customer.

---

## How AI assistants actually find restaurants in 2026

- AI assistants do NOT all read Google/Yelp reviews directly. ChatGPT leans on consensus sources; Perplexity leans heavily on **Reddit** (~47% of top citations); Google AI Overviews track normal Google rankings. A restaurant with 2,000 Google reviews can still be invisible to ChatGPT. [SOFT][IND]
- **Structured data (Schema.org) on your own site is the primary lever** AI uses to understand/trust your menu, hours, location (sites with schema reported ~2.3× more likely to be cited — directional). [SOFT]
- **Google Business Profile is still king for "near me"** and feeds Maps + AI answers (est. 30–60% of new-customer traffic for an independent). [SOFT][VENDOR]
- A study found **most restaurants are simply missing from AI recommendations**; those that show up have clean structured data, strong recent GBP reviews, and editorial/community mentions. [IND]

**Translation:** near-term AI strategy is 70% "be clean and readable everywhere," 20% "get talked about (Reddit, local press)," 10% "be on an agent-ready POS."

---

## PART 1 — FOUNDATION: make AI able to find and trust you (mostly DIY, do first)

**1.1 Fix the website 403 block (CRITICAL — this week).** AI crawlers (GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot, Google-Extended) get blocked just like my reader did. Ask your web manager/host to allow major AI/search crawlers and remove aggressive bot-blocking / "under construction" rules. On Wix/Squarespace/GoDaddy, confirm the site is published/public and no "block search engines" toggle is on. Verify: Google `site:wokandkarahitexas.com`. *Effort: Low · Impact: Critical · likely needs web person.*

**1.2 Add Schema.org structured data (this week/month).** JSON-LD for: **`Restaurant`** (name, `PostalAddress`, `telephone`, `geo`, `priceRange`, `servesCuisine:["Halal","Chinese","Pakistani","Indian"]`, `openingHoursSpecification` per shift); **`Menu`→`MenuSection`→`MenuItem`→`Offer`** (name, description, price); **`FAQPage`** (halal certified? catering? delivery? parking?). Generate free at technicalseo.com/tools/schema-markup-generator; validate at search.google.com/test/rich-results. *Effort: Medium · Impact: High · template-DIY or 1–2 dev hrs.*

**1.3 Publish a clean, machine-readable menu page (this month).** Full menu as **real HTML text** (not PDF/image — AI can't reliably read menu photos), with prices, descriptions, halal/spice/veg tags, marked up per 1.2. *Effort: Medium · Impact: High · DIY.*

**1.4 Google Business Profile — highest-ROI free work (this week + ongoing).** Claim/verify; exact NAP, both shifts, categories (primary "Halal Restaurant" or "Chinese Restaurant"; secondary Pakistani/Indian), attributes (halal, dine-in, takeout, delivery, catering); upload **5–10 food photos/month**; add menu + an **"Order Online" link to your own page**. *Effort: Low · Impact: Very High · DIY — the #1 thing you personally should do.*

**1.5 Consistent NAP + reviews everywhere (this month + ongoing).** Byte-identical NAP on Yelp, DoorDash, FB, IG bio, Zabihah, **Apple Business Connect** (free, feeds Siri), **Bing Places** (feeds Copilot). Routinely ask for Google reviews (QR/receipt). Get genuinely mentioned where AI reads (a real r/houston "best halal Chinese" thread, a local food blogger, a Houston "best halal" listicle). *Effort: Low–Medium · Impact: High · DIY.*

---

## PART 2 — EMERGING AGENT STANDARDS: what's real, what to do (and NOT do)

As an independent, you do NOT build these yourself — you ride them via your POS.

| Standard | What it is | Status for a small restaurant (2026) | What you do |
|---|---|---|---|
| **OpenAI ACP + Stripe** (Instant Checkout) | Open standard for AI agents to buy; live for Etsy, rolling to Shopify | **Beta; not restaurant self-serve.** Needs product feed + 5 REST endpoints + Stripe Shared Payment Tokens (dev effort); OpenAI scaled back direct checkout in 2026 | **Don't build it.** Get it via POS (Part 3) |
| **Google AP2** | Open agent-payments protocol (signed mandates); 60+ partners, v0.2 Apr 2026 | **Infrastructure for networks/platforms,** not restaurants | Nothing direct; your POS/processor adopts it |
| **Visa Intelligent Commerce / Mastercard Agent Pay** | Card networks letting AI assistants pay via tokenized cards | **Network/enabler level** | Ask your processor (Square/Toast/Stripe) if enabled |
| **llms.txt** | Text file listing key pages for AI | **Low-cost, low-yield today**; AI search crawlers mostly ignore it | Optional 30-min `/llms.txt`; don't prioritize over Parts 1 & 4 |
| **MCP** | Open standard to expose tools/data (menu/ordering API) to agents | **Real but a developer feature**; no turnkey restaurant product yet | Skip now; revisit in 6–12 mo |
| **Product/menu feeds** | Structured catalog files AI indexes | **The practical on-ramp** | Covered by Parts 1 & 3 |

---

## PART 3 — ORDERING & PAYMENTS: get your menu where agents can transact

Key 2026 development: **agent checkout is arriving through POS/ordering platforms, not direct.** Example — **Bites** launched on ChatGPT (Apr 15, 2026): diners order in ChatGPT with no marketplace markup, and **restaurants are opted in automatically via their POS** ("the restaurant doesn't have to do anything"). [IND]

**Your ordering strategy: own a first-party, agent-readable ordering channel AND be on POS rails the agents are wiring into.**
- Stand up **commission-free first-party online ordering** tied to your site + GBP: **Square Online** (free/low-cost, simple), **Toast** (full POS, deep integrations), or **ChowNow** (commission-free, integrates 20+ POS). Gives Google "Order Online" a destination and keeps your customer.
- **Pick the POS as a strategic bet.** Ask each vendor: *"Are you integrating with ChatGPT/Bites/agentic ordering, and will my menu be exposed to AI shopping agents automatically?"* The right answer future-proofs Part 2 with zero dev work.
- Keep DoorDash for reach, but drive repeat customers to your own link.
- Payments: on Stripe/Square/Toast you're already positioned for agent payment rails as they switch on.

*Effort: Medium · Impact: High · setup DIY, vendor choice deliberate.*

---

## PART 4 — VOICE AI: your most realistic "agentic" win TODAY

~30% of calls go unanswered during rushes = lost orders and catering leads. An **AI voice agent** answers 24/7, takes orders/reservations, answers "are you halal?/hours?/do you cater?", pushes to POS. The one agentic capability an independent can fully deploy now with clear ROI.

- **ConverseNow** — purpose-built AI phone ordering, POS integration (Deliverect), handles simultaneous calls. [VENDOR][IND]
- **Slang.ai** — calls, reservations, FAQs; good for a smaller independent. [IND]
- Others: Revmo AI, Voiceflow (DIY/no-code).
- **Rough cost:** ~$0.05–$0.35/min; typical small-business **~$200–$600/mo** light use, up to **$500–$1,500/mo** higher volume. [IND] For your volume, expect the lower end.

*What you do:* demo Slang.ai + ConverseNow; pick on POS integration + ability to speak naturally about halal/spice/catering; confirm human transfer + two-shift hours. *Effort: Medium · Impact: High & measurable · mostly DIY.*

---

## PART 5 — EXPECTED UPLIFT & REALISTIC EXPECTATIONS (honest)

**Real today (0–6 months)**
- **GBP optimization + reviews + photos:** well-run GBP ≈ 30–60% of new-customer traffic for a competitive-metro independent; realistic incremental gain in Maps/"near me" orders and calls over 1–3 months. [SOFT]
- **Schema + readable menu + fixing the 403:** moves you from "AI can't see me" to "AI can name and quote me" — the difference between invisible vs. recommendable in ChatGPT/Gemini/Perplexity.
- **AI voice agent:** recover even half of unanswered calls = direct, countable lift — usually the fastest payback here.
- **First-party ordering:** every order moved off DoorDash saves up to ~30% commission.

**Positioning for 2026–2027 (true agent checkout)**
- **ChatGPT/Bites-style in-chat ordering** is live, rolling out via POS partners by region — likely reaches Houston-area independents over the next several months to ~18 months, **automatically if you're on the right POS.**
- **Full agent checkout (ACP/AP2/Visa/Mastercard)** for a standalone restaurant remains gated/enterprise. Don't pay anyone to "ACP-enable your restaurant" now.

**What success looks like**
- **3 months:** named when you ask ChatGPT/Gemini/Perplexity "best halal Chinese in Spring TX"; GBP fully optimized w/ growing recent reviews; AI voice agent live; first-party ordering link on site + GBP.
- **6–12 months:** POS-driven menu exposed to ≥1 AI ordering channel; measurable share of orders direct rather than via 30% marketplaces.
- **Don't expect:** a flood of autonomous AI purchases in 2026 — that's the 2027+ scenario you're positioning for.

---

## PART 6 — PRIORITIZED CHECKLIST

**THIS WEEK** (highest impact, lowest effort)
- Fix website **403 / bot-blocking** — *Critical · web person/host*
- **Claim + fully optimize Google Business Profile** — *Very High · DIY*
- Upload **5–10 food photos** to GBP — *High · DIY*
- Tell us **what platform the site is on** — *enables next steps · DIY*
- Claim **Apple Business Connect** + **Bing Places** — *Medium · DIY*

**THIS MONTH**
- Publish **full HTML menu with prices** — *High · DIY/Dev*
- Add **Schema.org** Restaurant + Menu/Offer + FAQ + hours + geo; validate — *High · Dev 1–2 hrs or template*
- **Standardize NAP** across all listings — *High · DIY*
- Launch **AI voice agent** (demo Slang.ai + ConverseNow) — *High · DIY + vendor*
- Start a **review-generation routine** — *High · DIY*

**THIS QUARTER**
- Stand up **commission-free first-party ordering** (Square/Toast/ChowNow); link from site + GBP — *High · DIY + vendor*
- **Choose POS as a strategic bet** — confirm ChatGPT/Bites/agent-ordering integration — *High (future-proofing) · decision*
- Seed **editorial/Reddit/local-blog mentions** — *Medium–High · DIY*
- (Optional) add **`/llms.txt`** — *Low · DIY/Dev*
- Re-test: ask ChatGPT/Gemini/Perplexity "best halal Chinese near Spring TX" — *measurement · DIY*

**Explicitly DON'T do now:** pay to "ACP/AP2-enable" a single restaurant; build a custom MCP server; prioritize llms.txt over GBP/schema/voice/ordering.

---

## One thing needed to finish the technical steps
The website blocks bots (403), so its platform is unconfirmed. **Identify what it's built on** (Wix, Squarespace, WordPress, GoDaddy, Toast/Square site, custom) → then the exact click-path for menu schema + Order Online link can be specified.

---

*Sources (full URLs) retained in the research transcript; key references: OpenAI/Stripe ACP docs, Google AP2 (cloud.google.com, ap2-protocol.org), The Paypers (Visa Intelligent Commerce), Forrester (agentic payments), PR Newswire & Restaurant Business Online (Bites on ChatGPT), TechNewsWorld (restaurants missing from AI recs), Malou/SOCi/Birdeye/Search Engine Land (schema/GBP/AI discoverability), ConverseNow/Slang.ai/Aircall (voice AI), aeo.press (llms.txt). All protocol statuses verified against multiple 2026 sources; the 403 issue verified directly.*
