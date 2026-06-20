# AZ Integrations — Website

Marketing website for **AZ Integrations**, an AI integration consultancy founded by
Abbas Zoeb (ex-Google Solutions Engineer, Senior Lead Solutions Architect at WSO2).
The site helps restaurants and small businesses adopt the right AI tools with fully
transparent costs, savings, and fees — starting with the restaurant industry.

## Stack

Plain, dependency-free static site — fast and host-anywhere:

- `index.html` — page content & structure
- `styles.css` — design system & responsive layout
- `script.js` — sticky nav, mobile menu, scroll-reveal animations

No build step. No frameworks.

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
