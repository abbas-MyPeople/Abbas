# Economic foundations — why this pattern recurs, and when it fails

The taxonomy says *what*. The forces doc says *which pressures*. This document says *why any of this
should be true*, using the economics that already exists, plus the historical cases where the same
argument was made and got the answer wrong.

The reason to do this properly: "AI can't do human things" is a folk theory, and folk theories about
automation have an atrocious track record in both directions. People confidently said machines
couldn't play chess, drive, fold laundry, write competent prose, or diagnose. People equally
confidently said ATMs would end bank tellers and that recorded music would end live performance.
Both camps were wrong, and it's worth knowing *why* before betting on the third version.

---

## Part 1 — Seven pieces of theory that actually apply

### 1.1 Baumol's cost disease (Baumol & Bowen, 1966)

**The mechanism.** In a two-sector economy where productivity rises in sector A and not in sector B,
wages in B must still rise to keep workers from leaving for A. So B's *costs* rise without any
change in B's output. Prices in B rise relative to A, permanently.

The canonical example is a string quartet: Beethoven wrote for four players and it still takes four,
for the same forty minutes. Two centuries of industrial productivity produced exactly zero
improvement in the labor efficiency of performing a string quartet.

**Why it applies with unusual force now.** AI is the largest and fastest productivity shock ever
applied asymmetrically. The bigger the gap between the two sectors, the steeper the relative price
divergence — and the gap has never been anywhere near this wide.

**The crucial refinement people miss.** Baumol predicts *relative price increases*, not prosperity.
It says nothing about who captures the money. Historically the surplus goes to whoever owns the
constrained asset: the venue, the license, the hospital system, the brand. The string quartet gets
more expensive; the violist does not necessarily get rich. Health care is the standing example — 60
years of Baumol effects, and aides are still near minimum wage while hospital systems and insurers
grew enormous.

**So the honest version of the thesis is:** the human-contact *sector* inflates. Whether human-contact
*workers* prosper is a bargaining question, not an economic-law question. Which is exactly why the
2026 nurse strike wave — 16 strikes by mid-year, 21.5% won at Kaiser, strike frequency nearly
quadrupled since 2017 — is one of the most important signals in this folder. It's the surplus being
fought over in real time.

---

### 1.2 Moravec's paradox (1988)

**The statement.** High-level reasoning requires surprisingly little computation; low-level
sensorimotor skill requires enormous amounts. Chess is easy; picking up a mug is hard.

**Why:** evolution spent hundreds of millions of years optimizing perception and manipulation, and
about 50,000 on abstract reasoning. The old capabilities are deeply optimized and *unconscious* —
which also makes them impossible to introspect and therefore hard to specify.

