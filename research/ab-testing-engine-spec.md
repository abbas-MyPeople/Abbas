# A/B Testing Engine — spec (loop engineering applied to AZ)

> **Goal:** make the growth engine *prove* every change instead of hoping. Ship each change as an
> **experiment**, measure the **lead-rate** lift per variant on real traffic, and **auto-promote winners /
> auto-revert losers** — a self-improving optimization loop. This is the `/goal`-style verifiable
> done-condition ([`loop-engineering.md`](loop-engineering.md) §2) applied to marketing. Objective =
> **more of the RIGHT visitors converting** (lead_submit / call_click / finder_capture per 100 sessions),
> not just more traffic.

---

## 1. Why A/B (not just ship-and-hope)
Today the loop proposes → owner approves → it hard-swaps the copy → done. It never learns whether the
change actually helped. A/B closes that: the control stays live, the variant runs on a slice of traffic,
GA4 measures conversion by variant, and the engine keeps only what wins. **Every change becomes evidence.**
Static GitHub Pages can't split server-side, so the split is **client-side JS + GA4 attribution** — which
the site already has the tracking layer for.

## 2. Data model — `experiments.json` (committed; owner-gated to START)
```json
{
  "experiments": [{
    "id": "hero-headline-2026-07",
    "status": "running",                // draft | running | decided | shipped | reverted
    "page": "index.html",
    "anchor": "hero",                    // logical section the runner targets
    "hypothesis": "An audience-fit hero lifts lead-rate for corporate caterers",
    "metric": "conversion",              // lead_submit + call_click + finder_capture
    "split": 0.5,                        // share of visitors who see B
    "variants": {
      "A": {"label": "control"},
      "B": {"selector": "#hero-title", "attr": "innerHTML", "value": "…new headline…"}
    },
    "started": "2026-07-08",
    "min_sessions_per_variant": 200,     // no decision before this (avoid false winners)
    "max_days": 21,                      // hard stop → decide or revert
    "result": null                       // filled on decide: {winner, lift_pct, p, n_a, n_b}
  }]
}
```

## 3. Client-side runner (in the site JS)
On every page load, for each `running` experiment whose `page` matches:
1. **Stable assignment.** Compute a persistent visitor id (localStorage, first visit) → hash with the
   experiment id → bucket into A/B by `split`. **Same visitor always sees the same variant** (no flicker,
   honest measurement). Persist the assignment.
2. **Apply the variant.** For B, set the target element's `attr` to `value` (e.g. swap `#hero-title`
   innerHTML). A = leave control untouched. Apply *before paint* where possible to avoid flash.
3. **Attribute in GA4.** Register a GA4 **event parameter / user property** `exp_<id> = A|B` so EVERY
   subsequent event (incl. `lead_submit`, `call_click`, `finder_capture`, `section_view`) is tagged with
   the variant. Fire one `experiment_exposure` event on assignment.
4. **Guardrails.** Never apply a variant whose selector isn't found (fail safe → control). One experiment
   per element (the engine enforces non-overlap). If JS is off, everyone gets control (fine).

## 4. Engine lifecycle (states + who decides)
```
draft ──(owner approves in the daily brief)──▶ running
running ──(GA4: enough samples + significant)──▶ decided ──▶ shipped  (winner baked in permanently)
running ──(max_days reached, no winner)──────▶ decided ──▶ reverted (control kept)
```
- **PROPOSE (engine):** when a finding suggests a copy/targeting change (e.g. rule **G7** "traffic up but
  lead-rate flat"), the engine proposes it **as an experiment** (control vs a specific variant), not a hard
  edit. The brief shows: hypothesis, the exact variant, the metric, the split.
- **START (owner-gated):** owner replies "approve" (or gives the angle → Claude drafts variant B). Engine
  writes the experiment into `experiments.json` (validated: selector exists, no element overlap, page in
  scope) and commits → live A/B within minutes.
- **MEASURE (engine, deterministic):** `sensors/ga4_traffic.py` gains a per-variant read: sessions +
  conversions where `exp_<id>=A` vs `=B` → lead-rate per variant.
- **DECIDE (engine, deterministic + honest stats):** see §5. Auto-promote/revert **without** re-asking the
  owner — the experiment was already approved; the *data* is the judge. This is the aggressive part.
- **SHIP (engine):** winner B → write B's value permanently into the page (fence + `validate_edit` +
  one revertible commit), set status `shipped`, remove the client-side split. Loser/inconclusive → status
  `reverted`, control unchanged. Either way, the **daily brief reports the result with the numbers.**

