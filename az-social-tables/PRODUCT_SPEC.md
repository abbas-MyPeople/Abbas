# PRODUCT_SPEC — AZ Social Tables

**One-line definition:** A restaurant social dining demand engine — restaurants publish
curated dinner events for their slow hours, local people book seats at them, and the
operator fills, balances, and measures each table so the restaurant gets pre-booked,
high-intent foot traffic it can count in dollars.

Working consumer brand: **Social Tables** ("Meet real people over real food").
Working restaurant brand: **AZ Social Tables by AZ Restaurant Partners**
("Fill slow restaurant nights with pre-booked local customers").
*Naming note: "Social Tables" collides with Cvent's event-planning product — fine for a
local pilot, needs a trademark check before any scale/spend.*

---

## Personas

### Restaurant customer (the one who pays)
**"Owner-operator with empty Tuesdays."** Independent restaurant owner in greater
Houston, 20–80 seats, does $X on Fri/Sat and a fraction of it Tue–Thu. Already pays
~30% to delivery apps and hates it. Doesn't want another dashboard or another app to
babysit; wants *covers* — real humans in chairs on slow nights, at near-zero risk.
Pilot instance: **Wok & Karahi, Spring TX** (Abbas's own restaurant — Monday closed,
kitchen closed 4–5 PM daily, Tue–Thu dinners softest; the lab where every AZ product
is proven first).

What they care about: incremental revenue on a night that was going to be dead,
zero upfront cost, no staff burden, new regulars, reviews/photos, and not having
their dining room turned into a cringe "singles mixer."

### Consumer participant (the one who shows up)
**"Social-hungry local, 24–45."** Newer to Houston/Spring or just tired of apps;
wants low-pressure, structured ways to meet people that don't feel like a bar crawl
or a swipe session. Comfortable paying a small deposit for a real plan on a real
date. Four intents, four formats: dating (Singles Dinner Night), platonic (New
Friends Dinner), food-first (Food Discovery Table), belonging (Community Dinner
Night). Halal-friendly formats are a genuine differentiator in this trade area.

---

## Competitive landscape (researched 2026-07; don't skip this)

The *consumer experience* is validated and crowded; the *restaurant-side business*
is not. Position accordingly.

- **Timeleft** (timeleft.com) — the category giant: ~6,500 dinners/week, ~150k
  monthly participants, €18M ARR, 200+ cities **including Houston**. Consumer pays
  a ticket fee; restaurants pay nothing and are treated as free inventory (their
  stated scaling strategy: no hosts, no restaurant ops). One SKU: 6 strangers,
  algorithm-matched, weeknight dinner.
- **222** (222.place) — $10.1M Series A; LA/NYC-centric. Consumer curation fee /
  subscription, plus a restaurant partner program (~$3/person sent). Closest to
  monetizing the venue side, but still a consumer-app company; no slow-night
  program, no ROI accounting, no hosting.
- **OpenToBites** — local Houston app for dinner meetups; early, consumer-side.

**What this means:**
1. Demand is proven — people demonstrably pay $16–20 just to be seated with
   strangers. Our deposit-that-becomes-food is an easier ask, not a harder one.
2. The undefended ground is **venue-side**: selling restaurants a measured
   slow-night revenue program (hosted formats, POS baseline comparison,
   pay-per-seated-guest) in **suburban trade areas** (Spring/Klein/Woodlands)
   below the density these machines need — plus formats only a venue operator can
   run (Food Discovery as menu marketing, halal-friendly tables, community nights).
3. The risk is drifting into their lane: a generic "dinner with strangers" brand
   competing for Inner-Loop consumers loses to Timeleft's polish. If a consumer in
   our funnel could have used Timeleft instead, we're off-position.
4. Cheap intelligence play: attend a Houston Timeleft dinner before pilot week 1;
   consider listing W&K as a venue for such platforms — free covers + a view of
   the machine from inside.

## Why this is not a dating app

- **The customer is the restaurant.** Revenue comes from venues paying for seated
  guests, not from consumers paying for matches. Consumers pay at most a deposit
  that converts to food.
