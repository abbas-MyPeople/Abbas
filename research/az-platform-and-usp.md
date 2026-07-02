# AZ as a Platform — the capability architecture + the real USP

> **Why this doc:** Abbas asked to break down AZ's capabilities "like the APIM platform by WSO2" —
> i.e. present them not as a flat list of services but as **one integrated platform with named layers**,
> where the differentiator is that a **single mind spans every layer**. This doc is that breakdown, plus
> the two positioning theses it forces (Abbas-as-platform, and voice-AI-as-identity), plus a candid
> site critique. It drives the copy on the live pages. Source of truth for *status* is
> [`../flagship/CAPABILITY-LEDGER.md`](../flagship/CAPABILITY-LEDGER.md).

---

## 1. The USP, stated plainly
**The USP is Abbas.** Not "a restaurant family plus a tech team" — that's table stakes and it actually
*buries* the edge. The edge is this: almost nobody on earth is **both** a production software engineer
(ex-Google) **and** a hands-on restaurant owner-operator who has personally run the POS, worked the
rush, and lived the margins. Every other option the owner has is a *specialist who only sees one layer*:
- a POS vendor who doesn't care about your reviews,
- a marketing agency who's never reconciled a DoorDash payout,
- a consultant who advises and leaves,
- 20 point tools that don't talk to each other (the fragmentation wound from `restaurant-tech-market-research.md`).

AZ is the opposite: **one integrated platform, led by one person who understands the nuances *and* the
optimizations at every level** — from the kitchen ticket to the customer's feeling to the unit economics.
That's why the layers actually connect. **The platform *is* a person, and that's the moat a competitor
can't copy.**

