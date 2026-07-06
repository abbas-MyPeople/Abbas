---
title: AZ Restaurant Partners — Analytics
emoji: 📊
colorFrom: gray
colorTo: orange
sdk: docker
app_port: 7860
pinned: false
---

# AZ Restaurant Partners — GA4 Analytics

A private, guarded analytics dashboard for **azrestaurantpartners.com**. It reads the site's GA4
property through the GA4 Data API (service-account, read-only) and surfaces traffic, top pages,
sources, the `section_view` funnel, and the conversion events the site fires
(`lead_submit`, `call_click`, `finder_capture`, plus `email_click`, `whatsapp_click`,
`pdf_download`, `outbound_click`, `click`).

Private by design: HTTP Basic auth on the dashboard, `X-Robots-Tag: noindex` on every response,
and `/robots.txt` disallows all crawlers. It never crashes on missing creds and never fabricates
numbers — with no GA4 config it shows a "Connect GA4" state; on a brand-new property it shows
"No data yet".

## Routes

| Route | Auth | Purpose |
|-------|------|---------|
| `/` | Basic | The dashboard (self-contained HTML/JS, no external CDN) |
| `/api/ga4` | Basic | Metrics JSON |
| `/health` | none | `{"ok":true,"ga4_configured":<bool>}` liveness probe |
| `/robots.txt` | none | `Disallow: /` |

## Environment variables (set as Space Secrets)

| Var | Purpose | Default |
|-----|---------|---------|
| `AUTH_USER` | Basic-auth username | `az` |
| `AUTH_PASS` | Basic-auth password | `az2026` |
| `GA4_PROPERTY_ID` | AZ GA4 property id (numeric) | — (required) |
| `GA4_SA_JSON` | Service-account key — raw JSON or base64 | — (required) |
| `GROQ_API_KEY` | Optional; reserved for future narrative summaries | — |

The service account must be added as a **Viewer** on the GA4 property, and the **Google Analytics
Data API** must be enabled on its project.

## Local dev

```bash
export GA4_PROPERTY_ID=…            # AZ property id
export GA4_SA_JSON="$(cat path/to/ga4-reader-sa.json)"
export AUTH_USER=az AUTH_PASS=az2026
python3 app.py                     # http://localhost:7860
```

Deploy entrypoint: `gunicorn app:app --bind 0.0.0.0:7860 --timeout 120 --workers 2`.
