# Restaurant Intelligence Dossier - architecture

The template every restaurant runs through. Written before the collectors, on purpose,
because the guardrails are the valuable part and they are hard to retrofit.

Version 1, 2026-08-18.

---

## 0. The one rule

**Every field carries its own provenance and its own evidence tier. No exceptions.**

```json
{
  "value": "no direct ordering",
  "tier": "OBSERVED",
  "source": "https://example.com/",
  "method": "static fetch + link scan",
  "observed_at": "2026-08-18T14:22:07Z",
  "confidence": 0.95,
  "expires": "2026-09-18"
}
```

Four tiers, and they never blur:

| Tier | Means | Example |
|---|---|---|
| `OBSERVED` | We saw it directly, at a URL, at a time | 3.9 stars, 412 reviews, read 18 Aug |
| `DERIVED` | Arithmetic on observed values only | Review velocity fell 60% year over year |
| `INFERRED` | Our judgement about cause. Always carries confidence and an alternative | Slow weeknight service is a staffing pattern, 0.55 |
| `UNKNOWN` | We could not get it. Says so out loud | Weekly covers |

**Why this rule exists and is not negotiable:** the failure mode is a hedge hardening into a
fact as it moves from collection to summary to conversation. An inference that loses its tier
becomes something we say to an owner as though we know it. That is how you lose a room.

Corollary: **an empty field is a finding, never a blank.** `UNKNOWN` with a reason beats a
guessed value every time.

---

## 1. The abstraction ladder

He asked for surface, then why, then deeper. That is six rungs, and a finding that stops
below rung 4 is noise.

```
L0  SIGNAL     what we literally saw
L1  PATTERN    what repeats across signals
L2  MECHANISM  the operational behaviour that produces the pattern
L3  ROOT       the decision, constraint or absence underneath it
L4  MONEY      what it costs per week, with the arithmetic shown
L5  MOVE       what we would do, effort, and what changes first
```

Worked example, all six rungs:

```
L0  17 of 60 recent reviews mention waiting; 12 of those posted Fri or Sat
L1  Complaints cluster Fri/Sat 6-8pm, not spread through the week
L2  The room fills faster than the kitchen or the front can absorb at peak
L3  Staffing and prep are planned to a weekly average, not to the peak shape
L4  ~8 tables/wk turned away or soured x avg ticket $46 = ~$370/wk, plus the
    rating drag on future discovery
L5  Demand-shape read from their own POS, prep and roster to the peak, phone
    coverage during the rush. Two weeks. Wait complaints move first.
```

**Rules for the ladder**
- Never skip a rung. L0 to L4 without L2 and L3 is a guess dressed as analysis.
- L3 must name something an owner could actually change.
- L4 must show its arithmetic and its assumptions, and mark every assumption.
- Where the ladder cannot reach L3 honestly, stop at L2 and say so.

---

## 2. Collection domains

Fourteen domains. Each field carries the tier block from section 0.

Domains A-J are collection. K-N are the reads that turn collection into a
conversation: the menu teardown (section 4), the guest journey (5), the two
discovery scores (6) and the improvement map (7).

### A. Identity and premises
| Field | Source | Obtainable |
|---|---|---|
| Legal name, DBA, owner entity | HCAD, TX Comptroller, TABC | Free, public record |
| Address, suite, centre name | Their site, Maps | Free |
| **Building square footage, year built** | **HCAD (public.hcad.org)** | **Free, public record** |
| Lease vs own, land value | HCAD | Free |
| Estimated seats | sqft heuristic, photos, reservation grid | Derived, low confidence |
| Kitchen type (hood, patio, drive-thru) | HCAD improvements, photos | Free |
| Alcohol permit, type, issue date | TABC public inquiry | Free, public record |
| Sales tax permit, start date, tenure | TX Comptroller | Free, public record |

Why this matters: square footage and permit dates are the only hard, verifiable facts we
can get about the physical business. Tenure separates an operator with ten years of habits
from one still finding their feet. Alcohol permit tells you whether bar margin is even on
the table.