- **Aligned incentives.** A dating app monetizes *continued searching*; success
  (finding someone) churns the user. A restaurant benefits *every single time*
  people meet in person — food is bought, reviews are posted, people return. Our
  success metric is seated covers and repeat dinners, not engagement minutes.
- **Dating is one format of four.** Singles Dinner Night sits beside New Friends,
  Food Discovery, and Community Dinner. The product is the *table*, not the match.
- **No profiles, no swiping, no chat, no matching algorithm.** There is an
  application for a seat at a dinner. That's it.
- Positioning rule (from the owner, binding on all copy): never "dating app" —
  always "restaurant social dining demand engine" / "curated social dining."

---

## MVP scope (this build)

1. **Public site (Flask, server-rendered):**
   - Landing page: concept, "Find a Dinner" (consumer CTA), "Fill Empty Tables"
     (restaurant CTA), explicit "real-world dining, not a dating app" framing.
   - Events listing with event-type filter; shows date/time, venue, seats left,
     deposit, vibe.
   - Event detail + application/reservation form with trust & safety language and
     consent checkbox. Deposit is **placeholder language only** (no payment rails).
   - Restaurant lead page: pay-per-seated-guest model, worked ROI example, inquiry
     form.
2. **Admin/operator dashboard** (HTTP Basic auth, local): create/edit events across
   the full status lifecycle (draft/open/full/completed/cancelled); view applicants;
   approve/waitlist/reject; track confirmed; mark seated/no-show; capture final
   sales estimate + baseline; per-event ROI summary; restaurant inquiries list.
3. **Storage:** local JSON file (`data/db.json`), seeded with three Wok & Karahi
   events. No production DB.
4. **Clover adapter (mocked)** in `integrations/clover/` defining the future
   read-only integration: sales by time window, event-night vs baseline comparison,
   check-in tracking, incremental revenue estimate.
5. **Docs:** this spec, PROJECT_NOTES, MARKETING_COPY, VALIDATION_PLAN, QA_REPORT.

### Out of scope (deliberately)
- Real payments/deposit collection (pilot: Zelle / Clover payment link, manual).
- Accounts, login, profiles, messaging/chat between guests, matching algorithms.
- Automated seating/balancing (operator does it by hand from the applicant list).
- SMS/email automation (pilot: operator texts from their phone; templates provided).
- Live Clover API calls, background checks/ID verification (stated policy + host
  presence instead), multi-tenant restaurant self-serve, native apps, deployment.

---

## Flows

### First pilot flow (Wok & Karahi, end-to-end)
1. Operator (Abbas/AZ) creates "Houston Singles Dinner" at Wok & Karahi on a slow
   Tue/Wed/Thu 6:30 PM slot, capacity ~16–20, $10 deposit-toward-meal, small perk
   (e.g. free appetizer platter for the table).
2. Demand gen runs from MARKETING_COPY assets (GBP post, WhatsApp/community groups,
   Eventbrite/Meetup cross-list, personal networks). All links → event detail page.
3. Applications arrive; operator reviews daily, approves for balance (singles
   events: roughly even gender split, compatible age bands), waitlists overflow.
4. Approved guests get a confirmation text (template provided) + deposit
   instructions (manual). Confirmed = deposit received, marked in admin.
5. Event night: operator (or trained host) greets, checks names off (mark seated /
   no-show), seats people at assigned tables, runs 1–2 light icebreakers, stays
   ~30 min, then lets dinner happen.
6. Next morning: capture restaurant's read of the night (sales during window vs a
   normal night — later automated via Clover), record in admin ROI panel, send
   guests the feedback ask + next-event invite.
7. After 2–3 events: write the case study from real numbers (VALIDATION_PLAN).

### Restaurant-facing flow
Inquiry (lead page form) → discovery call (slow windows, capacity, perk budget) →
agree pilot terms (first event free or pay-per-seated-guest, ~$6/seated guest;
restaurant provides perk) → AZ creates + fills + hosts the event → morning-after
one-page recap: applicants, confirmed, seated, no-shows, estimated event revenue vs
baseline, fee owed → repeat weekly/biweekly; convert to a monthly "slow-night
program" once ROI is shown 2–3 times.

