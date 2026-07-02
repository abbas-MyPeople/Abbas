# Stocks Dashboard

A private, self-contained markets desk. Lives at **`/stocks`** in this repo and is
designed to be served at **`abbaszoeb.com/stocks`** (interim: `azrestaurantpartners.com/stocks`,
since that's the domain currently on this repo's `CNAME`).

It's a static site — no backend — so it drops straight onto GitHub Pages. Live data
comes from two sources that keep keys out of the browser:

- **Charts** → free TradingView embed widgets (near-real-time, all timeframes).
- **Quotes + options chain + morning research** → committed JSON snapshots produced by
  scheduled GitHub Actions. The pages just render the JSON.

> ⚠️ Personal research tool, **not financial advice**. Options analytics are Black-Scholes
> model estimates. Free feeds may be delayed (~15 min on options).

## Layout

```
stocks/
├── index.html                 # dashboard home — pick an asset (stocks / crypto)
├── spy/
│   ├── index.html             # SPY desk: quote, multi-timeframe charts, morning brief
│   └── options/index.html     # SPY options ≤7 DTE: chain, Greeks, synthesis, recommendations
├── assets/
│   ├── css/dashboard.css       # design system (dark trading aesthetic + light mode)
│   └── js/
│       ├── app.js              # utils: formatting, market clock, nav, loaders, sparkline, gauge
│       ├── charts.js           # TradingView widget helpers (7 timeframes)
│       ├── options.js          # Black-Scholes pricing/Greeks + per-contract scoring
│       └── research.js         # renders the morning briefing JSON
├── data/
│   ├── registry.json           # symbols + categories (add more here)
│   └── spy/
│       ├── quote/latest.json    # spot, change, VIX, implied daily move, sparkline
│       ├── options/latest.json  # ≤7 DTE chain with Greeks/IV/vol/OI
│       └── research/latest.json # today's brief (+ dated archive copies)
└── scripts/
    ├── fetch_market.py         # CBOE delayed quotes → quote + options JSON (stdlib only)
    └── morning_research.py     # Claude + web search → research JSON (needs ANTHROPIC_API_KEY)
```

## Automation

Two workflows at repo root (`.github/workflows/`):

| Workflow | Schedule (UTC) | Does |
|---|---|---|
| `stocks-market-snapshot.yml` | every 15 min, 13:30–20:00, Mon–Fri | commits fresh SPY quote + options chain |
| `stocks-morning-brief.yml` | 12:00, Mon–Fri (~8 AM ET) | refreshes snapshot, runs deep research, commits the brief |

**Required secret:** `ANTHROPIC_API_KEY` (repo → Settings → Secrets → Actions) for the
morning brief. Without it, that job no-ops and the last good brief stays up.

Both also have **Run workflow** buttons (`workflow_dispatch`) for manual runs.

> Scheduled workflows run from the **default branch**, so merge this to the Pages
> deploy branch to activate them. The current committed JSON is clearly-labeled
> **sample seed** data plus a real 2026-07-02 briefing, so every page renders before
> the first live run.

## Adding a symbol

1. Add an entry to `data/registry.json` (set `tvSymbol`, `category`, `options`, `maxDTE`).
2. Copy `spy/` to `<symbol>/` and swap the TradingView symbol + data paths.
3. Point the fetch scripts at the new symbol (parameterize `SYMBOL`).

## Data source, swapping later

`fetch_market.py` reads CBOE's free delayed feed. To go fully real-time, replace the
`http_json(...CBOE...)` call with a keyed provider (Polygon / Tradier / Finnhub) using a
secret — the frontend contract (the JSON shape) doesn't change.
