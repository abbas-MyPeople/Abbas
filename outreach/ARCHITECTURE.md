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

Ten domains. Each field carries the tier block from section 0.

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

## 4. Site crawl specification

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

## 5. Guardrails

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

## 6. Output shape

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
  "completeness": { "domains_attempted": 10, "domains_returned": 7, "unknown_fields": 23 },
  "domains": { "identity": {}, "discovery": {}, "reputation": {},
               "ordering": {}, "menu": {}, "social": {}, "media": {},
               "competitive": {}, "operations": {}, "owner": {} },
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

## 7. Obtainability, honestly

| Tier | Domains | Cost |
|---|---|---|
| Automatable now, free | Site crawl, schema, ordering, menu, HCAD, TABC, Comptroller, health scores, Wayback, mention search | Time only |
| Automatable, paid API | Google Places reviews, PageSpeed at volume, SERP ranks, backlinks | Metered |
| Manual, high value | AI answer checks, social top-posts, influencer mentions, competitor AI ranking | Minutes per restaurant |
| Not obtainable, ever | Revenue, margins, labour cost, rent, covers, POS data, owner intent | Only the owner has these |

That last row is the discipline. **We can see everything about how a restaurant appears and
nothing about how it performs.** The dossier is a map of the surface and a set of honest
hypotheses about what is under it. The moment we pretend otherwise, the first conversation
with an owner who knows their own numbers goes badly.

Which is also the pitch: we can show them the outside better than anyone. They have the
inside. Put the two together and the leaks are obvious.

---

## 8. Build order

1. Site crawl with proper classification and rendering - fixes the known v1 defect
2. Public records: HCAD, TABC, Comptroller, health scores - free, hard facts, nobody else does it
3. Review teardown - richest signal, needs the Places API for volume
4. Menu and catering parse
5. Social and mentions
6. Competitive set, by running 1-5 on the neighbours
7. Ladder synthesis and the board