### B. Discovery
| Field | Source | Obtainable |
|---|---|---|
| Site status: dead / parked / JS-shell / real | Our crawler | Free |
| HTTPS, mobile, Core Web Vitals proxy | Fetch, PSI API | Free |
| Restaurant / LocalBusiness schema | Parse | Free |
| Menu format: HTML, PDF, image, JS-only | Crawl | Free |
| Hours published, and do they agree across surfaces | Site vs Maps vs Yelp | Free |
| GBP claimed, categories, attributes, photo count | Maps | Free to read |
| Ranks for "<cuisine> near me" style queries | Manual or SERP API | Paid or sampled |
| **Named by ChatGPT / Gemini / Perplexity for local prompts** | Prompt each, log verbatim | Free, manual |
| Indexed page count | `site:` query | Free |

### C. Reputation - the deep one
See section 3. This is the richest source and the most misread.

### D. Ordering and channel economics
| Field | Source |
|---|---|
| Direct ordering platform (Toast, Owner, ChowNow, Square, Popmenu, Menufy, Slice) | Link scan |
| Third-party presence: DoorDash, Uber Eats, Grubhub | Their site, each app |
| Menu price delta between direct and 3P | Compare same dish |
| Delivery radius and fees | 3P listing |
| Estimated commission exposure | Derived, assumptions marked |
| Reservations platform | Link scan |
| Gift cards, merch | Site |

The price delta is the sharpest single number we can hand an owner: if their DoorDash price
is already marked up 15%, they have felt the commission and responded to it. If it is not,
they may not have done the arithmetic yet.

### E. Menu and offer
| Field | Source |
|---|---|
| Item count, category count, price band, min/median/max | Menu parse |
| Last menu change we can detect | Wayback diff |
| **Catering: offered? how ordered? minimums? lead time?** | Site crawl of /catering |
| Private dining, events, buyouts | Site, Maps attributes |
| Lunch special, happy hour, daypart offers | Menu |
| Dietary coverage (veg, halal, gluten) | Menu text |
| Family packs, bundles | Menu |

**On catering specifically, since it was called out:** the interesting question is never
"do they cater" but "why not, and what is in the way". Distinguish these cases, because the
pitch differs completely:
1. No catering anywhere. Capability unknown. Usually never considered.
2. Catering mentioned, no way to order or price it. Demand exists, channel does not.
3. Catering page exists, stale or broken. Tried, no owner of it.
4. Catering with a real order path. Competent, look for volume levers instead.

### F. Social and content
| Field | Source | Note |
|---|---|---|
| Platforms, handles, follower counts | Public profiles | Free |
| Posting cadence, last post date | Public profile | Dormancy is the signal |
| **Top posts by views, and what they are about** | Public profile | Tells you what their audience actually responds to |
| Comment volume and whether the owner replies | Public post | Engagement is not reach |
| **Creators and influencers who posted about them** | Search handle mentions | Free, manual |
| Whether creator content was reshared by the venue | Compare | A missed reshare is free reach thrown away |
| UGC volume: tagged posts, location tag count | Location page | Free |
| Video content: exists? phone-shot? menu-led? | Profile | Free |

The point is not vanity metrics. It is: **who is already doing their marketing for them for
free, and are they even picking it up.**

### G. Earned media and mentions
| Field | Source |
|---|---|
| Local press: Community Impact, Houston Chronicle, Houstonia, CultureMap, Chron | Search |
| Neighbourhood media: Cypress Digest, MyNeighborhoodNews | Search |
| Blogs, roundups, "best of" lists | Search |
| Reddit r/houston, r/CyFair threads | Search, read only |
| Nextdoor recommendations | Search |
| Awards, mentions, TV | Search |
| Backlinks and referring domains | Paid tool, or approximate by mention search |
| Directory presence and NAP consistency | Yelp, TripAdvisor, MenuPix, YellowPages |

NAP consistency (name, address, phone) across directories is unglamorous and one of the most
common silent killers of local ranking.

### H. Competitive set
| Field | Method |
|---|---|
| Same cuisine within 3 miles | Maps |
| Their rating and review count vs this restaurant | Maps |
| Which competitors have direct ordering, schema, catering | Run this same dossier on them |
| Who is winning the AI answer for the obvious prompts | Prompt and log |

A finding is only actionable relative to the neighbours. 4.1 stars is strong in a 3.9
neighbourhood and weak in a 4.6 one.

### I. Operations and compliance signals
| Field | Source |
|---|---|
| Health inspection scores and history | Harris County Public Health, public |
| Violation themes over time | Same |
| Hours changed or reduced recently | Maps edits, Wayback |
| "Temporarily closed" history | Maps |
| Job postings, and for which roles | Indeed, their socials |

