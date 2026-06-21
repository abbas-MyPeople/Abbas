# Hyperlocal Restaurant Marketplace — Feasibility Analysis

**Question:** Should AZ Integrations build a city/neighborhood restaurant delivery & discovery marketplace (e.g. "Cypress Marketplace") — commission-free / low-fee, profit-sharing, shared local driver pool, AI tag-based discovery — to compete with DoorDash/Uber Eats on a fairer model?

**Scope:** US · 2024–2026 figures · synthesized from 6 research streams. Tags: **[IND]** independent/academic/gov · **[VND]** vendor · **[SOFT]** weakly sourced.

---

## ⭐ The verdict (read this first)

**Do not build a head-on DoorDash competitor. The full marketplace-with-own-fleet version is the single hardest, most capital-intensive, lowest-margin business in food tech — and it's a documented graveyard.** Nearly every restaurant-owned local delivery co-op of 2020–2022 has failed or gone on hiatus.

**But your underlying instincts are right, and there's a defensible version.** The durable winners don't run delivery logistics and don't fight for diners with ad budgets. They either (a) sell **commission-free software** and let restaurants own the customer (ChowNow, Slice), or (b) use a **franchise/share-rebate co-op** structure with deep local roots (LoCo, CHOMP).

**The version that fits AZ Integrations:** a **local "Order-Direct" discovery layer + concierge**, where you (1) build each restaurant's own commission-free direct-ordering channel, (2) plug in **white-label last-mile** (DoorDash Drive / Uber Direct, ~$7–10/order) so nobody runs a fleet, (3) aggregate the town's independents into one **AI tag-based discovery site** for local diners, and (4) run the proven **delivery→direct conversion** play (thank-you inserts, QR). You get discovery + low fees + local loyalty **without** the four walls that kill marketplaces. This is a *service + light-software* business — exactly your wheelhouse — not a venture-scale logistics bet.

---

## Why the head-on version fails — the four walls

### Wall 1 — The 30% isn't greed, it's mostly cost. You'd inherit it.
- DoorDash's actual **take rate is only ~13.5% of order value**; **EBITDA ~2.7%**. Uber's delivery arm runs **~3.6–4%**. Both became profitable only recently, after a decade and billions. [IND — SEC filings]
- The big four delivery players racked up **$20B+ in combined operating losses since IPO** fighting for share. [IND — FT/Irish Times]
- The NYC government order-level breakdown: the platform's cut is consumed by **driver pay (the biggest cost), insurance, support, refunds, payment processing, and customer acquisition.** [IND — NYC DCWP]
- **Implication:** "We'll just charge 10%" means *you* eat the costs DoorDash currently covers. The savings have to come from somewhere — your margin, or underpaid/idle drivers.

### Wall 2 — Density is the moat, and you start with none.
- McKinsey: in low-density markets "profitable instant delivery is exceptionally difficult." Delivery costs **~$1 in China vs ~$5 in the US**, driven almost entirely by **~8× population density.** [IND — McKinsey]
- Average driver does **~1.5 deliveries/hour**; only **batching** (one driver, multiple nearby orders) gets that to 2+. Batching needs order volume you won't have on day one. [SOFT/VND]
- Low volume → drivers sit idle (you pay anyway) **or** deliveries are slow (diners leave). This "liquidity trap" is what killed Maple and the co-ops. [IND — a16z, McKinsey]

### Wall 3 — Cold-start + CAC: you can't outspend the incumbents for diners.
- US share is entrenched: **DoorDash ~61%, Uber Eats ~26%, Grubhub ~6%** (end-2024). [IND — Earnest Analytics]
- DoorDash spends **$500M+/quarter on sales & marketing**; new food-app CAC is cited at **$45–85/diner** [SOFT]. You're asking a diner to install yet another app when DoorDash is already on their phone with a DashPass subscription (~75% monthly retention). [SOFT]
- A three-sided marketplace (diners + restaurants + drivers) has to solve chicken-and-egg on all sides at once. The winning playbook is **"come for the tool, stay for the network"** — start as a single-side tool, add the network later. [IND — Andrew Chen]

