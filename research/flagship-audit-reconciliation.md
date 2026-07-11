# Flagship Audit → AZ Reconciliation

*Source: the independent read-only audit of the `WokAndKarahiTexas.com` repo (2026-07-11, commit
624f946), reconciled against `research/moat-and-breadth.md` and `flagship/CAPABILITY-LEDGER.md`.
I have the audit's Sections 0–2 (summary, full inventory, claim verification); Sections 3–6
(portability, moat, risks, recommendations) were not in the exported PDF — paste them and I'll fold
them in. This corrects several claims I and the ledger made from secondhand reading.*

---

## 1. The moat thesis — SHARPENED (I had it partly wrong)

My memo named a 4-part moat (founder fusion + restaurant lab + growth engine + frontier SKUs).
The audit says the growth engine and frontier SKUs are **built but not yet proven in use**, and the
restaurant is being **sold**. So the real, defensible moat narrows to one thing:

> **The dollar-grounded judgment layer.** `operator/state/value_model.yaml` + a 24-month
> books/POS reconciliation: actual effective commission rates (DoorDash 23.4%, Uber 29.7%,
> Grubhub 30.0%), real cash-labor reality, month-by-month *true* net — fused with the POS order
> graph into a ranked, falsifiable model of "where the next dollar is," which then drives what the
> software builds. And its **honesty**: the model concluded the restaurant ran *near-breakeven once
> cash labor is counted*. **A competitor cannot copy 24 months of a real restaurant's statements
> fused to its order graph.** That closed data asset is the moat *and* the demo.

The founder fusion + owned-restaurant-as-lab is still real and still rare — but the *durable* asset is
the **data + judgment model**, not the automation (which hasn't shipped autonomously) and not the
frontier SKUs (which have zero usage). Rebuild the AZ moat story around the data layer.

---

## 2. Claims that are OVERSTATED — fix these before they cost trust

The whole brand is "honest, pay-only-when-you-save." Publishing claims the flagship repo can't
support attacks the exact trust that is the moat. The audit found four:

| Claim (on AZ site / ledger) | Reality per audit | Fix |
|---|---|---|
| **"4.6★ · 872 reviews"** (homepage proof bar) | "872" appears **nowhere** in the repo; it's owner-narrated ("~400→800+"), never measured; the review count needs a Places API key (fetcher built, not run). The repo's own critique flags "4.6★" as sourceless. | Either verify the live Google count and cite it with a date, or soften to a defensible statement. **Do not publish 872 until it's verified.** |
| **AI phone agent "live," bilingual ordering** | Live only on its **own Vapi test number** (+1-903-602-4012); **orders gated OFF**; main line (281-362-5354) **not forwarded**; transcriber is **English-only** (Urdu/Hindi deferred). Zero call metrics exist. | Market as "built & in staged rollout," not "answering your line today." Don't claim bilingual ordering is live. |
| **Closed-loop growth engine "running / productized"** | Real code, armed, crons run — but **0 autonomous changes ever shipped**, 2 of ~12 rules have executors, email leg retired. Only `growth_brain` (daily money-ranked brief) is **proven autonomous**. | Sell "a daily AI analyst that emails money-ranked moves" (true) — not "a website that ships its own changes" (not yet demonstrated). |
| **"Commission Rescue — proven"** | The measured channel shift so far is **toward** 3P (10-12%→20-26%), **not** 3P→direct. $0 commission recovered to date; recovery figures are scenarios. The QR→direct baseline was set 2026-07-09. | Frame as capability + the *drag we measured* ($29K/yr), not a recovered result yet. |

---

## 3. The REAL proof numbers (case-study-ready) — this closes the `[OWNER]` gap

### Publicly usable (defensible, not sensitive) — use these on the case study / in pitches
- **90-day Clover window (Mar 25–Jun 23, 2026):** 1,501 paid orders · **$87,323 gross** · **AOV
  $58.18** · ~$970/day (~$355K/yr run-rate).
- **Third-party drag we measured:** 492 orders = 27.6% of revenue; **commission drag ≈ $29,267/yr
  (~$80/day)** at effective rates of **DoorDash 23.4% / Uber Eats 29.7% / Grubhub 30.0%**. ← the
  single best "found-money" number; it's from actual statements, not an estimate.
- **AOV ladder (why direct wins):** Dine-In $69.94 > Takeout $53.55 > **DoorDash $50.99 > Uber
  $47.07 > GrubHub $45.89.** Third-party tickets are ~$15–24 smaller *and* pay 23–30% away.
- **The website works, measured:** post-rebuild, **113 order-clicks (8.31% of sessions) + 4 catering
  inquiries in 28 days vs. zero tracked conversions before the rebuild.** GSC ~115 clicks / 8.4K
  impressions / avg pos 11 in 90d.
- **Catering is real and untapped:** 43 orders ≥$150 = $9,061/90d (~**$36.7K/yr floor**), 0 typed as
  catering (so it's invisible to the current system — a clean upside story).
- **Brand leak (a great "get found" hook):** avg position **4.2 for "wok and karahi"** — marketplaces
  outrank the restaurant for its *own name*.
- **GBP scale (context):** 81,572 profile views, 7,387 interactions, 1,048 calls (Jan–Jun 2026).

### Private / sensitive (owner's use only — DO NOT publish)
- 2025: card-only P&L net **$156,713**; cash labor omitted **$179,827**; true net after full labor
  **≈ −$23K to −$82K** depending on model; FY2025 revenue ex-tax **$515,195**. May-2026 fees
  $3,898 incl. ~$911 DoorDash ads. *These power private proposals and the "true-net" demo, not the
  public page.*

### Do NOT cite
- The "872 reviews / 4.6★" (unverified). The GA4 sessions figure (1,360 vs 573 — irreconcilable).
  Any "$ recovered" (zero measured). "4 after-hours calls ≈ $180" (illustrative, not data).

---

## 4. Two new realities to fold into strategy

- **The restaurant is being sold** (recorded 2026-07-10; ~2 months), kept as the AZ *demo*. The
  "permanent live lab / long-running flywheel" framing must change to **"proven on a real restaurant
  we operated; now the reference demo."** Every flagship judgment is now weighted to short-payback,
  case-study-quotable moves — align AZ's asks accordingly.
- **Security liability (urgent, Wok repo):** "FULL BACKUP MODE" intentionally commits live secrets +
  PII (Clover token — noted *"was briefly public, rotate"* — GCP service-account private key, ~530-row
  contact list, customer PII). Safe *only* while private. **Rotate the exposed Clover token now** and
  scrub history before the repo is ever shared/sold. This is the highest-priority risk in either repo.

---

## 5. What this means (net)
- The **method demonstrably works and is measured** — the drag, the AOV gap, the web conversion,
  the catering floor are all real and case-study-grade. That's a strong proof-of-value.
- But **proof-of-demand is still zero** (no external client) and **several site claims run ahead of the
  repo** — fix those to protect the trust that is the actual moat.
- Rebuild the moat story on the **dollar-grounded data/judgment layer** (unforgeable) rather than the
  automation or the SKU list.