Hiring for front of house repeatedly is a retention signal. Reduced hours is a labour or
demand signal. Both change what you lead with.

### J. Owner and tenure
Business-level only. Owner entity from public record, years trading, number of locations,
whether the owner appears in their own content. **Never build a profile of a private
individual.** See guardrails.

---

## 3. The review teardown

The richest signal and the one most often read lazily. Star average alone is nearly useless.

### 3.1 Shape
- Volume, and velocity: reviews per month over 24 months
- **Velocity trend**, which matters far more than the average. Falling velocity means fading
  relevance even when the rating holds
- Distribution across 1-5, not just the mean. A 4.2 made of 5s and 1s is a consistency
  problem; a 4.2 made of 4s is a ceiling problem
- Rating trajectory: last 90 days vs lifetime
- Platform spread: Google vs Yelp vs TripAdvisor vs Facebook, and where they disagree

### 3.2 Owner response behaviour
- Response rate, split by rating. Many owners answer only 5-star reviews, which is backwards
- Median response latency
- Template detection: are replies near-identical
- Tone on negatives: defensive, apologetic, corrective, absent
- Does a reply ever resolve, or only acknowledge

Response behaviour is a proxy for whether anyone owns reputation at all.

### 3.3 Theme extraction
Classify every review into recurring themes, and track each theme's own trend:

```
food quality      consistency      portion vs price
speed of service  wait for a table wait for food
order accuracy    missing items    delivery condition
phone unanswered  booking friction parking
cleanliness       noise            temperature of room
staff warmth      staff shortage   management response
```

For each theme: count, share of total, sentiment, direction over time, and **the exact
verbatim quotes**, because the quote is what an owner reacts to.

### 3.4 Temporal analysis
- Day of week distribution of negatives
- Daypart where inferable from the text ("Friday night", "at lunch")
- Seasonality
- **Incident clusters:** three or more negatives inside a fortnight after a quiet period
  usually marks a real event - a departure, a menu change, a POS migration, an ownership
  change. Find the cluster, then look for what changed around it

### 3.5 Entity extraction
- Dishes named, split by positive and negative. This is the single most useful output for an
  operator: which dishes create advocates and which create refunds
- Occasions named: date night, family, business lunch, catering, large party
- Competitors named in comparisons

### 3.6 Root-cause hypotheses
For each theme that matters, produce candidate causes with confidence, and always at least
one alternative explanation. Wait complaints clustered on Friday nights could be
understaffing, kitchen capacity, a menu with too many made-to-order items, or a POS that
slows the pass. **The dossier proposes; only the owner's own numbers confirm.**

---

## 4. The menu teardown

The menu is the only document a restaurant publishes that is simultaneously its product
catalogue, its pricing strategy and its margin structure. Most owners have never had it read
back to them as any of those.

### 4.1 Structure
- Category count, order of categories, item count per category
- Items per category: 5-7 reads as curated, 20+ reads as a kitchen that cannot say no
- Is the first category the one they want to sell, or the one convention expects
- Total item count. Above roughly 60, prep complexity and waste usually climb faster than sales
- Navigation depth on a phone: taps from landing to a given dish

### 4.2 Price architecture
- Min, median, max per category, and the spread
- **Price anchoring:** is there a high item that makes the middle look reasonable, or does the
  menu open at the top and fall
- Price clustering: three items within 50 cents means no deliberate tiering
- Currency formatting. `$` signs measurably increase price salience; plain numerals do not
- Charm pricing (.99 / .95) vs round. Round reads premium, charm reads value. Mixed reads accidental
- **Direct vs third-party delta per dish.** If 3P prices are not marked up, they are absorbing
  the full commission and have not done the arithmetic

### 4.3 Add-ons, modifiers and the attach rate
This is the single largest untouched lever on average order value in almost every independent.
- Do modifiers exist at all in the online flow, or only in person
- Are they priced, and are they free-text or structured
- Required vs optional modifiers, and default selections
- Are the profitable attaches offered: drinks, sides, sauces, extra protein, dessert
- Is anything suggested **at the right moment** in the order flow, or only listed
- Combos, family packs, bundles - and whether the bundle actually saves the guest anything
- Catering minimums, per-head pricing, lead time

Cheap attaches with high margin - a drink, a side, a sauce - are worth more per week than most
marketing. If the online flow offers none, that is a specific, fixable number.