### Wall 4 — Running your own driver pool is a legal/insurance minefield.
- **Classification:** a self-run fleet that sets schedules or requires job acceptance risks **employee** status under the DOL economic-reality test and state ABC tests. Prop 22's contractor safe-harbor protects *app platforms*, not a small fleet operator. Misclassification = back wages, taxes, penalties. [IND/SOFT]
- **Insurance:** personal auto policies exclude delivery ("livery exclusion"); there's a "Period 1" coverage gap; you'd need commercial auto + workers' comp (**~$6.33 per $100 of payroll** for drivers) or occupational-accident insurance. [VND/SOFT]
- **Minimum-pay laws:** NYC **$22.13/hr** active time (Apr 2026); Seattle **$0.44/min + $0.74/mile + $5/offer floor.** [IND]
- **Plus** FCRA-compliant background checks (Checkr), per-city compliance, etc. **The platforms absorb all of this for you via white-label.** [IND]

---

## The graveyard — what actually happened to local co-ops

| Venture | City | Model | Status | Why |
|---|---|---|---|---|
| **Nosh** | Boulder, CO | Restaurant-owned, 15% cap, 60 drivers | **Failed Feb 2022** (14 mo) | "Ran out of runway"; no budget for DoorDash-quality app; leaned on $164K city subsidy [IND] |
| **NoCo Nosh** | Fort Collins, CO | Local co-op | **Closed Mar 2026** (~7 yrs) | "Breaking point" vs monopolized market + economy [IND] |
| **937 Delivers** | Dayton, OH | Restaurant + employee co-op, 8–14% | **Hiatus <1 yr** | Pandemic response; demand collapsed when dine-in returned [IND] |
| **ChopChop / FoodUp** | Richmond, VA | Local app → co-op M&A | **Shut Jan 2024** | Botched merger, data never transferred, dispute [IND] |
| **Locale** | San Jose, CA | YC-backed local meals | **Pivoted away 2025** | Abandoned restaurant-delivery model entirely [IND] |
| **Delivery Co-Op** | Lexington, KY | Subscription, W-2 drivers | Dormant after 2021 | No recent activity [IND] |
| **Omaha LoCo** | Omaha, NE | Co-op, 13–20% | Unconfirmed/likely gone | CARES-funded launch; no 2026 trace [IND] |

### What survives — and the pattern that matters
- **LoCo Coop / CHOMP** (Iowa City, Knoxville, Richmond, Tampa, Vegas): **survives** via a **franchise + share-rebate co-op** structure (members own shares, get profit rebates, ~10% effective commission in mature markets) and **pre-pandemic roots.** CHOMP started 2017, ~400 orders/day, 125+ restaurants. [IND/VND]
- **ChowNow** (22,000+ restaurants, $700M+ commissions saved): **survives** because it sells **commission-free software (~$199/mo + processing)** and **does NOT run delivery** — it sidesteps the money-losing logistics. [IND]
- **Slice** (~19,000 pizzerias, ~$1.95/order): **survives** by being a **vertical tool for restaurants first**, not fighting DoorDash for diners. [IND]

**The lesson is unambiguous: the survivors avoid owning delivery logistics. They win as software/enablers or as share-based co-ops — never by out-operating DoorDash on the road.**

---

## The unlock — white-label last-mile (so nobody runs a fleet)

These let a restaurant take the order on **its own** site/app and pay a flat last-mile fee. 0% commission, no fleet, no driver employment.

