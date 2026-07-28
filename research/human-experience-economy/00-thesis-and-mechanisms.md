# The Human Premium — thesis and the forces underneath it

*Side project. Started 2026-07-28. Internal research, not customer-facing.*

---

## 1. The claim being tested

> *"Every profession that involves human-to-human contact or human experiences is going to go bananas."*

That is the starting proposition. This folder exists to take it seriously enough to break it, and
to map the categories it implies — including the ones nobody has named yet.

**A note on attribution before we build on it.** The quote was recalled as "Mark Anderson." Two
plausible people, and I could not confirm the exact wording from either, so the thesis is treated
here as *a proposition worth testing*, not as a citation:

- **Marc Andreessen** (a16z) has argued the adjacent case repeatedly and on the record: that the
  AI job apocalypse is overstated, that a large share of US employment is licensed, unionized or
  otherwise structurally protected, that patients "will always want a human connection," and —
  most importantly for us — a **scarcity-ladder** argument: when one layer of scarcity falls,
  spending climbs to the next one.
  ([a16z](https://a16z.com/the-ai-job-apocalypse-is-a-complete-fantasy/),
  [Fortune](https://fortune.com/2025/10/08/billionaire-investor-marc-andreesssen-ai-jobs-personal-finance-careers-costs-plummet-healthcare-law),
  [Forbes](https://www.forbes.com/sites/josipamajic/2026/04/12/marc-andreessen-says-ai-productivity-will-trigger-a-hiring-boom/))
- **Mark R. Anderson** (Strategic News Service / Future in Review, now Pattern) is a working tech
  forecaster who publishes annual Top-10 predictions and could plausibly have said it verbatim.
  ([SNS](https://www.stratnews.com/about/))

Either way the thesis stands or falls on the mechanics, not the name. **To confirm later:** find the
primary source. If it's SNS, the exact framing may be sharper than the reconstruction here.

---

## 2. The sharper version of the thesis

The popular version — "AI can't do human stuff, so human stuff wins" — is lazy and will get you
killed in the details. AI is already extremely good at *simulating* human contact: warmth, patience,
recall, availability at 3am. 72% of US teenagers have used AI for companionship
([MIT Tech Review](https://www.technologyreview.com/2026/01/12/1130018/ai-companions-chatbots-relationships-2026-breakthrough-technology/)).
If the thesis were "machines can't be warm," it would already be falsified.

The version that survives contact with the evidence is narrower and stranger:

> **What gets repriced upward is not human *labor*. It is human *scarcity, presence, accountability,
> and provability*.** AI collapses the price of cognition and of infinitely-reproducible output.
> Everything whose value depended on being *hard to produce* deflates. Everything whose value
> depends on being *impossible to reproduce* — a body in a room, a person who can be sued, a night
> that happened once, a hand on a shoulder — inflates against it.

Three corollaries follow, and they matter more than the headline:

1. **It is a relative-price story, not a demand story.** Human services get more expensive whether
   or not more people want them. Baumol's cost disease stops being a bug and becomes the entire
   business model. (§3.1)
2. **The winners are not "jobs involving people." They are jobs selling one of ~12 irreducible
   human goods** — presence, touch, accountability, belonging, witness, taste, transformation,
   embodiment, verification, redress, care, and *being human as training data*. The industry label
   is the wrong unit of analysis. See [`01-taxonomy.md`](01-taxonomy.md).
3. **Most of the value migrates to formats that don't exist yet.** A concert is the obvious version.
   The non-obvious version is that half these categories arrive as *mutations of existing
   professions* — the teacher becomes a coach, the doctor becomes a pair of hands and a liability
   sponge, the recruiter becomes a matchmaker, the analyst becomes an expert-data supplier. See
   [`03-frontier-weak-signals.md`](03-frontier-weak-signals.md).

---

## 3. The nine forces

Each force is a distinct causal engine. A category is durable roughly in proportion to *how many
forces stack behind it* — that's the scoring method used in the taxonomy.

### 3.1 Scarcity inversion (Baumol as a feature)

The oldest and strongest mechanism. When productivity explodes in one sector and not another, the
*relative* price of the unimproved sector rises — because it must still compete for labor against
the booming one. Baumol's original example was a string quartet: it takes exactly as many
musician-hours in 2026 as in 1826.

AI is the most extreme productivity shock ever applied to one side of that equation. UNESCO frames
the long-run implication directly: sectors where machines cannot replace humans get their prices
dragged up by economy-wide wage levels
([UNESCO](https://www.unesco.org/en/articles/baumols-cost-disease-long-term-economic-implications-where-machines-cannot-replace-humans)).
The commentary shorthand that stuck with me: **technological deflation produces human inflation.**

This is why "go bananas" is ambiguous and needs splitting. It can mean *more jobs*, *higher prices*,
or *higher status*. Baumol predicts **higher prices with flat or falling volume** unless another
force adds demand. Most of the other eight forces are demand-side.

### 3.2 The verification premium

When generating a plausible fake costs nothing, the ability to prove something is real becomes a
priced good. This is the fastest-moving force in the set and the least anticipated in 2023-era
takes.

The evidence is no longer speculative: World raised $52.5M in 2026 specifically for proof-of-human
infrastructure, with World ID integrations rolling into Zoom, DocuSign, Okta and Tinder; Zoom
shipped biometric "Verified Human" badges for meeting participants in April 2026
([Biometric Update](https://www.biometricupdate.com/202607/world-raises-52-5m-as-investors-back-proof-of-human-infrastructure-for-ai),
[Adaptive Security](https://www.adaptivesecurity.com/blog/deepfake-statistics-2026-the-data-security-leaders-need-to-know)).
The Arup deepfake wire fraud — $25M lost on a video call where every participant but the victim was
synthetic — did more to create this market than any thought piece.

The second-order effect is the one to watch: **when remote verification fails, verification retreats
to physical space.** In-person becomes not a preference but a control. That reprices a long list of
things — closings, notarization, onboarding, executive meetings, diligence, hiring.

### 3.3 The liability sink

Someone has to be responsible. An AI system cannot hold a license, carry malpractice insurance,
testify, be disbarred, or go to prison. So regulation, insurance and tort law all converge on the
same structure: a credentialed human who signs.

EU AI Act Article 14 and NIST's AI RMF both require demonstrable, provable human oversight; more
than 700 AI-related bills were introduced in the US in 2024 alone, with 40+ more early in 2026
([Kiteworks](https://www.kiteworks.com/regulatory-compliance/human-in-the-loop-ai-compliance/),
[Strata](https://www.strata.io/blog/agentic-identity/practicing-the-human-in-the-loop/)).

This creates a genuinely new job shape — not "the person who does the work" but **"the person who is
accountable for the work the machine did."** It looks like a downgrade and is actually a
concentration of power: fewer humans, each carrying vastly more liability, and priced accordingly.
Note the failure mode, stated well in the compliance literature: a human in the loop without the
training or authority to overrule is *"a liability dressed up as process."*

### 3.4 The embodiment gap

Bits moved first; atoms lag. Robotics is improving fast but is bottlenecked on exactly the thing
that's hardest to synthesize — real-world manipulation data. Meanwhile the AI buildout itself is
consuming physical labor at a rate the training pipeline can't match: 300,000+ new electricians
needed for AI data center demand, data-center electricians commanding well into six figures,
trade-school enrollment up sharply
([Fortune](https://fortune.com/2026/03/20/skilled-trade-demand-randstand-report-electricans-technicans-construction-workers-six-figure-salaries-data-center-boom/),
[Build](https://build.inc/insights/data-center-construction-labor-shortage-2026)).

The irony worth holding onto: **the AI boom is currently the largest single subsidy to human
physical labor in the economy.**

### 3.5 The belonging deficit

Loneliness is now a demand signal with a P&L. Third places eroded; the market is rebuilding them
commercially. Run clubs, bathhouses, wellness memberships, supper clubs, congregations — all growing
against a backdrop where roughly two-thirds of Gen Z and millennials report loneliness
([CNBC](https://www.cnbc.com/2026/03/07/wellness-third-spaces-othership-bathhouse-glo30.html),
[Axios](https://www.axios.com/2026/07/05/loneliness-epidemic-third-places-social-infrastructure)).

Critically, this force runs *counter* to AI companionship rather than alongside it. Both are growing.
See [`04-counterarguments.md`](04-counterarguments.md) §2 — this is the single biggest live risk to
the thesis, and it is genuinely unresolved.

### 3.6 The demographic wave

The least fashionable and most reliable force. US 65+ population goes from 59.7M (2024) to 72.5M
(2034). Home health and personal care aides are projected to add ~739,800 jobs — the largest absolute
increase of any occupation — and healthcare/social assistance is the fastest-growing sector at +8.4%
([BLS](https://www.bls.gov/news.release/ecopro.nr0.htm)).

No AI narrative required. This happens even if model progress stops tomorrow. It is also the force
most likely to be *partially* met by robots after ~2032, which is why care is scored as durable but
not permanent.

### 3.7 The status and ritual premium

Human attention becomes a Veblen good. Once machine service is free and adequate, being served by a
person is a signal — of wealth, of importance, of being worth someone's finite time.

This has already crossed from theory to pricing. More than two-thirds of consumers expect
machine-driven service to become the default and human service to become a *premium feature*;
brands are actively selling "talk to a human" as a paid tier; Klarna's CEO put it plainly — if AI
can do customer service, then AI customer service is the *cheap* customer service, and the future
VIP experience is human connection
([CX Dive](https://www.customerexperiencedive.com/news/human-driven-customer-service-luxury-premium/816501/)).
Some luxury hospitality is reportedly pricing human-operated service at a large multiple.

The uncomfortable implication: the human premium is, in part, **an inequality machine.** §4 and
[`04-counterarguments.md`](04-counterarguments.md) §3.

### 3.8 The authenticity/provenance premium

Adjacent to verification but distinct: verification is about *fraud*, authenticity is about *taste
and meaning*. People are paying more for things because a human made them, and punishing brands that
feel machine-made. 68% of surveyed US consumers say they'd choose a "human-made" product over an
identical "AI-made" one at the same price; 36% report having actively punished a brand in the past
six months for feeling too AI-driven — and the wealthiest punish hardest
([MindStudio](https://www.mindstudio.ai/blog/human-made-premium-ai-backlash-authentic-content),
[PR.com](https://www.pr.com/press-release/971818),
[Cybernews](https://cybernews.com/ai-news/anti-ai-marketing/)).

Two cautions. First, stated preference ≠ paid preference; survey-to-till leakage in this literature
is large. Second, Capgemini found an explicit "human-made" label adds little over no label —
**because the default assumption is still human.** That's a temporary condition. The label becomes
valuable precisely at the moment the default assumption flips, which is the thing to watch.

### 3.9 Presence as the scarce format

Content is infinite; *unrepeatable* content is not. A recording can be copied; a night cannot. This
force explains why the live-event economy is booming while recorded media deflates, and why
phone-free events went from novelty to demand driver — in Q1 2026 alone, phone-free event volume hit
more than a third of the entire prior year's global total
([Eventbrite](https://www.eventbrite.com/blog/press/newsroom/the-rise-of-phone-free-experiences/),
[TicketNews](https://www.ticketnews.com/2026/04/year-of-analog-phone-free-events-surge/)).

Note what phone-free actually sells: **not the absence of technology, but the guarantee that
everyone present is fully present.** That's an enforcement product. Expect more of them.

### 3.10 The judgment supply crisis *(added 2026-07-28)*

The newest force and the one with the longest fuse. Stanford finds a **13–16% relative decline in
entry-level hiring for 22–25 year olds** in AI-exposed occupations; UK exposed job adverts are down
38%; AI is now, for the first time on record, the leading stated reason US firms give for layoffs.
Meanwhile junior roles in exposed occupations are **seven times more likely to demand senior-level
judgment**, and these "seniorized" entry roles grew 35% since 2019 while ordinary entry roles fell
10% ([Forbes, Jul 2026](https://www.forbes.com/sites/ronschmelzer/2026/07/14/ai-isnt-taking-every-job-its-targeting-these-workers/)).

**What's being destroyed is the apprenticeship function of the economy** — the rungs on which humans
historically acquired the judgment this entire thesis says is now precious. Every family that runs
on seasoned human judgment (4, 7, 11) faces a supply cliff in roughly a decade, because we are not
currently manufacturing juniors.

This is a *scarcity amplifier*: it raises the human premium and makes it more unequal at the same
time. See [`06-recent-signals-log.md`](06-recent-signals-log.md) §1.

---

## 4. How the forces combine (and where they fight)

Not additive. Some forces amplify each other and some cancel.

**Stacks that compound:**
- Verification × liability × embodiment → *in-person high-stakes work* (closings, diligence,
  clinical hands-on, field inspection). Strongest combination in the set. Three independent moats.
- Belonging × presence × status → *the club economy* (run clubs, congregations, supper clubs,
  private membership). Fast-growing, low barriers, therefore also fast-commoditizing.
- Baumol × demographics → *care*. Enormous volume, brutal margins, chronic underpayment. Volume
  ≠ prosperity for the worker. This is the largest category and the worst-paid one, and any honest
  version of this thesis has to say so.

**Forces that fight each other:**
- Status premium **vs.** belonging deficit. If human contact prices as luxury, the people with the
  largest belonging deficit can least afford it, and they get AI companions instead. The market
  bifurcates: *human contact for the top, synthetic contact for everyone else.* This is the most
  important — and most under-discussed — dynamic in the whole thesis.
- Baumol **vs.** affordability. Rising relative prices in care and education without productivity
  gains is not a boom, it's a crisis with good margins for incumbents. The K-shaped/"E-shaped"
  consumer data is the constraint here
  ([Equifax](https://www.equifax.com/business/blog/-/insight/article/the-k-shaped-economy-in-2026-understanding-what-it-is-and-what-it-means-for-you-now/),
  [CNBC](https://www.cnbc.com/2026/03/06/e-shaped-economy-replacing-k-shape-2026.html)).
- Authenticity premium **vs.** AI-assisted everything. Nearly every "human-made" business quietly
  runs on AI in the back office. The label is about the *touchpoint*, not the process — and that
  gap is a scandal waiting to happen, plus a certification market waiting to be built.

---

## 5. What "goes bananas" actually means — four different outcomes

The thesis is only useful if we distinguish these, because they imply completely different bets:

| Outcome | Meaning | Example | Who wins |
|---|---|---|---|
| **Price boom** | Same volume, much higher prices | Live event tickets, concierge medicine | Incumbents, owners of scarce supply |
| **Volume boom** | Many more people employed | Home care, skilled trades | Workers, training pipelines, staffing |
| **Status boom** | Same money, much higher prestige | Trades, teaching-as-coaching, hospitality | Recruiting, culture, next-gen entrants |
| **Format boom** | New categories that didn't exist | Expert-data marketplaces, proof-of-human, AI redress | Founders |

Most commentary conflates all four. A category can price-boom while shedding jobs (ticketing), or
volume-boom while staying poor (care work). **The founder-relevant one is the format boom** — and
that's what [`03-frontier-weak-signals.md`](03-frontier-weak-signals.md) is for.

---

## 6. Falsifiers

Stated up front so this stays a research document and not a manifesto. The thesis is wrong if:

1. **AI companionship crosses from supplement to substitute at scale** — measured by declining
   in-person social time among heavy AI-companion users, controlling for baseline. Early
   "deskilling" research points this way ([APA](https://www.apa.org/monitor/2026/01-02/trends-digital-ai-relationships-emotional-connection),
   [Drexel](https://drexel.edu/news/archive/2026/April/teen-AI-chatbot-addiction)).
2. **Humanoid robots close the embodiment gap faster than expected** — the teleoperation data
   bottleneck is the current constraint; watch it, because the moment it breaks, force 3.4 inverts
   and the *same* data-collection jobs that are booming now disappear first.
3. **Incomes fall enough that the experience economy is a top-decile phenomenon** — in which case
   the boom is real but tiny, and it's a luxury story, not an economic one.
4. **Regulation removes humans instead of requiring them** — precedent exists (autonomous vehicles).
   Force 3.3 is a political fact, not a physical one, and political facts reverse.
5. **The authenticity premium proves to be stated-preference only** — 68% say they'd pick human-made;
   watch what happens to that when the AI version is 40% cheaper.

Full treatment in [`04-counterarguments.md`](04-counterarguments.md).

---

**Next:** [`01-taxonomy.md`](01-taxonomy.md) — the master map of categories, organized by what the
human is actually selling.
