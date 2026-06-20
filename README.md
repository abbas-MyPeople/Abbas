# AZ Integrations — Website

A single-page site for **AZ Integrations** — restaurant technology consulting by
Abbas Zoeb, a software engineer (ex-Google) who also owns an award-winning
restaurant (Wok & Karahi, Spring TX).

Positioning: *an engineer who runs a restaurant himself, so he cuts the AI hype
and sets up only what pays off — transparently, and done for you.*

## Design

Warm, editorial, light — not a generic dark "AI SaaS" template:
- Cream paper, ink text, a single ember accent
- Fraunces (serif display) + Inter (body)
- Real portrait, generous whitespace, quiet fade-ins only — no gimmicks

## Files

- `index.html` — the whole page
- `styles.css` — design system + responsive/mobile layout
- `script.js` — sticky nav, mobile menu, scroll reveal (minimal)
- `assets/` — optimized headshot (`abbas-800/480.{webp,jpg}`)

No build step, no frameworks. Mobile-first; verified no horizontal overflow.

## Run locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Deploy (GitHub Pages)

Repo Settings → Pages → "Deploy from a branch" → this branch, `/ (root)` → Save.
Live at `https://abbas-mypeople.github.io/Abbas/`. (`.nojekyll` is included.)

## To confirm later

- Final business email once a custom domain is ready (currently `azoeb27@gmail.com`)
- Wire the contact form to a delivery service (Formspree/Netlify) for reliability