| Service | Pricing (2026, advertised) | Coverage | Notes |
|---|---|---|---|
| **DoorDash Drive On-Demand** | **$6.49–$10.99**/delivery; API tier ~**$9.75 base ≤5mi**, +$0.75/mi to 15mi | Broadest US | No subscription/processing/termination fees; refunds need manual request |
| **Uber Direct** | **From ~$7**; ~$6.99 base + $1.10 distance + wait fees | Broad US | 0% commission; merchant eats undeliverable "return fee" |
| **Relay** | **~$5** (e.g. $30 order = $5) | ~5 metros (NYC-heavy) | Cheapest but narrow + viability questioned |
| **Olo Dispatch / Cartwheel / Burq / Nash** | DSP quote + platform fee (not flat) | Aggregators | Route across many DSPs for best price/reliability; less lock-in; need platform subscription |
| **Metrobi** | Flat driver-pool access fee; you set route price | Local courier | No % commission |

**Caveat:** "flat fee" is rarely truly flat — distance overages, wait fees, undeliverable-return fees (merchant bears them), and middleware add-ons (Shipday +3%, aggregator subscriptions) apply. Treat advertised rates as a floor. And critically: **white-label delivers only — it brings zero discovery.** That discovery gap is exactly what the local layer adds.

---

## The defensible version for AZ Integrations (phased)

**Don't build a marketplace. Build a local order-direct *system* and grow into a light network.**

**Phase 1 — Per-restaurant (this is already your business):**
- Build each client's **commission-free direct-ordering** channel (ChowNow/Owner-style or POS-native).
- Plug in **white-label last-mile** (DoorDash Drive/Uber Direct) so they deliver without a fleet — this kills the "but I have no drivers" objection.
- Run the **delivery→direct conversion** play: thank-you insert + QR in every third-party bag ("order direct next time, save more, we handle any issues"). You recover the **15–30% commission** on every converted order. *(Best-evidenced ROI in the whole strategy.)*
- Run the **review-generation** system (tableside QR to known-happy guests) — you've already proven this doubles ratings, and each star is worth **5–9% revenue for independents** [IND — Harvard/Luca].

**Phase 2 — Local network layer (the "marketplace," de-risked):**
- Aggregate your client restaurants in a town into one **"Eat [City]" discovery site** with the **AI tag-based search** ("find the food you want") — this is the discovery diners want and white-label lacks.
- Shared logistics = **pooled white-label**, not an owned fleet. If/when density justifies it, *then* consider a shared local driver pool — structured as a **share-based co-op** (the only model that survives), never as your own W-2 fleet on day one.
- Keep it **free to diners, low flat fee to restaurants** — funded by your Phase-1 service relationships, not by burning cash on diner CAC.

**Why this works where the co-ops failed:** no fleet (no Wall 4), no diner ad war (no Wall 3), no logistics losses (no Walls 1–2). You monetize the **service** (setup + integration + ongoing optimization) you're already great at; the network is a retention/discovery bonus layered on top, not the thing you bet the company on.

---

## What this means for the website

1. **Lead with delivery→direct conversion, not "quit the apps."** Frame: *"Let the apps buy you the customer once — then own them for every order after."* Pair it with white-label delivery so the "I can't deliver myself" objection is answered on the page.
2. **Make white-label last-mile a named offering** (DoorDash Drive ~$7.99/5mi via Clover). Most owners don't know it exists; it's a concrete, credible hook.
3. **Use your review case study as proof** — "we doubled a restaurant's ratings" + "each star ≈ 5–9% revenue (independents)." This is your strongest, most rigorous number.
4. **Position as operator-led enabler, not software vendor or marketplace.** The research says the enabler wins; the marketplace dies. Your moat = you've actually run/acquired restaurants.
5. **Hold the marketplace as a vision, not a launch.** If you mention "local discovery" on the site, frame it as a community network you're *building with* clients — not a DoorDash-killer you're shipping tomorrow.

---

*Synthesized from 6 research streams: commission economics, density/logistics, white-label last-mile, cold-start/CAC, gig-driver regulation, and real co-op case studies (~50 sources). Full URLs inline above. Reliability tags applied throughout; vendor ROI and CAC figures flagged as directional.*
