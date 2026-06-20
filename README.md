# AZ Integrations — Website

Marketing website for **AZ Integrations**, an AI integration consultancy founded by
Abbas Zoeb (ex-Google Solutions Engineer, Senior Lead Solutions Architect at WSO2).
The site helps restaurants and small businesses adopt the right AI tools with fully
transparent costs, savings, and fees — starting with the restaurant industry.

## Stack

Plain, dependency-free static site — fast and host-anywhere. **No build step, no frameworks** — yet it ships flagship-tier effects, all hand-written in vanilla JS/CSS:

- `index.html` — page content & structure
- `styles.css` — design system, bento grids, responsive layout
- `script.js` — interaction engine

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

## TODO / placeholders to confirm

- [ ] Real LinkedIn profile URL (currently `linkedin.com/in/abbas-zoeb`)
- [ ] Final business email once the custom domain is ready
- [ ] Add a real headshot in the About card (replaces the "AZ" monogram)
- [ ] Confirm which client logos may be displayed (only Hard Rock Cafe is currently shown by name)