### 4.4 Beverage programme
Separate because it is the highest-margin line on any menu.
- Is there a beverage menu at all, or an afterthought list
- Soft drink, tea, coffee, speciality, alcohol
- Cross-referenced with the TABC permit: a permit and no visible drinks list is money on the floor
- Are drinks visible in the online ordering flow

### 4.5 Description and merchandising
- Do items have descriptions, or only names. A name sells nothing to a first-timer
- Description length and whether it names ingredients, origin, heat, or preparation
- **Photo coverage:** share of items with a photo. Photos are the strongest single conversion
  lever in online ordering
- Dietary and allergen labelling: vegetarian, vegan, gluten, halal, spice level
- Signature or recommended markers
- Does anything explain what a guest unfamiliar with the cuisine should order first

### 4.6 Menu engineering, as far as we honestly can
The real matrix needs popularity and food cost, and we have neither. What we can do:
- **Popularity proxy** from review dish mentions, weighted by recency
- **Margin proxy** from category heuristics: rice, noodle, bread, fried and beverage items
  are typically high margin; whole protein and seafood typically low
- Place items on the matrix, and label the whole thing `INFERRED` with the reasoning visible
- The output is a question for the owner, not a verdict: "these look like your stars and these
  look like they cost you money - does that match your numbers"

### 4.7 Change history
Wayback diff on the menu page. Frequency of change, direction of price change over 24 months,
and whether items were cut or added. A menu untouched for three years while food costs rose is
itself a finding.

---

## 5. The guest journey audit

Everything above is what we can measure. This is what a normal person actually feels, stage by
stage, run **on a phone**, timed and counted, by walking the funnel as a first-time guest.

For every stage: what they see, how long it takes, how many taps, where they would give up,
and a one-line impression written in a guest's voice rather than ours.

| # | Stage | What we capture | The felt question |
|---|---|---|---|
| 1 | Intent | Search "<cuisine> near me" and 4 more prompts. Do they appear, in what position, on Maps and in AI answers | Do they exist at all |
| 2 | First glance | Maps card: rating, count, photo quality, category, hours accuracy, price band | Does this look like somewhere I would eat |
| 3 | Consider | Tap through. Load time, what is above the fold, is the phone tappable | Do I trust this |
| 4 | Menu | Taps to menu, readable on a phone, current, prices visible | Can I decide |
| 5 | Decide | Is there any path to order, and is it obvious | Can I act |
| 6 | Order | Taps to complete, account required, guest checkout, minimums, fees revealed early or late, upsells | How hard is this |
| 7 | Confirm | Confirmation clarity, time estimate, tracking | Do I know what happens now |
| 8 | Receive | Accuracy and packaging themes from reviews | Did I get what I chose |
| 9 | Return | Any review request, any way to be remembered, any reason to come back | Will I ever hear from them again |

**Scoring per stage:** 0 impossible, 1 painful, 2 works, 3 good, 4 better than the neighbours.
Report the **weakest stage, not the average.** A funnel is only as good as its worst step, and
the fix belongs there rather than wherever we happen to be strongest.

**Two hard rules.**
Run it on a phone viewport, because that is where the decision is made.
**Never complete an order.** Walk to the final confirm screen and stop. We do not place real
orders on other people's kitchens to fill in a spreadsheet.

Output is a nine-line narrative, in a guest's voice. Read aloud to an owner it is usually the
most persuasive thing in the dossier, because it is their restaurant described by a stranger.

---

## 6. Discovery scores: SEO and AEO, kept apart

Two scores, never one. They are related and not the same, and being strong on one does not
carry you on the other. Both 0-100, both reported **against the local competitive median**,
because an absolute number means nothing in isolation.

### 6.1 SEO score
| Weight | Component |
|---|---|
| 25 | **Google Business Profile:** claimed, categories, hours, attributes, photo count and recency, posts, Q&A |
| 20 | **Reviews as a ranking input:** count, velocity, recency, response rate |
| 15 | **Technical:** HTTPS, mobile, load, no blocking robots, indexed pages |
| 15 | **On-page:** title, meta, headings, menu as real text, location named |
| 15 | **NAP consistency** across Google, Yelp, Facebook, TripAdvisor, directories |
| 10 | **Content and links:** pages beyond the menu, referring domains, local press |

