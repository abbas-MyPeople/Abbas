# AZ site + bridge — changelog

Dated log of what shipped, so any future session can pick up without re-deriving it.
Newest first. Capability status lives in [`CAPABILITY-LEDGER.md`](CAPABILITY-LEDGER.md); positioning
rationale in [`../research/az-platform-and-usp.md`](../research/az-platform-and-usp.md).

## 2026-07-01 → 07-05 — bridge + repositioning + analytics (this work block)

**The bridge (Wok → AZ productization flow)**
- Created the self-contained `flagship/` proof layer in the AZ repo: `CAPABILITY-LEDGER.md` (source of
  truth), `capabilities-catalog.md` (migrated + reconciled to the live site), `voice-agent-playbook.md`
  (migrated), `case-study-wok-and-karahi.md`, `SYNC-PROTOCOL.md`, `README.md`. Migrated the two stranded
  bridge docs out of the restaurant repo. Restaurant-side pointer added at `docs/az-bridge.md` (Wok repo).
- Ledger reconciled with owner input to credit real, non-code operational work: tablet consolidation
  (live 1+yr), the two-track review system (**~400→872 Google reviews, 4.6★**), the order-type
  "thank-you note" 3P→direct tactic, POS/table attribution, in-build SMS loyalty + self-optimizing menu,
  and (new) **#17 unified customer identity (CDP) + receipt-scan 3P→direct conversion**.

**Positioning (the USP reframe)**
- Wrote `research/az-platform-and-usp.md`: capabilities as **one platform, five layers** (WSO2-APIM
  style) with **Abbas as the control plane** — the person is the USP, *with a team behind him* (not
  "just one guy," not "an agency").
- Homepage: new **platform** section (layered stack + On-your-terms / One-mind pillars); flipped the
  "is this just one person?" framing on details to own it; framed the plays as platform layers.

**Proof (grounded only)**
- Verified real numbers and added a homepage **proof bar** + **case-study section**: 4.6★ / 872 Google
  reviews, Top 10 Halal 2024 (You Had Me At Halal), Zabihah-certified, ex-Google founder, AI-readable
  site. Removed unprovable "profitable every year" boasts (index, onepager, toolbox). No 2× claim.

**Voice showcase**
- Elevated voice AI from one card to a full section: live "Hear it live — call (281) 362-5354" CTA
  (the real restaurant line), a feature grid from the actual 21-tool build, and the "never falsely
  confirms" reliability line. **Agent name removed from the site** (owner call — naming a specific
  agent on a site selling to other restaurants is confusing).

**Housekeeping / fixes**
- Fixed the father/son photo crop (was cut off at the nose).
- Onepager refreshed to the new positioning; regenerated `AZ-RP-leave-behind.pdf` (1 page).
- Refreshed the stale README; robots-disallowed `/flagship/` and `/research/` (internal, public repo).

**Analytics**
- Added GA4 + **granular auto-tracking** in `script.js` (mirrors the restaurant site, extended):
  auto-captures every click (typed: `call_click`/`email_click`/`whatsapp_click`/`pdf_download`/
  `outbound_click`), `section_view` via IntersectionObserver, and conversions (`lead_submit`,
  `finder_capture`) — each tagged with UTM/referrer/landing. **No-ops until the owner sets the GA4
  Measurement ID.**

### Open items (owner / next session)
- **GA4 Measurement ID** for azrestaurantpartners.com → paste it, wire into `script.js` `GA4_ID`.
- **Auto-optimize loop** (phase 2): scheduled GA4-Data-API → diagnose → A/B test → owner-approved PR
  (mirror `docs/aeo-seo-engine` from the restaurant repo). Needs ~2 weeks of GA4 data first.
- (281) 362-5354 line: owner says treat as live. Regenerate the full-details PDF
  (`AZ-Restaurant-Partners.pdf`) from `details.html`. Translate new copy (Hindi/Urdu i18n). Tie the
  tool-finder results to the five platform layers.
- Trust items (owner-declined for now): (408) phone + gmail are fine per owner.