**Important nuance (owner's steer):** the USP is *the person* — but the pitch must not read as "it's
literally one guy doing everything," which sounds small and risky to a buyer. The correct framing is:
**one mind sets the standard and leads every engagement, with a team behind him building and running it.**
So the buyer gets the singular, cross-domain expertise *and* real execution horsepower — no single point
of failure. Don't deny the team (the old copy did); don't dilute the singular-expert differentiator into
"we're an agency" either. Hold both.

## 2. The platform architecture (the WSO2-APIM analogy, made restaurant-native)
WSO2 API Manager isn't sold as "a gateway, and also a portal, and also analytics." It's sold as **one
platform** with a **control plane** coordinating layers across a lifecycle. AZ is the same shape. Owner-
plain layer names on the left; the WSO2 mental model on the right (for Abbas, not the public site).

| Layer (owner-facing name) | What lives in it (capabilities) | WSO2-APIM analog |
|---|---|---|
| **① The Spine — your data & POS** | One source of truth on Clover: tablet/3P-app consolidation into the POS, clean order flow, real numbers everyone else builds on. | **Data plane / Gateway** — everything flows through one controlled path. |
| **② Get Found** | AEO/SEO site AI assistants can read, Google Business Profile, AI-visibility, the MCP "get-cited-by-AI" connector, reviews & reputation. | **Developer portal** — how the outside world discovers you. |
| **③ Win the Order** | The **AI voice agent**, direct online ordering & commission rescue, catering & corporate lunches, "answer every call." | **API exposure / consumption** — turning discovery into transactions. |
| **④ Keep the Guest** | Loyalty, win-back, consent-based SMS, the guest list you own, returning-customer memory ("the usual"). | **Subscriptions / lifecycle** — the ongoing relationship, owned by you not the apps. |
| **⑤ The Brain** | Conversational analytics/BI, true-net P&L, menu engineering, and the **self-optimizing menu** (dynamic pricing & deals from real demand). | **Analytics & observability** — see everything, and act on it. |
| **⑥ On Your Terms** *(cross-cutting)* | Owner-authorization on every change, you own the customer & data, **no vendor commissions**, human-in-the-loop, pay-after-you-save, dry-run→gated rollout. | **Key Manager / security & governance** — nothing acts without authorization. |
| **⑦ The Architect** *(the USP, cross-cutting)* | **Abbas** — one operator-engineer who designs, wires, and runs all six layers so they integrate. | **The unified control plane** — one coherent system, not point products. |

**The one-sentence version for the site:** *"Most restaurants are stuck stitching together 20 tools
that don't talk. AZ is one platform across every layer — get found, win the order, keep the guest, and
a brain that optimizes it all — built and run by one person who's both the engineer and the operator, on
your terms, nothing done without your say-so."*

## 3. Thesis two — voice AI is the most under-sold capability
People dismiss restaurant voice AI as "an order-taking bot." That misses what it actually is, and it's
the thing the site most under-sells (currently one small card). Three points to lead with:

1. **It's the best human employee, captured as AI.** Never has an off day, never forgets a special,
   never mangles the biryani's name, handles the angry caller with the same real care every single time,
   upsells like a friend, remembers regulars. **Consistency no human can sustain across every call.**
   This is *industry-expert-specific* AI — grounded in the restaurant's real menu/data plus the distilled
   craft of a great operator (objection handling, upsell logic, catering sizing, complaint triage) — **not
   a generic chatbot.**
2. **Identity is a choosable asset.** The owner dictates the voice — language, accent, warmth, cultural
   fit. At Wok & Karahi, the agent "Haania" (on the "Naina" Vapi voice engine) speaks English *and*
   Urdu/Hindi and says the dishes right, so a desi
   customer feels *at home and recognized* the moment they call. For a demographic-specific restaurant
   that **changes the customer dynamic** and becomes a brand identity the owner owns and controls.
3. **You dictate public perception at every touchpoint.** Humans err — a rushed server, a missed call, a
   wrong price. The expert-in-AI presents the restaurant's best self *consistently, everywhere*. AZ hands
   the owner the controls on how their restaurant is experienced at every point of contact.

**Site implication:** voice gets its own prominent section (home + details), framed as identity +
expert-in-AI + perception control — not "answers the phone."

## 4. Candid site critique (per Abbas's ask — what's weak / to change / to cut)
**Homepage (`index.html`)** — the emotional hook is genuinely strong; keep it. Weaknesses:
- USP is muddled ("family + a team") and never names the real edge (one engineer-operator = one platform).
- Zero capability specifics — a skeptical operator can't see *what* they get. → add the Platform section.
- Voice AI is entirely absent. → add a Voice section.
- No proof. → add a proof strip from the flagship (e.g. ~400→800 reviews, all 5★; site AI-readable) once owner-approved.

**Details (`details.html`)** — thorough and clear. Weaknesses:
- **The "Is this just one person? No…" FAQ actively fights the USP.** → reframe to *own the person* while
  keeping the team: the differentiator is Abbas (engineer + operator) who sets the standard and leads,
  **with a full team behind him** building and running it — singular expertise AND horsepower, no single
  point of failure.
- The 9 "plays" are a flat list with no structure. → group them under the platform layers so they read as
  one integrated system, not a menu of disconnected services.
- Voice is one small card among nine. → elevate it.

**Global trust dings (fix or decide):**
- **Phone is a (408) California area code on a Houston-local brand** — a real credibility ding. Get a
  Houston (281/713/832) number (or the restaurant's) and use it everywhere.
- **Contact email is a personal gmail** (`azoeb27@gmail.com`) — move to `abbas@azrestaurantpartners.com`.
- **i18n Hindi/Urdu are unreviewed machine drafts** — have a native speaker pass before leaning on them.

**Keep as-is:** the toolbox/finder lead magnet, the 12 SEO guides, the Founding-5 pilot, the pay-after-
you-save guarantee, the no-vendor-commissions promise, the warm editorial design system.

## 5. Wiring to the rest of the repo
- Status/proof for every capability above → [`../flagship/CAPABILITY-LEDGER.md`](../flagship/CAPABILITY-LEDGER.md).
- Voice depth → [`../flagship/voice-agent-playbook.md`](../flagship/voice-agent-playbook.md).
- Proof numbers → [`../flagship/case-study-wok-and-karahi.md`](../flagship/case-study-wok-and-karahi.md).
- This supersedes the flat "9 plays" framing in `00-STRATEGY-SYNTHESIS.md` — the plays now live *inside*
  the platform layers.