### Consumer-facing flow
Sees a post/link → landing or event detail → applies (name, phone/email, age range,
gender where relevant for balancing, intent, dietary, area, one vibe question,
consent) → gets "application received, you'll hear within 48h" → approved →
confirmation + deposit instructions → reminder day-of → dinner → feedback ask +
first-look invite to the next table.

### Admin/operator flow
Dashboard (events + pipeline counts + inquiries) → per-event: applicant queue with
approve/waitlist/reject, gender/intent tallies for balancing, confirmed tracker →
event night: seated/no-show toggles → close-out: enter sales estimate + baseline,
ROI summary auto-computed (incremental revenue, fee, restaurant net) → mark event
completed.

---

## Data model (MVP)

**Event:** id · title · type (singles/friends/discovery/community) · venue name +
area · date · time · age_range · capacity · deposit (USD, toward meal) · offer ·
dietary_notes · description · status (draft/open/full/completed/cancelled) ·
per_guest_fee · roi {sales_estimate, baseline_estimate, notes}.

**Application:** id · event_id · name · phone · email · age_range · gender
(optional; asked when the event balances by it) · intent (dating/friends/food/
community) · dietary · area · vibe (short answer) · consent (bool, required) ·
status (pending/approved/waitlist/rejected) · confirmed (deposit received) ·
attendance (—/seated/no_show).

**RestaurantInquiry:** id · restaurant · contact name · email/phone · neighborhood ·
slow nights · notes · status (new/contacted/closed).

---

## Metrics to track (pilot)

Per event: applications · approval rate · confirmed seats · show-up rate ·
gender/intent balance achieved · avg spend/head (from restaurant) · event-window
revenue vs baseline (incremental $) · fee charged vs incremental (restaurant ROI
multiple) · consumer feedback count + would-return % · social posts/reviews
generated · repeat-attendance rate across events · cost per application by channel.

North-star: **incremental restaurant revenue per event** and **repeat attendance**.

## Risks
- **No-shows** kill economics → deposit-toward-meal + day-of reminder + waitlist
  backfill; measure show rate from event 1.
- **Gender/intent imbalance** at singles events → approve from a queue, don't
  auto-accept; waitlist is the balancing buffer; New Friends format as the fallback.
- **Cold-start demand** (39 organic-social sessions/6mo at the lab) → borrow
  distribution: GBP 81k views/6mo, community WhatsApp/Facebook groups,
  Eventbrite/Meetup marketplaces, not owned social.
- **"Dating app" perception** → copy discipline (see MARKETING_COPY), 4 formats
  visibly co-equal, venue-first brand.
- **Safety incident** → public venue, host present, consent + conduct language at
  application, right-to-refuse; phone numbers collected for accountability.
- **Measuring "incremental" honestly** → define baseline as same-weekday average
  (last 4 weeks) for the same time window; later automate via Clover.

## Assumptions (labeled)
- Pilot venue = Wok & Karahi; its slow windows are Tue–Thu dinner (inferred from
  hours + owner context; verify against JOB B sales analysis before scheduling).
- ~$6 per seated guest fee and $10 deposit are placeholder economics to validate,
  not settled pricing; first pilot event may run free to the venue.
- Avg spend $20+/head is plausible at W&K price points (live-site prices; verify
  event 1). Manual ops can handle ≤ 2 events/week without automation.

## Validation plan (summary — full plan in VALIDATION_PLAN.md)
Run 3–4 manual events at Wok & Karahi in 30 days. Success gates: 40+ applications
for event 1, 16–24 confirmed, 70%+ show rate, $20+ avg spend, measurable lift vs
baseline, ≥5 feedback responses, ≥2 organic posts/reviews. If gates pass, write the
case study and take it to 3 non-owned restaurants; if demand fails, pivot format
(brunch/lunch, community-org partnerships) before adding any software.
