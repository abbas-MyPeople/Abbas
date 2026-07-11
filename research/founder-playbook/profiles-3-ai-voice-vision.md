# Restaurant AI Companies — Deep Profiles (Batch 3: Voice & Vision)

*Prepared for AZ Restaurant Partners — founder's-playbook research series.*
*Compiled 2026-07-11. Sources cited inline as (source: domain). Where facts are thin or single-sourced, this is flagged as UNVERIFIED. Nothing here is fabricated; gaps are stated plainly.*

Companies covered: **Slang.ai, Loman.ai, Newo.ai, ConverseNow, SoundHound (restaurant voice AI + SYNQ3), Hi Auto, Loop (tryloop.ai), Voosh, Agot AI, PreciTaste, Popmenu.**

A note on the landscape: these companies cluster into three sub-categories, and the category shapes the entire playbook:
1. **Front-of-house voice AI** (Slang, Loman, Newo, ConverseNow, SoundHound, Hi Auto, Popmenu's AI Answering) — answering phones / taking drive-thru orders.
2. **Back-of-house / kitchen computer vision** (Agot AI, PreciTaste) — order accuracy, prep forecasting, waste.
3. **Delivery/marketplace financial intelligence** (Loop, Voosh) — reconciliation, dispute recovery, "AI" more as data automation than conversational AI.

---

### Slang.ai

- **What it is / category.** Front-of-house voice AI for hospitality. An AI phone agent that answers restaurant calls 24/7, handles FAQs, and books/manages reservations by integrating with OpenTable, SevenRooms, Resy, etc. Positioned specifically at full-service / reservation-driven restaurants rather than QSR drive-thru (source: slang.ai; forbes.com).

- **Founders & backgrounds.** Alex Sambvani (CEO) and Gabriel "Gabe" Duncan (CTO). Both are **data scientists, not restaurant operators** — they met on Spotify's data-science team building personalized voice AI at scale. They won an internal Spotify hackathon (out of 100+ ideas) with a "personality-forward" voice AI app, which became the creative seed for Slang (source: slang.ai; underscore.vc). This is a classic ex-big-tech ML-researcher founding pair.

- **Founding story.** Founded 2019. Origin insight: consumer voice assistants (Alexa/Google) had normalized talking to machines, but small businesses — especially restaurants — were drowning in unanswered phone calls with no affordable way to capture them. The wedge was *personality* (a branded, warm-sounding voice agent) rather than raw automation. Built on speech recognition + dialog management; over time layered in LLM capability. Emerged from stealth June 2023 (source: slang.ai; underscore.vc).

- **Funding history.**
  - Seed (pre-2023, amount not cleanly disclosed).
  - **Series A — $20M, June 2023**, led by Homebrew; participation from Stage 2 Capital, Wing VC, Underscore VC, Active Capital, Collide Capital. Notable angels: chef Tom Colicchio and Scott Belsky (Behance founder) (source: slang.ai; gunder.com; finance.yahoo.com).
  - **Series B — $36M, Feb 2026**, led by US Venture Partners (USVP): ~$28M equity + $8M debt. New investors: Thayer Investment Partners, ex-Stripe COO Claire Hughes Johnson; existing backers Homebrew, Stage 2, Underscore, Collide (source: finsmes.com; finance.yahoo.com).
  - **Total raised ≈ $68M.** Status: active, scaling. (PitchBook/CB Insights list the entity under a legacy name "Gablex.")

- **First customers & early GTM (KEY).** Slang went after **independents and small multi-unit full-service groups first**, not chains. The wedge was concrete and narrow: *missed reservation calls = lost revenue*. Their proof points are ROI-framed — restaurants report **50% more phone reservations, ~96% guest satisfaction, up to 200 staff-hours saved/month, ~10x ROI** (source: slang.ai). A representative early/reference customer is **Fearless Restaurants** (14 locations, 2 hotels, 1,500+ employees) — explicitly positioned as "augment, don't replace" staff (source: forbes.com). **Pricing is transparent per-location SaaS:** Core ~$399/mo per location; Premium ~$599/mo per location (adds custom branding, performance insights, bilingual support); customized by call volume/locations (source: slang.ai/pricing). This transparent, self-serviceable, per-location model is the opposite of the enterprise-RFP motion the QSR voice players run.

- **Evolution & pivots.** No major pivot; steady deepening from reservations into broader "hospitality voice platform" (ordering, retail). The Series B messaging ("voice AI for restaurants AND retailers") signals horizontal expansion beyond restaurants (source: finance.yahoo.com).

- **Restaurant/AI lessons.**
  - **Personality as a wedge:** in hospitality, a warm branded voice is itself the product differentiator, not just accuracy.
  - **Reservations is an easier first job than ordering** — lower error cost, clean integration targets (OpenTable/Resy/SevenRooms), and immediately measurable ROI (booked covers).
  - **Transparent per-location pricing** lets them sell to independents without a field sales army — a structural advantage vs. drive-thru players.
  - **Trust framing = augmentation:** every case study stresses freeing staff, not replacing them.
  - Pitfall they must manage: full-service operators are protective of guest experience; a bad AI call is a brand risk, so the bar for naturalness is high.

- **Sources.** slang.ai/post/announcing-slang-ais-20m-in-funding; finsmes.com/2026/02/slang-ai-raises-36m; underscore.vc/blog/why-we-invested-in-slang-ai; forbes.com (quickerbettertech, 2025-10-02); slang.ai/pricing.

---

### Loman.ai

- **What it is / category.** Front-of-house voice AI phone agent for restaurants: answers every call, takes phone orders, handles FAQs and reservations, integrates with POS and online-ordering systems. Directly competitive with Slang, but positioned more toward **order-taking / QSR & independent takeout** than reservations (source: loman.ai; businesswire.com).

- **Founders & backgrounds.** Christian Wiens (CEO), Jansen Derr (CTO), Anita Liu (CDO). Notably, Wiens is a **restaurant operator turned SaaS marketer** — the inverse of Slang's ML-researcher origin. He got his first restaurant job in 6th grade and worked every FOH/BOH role; then spent ~a decade in B2B SaaS go-to-market/marketing (MixMode, Anchore, AutoVitals) before founding Loman (source: okreporter.com; linkedin.com). This is an **operator + GTM founder**, less a deep-AI-research founder — Loman rides on off-the-shelf LLM/voice stacks.

- **Founding story.** Founded 2024, Austin TX. Origin insight is a vivid operator anecdote: at a busy beach-town restaurant, staff would literally *take the phone off the hook* during rushes — Wiens estimates that cost the business hundreds of thousands a year. Thesis: "40% of restaurant calls are put on hold or unanswered → $20B+/yr in lost revenue" (source: okreporter.com; streamorders.com). Built on modern LLM + speech stack (the 2024 founding date means it's natively an LLM-era product, unlike 2018–19 founders who started pre-LLM).

- **Funding history.** **$3.5M seed, Aug 2025**, led by Next Coast Ventures with TenOneTen Ventures and Antler. Company was an Antler cohort company. Status: early-stage, scaling nationally (source: antler.co; venturebeat.com; businesswire.com). No later rounds reported as of mid-2026.

- **First customers & early GTM (KEY).** Loman started **hyper-local with independents** — "grew from a local experiment into a national platform." The archetypal early customer is **Midland Pizza Factory (TX)**: was missing hundreds of calls/month; after Loman, recaptured ~$200K/yr in lost orders, eliminated missed calls, grew phone revenue 25%+ (source: okreporter.com). The wedge and proof are pure ROI on recaptured phone orders. Company claims (self-reported) millions of calls handled and tens of millions in order volume processed (source: businesswire.com). Pricing model: SaaS subscription; positions on **22% higher revenue from recaptured calls + upsells, ~17% labor savings** (source: businesswire.com). GTM is founder-led/content-led (podcasts, operator networks) leveraging Wiens' operator credibility.

- **Evolution & pivots.** Too young for a pivot; expanding from phone-answering into "restaurant operations" (orders, reservations, FAQs) as an all-in-one voice layer.

- **Restaurant/AI lessons.**
  - **Operator-founder credibility is the GTM wedge for independents** — Wiens sells peer-to-peer to operators who trust "one of us."
  - Being **LLM-native from 2024** lets a small team match capabilities that older voice startups spent years hand-building.
  - Independent-first is capital-efficient but has churn/scale risk: thousands of small accounts, low ACV, support-heavy.
  - The category is now **crowded** (Slang, Popmenu, SoundHound Smart Answering, Newo) — differentiation is increasingly about integrations and accuracy, not the idea.

- **Sources.** antler.co/press-releases/loman-ai-raises-3-5-million; businesswire.com (2025-08-26); okreporter.com/how-christian-wiens-is-building-loman-ai; venturebeat.com; tenoneten.com/portfolio/loman.

---

### Newo.ai

- **What it is / category.** Horizontal "AI Employee" / AI receptionist platform for SMBs (voice + SMS + web chat + messaging), with a **restaurant vertical ("Host AI")** among several (also fitness, spas, hospitality, home services). Not restaurant-only, but restaurants are a named target vertical (source: newo.ai; newo.ai/restaurant).

- **Founders & backgrounds.** David Yang, PhD (co-founder) and Luba Ovtsinnikova. Yang is a **heavyweight serial AI entrepreneur** — Chinese-Armenian, co-founder of **ABBYY** (enterprise OCR/document AI), plus other ventures (Morfeus, etc.). This is a deep-AI, enterprise-pedigree founder, arguably the most technically credentialed founder in this batch (source: linkedin.com; venturebeat.com).

- **Founding story.** Founded 2023. Thesis: production-grade, human-like AI agents that act as an always-on front desk for SMBs across phone/SMS/chat — replacing the perennially hard-to-staff receptionist role. Built on LLMs with a **drag-and-drop agent-builder** and a "1-Click Creator" that scans a business's website/menu/hours/reviews to auto-generate the agent in ~3 minutes (source: venturebeat.com; newo.ai). Restaurant angle: guest check-ins, reservations, call handling, queue management ("Host AI").

- **Funding history.** **$25M Series A, Feb 10 2026**, led by Ratmir Timashev (Veeam co-founder); investors Aloniq, Constructor, Acrobator, s16vc. Total raised ≈ **$32M** (source: thesaasnews.com; finance.yahoo.com; siliconangle.com). Getlatka lists ~$2.9M ARR / $8.6M valuation at an earlier point (UNVERIFIED, pre-Series A snapshot) (source: getlatka.com). Status: active, scaling.

- **First customers & early GTM (KEY).** Newo's GTM is **horizontal SMB, not restaurant-first** — it sells the same AI receptionist across many local-service verticals and lets self-serve setup do the acquisition (the 1-Click Creator lowers onboarding friction to near-zero). Restaurant reference: **Menlo Tavern** reports answering 100% of inbound calls and freeing managers to be on the floor (source: newo.ai/restaurant). **Pricing is low, self-serve SaaS: roughly $25–$500/mo** by call volume, explicitly benchmarked against a $4,100–$5,800/mo human receptionist; no setup fee, no charge for spam calls (source: newo.ai/pricing; upfirst.ai). The wedge is cost-substitution math (AI vs. human receptionist), sold across verticals.

- **Evolution & pivots.** Young; evolving from a builder platform toward productized vertical agents (restaurants, fitness, hospitality). Positioning shifted toward "production-ready AI receptionists for SMBs" (source: siliconangle.com).

- **Restaurant/AI lessons.**
  - **Horizontal-SMB players will compete with restaurant-specific voice startups** on price and self-serve onboarding — restaurants are just one vertical of a bigger front-desk TAM.
  - **Zero-friction onboarding (auto-build from a website)** is becoming table stakes and a real acquisition lever for the long tail of independents.
  - Risk (flagged even by press): a single wrong AI answer in a hospitality context can cost real money/trust — reliability is the gating factor for the low-touch model (source: ucstrategies.com).
  - A deep-AI founder (Yang) plus horizontal scope means Newo optimizes for breadth; restaurant-specific integrations (POS, reservations) may lag vertical specialists like Slang.

- **Sources.** venturebeat.com/ai/newo-ais-digital-employee; thesaasnews.com/news/newo-ai-bags-25-million; siliconangle.com/2026/02/10/newo-lands-25m; newo.ai/restaurant; newo.ai/pricing.

---

### ConverseNow

- **What it is / category.** Voice AI for restaurant order-taking — originally **phone-ordering automation**, extended into drive-thru and kiosk. Handles unlimited simultaneous calls to eliminate busy signals/missed orders; personalizes and upsells (source: conversenow.ai; techcrunch.com).

- **Founders & backgrounds.** Vinay Shukla (CEO) and Rahul Aggarwal. **Not restaurant operators and not pure ML academics — they're serial B2B-services/tech founders with restaurant-adjacent domain experience.** Their prior venture was a digital-transformation/BPO company serving restaurants, which they scaled and **sold to Genpact in 2016**. That earlier company gave them years of "close proximity" to restaurant operational pain (source: conversenow.ai/about; tracxn.com). So the profile is **domain-immersed operators-of-restaurant-tech**, not chefs.

- **Founding story.** Founded 2018, Austin TX. Origin insight came directly from the prior restaurant-services business: phones and order channels are chronic bottlenecks; voice AI could take orders at scale. Built on ASR + NLU voice assistants branded "George" and "Becky." COVID (2020) was a tailwind — contactless/off-premise ordering surged right as they launched their seed product (source: builtinaustin.com; conversenow.ai).

- **Funding history.**
  - **Seed — $3.25M, May 2020**, led by Bala Investments; LiveOak Venture Partners, Tensility Venture Partners (source: builtinaustin.com).
  - **Series A — $15M** (source: aibusiness.com).
  - **Growth — $10M, Aug 2022**, from **Enlightened Hospitality Investments (EHI)** — Danny Meyer's (Shake Shack / Union Square Hospitality) growth-equity fund (source: techcrunch.com; restaurantbusinessonline.com).
  - **Total ≈ $28.8M.** Status: active. (No 2024–2026 mega-round surfaced; competitive pressure from SoundHound is significant.)

- **First customers & early GTM (KEY).** ConverseNow went **chain/enterprise-first via pilots**, and its flagship wedge was **Domino's phone ordering** — when you call a Domino's, the AI personalizes the order, auto-applies coupons, and upsells (source: franchisetimes.com; linkedin.com). Early named chains: **Domino's, Fazoli's, Blake's Lotaburger, Wingstop**. Scaled from ~750 stores (2021) → 1,100–1,200+ restaurants across 40 states (2022) (source: builtinaustin.com; techcrunch.com). The proof shown to chains: throughput (unlimited concurrent calls), consistent upselling (higher average ticket), and labor offload. GTM leverage came from **strategic investor EHI (Danny Meyer)** giving industry credibility and warm chain intros — an important pattern: *take money from restaurant royalty to open restaurant doors.* Pricing is enterprise/per-location SaaS (not publicly transparent).

- **Evolution & pivots.** Notable **channel emphasis shift**: launched around phone ordering, pushed into **drive-thru** (the 2022 raise was explicitly to expand drive-thru), and in 2024 partnered with **Adora POS** and integrated with **Deliverect**, and **teamed with Valyant AI** (acquiring/absorbing Valyant's drive-thru capability) to accelerate drive-thru voice AI (source: foodondemand.com 2024-07-10; foodondemand.com 2024-09-11). So the arc is phone → drive-thru → omnichannel, with consolidation (Valyant) along the way. No evidence of layoffs/shutdown found (search noise conflated it with Nike's "Converse").

- **Restaurant/AI lessons.**
  - **Prior restaurant-services experience was the unlock** — they knew the buyers, the ops, and the integration reality before writing code.
  - **Land a marquee chain (Domino's) as the wedge**, then use it as proof for the next chains — chain logos compound.
  - **Strategic capital from restaurant insiders (EHI/Danny Meyer)** doubles as distribution and credibility.
  - Phone ordering is an easier beachhead than drive-thru (no ambient noise, no menu-board/POS hardware integration, less latency pressure) — ConverseNow proved on phone before tackling the drive-thru.
  - Consolidation risk: SoundHound's SYNQ3 deal and Hi Auto's scale-ups mean the drive-thru is getting winner-take-most; being sub-scale is dangerous.

- **Sources.** conversenow.ai/about; builtinaustin.com (seed + $10M); techcrunch.com/2022/08/23/conversenow-drive-thru-ordering-tech-10m; restaurantbusinessonline.com (Danny Meyer EHI); foodondemand.com (Valyant, Adora, 2024).

---

### SoundHound (restaurant voice AI + SYNQ3)

- **What it is / category.** Public voice-AI platform company (Nasdaq: SOUN) whose **restaurant division is now the largest US voice-AI provider for restaurants** — drive-thru ("Dynamic Drive-Thru"), phone ordering ("Smart Answering"/Smart Ordering), text/scan/in-car ordering, and Employee Assist. Restaurant voice AI is one pillar of a broader voice-AI business (also automotive, IoT, customer service) (source: soundhound.com; businesswire.com).

- **Founders & backgrounds.** Founded 2005 as **Melodis Corp** in a Stanford dorm by **Keyvan Mohajer (CEO), Majid Emami, and James Hom** — deep speech/AI engineers. Mohajer: Iranian-Canadian, Stanford PhD in EE, a 20-year voice-AI researcher. This is the **deepest AI-research pedigree in the batch** (source: en.wikipedia.org; soundhound.com; businessmodelcanvastemplate.com).

- **Founding story (and path into restaurants).** SoundHound began in **music recognition** (Midomi → rebranded SoundHound app, a Shazam competitor, hundreds of millions of downloads), while secretly building for 10 years its **Houndify** voice platform and proprietary **"Speech-to-Meaning"** architecture (skips the speech→text→meaning two-step for speed/accuracy). Went public April 2022 via SPAC (Archimedes Tech) at ~$2.1B valuation. Restaurants became a deliberate vertical land-grab in 2023 — voice ordering is a near-perfect fit for its low-latency, domain-constrained speech engine (source: en.wikipedia.org; soundhound.com).

- **The SYNQ3 acquisition (central event).**
  - **Announced Dec 7, 2023; ~$25M** (up to +$4M earnout over 3 yrs on revenue targets). **~20% cash, ~80% stock** (source: businesswire.com; pymnts.com; sec.gov 8-K).
  - **SYNQ3 background:** founded 2007 in Colorado Springs (formerly **Stellar Restaurant Solutions**); grew into the world's leading restaurant **call-center/order-taking** operator, processing **$1B+ in sales** for partner brands, then layered ASR/conversational AI on top; earlier acquired Dallas conversational-AI firm **Novo Labs** (source: tracxn.com; leadiq.com; dallasinnovates.com).
  - **Why it mattered:** overnight it extended SoundHound's restaurant reach by **an order of magnitude — from ~hundreds to 10,000+ signed locations and 25+ national/multinational chains** across drive-thru, fast-casual, casual, and c-stores (source: soundhound.com; businesswire.com). This is the batch's clearest example of **buying distribution/deployment footprint rather than building it.**

- **Funding/financials.** Public company; funds restaurant expansion off balance sheet + M&A (also acquired Amelia/SYNQ3/Allset around this period). Restaurant milestone: **100M+ customer interactions processed** (Oct 2024); platform in **~10,000 locations** (source: businesswire.com 2024-10-31; soundhound.com 2025-02).

- **First customers & early GTM (KEY).** SoundHound's restaurant GTM is **enterprise-chain, pilot-then-scale, and heavily M&A-accelerated.** Named brands using its ordering/answering AI: **Chipotle, Jersey Mike's, White Castle, Church's Texas Chicken, Applebee's, Habit Burger, Noodles & Company, Casey's General Stores, Beef 'O' Brady's** (source: restaurantdive.com; businesswire.com). Concrete wedge example: **Jersey Mike's** phone AI starting at 50+ restaurants; **White Castle** drive-thru voice AI at ~100 lanes (~30% of footprint). The proof shown to chains is **accuracy + throughput + labor offload**, now anchored on its **Polaris** speech-recognition model (Feb 2025) claiming best-in-class accuracy (source: businesswire.com 2025-02-25). Pricing is enterprise/negotiated per-location + usage.

- **Evolution & pivots.** Music-recognition → voice-AI platform (Houndify) → public company → **vertical roll-up in restaurants via SYNQ3** → omnichannel restaurant ordering (drive-thru + phone + text + in-car). The strategic pivot is from horizontal platform-licensing to **owning full-stack vertical solutions** in restaurants and autos.

- **Restaurant/AI lessons.**
  - **You can buy your way to #1 in restaurant voice** — SYNQ3 delivered 10,000 locations and chain relationships that would take years to sell organically.
  - **Legacy call-center relationships convert into AI deployments** — SYNQ3's human order-taking footprint became the on-ramp for AI order-taking (existing integrations + trust already in place).
  - **Proprietary low-latency speech (Speech-to-Meaning/Polaris)** is the technical moat that matters most in drive-thru (noise, latency, accents).
  - Public-company scrutiny cuts both ways: SOUN's volatility and the need to show restaurant ARR growth pressures pricing and pace.
  - Chains want **one throat to choke across channels** — omnichannel (drive-thru + phone + text) is becoming the enterprise requirement, disadvantaging single-channel startups.

- **Sources.** businesswire.com/20231207356573 (SYNQ3 deal); pymnts.com/acquisitions/2023/soundhound-pays-25-million; en.wikipedia.org/wiki/SoundHound_AI; businesswire.com/20241031567411 (100M interactions); businesswire.com/20250225367612 (Polaris/next-gen); restaurantdive.com (Jersey Mike's); dallasinnovates.com (SYNQ3–Novo Labs).

---

### Hi Auto

- **What it is / category.** Conversational voice AI purpose-built for **QSR drive-thru** order-taking (SaaS). Pure-play drive-thru — the hardest voice environment (noise, latency, accents, menu complexity) (source: hi.auto; prnewswire.com).

- **Founders & backgrounds.** Founded 2019 (Israel-rooted team). Founders/leaders: **Roy Baharav (CEO)** — ex-Google product (launched Google Smart Shopping Campaigns); **Eyal Shapira (CTO)** — 20+ yrs software R&D, prior AI startups; and **Zohar Zisapel** — legendary Israeli serial entrepreneur (RAD Group), who died in 2023. Profile: **ex-big-tech + deep Israeli deep-tech/AI**, not restaurant operators (source: restaurantbusinessonline.com; calcalistech.com).

- **Founding story.** Founded 2019. Hi Auto's roots are in **audio-visual speech enhancement / speech separation** (isolating a target speaker in noise) — a genuinely hard AI capability that maps perfectly onto the noisy drive-thru. They aimed the tech at the drive-thru order-taking problem, targeting high accuracy and completion without a human. Reported performance: **>96% order accuracy, >90% order completion** without human intervention (source: prnewswire.com; hi.auto).

- **Funding history.** **$15M Series A, ~Apr 2025**, led by **Delek Motors** (auto importer) with a **strategic investment from a publicly traded restaurant company** (an operator-investor). **Total raised ≈ $23M**, plus a **$4M credit line** (source: prnewswire.com; restaurantbusinessonline.com; calcalistech.com). Status: active, scaling.

- **First customers & early GTM (KEY).** Hi Auto ran the **pilot-then-scale-within-a-chain** playbook and won by proving on tough mid-market QSR chains:
  - **Bojangles** — after a successful pilot, agreed to roll out to **hundreds of ~800 locations** (company + franchise); AI named **"Bo-Linda"**; ~200 live and adding near-daily; **bilingual (English/Spanish) at 400+ drive-thrus** (source: foodondemand.com; restaurantdive.com; hi.auto).
  - **Checkers & Rally's** — ~**350 locations**, notably leaning on **Spanish-language** ordering (source: gocanopy.com; hi.auto).
  The wedge is **accuracy + Spanish-language coverage + labor relief** in QSR drive-thru; the proof is pilot metrics (accuracy/completion) that de-risk a chain-wide rollout. Note: **White Castle uses SoundHound, not Hi Auto** (a common misattribution). Pricing: per-location SaaS (undisclosed).

- **Evolution & pivots.** From speech-separation research → drive-thru voice product → scaling multi-hundred-location chain rollouts. A meaningful differentiator has become **bilingual (Spanish) ordering** as a rollout accelerant with US QSR chains.

- **Restaurant/AI lessons.**
  - **Deep audio AI (speech separation) is a real moat in the drive-thru** — the environment punishes generic ASR; accuracy/completion numbers are the entire sale.
  - **Land-and-expand inside one chain** (pilot → hundreds of locations) is more capital-efficient than chasing many logos.
  - **Strategic operator-investors** (a public restaurant co.) double as anchor customers and validation.
  - **Bilingual coverage** is an underrated GTM wedge in US QSR (large Spanish-speaking guest and labor base).
  - Pure-play drive-thru is a narrow, brutal niche — Hi Auto is directly in SoundHound's crosshairs, so execution/accuracy leadership is existential.

- **Sources.** prnewswire.com (Hi Auto $15M); restaurantbusinessonline.com/technology/another-drive-thru-ai-supplier; calcalistech.com; foodondemand.com/07302024/bojangles; restaurantdive.com (Bojangles); gocanopy.com/news-insights/ai-drive-thru-problems.

---

### Loop (Loop AI / tryloop.ai)

- **What it is / category.** **Delivery intelligence / financial reconciliation** SaaS for restaurants operating on third-party marketplaces (DoorDash, Uber Eats, Grubhub). Automates reconciliation/bookkeeping, chargeback & error-charge disputes, sales-tax/franchise-fee liability, real-time store-availability monitoring, and marketing optimization. "AI" here = data automation/analytics over messy marketplace data, not conversational voice (source: tryloop.ai; restaurantbusinessonline.com).

- **Founders & backgrounds.** Anand Karthik Tumuluru (CEO), Sundar Annamalai, Vinod Pachipulusu. **Ex-Uber + ex-Google engineers with restaurant exposure** — Tumuluru describes himself as both a restaurateur and an Uber software engineer (he saw the value of third-party delivery data from inside Uber); Annamalai also Uber engineering; Pachipulusu ex-Google (source: tryloop.ai; restaurantbusinessonline.com). Profile: **marketplace/data engineers who understood delivery economics from the platform side.**

- **Founding story.** The origin insight is *asymmetry of information*: delivery platforms hold the data, restaurants can't see where money leaks (wrong payouts, unrefunded errors, tax exposure). Tumuluru, having worked inside Uber, knew the data existed and could be reconciled programmatically. Built as an automated "delivery intelligence" layer that ingests marketplace data and recovers lost money (source: tryloop.ai; globenewswire.com).

- **Funding history.**
  - **Seed — $6M, Mar 2024**, led by **Base10 Partners** with Afore Capital (source: globenewswire.com; restaurantbusinessonline.com).
  - **Series A — $14M**, led by **Nyca Partners**; participation from **Gokul Rajaram**, Base10, Afore, Converge, Alumni Ventures, Data Tech Fund, John Pepper (ex-Boloco), 9Yards Capital, Operators Studio (source: tracxn.com; tryloop.ai blog).
  - **Total ≈ $20M.** Status: active, scaling.

- **First customers & early GTM (KEY).** Loop went after **multi-unit / emerging chains and franchisees** — operators with enough delivery volume that recovered dollars are material. Named brands: **Dave's Hot Chicken, Freddy's Frozen Custard, Mo'Bettahs, MOOYAH** — across thousands of locations, reconciling **$100M+ (later $1B+ via similar competitor claims) in transactions** (source: restauranttechnologynews.com; tryloop.ai). The wedge is **found money**: show an operator exactly how much they're being underpaid/overcharged by the marketplaces, then recover it automatically. The proof is a reconciliation report quantifying leakage — extremely tangible. **Pricing tends toward SaaS + performance (share of recovered funds)** in this category (Loop's exact model not fully public, but the "% of recovered funds / found-money" pitch is core to the wedge).

- **Evolution & pivots.** From reconciliation/bookkeeping into a broader **"delivery profitability" suite** (disputes, availability/uptime, promo & marketing optimization, tax) — expanding wallet share per account. No pivot; steady platform broadening.

- **Restaurant/AI lessons.**
  - **"Found money" is the easiest restaurant sale there is** — ROI is self-evident and often self-funding (recovered dollars pay the fee).
  - **Insider platform knowledge (ex-Uber) is the moat** — you must understand how DoorDash/UE/Grubhub payouts actually work to reconcile them.
  - **Chains/franchisees first** here (not independents) — recovery scales with delivery volume, so bigger operators = bigger, stickier ROI.
  - This "AI" is really data plumbing + automation; the defensibility is integrations and data coverage, not model IQ.
  - Competes head-to-head with Voosh — a two-horse (plus incumbents) race where breadth of platform integrations and dispute win-rates decide winners.

- **Sources.** tryloop.ai/blog/loop-raises-6m; globenewswire.com (2024-03-12); restaurantbusinessonline.com/technology/loopai-raises-6m; restauranttechnologynews.com/2024/03; tracxn.com/d/companies/loop.

---

### Voosh (voosh.ai)

- **What it is / category.** Direct competitor to Loop: **data-driven third-party-delivery management** for restaurants — dispute/chargeback recovery ("Dispute Manager"), reconciliation, reviews management, promotions, and uptime/availability across DoorDash/Uber Eats/Grubhub. Again, "AI" = automation/analytics over marketplace data (source: voosh.ai; ycombinator.com).

- **Founders & backgrounds.** Priyam Saraswat (CEO) and Kshitiz Sanghi (plus Lilit Ohanyan listed in some sources). **Founders are consumer-ops/marketplace operators, not restaurateurs or ML researchers** — Saraswat is a second-time founder (prior bike-sharing startup) with operating stints at **OYO (China) and Bounce**; Sanghi handles CX/ops (source: tracxn.com; content.calibbq.media). Profile: **marketplace-operations founders** who learned delivery pain by running restaurant operations themselves.

- **Founding story.** Founded 2020 (San Francisco / originally India-linked). Crucial origin detail: **Voosh started as a virtual-brand operator running 200+ restaurant partners' delivery businesses** — and felt the exact pain (marketplace data scattered across apps/reports/emails, disputes bleeding money) that its software now solves. It **pivoted from being a delivery operator to selling the tooling** it built for itself (source: voosh.ai/company; startupintros.com). A classic "we built it for ourselves, then productized it" origin.

- **Funding history.** **Y Combinator-backed** (source: ycombinator.com). Reported funding is small/early: Tracxn shows only **~$157K across 2 rounds / 13 investors** including Acequia Capital, Liquid 2 Ventures, Unpopular Ventures, Y Combinator, Better Capital (source: tracxn.com). NOTE: this figure looks incomplete/UNVERIFIED — it likely predates or omits the YC standard investment and any subsequent rounds; treat Voosh's true total raised as **uncertain/under-disclosed**. Status: active, revenue-generating (~$3.7M–$5M revenue per one third-party estimate — UNVERIFIED, source: extruct.ai).

- **First customers & early GTM (KEY).** The GTM wedge grew straight out of the founding pivot: **Voosh already operated 200+ restaurants' delivery**, so it had built-in first customers and proof before selling software externally. The flagship product wedge is **Dispute Manager**, with a hard, sales-ready proof point: **60–70% dispute success rates in the first month** (source: eznewswire.com; linkedin.com). It now claims **500+ restaurant brands, $1B+ in delivery sales processed, millions recovered** (source: voosh.ai; startupintros.com). Like Loop, the pitch is **found money / recovered chargebacks**, and pricing skews to **SaaS + performance on recovered funds**.

- **Evolution & pivots.** The big pivot: **virtual-brand/delivery operator → B2B SaaS platform** for delivery profitability. Then platform broadening from disputes into reconciliation, reviews, promos, uptime.

- **Restaurant/AI lessons.**
  - **"Dogfooding as an operator first" is a powerful origin** — Voosh had domain truth and reference customers before it was a software company.
  - **Dispute-win-rate is the single most persuasive metric** in delivery-recovery sales — it's concrete and monthly.
  - **YC + found-money positioning** lets a lean team land 500+ brands without heavy capital.
  - Under-disclosed funding + third-party-only revenue estimates mean **outside visibility is thin** — a reminder that private restaurant-tech numbers are often unverified.
  - Head-to-head with Loop: differentiation is integration breadth, dispute win-rates, and platform depth (reviews/promos), not brand.

- **Sources.** ycombinator.com/companies/voosh; voosh.ai/company; tracxn.com/d/companies/voosh; eznewswire.com (Dispute Manager); content.calibbq.media (Kshitiz Sanghi interview); startupintros.com/orgs/voosh.

---

### Agot AI

- **What it is / category.** **Computer-vision** for QSR — real-time **order-accuracy verification** (and food-prep/ops monitoring). Cameras watch assembly/expediting and flag errors (missing cheese, wrong items) *before* the food reaches the guest. Back-of-house vision, not voice (source: techcrunch.com; cnbc.com).

- **Founders & backgrounds.** **Evan DeSantola (CEO) and Alex Litzenberger (CTO)** — met as **computer-science students at Carnegie Mellon**. This is a **pure CV/ML-research founding pair** (source: techcrunch.com; cnbc.com). No restaurant-operator background; the bet is that hard computer vision is the moat.

- **Founding story.** Origin insight: **order inaccuracy** is a massive, quantifiable QSR problem (remakes, refunds, lost loyalty, delivery errors). Agot applied CMU-grade computer vision to *see* orders being made and catch errors in real time — claiming it can spot **>85% of order errors** before service (source: cnbc.com; techcrunch.com). Built on machine-learning computer vision (object/action recognition on kitchen line footage).

- **Funding history.** **$12M round (Feb 2022)** with **Conti Ventures** (Continental Grain's venture arm), **Kitchen Fund**, and **Grit Ventures**; **total ≈ $16M** to that point (source: prnewswire.com; techcrunch.com). No large subsequent round surfaced. Status: **effectively rolled into HME** (see pivot).

- **First customers & early GTM (KEY).** Agot ran a **chain-pilot** motion: it partnered with **Yum! Brands** (Taco Bell/KFC/Pizza Hut parent) to pilot in **~20 restaurants, with plans to expand to 100 if successful** (source: cnbc.com; techcrunch.com). The wedge: show a chain hard numbers on error-catch rate (>85%) and the downstream savings (fewer remakes/refunds, better accuracy scores). Pilot-driven, enterprise-first, proof = accuracy telemetry. This is the canonical **CV land-grab via a single big chain pilot**.

- **Evolution & pivots (IMPORTANT).** In **April 2025, Agot AI's computer-vision technology was acquired/absorbed by HME** (Hospitality & Specialty Communications — the dominant drive-thru timer/headset maker), powering HME's new **"Nitro Vision AI"** (ZOOM Nitro timer + Agot CV) to cut drive-offs and wait times (source: qsrmagazine.com). So Agot went from **standalone accuracy-CV startup → embedded technology inside an incumbent hardware platform** — an outcome (acqui-hire/tech acquisition) rather than independent scale. Standalone customer traction post-pilot appears limited in public sources (UNVERIFIED beyond the Yum! pilot).

- **Restaurant/AI lessons.**
  - **Order accuracy is a legitimately huge CV opportunity**, but standalone accuracy-verification is a **feature, not a platform** — hence absorption into HME's hardware ecosystem.
  - **CV in restaurants needs a distribution partner** — HME already has headsets/timers in tens of thousands of drive-thrus; Agot's tech + HME's install base is the logical marriage.
  - **A single chain pilot (Yum!) validates but doesn't guarantee scale** — converting a 20-store pilot into thousands of paid locations is where many CV startups stall.
  - Deep ML founders without operator/GTM muscle often end up as **the tech inside someone else's product.**

- **Sources.** techcrunch.com/2022/02/11/agot-ai; cnbc.com/2021/09/16 (Agot CV fast-food accuracy); prnewswire.com (Agot $12M); qsrmagazine.com/news/hme-introduces-new-drive-thru-computer-vision-technology (Nitro Vision AI, 2025).

---

### PreciTaste

- **What it is / category.** **AI + computer-vision kitchen operations** platform — demand forecasting, prep/production guidance, and order-accuracy/station monitoring to cut waste and boost throughput. Products: **Prep Assistant, Planner Assistant, Station Assistant.** Back-of-house/kitchen AI (source: precitaste.com; techcrunch.com).

- **Founders & backgrounds.** Co-founded ~2010s by **Dr. Ingo Stork genannt Wersborg** and his wife **Laura**, building on tech from **TU Munich**; Ingo holds a Doctor of Science in Machine Learning (TUM) and did master's research at **MIT**. **Hauke Feddersen** (joined ~2019) runs product/ops/business (source: precitaste.com; restaurantfinanceadvisors.com; alleywatch.com). Profile: **deep academic ML/CV founders**, with a business operator layered on later.

- **Founding story.** Origin: apply machine-vision + predictive AI to the **kitchen** — the messiest, most waste-prone, hardest-to-optimize part of a restaurant. Uses **computer vision to sense demand signals (foot/vehicle traffic) and monitor stations**, combined with historical sales to tell staff *what to prep and how much, in real time* — reducing both stockouts and waste. **40+ patents** on the kitchen-AI suite. Company was **bootstrapped for ~a decade** before raising (source: alleywatch.com; precitaste.com).

- **Funding history.** **$24M Series A, Aug 2022**, co-led by **Melitas Ventures** and **Cleveland Avenue** (Don Thompson, ex-McDonald's CEO), with **Enlightened Hospitality Investments (Danny Meyer)** and **Monogram Capital**. Strikingly, investors include the **CEOs of McDonald's and Burger King** personally (source: techcrunch.com; alleywatch.com). Status: active. (Being bootstrapped-then-one-big-round is unusual and notable.)

- **First customers & early GTM (KEY).** PreciTaste went **enterprise-chain, pilot-driven, waste-ROI-first.** Flagship reference: **Chipotle** — deployed at **~8 California locations** to predict demand and guide prep; pilots cut **food waste ~10–15%** (source: deeplearning.ai; qsrmagazine.com; precitaste.com burrito business-case PDF). The wedge is a **hard waste/labor ROI number** shown in a small pilot, backed by patents and academic credibility. Its **investor base is its GTM engine**: literally the CEOs of McDonald's/BK/Shake Shack as backers — an extraordinary set of warm doors into the biggest chains. Pricing: enterprise SaaS per-location (undisclosed).

- **Evolution & pivots.** From a European (TUM/MIT) research-driven vision company → US-based restaurant kitchen-AI platform; broadened from accuracy into full **prep/planning/production optimization** (the three Assistants). No pivot; deepening within kitchen ops. Won a 2024 "FoodTech AI Innovation Award" (AgTech Breakthrough) (source: precitaste.com).

- **Restaurant/AI lessons.**
  - **Kitchen/back-of-house AI sells on waste + labor ROI**, which is measurable per-store and compounding across a chain.
  - **Patents + academic pedigree build enterprise trust** for a category (letting AI direct the kitchen) that's inherently risky if wrong.
  - **Recruiting chain-CEO angels is a masterclass in GTM-through-cap-table** — PreciTaste, ConverseNow, and Agot all took strategic restaurant capital to open doors.
  - **Bootstrapping for a decade** before a single big round is viable in hard-tech restaurant AI — long R&D horizon, but you own the moat.
  - Pitfall: back-of-house AI must integrate with each chain's POS/KDS/ops and earn line-cook adoption — deployment is slow and consultative.

- **Sources.** techcrunch.com/2022/08/09/precitaste; alleywatch.com/2022/08/precitaste-vision-ai-platform; deeplearning.ai/the-batch/chipotle-tests-ai; qsrmagazine.com (AI in Chipotle kitchen); precitaste.com/news.

---

### Popmenu

- **What it is / category.** **AI-powered restaurant marketing & engagement platform** (not voice-AI-native, though it now has AI phone answering). Bundles SEO website + **interactive menus**, automated email/SMS/social marketing, commission-free direct online ordering, and **24/7 AI Phone Answering**. The broadest product surface in this batch; AI is a layer, not the origin (source: get.popmenu.com; techcrunch.com).

- **Founders & backgrounds.** Founded 2016, Atlanta. Core team: **Brendan Sweeney (CEO), Tony Tingle, Mike Sadowski** (incorporators), with co-founders **Mike Gullo, Anthony Roy, Justis Blasco** (accounts vary). **Not restaurateurs or ML researchers — they're marketing-tech operators**: Sweeney came from CareerBuilder, Kudzu, and Commissions Inc. (real-estate marketing SaaS), and the Commissions Inc. experience seeded the Popmenu idea (source: businessmodelcanvastemplate.com; techcrunch.com). Profile: **martech/SaaS GTM founders applying proven marketing-software playbooks to restaurants.**

- **Founding story.** Origin insight: a restaurant's **menu is its single most powerful marketing asset**, yet menus were static PDFs/images — invisible to search, un-engaging, un-trackable. Popmenu turned menus into **interactive, SEO-indexed, photo/review-rich pages** that drive discovery and capture guest data, then wrapped marketing automation around that data. AI (phone answering, content generation) was layered on later as LLM/voice tech matured (source: businessmodelcanvastemplate.com; get.popmenu.com).

- **Funding history.** Bootstrapped first ~18 months.
  - **Series A — $4.5M, 2019** (Base10 Partners; press also cites Bedrock/Felicis — sources vary) (source: restauranttechnologynews.com; businessmodelcanvastemplate.com).
  - **Series B — $15M** (Bedrock Capital).
  - **Series C — $65M, 2021**, led by **Tiger Global** — pushed valuation into the hundreds of millions and funded the **acquisition of OrderAI** (source: businessmodelcanvastemplate.com; pitchbook.com).
  - **Total ≈ $87–88M.** Investors also include Salesforce Ventures, ITC Capital, Chapter One. Est. ARR ~$59M (2024, getlatka — UNVERIFIED). Status: active, one of the larger/more mature players here.

- **First customers & early GTM (KEY).** Popmenu is the clearest **independents-first, land-the-long-tail** story in the batch. After launch it saw **rapid uptake among independent restaurant groups in the Southeast (Atlanta base)**, then expanded nationally to **US single-location independents and small multi-unit groups**, with a separate enterprise track later (source: businessmodelcanvastemplate.com; get.popmenu.com). The wedge was the **interactive menu** (immediate, visible marketing value — better Google visibility, guest engagement), which pulled operators onto the platform; Popmenu then upsold marketing automation, ordering, and (later) AI answering. Proof points are marketing ROI (traffic, repeat visits, captured guest data). **AI Answering claims 6.1M+ calls answered; ~12,000+ restaurants served** as of mid-2026 (source: get.popmenu.com; prnewswire.com). Pricing: per-location SaaS subscription + add-ons.

- **Evolution & pivots.** Interactive menus → full marketing suite → direct online ordering (post-COVID, commission-free wedge vs. delivery apps) → **AI layer (AI Answering, AI marketing content)**. Acquired **OrderAI** (2021) to bolster ordering. No pivot; classic land-and-expand into an all-in-one restaurant marketing OS.

- **Restaurant/AI lessons.**
  - **A visible, standalone wedge (interactive menu) wins the long tail of independents** — you don't lead with "AI," you lead with obvious marketing value, then add AI.
  - **Independents-first + product-led/expand model** can reach 10,000+ locations and $50M+ ARR — proof the independent market is real if you nail low-touch onboarding.
  - **COVID accelerant:** commission-free direct ordering was a timely wedge against DoorDash/UE economics.
  - **AI as an add-on, not the identity** — Popmenu bolts AI phone answering onto an existing distribution base of thousands, a fundamentally different (and lower-CAC) path than AI-native startups building distribution from scratch.
  - Breadth risk: an all-in-one competes on many fronts (websites, ordering, marketing, AI phone) against focused specialists in each.

- **Sources.** techcrunch.com/2020/10/15/popmenu; businessmodelcanvastemplate.com/blogs/brief-history/popmenu; restauranttechnologynews.com/2019/12 (Series A); get.popmenu.com/ai-answering; pitchbook.com (Popmenu profile).

---

## Cross-cutting observations (this batch)

1. **Two founder archetypes recur, and both work — but differently.** (a) *Deep-AI/ex-big-tech researchers* (Slang ex-Spotify, SoundHound Stanford, Hi Auto ex-Google/Israeli deep-tech, Agot CMU, PreciTaste TUM/MIT) win on a genuine technical moat (speech separation, speech-to-meaning, kitchen CV). (b) *Operators / domain-immersed GTM founders* (Loman ex-restaurant-operator, ConverseNow ex-restaurant-services, Loop/Voosh ex-marketplace, Popmenu ex-martech) win on distribution and knowing the buyer. The strongest outcomes pair the two; pure-researchers without GTM/operator muscle (Agot) risk becoming "the tech inside someone else's product."

2. **Chains vs. independents splits cleanly by product risk and error cost.** High-stakes, hardware-integrated, high-error-cost products (drive-thru voice: SoundHound, Hi Auto, ConverseNow; kitchen CV: PreciTaste, Agot) go **enterprise-chain, pilot-then-scale**. Lower-stakes, self-serviceable products (phone answering/reservations: Slang, Loman, Newo, Popmenu) go **independents-first with transparent per-location pricing**. Delivery reconciliation (Loop, Voosh) targets **multi-unit/franchisees** where recovered dollars are material.

3. **"Found money" and hard ROI numbers are the universal trust-builder.** Every successful sale rests on one concrete, quantified proof: recaptured calls ($200K/yr — Loman), dispute win-rates (60–70% — Voosh), reconciled leakage (Loop), order-error catch rate (>85% — Agot), waste reduction (10–15% — PreciTaste), accuracy/completion (>96%/>90% — Hi Auto), more reservations (+50% — Slang). Restaurants (thin-margin, skeptical) buy measurable ROI, not "AI."

4. **The pilot is the sales cycle for anything touching operations.** Drive-thru and kitchen players universally run a **small pilot (8–20 stores) → chain-wide rollout (hundreds)** motion (Agot→Yum! 20 stores; Hi Auto→Bojangles pilot→hundreds; PreciTaste→Chipotle 8 stores). Converting pilot to scale is where startups live or die — Agot stalled and got absorbed; Hi Auto converted.

5. **Cap-table-as-distribution is a signature restaurant-AI move.** Taking strategic capital from restaurant royalty opens doors that cold sales can't: **Danny Meyer's EHI** (ConverseNow, PreciTaste), **CEOs of McDonald's/Burger King/Shake Shack personally** (PreciTaste), **a public restaurant company** (Hi Auto), **chef Tom Colicchio** (Slang), **Gokul Rajaram** (Loop). Warm intros from investor-operators are the GTM unlock.

6. **M&A/roll-up is reshaping the voice-AI segment fast — sub-scale is dangerous.** SoundHound **bought SYNQ3 ($25M) to jump from hundreds to 10,000+ locations**; it also absorbed Amelia/Allset. ConverseNow **absorbed Valyant**. Agot's CV **folded into HME**. The drive-thru is consolidating toward winner-take-most; single-channel startups are pressured to sell or get acquired.

7. **Legacy relationships convert to AI deployments.** SYNQ3's decade-old **human call-center** footprint (existing POS integrations + chain trust) became the on-ramp for AI order-taking. Voosh's **virtual-brand operator** past gave it built-in first customers. Popmenu's **thousands of marketing-software accounts** became the distribution base for bolt-on AI answering. Owning an existing footprint beats building AI distribution from scratch.

8. **Omnichannel + bilingual are the new enterprise requirements.** Chains increasingly want **one vendor across drive-thru + phone + text + kiosk** (SoundHound's Polaris/omnichannel; ConverseNow's phone→drive-thru expansion), and **Spanish-language** coverage is a concrete rollout accelerant in US QSR (Hi Auto at Bojangles/Checkers; Bojangles' "Bo-Linda"). Single-channel, English-only products are increasingly disadvantaged.

9. **Pricing models cluster by category.** Front-of-house voice = **transparent per-location SaaS** ($25–$599/mo; Newo, Slang, Loman). Enterprise voice/vision = **negotiated per-location + usage** (SoundHound, ConverseNow, Hi Auto, PreciTaste). Delivery recovery = **SaaS + performance / % of recovered funds** (Loop, Voosh). The performance/found-money model is the most frictionless because the product self-funds.

10. **The core traps.** (a) **Accuracy/trust in a live guest moment** — one bad AI call or wrong order is a brand risk (flagged for Newo, and the reason drive-thru bars are so high). (b) **Integration burden** — POS/KDS/reservation/marketplace integrations are the real moat and the real slog; "AI" is often the easy part. (c) **Feature-not-platform risk** — narrow point solutions (Agot's accuracy CV) get absorbed; survivors broaden into suites (Loop, Voosh, Popmenu, SoundHound). (d) **Independent long-tail economics** — thousands of low-ACV, support-heavy accounts require near-zero-friction onboarding (Newo's 1-click, Popmenu's PLG) to be viable. (e) **Under-disclosed private numbers** — several players' funding/revenue are thin or third-party-estimated (Voosh especially); outside data must be treated as unverified.