**Where it lands in this map.** Families 2, 3 and 10 (Touch, Hands on the World, Care) sit directly
on Moravec. There's now formal work operationalizing this as a labor-market exposure index — a
theory-based alternative to just asking GPT which jobs it thinks it can do
([arXiv 2510.13369](https://arxiv.org/html/2510.13369)).

**The important caveat.** Moravec describes a *compute and data* asymmetry, not a permanent
impossibility. It is a statement about difficulty, and difficulty is a depreciating asset. Figure's
10,000+ warehouse deployments versus Optimus's non-start in July 2026 shows exactly where the
frontier is: **structured environments are falling, unstructured ones are holding.** A hospital room
and a residential kitchen are unstructured. A warehouse aisle is not.

---

### 1.3 Polanyi's paradox (1966; Autor, 2014)

**"We can know more than we can tell."** Most human competence is tacit — we can't articulate the
rules we're following, so we historically couldn't program them.

Autor built the modern task framework on this: the tasks that resisted automation were (a) abstract
work requiring problem-solving, intuition, creativity and persuasion, and (b) manual work requiring
situational adaptability, visual recognition and **in-person interaction**
([NBER w20485](https://www.nber.org/system/files/working_papers/w20485.pdf)).

**Why this needs updating rather than citing.** Machine learning is precisely the technology that
*routes around* Polanyi: you don't specify the rules, you learn them from examples. So Polanyi's
paradox stopped being a moat for anything with abundant demonstration data — which is why category
(a), abstract cognitive work, fell first, in reverse order from what Autor's framework implied.

**What survives is the sharpened version:** the moat is not tacit knowledge, it's **tacit knowledge
without a data trail.** Cognitive tacit knowledge left text everywhere and died. Physical and
relational tacit knowledge left almost none — which is exactly why Family 12 exists as a booming
industry: the entire expert-data and teleoperation market is a multi-billion-dollar effort to
manufacture the missing data trail. **Family 12 is Polanyi's paradox being bought out.**

---

### 1.4 Rosen's superstar economics (1981)

**The mechanism.** When a performer's output can be reproduced at near-zero marginal cost, tiny
differences in quality produce enormous differences in income. Everyone listens to the best singer,
so the best singer takes the market.

**The inversion that matters here.** Rosen explains why *recorded* markets are winner-take-all. The
live economy is the opposite: physical capacity caps the winner's take, so demand spills down to
the second-best, the local, the merely present. Reproducibility concentrates income; presence
distributes it.

**Prediction.** As AI makes reproducible output infinitely cheap, superstar dynamics intensify in
every reproducible category (content, software, design) and **more of the distributable income moves
into non-reproducible formats**. That's the mechanism under the live-music boom, and it says the same
should happen anywhere output is currently reproducible but experience is not. Which is why the
economics of a chef's counter beat the economics of a cookbook, and why the creator IRL migration is
economically forced rather than a fad.

---

### 1.5 Veblen (1899) and the status logic of service

Conspicuous consumption requires *visible waste*. Human attention is the ideal Veblen good post-AI,
because it is verifiably finite: a machine can serve infinite people, so being served by a person is
proof someone spent a scarce, non-scalable resource on you.

The 2026 evidence is unusually direct. Private chefs at up to $300K, butlers at $180K, the busiest
estate-staffing market in 20 years. More than two-thirds of consumers expect machine service to be
basic and human service to be premium. Klarna's CEO stated the pricing theory out loud.

**The implication people dislike:** this force is *strengthened* by AI getting better. The more
capable the free machine tier, the more the human tier reads as pure status. Family 7's growth is
therefore hedged against capability improvement — but it also means the human premium tends toward
being a luxury good, which is the affordability problem in
[`04-counterarguments.md`](04-counterarguments.md) §3.

---

### 1.6 Engel curves and Wagner's law

As income rises, spending shifts proportionally away from necessities toward services, health,
education and leisure. This is one of the most robust empirical regularities in economics.

Andreessen's scarcity-ladder framing is essentially this: when one layer of scarcity is solved,
spending climbs to the next. If AI massively deflates goods and cognitive services, the freed
income doesn't vanish — it goes up the ladder, and everything at the top of the ladder is
human-intensive.

**The condition, and it's binding:** this requires income to actually rise for most people. If AI's
gains accrue to capital while wages stagnate — the K-shaped/"E-shaped" pattern in 2026 data — the
Engel effect happens only in the top quintiles. **The entire optimistic case rests on a distribution
assumption that is currently not being met.**

---

### 1.7 Kremer's O-ring theory (1993)

**The mechanism.** In production processes where any failed step ruins the whole output, worker
quality is *multiplicative*, not additive, and the value of high-skill workers rises with the value
of everything else in the chain.

**Why it's the sharpest tool for the AI case.** If AI raises the value of everything upstream and
downstream of a human step, that human step gets more valuable *even if the human hasn't improved at
all.* The person who signs off, hands over, or shows up is now the O-ring on a much more expensive
rocket.

This is the rigorous version of Family 4. The liability sponge isn't paid for expertise — they're
paid because they're the failure point in a chain whose total value went up 100x. It also explains
why "seniorized" entry-level roles grew 35% while ordinary entry-level roles fell 10%: firms are
paying up for the one link they can't afford to have fail.

---

## Part 2 — Six historical cases, including the ones that go against us

Anyone can cite the cases that support them. Here are the ones that don't, first.

### 2.1 ATMs and bank tellers — the case *for*, and its expiry date

Bessen's analysis: ATMs cut tellers per branch from ~21 to ~13, which made branches cheaper, so
banks opened **43% more urban branches**, and total teller employment *rose* — from 485,000 in 1985
to 527,000 in 2002. The job's content changed from cash handling to sales and relationship work.
Classic Jevons: efficiency raised total consumption of the thing.

**Three reasons not to lean on it too hard**, all of which matter:

1. **Mobile banking eventually did what ATMs didn't.** When automation went from covering *some*
   teller tasks to *nearly all* of them, the Jevons effect broke and teller employment fell. Partial
   automation grows a job; comprehensive automation ends it. AI is aiming at comprehensive.
2. **Timescale.** The ATM transition ran ~40 years. The AI coding transition ran ~3. Even where the
   end state is "the job changes rather than disappears," a 3-year transition is a labor market
   catastrophe and a 40-year one is a career.
3. **The complement was cheap capital, not scarce judgment.** Branches expanded because branches
   were the growth strategy. There's no guarantee of an analogous expansion channel this time.

**Verdict:** supports Families 4 and 13 (the job refills with judgment and relationship). Does not
support blanket optimism.

### 2.2 Recorded music vs live performance — the strongest case *for*

In 1930 the American Federation of Musicians fought recorded sound as an existential threat, and
they were right about the immediate effect: recorded music destroyed the market for house musicians
in cinemas and restaurants — tens of thousands of jobs, gone.

A century later, recorded music is worth fractions of a cent per play and **live is a $25.2B business
for one company alone**, up 9%, with 159M fans. The reproducible half deflated toward zero and
the non-reproducible half became the industry.

**This is the single best historical template for the thesis** — and note the shape of it: not "the
technology failed to replace humans," but "the technology fully replaced humans in the reproducible
format, and *created* the value of the unreproducible one by contrast." The concert became precious
*because* the recording became free.

**Which reframes everything.** Don't ask "which jobs survive AI." Ask **"in each industry, which
half is the recording and which half is the concert?"** That single question is the most useful
output of this whole document, and it generalizes: education (the lecture is the recording, the
mentorship is the concert), medicine (the diagnosis is the recording, the care is the concert),
restaurants (the delivery order is the recording, the room is the concert), law (the document is the
recording, the advocacy is the concert).

### 2.3 Photography vs portrait painting — the case *against* romanticism

Photography arrived in 1839 and portrait painting as a mass profession was gone within a generation.
There was no "authentic human portraiture premium" that saved the trade. What survived was a much
smaller, higher-status fine-art market, plus an entirely new profession — photographer — that
employed more people than portraiture ever had, at lower status per head.

**Lesson.** "Humans do it more authentically" is not, by itself, a market. The premium accrued to a
tiny elite; the volume went to the new technology; the middle of the profession simply ended. Any
claim in this folder that rests on the authenticity premium alone (parts of Family 7, the "human-made"
label economy) should be read against this case.

### 2.4 The horse — the case *against* comparative advantage optimism

The standard reassurance is Ricardian: even if machines are better at everything, comparative
advantage guarantees humans have something profitable to do. Horses are the counterexample the
optimists have to answer. US horse population peaked around 1915 and collapsed; comparative
advantage did not save them, because their wage floor (feed and stabling) exceeded their marginal
product once tractors existed.

**Why humans probably aren't horses**, and it's worth being precise rather than glib: humans *own the
capital*, *set the policy*, *are the customers*, and *are the thing being optimized for*. Horses had
none of those. Demand for human presence is not exogenous — it is a demand *by humans, for humans*,
which is a self-sustaining loop that a horse never had access to.

**But the honest residual:** that argument protects humans *in aggregate* through ownership and
politics. It does not protect any *particular* profession, and it says nothing about distribution.
It's an argument that the pie exists, not that you get a slice.

### 2.5 Travel agents — the case for *bimodal* outcomes

The internet destroyed the transactional travel agent — booking a flight is now self-service. And
yet high-end travel advisory grew: small-group guided travel is now a multi-billion segment, with
TourRadar reporting 34% YoY growth in small-group bookings and 78% of multi-day operators
prioritizing intimate groups.

**Lesson, and it's the pattern that recurs everywhere in this research:** automation hollowed out the
middle. The transaction went to zero and the *advice and curation* went premium. The profession
didn't die — it **bimodalized**, and the people who were doing the transaction were not the same
people who could do the advice. That transition destroyed careers even though the industry survived.

Expect exactly this in real estate, insurance broking, financial advice, recruiting, and general
practice medicine.

### 2.6 Chess after Deep Blue — the case for Family 14

Chess was "solved" as a human contest in 1997, and every prediction said interest would collapse.
Instead chess is more popular now than at any point in its history, engines are universal training
tools, and the money is in humans playing humans while everyone watches an engine evaluation bar
that tells them exactly how wrong both players are.

**The lesson is genuinely strange and genuinely important:** knowing a machine is better did not
reduce interest in watching humans do it. It *increased* it, because the machine provided an
objective measure of how impressive the human performance was. The engine became the *scoreboard*
for human excellence rather than its replacement.

MLB's 2026 ABS decision is the same structure, chosen deliberately: the human umpire calls every
pitch, the machine is available on appeal twice a game, and the league picked that over full
automation because it was more palatable to fans. **Accuracy was outsourced; authority was kept
human on purpose.**

This is why Family 14 (Competition and Excellence) is in the taxonomy. There's a whole category of
activity where machine superiority *increases* the value of human performance, and it is the least
intuitive result in this entire body of research.

---

## Part 3 — The synthesis: five laws

Everything above compresses to five rules. These are the load-bearing conclusions.

### Law 1 — The recording/concert split
In every industry, ask which half is the recording (reproducible, deflating toward zero) and which
half is the concert (unreproducible, inflating). Automation doesn't eliminate industries; it splits
them and reprices the halves in opposite directions. *(From 2.2)*

### Law 2 — Partial automation grows a job; comprehensive automation ends it
The ATM grew teller employment for 30 years because it covered some tasks. Mobile banking ended it
because it covered nearly all. Ask what fraction of a role's tasks are exposed — under ~70%, expect
growth and enrichment; over ~90%, expect collapse. *(From 2.1)*

### Law 3 — Automation hollows the middle, not the top or bottom
Travel agents, bank tellers, portrait painters, radiology: the transactional middle goes, a smaller
high-status advisory tier survives at higher prices, and a larger low-wage tier survives on cost.
**The human premium is real and bimodal.** Careers in the middle must pick an end and move
deliberately. *(From 2.3, 2.5)*

### Law 4 — Value concentrates on the irreplaceable link, whatever it is
O-ring logic: as everything around a human step gets more valuable, the human step gets more
valuable regardless of any change in the human. Position yourself at the step that cannot fail —
the signature, the hands, the room, the relationship. *(From 1.7)*

### Law 5 — Scarcity is the product; humanity is just the current form of it
This is the one to remember. Nothing here is really about humans being special. It's about scarcity
migrating. Human presence is valuable *right now* because it is the currently-scarce input. **The
day something becomes reproducible, it deflates — regardless of whether a human does it.** Which
means the durable strategy isn't "be human." It's *"own something that cannot be reproduced,"* and
right now a lot of those things happen to be human. *(From 1.1, 1.4)*

---

## Part 4 — What would make me abandon this

Beyond the falsifiers in [`00-thesis-and-mechanisms.md`](00-thesis-and-mechanisms.md) §6, four
theory-level breaks:

1. **Robotics closes Moravec in unstructured environments.** Watch the ratio of teleoperated hours
   to autonomous hours in deployed fleets. Figure's warehouse numbers are the leading edge; homes
   and hospitals are the ones that matter.
2. **The Engel/distribution condition fails permanently.** If real median income doesn't rise
   through the AI transition, the ladder argument collapses and this becomes a luxury-goods thesis.
   Watch median wages, not GDP.
3. **The judgment pipeline break becomes terminal.** If entry-level destruction persists for a
   decade, the experienced humans the thesis depends on stop existing. This is the newest risk and
   the least discussed. *(F10, see [`06-recent-signals-log.md`](06-recent-signals-log.md) §1.)*
4. **Presence itself gets reproduced convincingly.** Not video calls — persistent, embodied,
   physically-present-feeling telepresence or AI companionship that satisfies the same need. Family 1
   and 5 rest on this not happening, and it's the one I'd least confidently bet against over 15
   years.

---

**Related:** [`08-master-index.md`](08-master-index.md) for the full category sweep,
[`04-counterarguments.md`](04-counterarguments.md) for the objections.
