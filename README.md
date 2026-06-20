# AZ Integrations — Website

Marketing website for **AZ Integrations**, an AI integration consultancy founded by
Abbas Zoeb (ex-Google Solutions Engineer, Senior Lead Solutions Architect at WSO2).
The site helps restaurants and small businesses adopt the right AI tools with fully
transparent costs, savings, and fees — starting with the restaurant industry.

## Stack

Plain, dependency-free static site — fast and host-anywhere. **No build step, no frameworks** — yet it ships flagship-tier effects, all hand-written in vanilla JS/CSS:

**Pages**
- `index.html` — Home (hook + routing, WebGL hero)
- `about.html` — About / Why Abbas (story, career timeline, principles)
- `restaurants.html` — For Restaurants (use-cases, process, transparency, case study, FAQ)

**Shared**
- `styles.css` — design system, bento grids, components, responsive/mobile layout
- `script.js` — interaction engine (shared across all pages)
- `assets/` — optimized headshot (`abbas-800/480.{webp,jpg}`, `abbas.png` master)

### Effects (all dependency-free, 60fps, `prefers-reduced-motion` aware)
- **Live WebGL aurora shader** hero background (cursor-reactive simplex-noise flow; auto CSS-gradient fallback if WebGL is unavailable; pauses when off-screen)
- **Bento-grid** about & services sections
- **Spotlight cards** (glow follows cursor) + subtle **3D tilt**
- **Magnetic buttons** + **custom cursor** glow (desktop / fine-pointer only)
- **Kinetic rotating headline**, **count-up stats**, **infinite marquees**
- **Scroll-progress bar**, staggered **scroll-reveal**, glassmorphic sticky nav

## Run locally

Just open `index.html` in a browser, or serve it:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploy

Any static host works. Easiest options:

- **GitHub Pages** — Settings → Pages → deploy from this branch (root).
- **Netlify / Vercel** — drag-and-drop the folder, or connect the repo (no build command, publish directory = root).
- **Cloudflare Pages** — connect repo, framework preset "None".

## Customize

Common edits, all in `index.html` unless noted:

| What | Where |
| --- | --- |
| Company name / brand | search `AZ Integrations` |
| Contact email | search `azoeb27@gmail.com` |
| Phone | search `4083936716` / `(408) 393-6716` |
| LinkedIn URL | search `linkedin.com/in/abbas-zoeb` *(verify/replace with your real profile URL)* |
| Colors / fonts | `:root` tokens in `styles.css` |
| Services, steps, copy | the respective `<section>` blocks |

### Contact form
The form currently uses a `mailto:` action as a no-backend fallback. For reliable
delivery, point it at a form service (Formspree, Netlify Forms, Basin, etc.) by
changing the `<form action="...">` in `index.html`.

## Mobile

Mobile is treated as the primary experience:
- WebGL hero renders at lower internal resolution on phones; falls back to a CSS
  gradient on reduced-motion, data-saver, or low-memory devices.
- Cursor/tilt/magnetic effects auto-disable on touch.
- 16px form inputs (no iOS zoom-on-focus), 44px minimum tap targets.
- FAQ uses native `<details>` accordions — accessible and reliable on touch.
- Verified: no horizontal overflow at 360 / 390 / 768px.

## TODO / placeholders to confirm

- [ ] Final business email once the custom domain is ready (currently `azoeb27@gmail.com`)
- [ ] Confirm which additional client logos may be displayed (only Hard Rock Cafe is named)
- [ ] Wire the contact form to a delivery service (Formspree/Netlify) for reliability