## 5. The decision rule (deterministic, no false wins)
Decide only when **both** variants have `≥ min_sessions_per_variant` (default 200) **and** `≥ 1` conversion
somewhere. Then:
- Two-proportion **z-test** on conversion rate (A vs B). Ship B if `p < 0.05` **and** B's rate ≥ A's by a
  minimum absolute lift (guard against trivial wins). Ship A (revert) if A wins significantly.
- If `max_days` hit without significance → **revert** (control) and log "inconclusive"; optionally the
  engine proposes a bolder next variant. (Bayesian posterior is a fine future upgrade; start with z-test —
  deterministic and explainable in the brief.)
- Never peek-and-stop early below min-sample (that manufactures false winners). The min-sample + max-days
  bounds are the "extremely smart, but not fooling itself" guardrail.

## 6. Aggressiveness (what "very aggressive" means here, safely)
- **Always-on:** the engine keeps 1–3 non-overlapping experiments running at all times, biased toward the
  highest-leverage surfaces (hero, primary CTA, proof, pricing) and the lead-rate goal.
- **High velocity:** short cycles — as soon as one experiment decides, propose the next on that surface
  (a ladder of improvements), and let winners compound.
- **Multi-surface parallelism:** different pages/sections tested at once (non-overlapping elements only).
- **Bounded:** cap concurrent experiments (default 3), enforce element non-overlap, keep the min-sample /
  max-days discipline, one revert per change. Owner approves the *start* of each experiment; the engine
  owns the measurement + the promote/revert call.

## 7. GA4 wiring (reuses what's live)
- The tracking layer registers `exp_<id>` as an event parameter on the shared `track()` (so all events
  carry it). Register the matching **custom dimension** in GA4 once per experiment id (or a generic
  `experiment`+`variant` pair — cleaner: one `experiment_id` + one `variant` dimension reused across tests).
- **Recommended:** use two reusable custom dimensions `experiment_id` and `variant` (not one-per-test), so
  no GA4 admin change is needed per experiment. The runner sets both; the sensor filters on them.

## 8. Guardrails (inherit the loop-engineering rules)
- **Owner-gated start**, data-gated decision. **Validate before any commit** (HTML/JSON-LD/`node --check`,
  scope fence — reuse `executors.validate_edit`). **Reversible** (one commit). **Min-sample before deciding.**
  **Cap concurrency + non-overlap.** **Kill switch** `ENGINE_DISABLED=1`. **Audit** every state transition in
  `state/experiments.jsonl`. Never test anything that could break the page or mislead a visitor.

## 9. Build roadmap
1. **Client runner** — add an experiments module to the site JS (reads `experiments.json`, assigns, applies,
   tags GA4). Register `experiment_id` + `variant` params on `track()`.
2. **GA4** — add the two custom dimensions (`experiment_id`, `variant`) once (owner, 2 min) — or I script it.
3. **Engine: propose-as-experiment** — G7 (and copy/CTA rules) emit an experiment proposal; approval writes
   `experiments.json`.
4. **Engine: measure + decide** — per-variant GA4 read + the z-test decision; auto promote/revert; brief
   reports results.
5. **Dashboard** — an "Experiments" panel: running tests, per-variant lead-rate, decisions.

**Sequence:** this is the rung-4 upgrade — build it after the current loop has a few days of trustworthy
rung-3 behavior. It reuses the entire existing engine (state, validation, fence, email, deploy); the new
code is the client runner + the experiment lifecycle in `growth_engine/`.
