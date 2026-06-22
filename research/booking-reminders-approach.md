# Booking reminder sequence — recommended approach

**Goal:** cut call/walkthrough no-shows (research: automated reminders cut no-shows **up to 50%**; >90% of texts are read within minutes). For this buyer, **WhatsApp is the channel**, SMS second, email last.

**Why this isn't built into the site:** the site is static (GitHub Pages). Reminders require something that runs on a schedule and sends messages — i.e. a backend or a no-code automation + a messaging provider. Below is the lowest-effort path, in two stages.

---

## Stage 1 — Manual, $0, do this for the Founding 5 (today)
Already in place: the finder and contact form capture **phone + email** and email the lead to azoeb27 (now with campaign source). So:
1. Install **WhatsApp Business** (free) on Abbas's phone. Set up **quick-reply templates** and an **away message**.
2. When a lead email arrives, reply by WhatsApp/text within minutes (speed-to-lead is the single biggest win), book the walkthrough, then **manually** send: a confirmation, a reminder ~24–48h before, and a nudge ~2–4h before.
3. Add one **consent line** at booking ("OK to text/WhatsApp you a couple of reminders?") and log the yes — keeps it clean under TCPA / TX SB 140.

This is enough to run the first 5–10 pilots with zero infrastructure. Automate only once volume makes manual painful.

---

## Stage 2 — Automated (when volume justifies ~$30–50/mo)

**Recommended stack (no custom code):**
- **Scheduler:** **Cal.com** (free, open-source) or Calendly. Embeds as an inline widget on the booking section, replacing/augmenting the contact form. Captures phone + a consent checkbox.
- **Automation:** **Make.com** (or Zapier) scenario triggered on "new booking."
- **Messaging:** a **WhatsApp Business API provider (BSP)** — **WATI**, **Interakt**, or **360dialog** (~$30–50/mo, includes template messaging + two-way replies). These are the WhatsApp-native equivalent of Twilio.

**The flow Make.com runs on each booking:**
1. **Instant confirmation** WhatsApp template ("You're booked for {time}. Reply Y to confirm — or tell me a better time.").
2. **T–48h reminder** template (scheduled).
3. **T–2 to 4h nudge** template.
4. **Two-way "reply Y"** captured back into the sheet; unconfirmed → Abbas gets a heads-up to call.
5. Pre-call message lists the **3 outcomes** ("we'll (1) find your biggest leak, (2) show its yearly cost, (3) tell you if you qualify for the Founding 5").

**SMS fallback (for non-WhatsApp users):** same flow via **Twilio**, but A2P **10DLC registration** is required, and **TX SB 140** treats texts as solicitation — so only message people who booked **and consented**, with an opt-out. Reminders to a consented booker are transactional and low-risk; keep the consent record.

**Compliance one-liner:** only message numbers given to you for this purpose, keep the consent checkbox, honor "stop" within 10 business days, never cold-text.

---

## What's already wired on the site (no backend needed)
- **Phone + email capture** in the finder gate and contact form.
- **Campaign attribution** (`utm_*` + referrer + landing page) persisted across pages and included in every lead email — so when ads run, each lead shows which channel/ad/hook produced it.
- **WhatsApp share** button on the finder page (owner-to-owner forwarding).
- **QR one-pager** (`onepager.html` → `AZ-RP-leave-behind.pdf`) for in-person drops, QR → the finder.

## Still needs an account/key (hand me these and I'll wire them)
- **Meta Pixel + Conversions API** on the finder result screen → needs the Pixel ID / ad account.
- **Cal.com/Calendly embed + Make.com + WhatsApp BSP** → needs the chosen accounts (Stage 2 above).