### 6.2 AEO score
| Weight | Component |
|---|---|
| 30 | **Named in AI answers.** Ask each engine the same standard prompt set and log the verbatim answer. This is the only component that measures the outcome rather than a proxy |
| 20 | **Structured data:** Restaurant, Menu, hours, geo, FAQ, and whether it validates |
| 15 | **Machine-readable menu:** text beats PDF beats image beats JS-only |
| 15 | **Entity clarity:** name, cuisine and location described identically everywhere. Assistants resolve entities, and contradictions make them cautious |
| 10 | **Answerable content:** does anything on the site answer a question a person would ask |
| 10 | **Crawler access:** are GPTBot, ClaudeBot, PerplexityBot and the rest permitted. Many sites block them by accident through a template `robots.txt` |

**The standard prompt set** - identical for every restaurant, so results compare:
1. best <cuisine> restaurant in <city> TX
2. where should I eat <cuisine> near <landmark>
3. <restaurant name> - what do you know about it
4. good <cuisine> for a family near <city>
5. who caters <cuisine> in <city> TX

Log the verbatim answer, whether they were named, in what position, and whether the description
was accurate. **A wrong description is worse than an absence** and is one of the most convincing
findings we can show an owner.

---

## 7. The improvement map

Where the dossier turns into work. Every finding produces candidate moves, and each move is
classified honestly, because the credibility of the whole exercise rests on not recommending
software when the answer is not software.

**Two kinds, kept separate:**

- **Technological** - something we build, buy, connect or configure.
- **Operational** - a change to how the restaurant runs. Prep timing, roster shape, phone
  cover during the rush, a script for asking for a review, which dish leads the menu.
  Frequently the higher return, almost always the cheaper, and nobody sells it to them
  because there is no commission in it.

Every move carries:

```json
{
  "move": "", "kind": "technological | operational",
  "job": "getting found | winning the order | growing the order |
          keeping the guest | keeping the money | watching it",
  "addresses": ["finding-id"],
  "effort_hours": 0, "owner_effort_hours": 0,
  "depends_on": [], "cost_to_them": 0,
  "expected_effect": { "metric": "", "direction": "", "size": "", "confidence": 0.0 },
  "time_to_signal_days": 0,
  "evidence_tier": "INFERRED"
}
```

**Sequencing rules**
1. Anything that makes them findable comes before anything that improves conversion. Traffic
   you do not have cannot convert.
2. Fix leaks before adding channels. A new channel pouring into a broken order flow wastes it.
3. First move must show signal inside 14 days, or momentum dies.
4. Owner effort near zero for the first two weeks. They are already working every hour.
5. **If the best move is operational and free, say so first.** That single habit is what makes
   the paid work believable afterwards.

Output is ranked by `expected_effect / (effort + owner_effort)`, not by what is most impressive
to build.

---

## 8. Site crawl specification

Written because version 1 got this wrong: it treated HTTP 200 as "has a website" and
reported 38 working sites when only 26 were substantive. Twelve were parked domains, empty
shells or JS apps that served an empty body.

**Classify before analysing:**

```
DEAD        no response, DNS failure, or < 500 bytes
PARKED      registrar or "coming soon" fingerprint, ~1 link, no menu
JS_SHELL    links present, text absent  ->  must render before any claim
STATIC      text present, parseable
```

**Substance test, and nothing is claimed until it passes:**
`text >= 150 words AND internal links >= 3 AND (menu OR hours OR contact present)`

**Crawl, do not just fetch the homepage.** Follow, up to 15 pages, one host:
`/menu /menus /catering /order /about /contact /hours /events /private-dining /specials /reviews`

**Render JS shells** with headless Chrome. A JS shell is not a finding of absence; it is a
finding that a static read is insufficient. Reporting "no menu" on an unrendered React app
is a false negative that would embarrass us in front of an owner.

**Also capture:** Wayback first and last snapshot, redirect chain, page weight, mobile
viewport, and whether the phone number is a `tel:` link.

---

## 9. Guardrails

**Sources**
- Public, unauthenticated pages only. Never anything behind a login.
- Honour `robots.txt` and platform terms. Where terms forbid automated collection, the field
  is collected manually or marked `UNKNOWN`. It is never quietly scraped anyway.
- Identify honestly in the user agent. Rate limit to one request per host per two seconds.
- Cache aggressively. Never re-hit a host for data we already hold and that has not expired.

