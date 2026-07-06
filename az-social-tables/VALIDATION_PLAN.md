# VALIDATION_PLAN — 30-day Wok & Karahi pilot

**Question being validated:** will local people pay a deposit and show up to curated
restaurant dinners on slow nights, at unit economics a restaurant would pay for?

**Principle: run it manually before scaling.** The software (this MVP) is an
operator console + application funnel — nothing more. Deposits by Zelle/Clover
payment link, confirmations by personal text, seating chart on paper. Automate only
what breaks twice.

---

## The 30 days (four weeks, three–four events)

**Week 0 (prep, ~3 days)**
- Pick dates on W&K's soft nights (Tue/Wed/Thu dinner; **verify the softest window
  against the JOB B sales analysis** in the restaurant repo before locking dates).
- Confirm with the venue (i.e., with yourself as owner — but write the agreement
  down anyway; it becomes the template for restaurant #2): capacity, table layout,
  the perk (appetizer platters), fee ($6/seated guest, waived event 1).
- Stand up the MVP locally/on a $0 host; set real `AUTH_USER/PASS`; create the
  three seed events with real dates.
- Prepare channel posts from MARKETING_COPY (GBP post, Eventbrite, Meetup, 3–5
  local Facebook/WhatsApp groups, personal networks). Tag every link
  (`?src=gbp|eb|meetup|fb|wa`) so cost-per-application by channel is measurable
  from server logs.

**Week 1 — Event 1: Houston Singles Dinner (the demand stress-test)**
- Publish everywhere Mon; approve daily; balance the table (target ~50/50 gender,
  one age band); confirm 20 against 16 seats (overbook ~25% vs. expected no-shows);
  deposit instructions by text; day-of reminder.
- Run the night: check-in sheet, mark seated/no-show in admin, two icebreakers,
  host stays 30–45 min then hovers lightly.
- Next morning: pull the event-window sales from Clover, enter sales + baseline
  (same weekday avg, last 4 weeks) in the ROI panel, text guests a 3-question
  feedback ask + first-look invite to the next dinner, and ask the happy ones for
  a Google review/photo post.

**Week 2 — Event 2: New Friends Dinner.** Repeat the machine. Watch which format
draws harder. **Week 3 — Event 3: Food Discovery Table** (12 seats, prix-fixe
tasting — tests a higher-deposit, food-first audience). **Week 4 — repeat the
winner**, this time with the $6/seated-guest fee "charged" on paper even to
yourself — the invoice becomes the case-study artifact.

## Target metrics (success gates, per the owner)

| Metric | Gate |
|---|---|
| Applications for event 1 | **40+** |
| Confirmed seats | **16–24** |
| Show-up rate | **70%+** |
| Average spend per person | **$20+** |
| Consumer feedback responses | **≥ 5** |
| Social posts / reviews generated | **≥ 2** |
| Slow-night sales lift | **measurable vs. 4-week same-weekday baseline** |
| Repeat applications by event 3–4 | (tracking) **≥ 20%** of past attendees |

**Success =** ≥6 of 8 gates hit, including show-up rate and measurable lift — and
the operator effort per event is ≤ ~6 hours. That's a sellable, repeatable product:
write the case study, go to restaurant #2.

**Failure =** applications < 20 for event 1 after a full channel push (demand
problem), or show-rate < 50% despite deposits (commitment problem), or lift ≤ $0
(economics problem). Each has a different response — see kill/pivot rules.

## What must be true before selling to other restaurants

1. Two consecutive events with 70%+ show rate and clean ROI math from real POS data.
2. A repeatable fill playbook: known cost-per-application by channel, known
   application→confirmed conversion, a reusable 2-week promotion calendar.
3. The morning-after recap takes < 30 minutes to produce.
4. At least one event where the fee was actually accounted for and the restaurant
   still netted positive — that line is the whole sales pitch.
5. Host runbook written down (check-in, icebreakers, problem-guest handling) so a
   non-founder can run event 4.

## Kill / pivot rules (decided now, not in the moment)

- **Demand fails** (apps < 20): don't build more software. Test the same event
  through partnerships (mosque/community orgs, ISA/professional groups, apartment
  complexes) and brunch/lunch slots before abandoning.
- **Show-up fails** (< 50%): raise deposit to $15–20, shrink tables to 10–12,
  switch to prepaid prix-fixe. If it still fails, the format is wrong, not the price.
- **Economics fail** (lift ≈ 0 because the night cannibalized regulars): move
  events to the genuinely dead 5–7 PM window or Monday-style private buyouts.
- **Balancing fails** (singles table skews hard one way): lead with New Friends +
  Food Discovery — they don't need balance and still sell covers.

## The case study (the real deliverable of the pilot)

One page, published to `azrestaurantpartners.com` alongside the existing flagship
case study, built only from measured numbers:

> **"How Wok & Karahi turned a dead Tuesday into $X,XXX of tracked revenue"**
> The empty-night problem → the format (photo of the actual table) → the funnel
> numbers (applications → confirmed → seated, by channel) → the POS math
> (event window vs. 4-week baseline, spend/head, fee, net) → guest quotes +
> review screenshots → "Your first event is free" CTA.

Collect during the pilot, not after: photos of the full table (with consent),
guest quotes from feedback texts, the Clover screenshots, the paper invoice.