**People**
- This is business intelligence, not people intelligence.
- Staff named in reviews are **aggregated and never named in output**. "Reviews name the same
  server positively 14 times" is useful. Naming them is not ours to publish.
- Owner information is limited to what public business records already state.
- No home addresses, no personal social accounts, no family.

**Claims**
- Nothing enters the dossier without source and timestamp.
- Inference is labelled as inference wherever it is displayed, not only where it is stored.
- Every money figure shows its arithmetic and marks its assumptions.
- Competitor comparisons use the same method for both sides or they are not made.

**Use**
- The dossier informs a conversation. It is never sent to the restaurant.
- We do not open with a list of their failings. We open with one thing, and we are right
  about it.
- If a finding would embarrass an owner in front of staff, it does not go in an opener.

**Freshness**
- Every field has an expiry. Reviews 14 days, site 30, social 14, public records 180.
- A dossier older than 30 days is re-run before it is used, or it is shown as stale.

---

## 10. Output shape

```
outreach/
  targets/<area>.json          the input list
  dossiers/<slug>.json         one full dossier per restaurant
  board-<area>.html            the working board
  ARCHITECTURE.md              this file
```

Each dossier:

```json
{
  "restaurant": { "name": "", "slug": "", "area": "" },
  "collected_at": "",
  "completeness": { "domains_attempted": 14, "domains_returned": 7, "unknown_fields": 23 },
  "domains": { "identity": {}, "discovery": {}, "reputation": {},
               "ordering": {}, "menu": {}, "social": {}, "media": {},
               "competitive": {}, "operations": {}, "owner": {} },
  "menu_teardown": { "structure": {}, "price": {}, "modifiers": {},
                     "beverage": {}, "merchandising": {}, "engineering": {} },
  "journey": { "stages": [], "weakest_stage": "", "narrative": [] },
  "scores": { "seo": { "total": 0, "components": {}, "vs_local_median": 0 },
              "aeo": { "total": 0, "components": {}, "prompts": [] } },
  "improvement_map": [],
  "ladder": [ { "l0": "", "l1": "", "l2": "", "l3": "", "l4": {}, "l5": {} } ],
  "headline": { "one_thing": "", "evidence": "", "money_per_week": 0, "tier": "" },
  "opener": "",
  "do_not_say": []
}
```

`completeness` is deliberately prominent. A dossier that returned 3 of 10 domains must look
different from one that returned 10, so nobody mistakes thin for clean.

`do_not_say` carries anything true but unusable - a health violation, a bad review naming a
family member. Knowing it and not leading with it is the difference between a partner and a
vendor.

---

## 11. Obtainability, honestly

| Tier | Domains | Cost |
|---|---|---|
| Automatable now, free | Site crawl, schema, ordering, menu parse, price architecture, modifiers, HCAD, TABC, Comptroller, health scores, Wayback, mention search, robots crawler-access | Time only |
| Automatable, paid API | Google Places reviews, PageSpeed at volume, SERP ranks, backlinks | Metered |
| Manual, high value | AI answer checks against the standard prompt set, the nine-stage guest journey, social top-posts, influencer mentions, competitor AI ranking | 20-30 min per restaurant |
| Not obtainable, ever | Revenue, margins, food cost, labour, rent, covers, item popularity, POS data, owner intent | Only the owner has these |

That last row is the discipline. **We can see everything about how a restaurant appears and
nothing about how it performs.** The dossier is a map of the surface and a set of honest
hypotheses about what is under it. The moment we pretend otherwise, the first conversation
with an owner who knows their own numbers goes badly.

Which is also the pitch: we can show them the outside better than anyone. They have the
inside. Put the two together and the leaks are obvious.

---

## 12. Build order

1. Site crawl with proper classification and rendering - fixes the known v1 defect
2. Menu teardown - structure, price architecture, modifiers, beverage, photo coverage.
   Highest ratio of insight to effort, and entirely free
3. Public records: HCAD, TABC, Comptroller, health scores - hard facts nobody else pulls
4. The guest journey, manual, on a phone. Slowest per restaurant and the most persuasive
   thing we produce, so it is worth the 20 minutes on anyone we are serious about
5. AEO score, because the prompt set is manual and the results are startling
6. Review teardown - richest signal, needs the Places API for volume
7. Social and mentions
8. SEO score, once GBP reading is automated
9. Competitive set, by running 1-8 on the neighbours
10. Ladder synthesis, improvement map, board
