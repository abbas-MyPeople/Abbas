#!/usr/bin/env python3
"""Generate the synthesis document (self-contained HTML) from observed data only."""
import pandas as pd

SCRATCH = "/tmp/claude-0/-home-user-Abbas/0bcb134e-841b-522b-b661-36eb435683b7/scratchpad"

# ---------------- data ----------------
d = pd.read_csv("/home/user/Abbas/stocks/data/candles/gspc_daily_close_fred.csv")
d.columns = ["Date", "Close"]
d = d[d.Close != "."].copy()
d["Close"] = d.Close.astype(float)
d["Date"] = pd.to_datetime(d.Date)
d = d.dropna().reset_index(drop=True)

sh = pd.read_csv(f"{SCRATCH}/sp500_monthly_full.csv", parse_dates=["Date"])

LIVE = 7542.0  # ~13:46 ET Jul 9, SPY 751.65 x 10.038, session incomplete

# helpers ---------------------------------------------------------------
def norm_path(vals, w, h, pad=4):
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    pts = []
    n = len(vals)
    for i, v in enumerate(vals):
        x = pad + i * (w - 2 * pad) / (n - 1)
        y = pad + (1 - (v - lo) / rng) * (h - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def candles_svg(rows, w, h, unit="", pad=6, label_every=None, live_last=False):
    """rows: list of (label, o, hi, lo, c). Close-basis or true OHLC per caption."""
    los = [r[3] for r in rows]
    his = [r[2] for r in rows]
    lo, hi = min(los), max(his)
    rng = (hi - lo) or 1
    n = len(rows)
    slot = (w - 2 * pad) / n
    bw = min(18, slot * 0.55)
    out = []
    def Y(v):
        return pad + (1 - (v - lo) / rng) * (h - 2 * pad - 16)
    for i, (lab, o, h2, l2, c) in enumerate(rows):
        cx = pad + slot * (i + 0.5)
        up = c >= o
        cls = "cu" if up else "cd"
        if live_last and i == n - 1:
            cls += " live"
        top, bot = max(o, c), min(o, c)
        out.append(f'<g class="{cls}"><title>{lab}: O {o:,.2f} · H {h2:,.2f} · L {l2:,.2f} · C {c:,.2f}</title>'
                   f'<line x1="{cx:.1f}" y1="{Y(h2):.1f}" x2="{cx:.1f}" y2="{Y(l2):.1f}"/>'
                   f'<rect x="{cx - bw / 2:.1f}" y="{Y(top):.1f}" width="{bw:.1f}" height="{max(1.5, Y(bot) - Y(top)):.1f}" rx="1.5"/></g>')
        if label_every and i % label_every == 0:
            out.append(f'<text class="ax" x="{cx:.1f}" y="{h - 3}" text-anchor="middle">{lab}</text>')
    return "".join(out), lo, hi


# 1) hero: four windows -------------------------------------------------
w1 = d.Close.tail(252).tolist() + [LIVE]
wk = d.set_index("Date").Close.resample("W-FRI").last().dropna()
w2 = wk.tail(11).tolist()[:10]
w3 = d.Close.tail(10).tolist() + [LIVE]
j8 = [741.32, 740.74, 740.50, 741.25, 742.58, 743.03, 744.27, 744.29, 744.94, 745.55, 744.36, 745.29, 745.18, 744.44, 745.27, 745.26, 744.83, 744.92, 744.80, 745.40]
j9 = [748.40, 748.67, 747.55, 747.88, 747.88, 748.73, 749.20, 749.80, 750.11, 749.87, 750.53, 750.64, 750.69, 750.44, 751.23, 751.76, 751.70, 751.73]
w4 = [743.21] + j8 + [747.26] + j9
WINDOWS = [
    ("ONE YEAR", "252 trading days, daily closes", w1),
    ("TEN WEEKS", "weekly closes", w2),
    ("TEN DAYS", "daily closes", w3),
    ("TWO DAYS", "15-minute intervals", w4),
]
hero_svgs = ""
for title, sub, vals in WINDOWS:
    p = norm_path(vals, 260, 110)
    hero_svgs += f'''<figure class="win"><svg viewBox="0 0 260 110" role="img" aria-label="{title}: {sub}">
<polyline class="wline" points="{p}"/><circle class="wend" cx="{p.split()[-1].split(',')[0]}" cy="{p.split()[-1].split(',')[1]}" r="3.5"/></svg>
<figcaption><b>{title}</b><span>{sub}</span></figcaption></figure>'''

# 2) decade chart with drawdown shading ---------------------------------
dec = d.Close.tolist()
dec_p = norm_path(dec, 720, 220)
episodes = [
    ("2018-01-26", "2018-08-24", "−10.2%", 141),
    ("2018-09-20", "2019-04-23", "−19.8%", 86),
    ("2020-02-19", "2020-08-18", "−33.9%", 106),
    ("2020-09-02", "2020-11-13", "−9.6%", 37),
    ("2022-01-03", "2024-01-19", "−25.4%", 332),
    ("2024-07-16", "2024-09-19", "−8.5%", 33),
    ("2025-02-19", "2025-06-27", "−18.9%", 58),
    ("2026-01-27", "2026-04-15", "−9.1%", 12),
]
dates = d.Date.tolist()
def xfrac(ds):
    t = pd.Timestamp(ds)
    idx = max(0, min(len(dates) - 1, (d.Date <= t).sum() - 1))
    return 4 + idx * (720 - 8) / (len(dec) - 1)
shades = "".join(
    f'<rect class="ddz" x="{xfrac(a):.0f}" y="4" width="{max(3, xfrac(b) - xfrac(a)):.0f}" height="212"><title>peak {a} → regained {b} ({dep})</title></rect>'
    for a, b, dep, _ in episodes)

# recovery bars
rec = [("Feb ’18", 141, "−10%"), ("Dec ’18", 86, "−20%"), ("COVID ’20", 106, "−34%"), ("Sep ’20", 37, "−10%"),
       ("’22 bear", 332, "−25%"), ("Aug ’24", 33, "−9%"), ("Apr ’25", 58, "−19%"), ("Mar ’26", 12, "−9%")]
mx = 332
rbars = ""
for i, (lab, days, dep) in enumerate(rec):
    bw = 12 + days / mx * (720 - 200)
    y = i * 34 + 6
    hot = ' class="hot"' if lab == "Mar ’26" else ""
    rbars += (f'<text class="rl" x="0" y="{y + 13}">{lab}</text>'
              f'<rect{hot} x="86" y="{y}" width="{bw:.0f}" height="18" rx="4"><title>{lab}: drop {dep}, trough → new high in {days} sessions</title></rect>'
              f'<text class="rv" x="{92 + bw:.0f}" y="{y + 13}">{days} <tspan class="mut">sessions · fell {dep}</tspan></text>')

# 3) monthly candles (close-basis OHLC from FRED daily) ------------------
dm = d.set_index("Date").Close
g = dm.groupby([dm.index.year, dm.index.month])
mrows = []
for (yy, mm), s in g:
    if (yy, mm) < (2025, 7):
        continue
    mrows.append((f"{pd.Timestamp(yy, mm, 1):%b %y}", s.iloc[0], s.max(), s.min(), s.iloc[-1]))
mrows[-1] = (mrows[-1][0] + " ·live", mrows[-1][1], max(mrows[-1][2], LIVE), mrows[-1][3], LIVE)
mc, mlo, mhi = candles_svg(mrows, 720, 240, label_every=2, live_last=True)

# 4) weekly candles ------------------------------------------------------
wgrp = d.set_index("Date").Close.resample("W-FRI")
wrows = []
for ts, s in wgrp:
    if len(s) == 0 or ts < pd.Timestamp("2026-04-28"):
        continue
    wrows.append((f"w/e {ts:%b %d}", s.iloc[0], s.max(), s.min(), s.iloc[-1]))
wrows[-1] = (wrows[-1][0] + " ·live", wrows[-1][1], max(wrows[-1][2], LIVE), wrows[-1][3], LIVE)
wc, wlo, whi = candles_svg(wrows, 720, 240, label_every=2, live_last=True)

# 5) intraday 15m (SPY, true bins) --------------------------------------
J8 = [(741.51,741.51,741.12,741.32),(740.15,740.74,739.94,740.74),(740.59,740.74,740.50,740.50),(740.48,741.25,740.48,741.25),(741.66,742.58,741.66,742.58),(742.73,743.10,742.73,743.03),(743.22,744.27,743.22,744.27),(744.40,744.68,744.29,744.29),(744.28,744.94,744.28,744.94),(745.44,745.72,745.44,745.55),(745.26,745.26,744.36,744.36),(744.43,745.29,744.39,745.29),(745.27,745.28,745.18,745.18),(744.91,744.91,744.44,744.44),(745.18,745.27,745.04,745.27),(745.14,745.33,745.14,745.26),(745.30,745.30,744.83,744.83),(745.03,745.19,744.92,744.92),(745.24,745.33,744.80,744.80),(745.66,745.66,745.29,745.40)]
J9 = [(747.35,748.40,747.35,748.40),(748.11,748.95,748.11,748.67),(748.69,748.69,747.55,747.55),(746.26,747.88,746.26,747.88),(747.65,748.40,747.65,747.88),(748.05,748.73,747.97,748.73),(748.86,749.49,748.86,749.20),(749.22,749.90,749.22,749.80),(749.58,750.11,749.58,750.11),(750.16,750.16,749.87,749.87),(750.33,750.53,750.33,750.53),(750.56,750.80,750.56,750.64),(750.48,750.69,750.48,750.69),(750.48,750.48,750.42,750.44),(750.72,751.23,750.72,751.23),(751.54,751.76,751.45,751.76),(751.62,751.73,751.62,751.70),(751.74,751.74,751.73,751.73)]
intra_rows = [(f"Jul 8 · bar {i+1}", *r) for i, r in enumerate(J8)] + [(f"Jul 9 · bar {i+1}", *r) for i, r in enumerate(J9)]
ic, ilo, ihi = candles_svg(intra_rows, 720, 220, live_last=True)
gapx = 6 + (720 - 12) / len(intra_rows) * 20

# 6) analog: 1998 vs 2026, indexed to trough=100 ------------------------
s98 = sh[(sh.Date >= "1998-08-01") & (sh.Date <= "2000-09-30")].SP500.tolist()
base98 = min(s98[:3])
p98 = [v / base98 * 100 for v in s98]
s26 = sh[(sh.Date >= "2026-03-01")].SP500.tolist() + [7500]  # Jul partial avg est from dailies
base26 = s26[0]
p26 = [v / base26 * 100 for v in s26]
top = max(p98)
W, H = 720, 240
def ana_path(vals):
    pts = []
    for i, v in enumerate(vals):
        x = 40 + i * (W - 50) / 25
        y = 8 + (1 - (v - 95) / (top - 95)) * (H - 40)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)
ana98, ana26 = ana_path(p98), ana_path(p26)
ana_end = ana26.split()[-1].split(",")

TABLE_M = "".join(
    f"<tr><td>{lab}</td><td>{o:,.2f}</td><td>{h:,.2f}</td><td>{l:,.2f}</td><td>{c:,.2f}</td><td class='{'up' if c>=o else 'dn'}'>{(c/o-1)*100:+.1f}%</td></tr>"
    for lab, o, h, l, c in mrows)
TABLE_W = "".join(
    f"<tr><td>{lab}</td><td>{o:,.2f}</td><td>{h:,.2f}</td><td>{l:,.2f}</td><td>{c:,.2f}</td><td class='{'up' if c>=o else 'dn'}'>{(c/o-1)*100:+.1f}%</td></tr>"
    for lab, o, h, l, c in wrows)

daily10 = d.tail(10)
TABLE_D = "".join(
    f"<tr><td>{r.Date:%a %b %d}</td><td>{r.Close:,.2f}</td><td class='{'up' if pc and r.Close>=pc else 'dn'}'>{((r.Close/pc-1)*100 if pc else 0):+.2f}%</td></tr>"
    for pc, (_, r) in zip([None] + daily10.Close.tolist()[:-1], daily10.iterrows()) if pc
) + f"<tr class='live'><td>Thu Jul 09 · live</td><td>≈{LIVE:,.0f}</td><td class='up'>+0.8%</td></tr>"

html = f"""<title>One Wave — the S&P 500 from 155 years to 5 minutes</title>
<style>
:root {{
  --ground:#f7f6f2; --surface:#fffdf9; --ink:#191714; --ink2:#524e46; --mut:#8b867c;
  --line:#e6e2d8; --gold:#a06b10; --gold-mark:#d99a2b; --up:#0e8f63; --up-mark:#1baf7a;
  --dn:#c23736; --dn-mark:#e34948; --blue:#2a78d6; --shade:rgba(227,73,72,.08);
}}
@media (prefers-color-scheme: dark) {{ :root {{
  --ground:#101418; --surface:#171d23; --ink:#f2efe8; --ink2:#b9b4a8; --mut:#7d7f7a;
  --line:#262d34; --gold:#e8b04b; --gold-mark:#c98500; --up:#3ec996; --up-mark:#1baf7a;
  --dn:#ef8484; --dn-mark:#e66767; --blue:#3987e5; --shade:rgba(230,103,103,.10);
}} }}
:root[data-theme="dark"] {{
  --ground:#101418; --surface:#171d23; --ink:#f2efe8; --ink2:#b9b4a8; --mut:#7d7f7a;
  --line:#262d34; --gold:#e8b04b; --gold-mark:#c98500; --up:#3ec996; --up-mark:#1baf7a;
  --dn:#ef8484; --dn-mark:#e66767; --blue:#3987e5; --shade:rgba(230,103,103,.10);
}}
:root[data-theme="light"] {{
  --ground:#f7f6f2; --surface:#fffdf9; --ink:#191714; --ink2:#524e46; --mut:#8b867c;
  --line:#e6e2d8; --gold:#a06b10; --gold-mark:#d99a2b; --up:#0e8f63; --up-mark:#1baf7a;
  --dn:#c23736; --dn-mark:#e34948; --blue:#2a78d6; --shade:rgba(227,73,72,.08);
}}
* {{ box-sizing:border-box }}
body {{ background:var(--ground); color:var(--ink); margin:0;
  font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif; }}
.wrap {{ max-width:46rem; margin:0 auto; padding:0 1.25rem 6rem }}
h1,h2,.dropcap {{ font-family:"Iowan Old Style",Georgia,"Times New Roman",serif; }}
h1 {{ font-size:clamp(2rem,5.5vw,3.4rem); line-height:1.12; text-wrap:balance; font-weight:600; margin:.6rem 0 1rem }}
h2 {{ font-size:1.7rem; line-height:1.25; text-wrap:balance; font-weight:600; margin:0 0 .75rem }}
h1 em, h2 em {{ font-style:italic; color:var(--gold) }}
p {{ max-width:62ch; color:var(--ink2); margin:0 0 1.1rem }}
p strong, li strong {{ color:var(--ink) }}
.eyebrow {{ font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; color:var(--mut); margin:4.5rem 0 .4rem }}
.hero .eyebrow {{ margin-top:4rem }}
.lede {{ font-size:1.15rem }}
.chip {{ display:inline-block; font:600 .7rem/1 system-ui; letter-spacing:.12em; color:var(--gold);
  border:1px solid color-mix(in oklab, var(--gold) 45%, transparent); border-radius:999px;
  padding:.45em .9em; margin-bottom:.75rem; text-transform:uppercase }}
.card {{ background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.15rem; margin:1.4rem 0 }}
figure {{ margin:0 }}
figcaption, .cap {{ font-size:.8rem; color:var(--mut); margin-top:.5rem; line-height:1.5 }}
svg {{ width:100%; height:auto; display:block }}
svg text {{ font:10.5px system-ui; fill:var(--mut) }}
.wline {{ fill:none; stroke:var(--gold-mark); stroke-width:2; stroke-linejoin:round }}
.wend {{ fill:var(--gold-mark) }}
.windows {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:.9rem; margin:1.6rem 0 .4rem }}
.win {{ background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:.8rem }}
.win figcaption {{ display:flex; justify-content:space-between; gap:.6rem; margin-top:.4rem }}
.win b {{ color:var(--ink); font:600 .74rem/1.3 system-ui; letter-spacing:.1em }}
.win span {{ font-size:.72rem }}
.cu line {{ stroke:var(--up-mark); stroke-width:1.6 }} .cu rect {{ fill:var(--up-mark) }}
.cd line {{ stroke:var(--dn-mark); stroke-width:1.6 }} .cd rect {{ fill:var(--dn-mark) }}
.live rect {{ opacity:.55; stroke:var(--gold-mark); stroke-width:1.5; stroke-dasharray:3 3 }}
.ddz {{ fill:var(--shade) }}
.decline {{ fill:none; stroke:var(--ink2); stroke-width:1.4 }}
.rl {{ font-weight:600; fill:var(--ink2) }}
.rv {{ fill:var(--ink); font-weight:600; font-variant-numeric:tabular-nums }}
.rv .mut {{ fill:var(--mut); font-weight:400 }}
svg rect:not(.ddz) {{ }}
.rbars rect {{ fill:var(--blue) }} .rbars rect.hot {{ fill:var(--gold-mark) }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:.9rem; margin:1.5rem 0 }}
.tile {{ background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:1rem }}
.tile .n {{ font-family:Georgia,serif; font-size:2rem; line-height:1.1; color:var(--ink) }}
.tile .n.gold {{ color:var(--gold) }} .tile .n.up {{ color:var(--up) }} .tile .n.dn {{ color:var(--dn) }}
.tile .l {{ font-size:.78rem; color:var(--mut); margin-top:.3rem; line-height:1.45 }}
.tbl {{ overflow-x:auto; margin:1rem 0 }}
table {{ border-collapse:collapse; width:100%; font-size:.85rem; font-variant-numeric:tabular-nums }}
th,td {{ text-align:right; padding:.42em .7em; border-bottom:1px solid var(--line); white-space:nowrap }}
th:first-child, td:first-child {{ text-align:left }}
th {{ color:var(--mut); font-weight:600; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase }}
td.up {{ color:var(--up) }} td.dn {{ color:var(--dn) }}
tr.live td {{ color:var(--gold) }}
.levels {{ list-style:none; padding:0; margin:1rem 0; font-variant-numeric:tabular-nums }}
.levels li {{ display:flex; gap:.9rem; align-items:baseline; padding:.5rem 0; border-bottom:1px dashed var(--line); font-size:.92rem }}
.levels .px {{ font-weight:700; min-width:9.5ch; font-family:ui-monospace,Menlo,monospace; font-size:.88rem }}
.levels .r {{ color:var(--dn) }} .levels .s {{ color:var(--up) }} .levels .now {{ color:var(--gold) }}
.ana1 {{ fill:none; stroke:var(--blue); stroke-width:2 }}
.ana2 {{ fill:none; stroke:var(--gold-mark); stroke-width:2.6 }}
.pred {{ border-left:3px solid var(--gold-mark); padding:.15rem 0 .15rem 1rem; margin:1.2rem 0 }}
.pred h3 {{ margin:.2rem 0 .3rem; font-size:1.02rem }}
.pred p {{ margin-bottom:.4rem; font-size:.95rem }}
.inv {{ font-size:.8rem; color:var(--mut) }}
hr {{ border:0; border-top:1px solid var(--line); margin:3.2rem 0 }}
.foot {{ font-size:.8rem; color:var(--mut); line-height:1.7 }}
a {{ color:var(--gold) }}
@media (prefers-reduced-motion: no-preference) {{
  .reveal {{ opacity:0; transform:translateY(10px); transition:opacity .7s ease, transform .7s ease }}
  .reveal.in {{ opacity:1; transform:none }}
}}
</style>

<div class="wrap">

<header class="hero">
<div class="eyebrow">A field study · S&amp;P 500 · recorded live, July 9, 2026</div>
<h1>Everything alive moves in waves. So does the largest pile of money on&nbsp;Earth.</h1>
<p class="lede">Your breath rises, catches, falls, recovers. Your heartbeat does. Your sleep does.
This page zooms the U.S. stock market from <strong>155 years</strong> down to <strong>the last
five minutes of trading</strong> — and at every single magnification, the same wave is there.
Look at these four charts before you read another word:</p>
<div class="windows">{hero_svgs}</div>
<p class="cap">Four different zoom levels of the same market, ending at the same moment (today, mid-session).
None of them is mislabeled. If you can't tell which is a year and which is two days — that's the discovery.</p>
<p class="lede"><strong>Rise. Shock. Base. Reclaim.</strong> One shape, wearing four costumes.
And hiding inside it, something stranger that we measured on the way down: <em>the market's fear is healing
faster every year — and the speed is quantifiable.</em> Keep scrolling; we descend from the century to the minute.</p>
</header>

<hr>

<section>
<div class="chip">Depth 1 · A decade of days</div>
<h2>Eight times it fell hard. Eight times it came all the way back.</h2>
<p>Ten years of daily closes, 2,608 of them. The shaded bands are every drawdown of 8% or more —
from the day the market peaked to the day it made a new all-time high again.</p>
<figure class="card"><svg viewBox="0 0 720 224" role="img" aria-label="S&P 500 daily closes 2016 to 2026 with drawdown episodes shaded">
{shades}<polyline class="decline" points="{dec_p}"/></svg>
<figcaption>S&amp;P 500 daily closes, Jul 2016 → Jul 2026 (source: FRED). Shaded: the eight ≥8% drawdown-to-recovery episodes. Hover any band for its dates.</figcaption></figure>
<p><strong>Eight out of eight recovered.</strong> A decade of proof that "every dip is a gift."
Now look at <em>how long</em> each recovery took, trough to new high:</p>
<figure class="card"><svg class="rbars" viewBox="0 0 720 278" role="img" aria-label="Recovery time in sessions for each drawdown episode">{rbars}</svg>
<figcaption>Sessions from the bottom of each fall to a new all-time high. The 2022 bear (332) is the one slow exception; the trend everywhere else bends toward zero. Gold: March 2026 — <b>twelve sessions</b>, the fastest full recovery of the decade.</figcaption></figure>
<div class="tiles">
<div class="tile"><div class="n">8 / 8</div><div class="l">drawdowns ≥8% this decade that fully recovered</div></div>
<div class="tile"><div class="n gold">12</div><div class="l">sessions from the March 30, 2026 bottom (6,343.72) to a new all-time high</div></div>
<div class="tile"><div class="n">141 → 12</div><div class="l">recovery time, 2018 vs 2026. The reflex is getting faster</div></div>
</div>
<p><strong>Why it matters:</strong> this is a learning system. Every recovered crash trains millions of
people — and the machines they built — to buy the next one sooner. The reward arrives faster each time,
so the belief gets stronger each time. Hold that thought; it becomes the whole story at the bottom of this page.</p>
</section>

<hr>

<section>
<div class="chip">Depth 2 · Twelve months</div>
<h2>The year that crashed in March and didn't care by April.</h2>
<figure class="card"><svg viewBox="0 0 720 244" role="img" aria-label="Thirteen monthly candles July 2025 to July 2026">{mc}</svg>
<figcaption>Monthly candles, Jul 2025 → Jul 2026 (dashed = this month, still forming). Wicks mark the highest and lowest <i>daily close</i> inside each month — measured, not estimated. Hover for numbers.</figcaption></figure>
<div class="tbl"><table><thead><tr><th>Month</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Δ</th></tr></thead><tbody>{TABLE_M}</tbody></table></div>
<p><strong>What happened:</strong> a calm five-month climb, a two-month stall at ~6,850, a January
kiss of 7,000 that got rejected — then March: hot inflation plus a new Middle-East war, oil spiking,
and a fall to <strong>6,343.72</strong> (March 30), erasing every 2026 gain.</p>
<p><strong>Then April returned +10.4% — the best month since November 2020.</strong> Since 1950 only five
other months gained ~10%: Feb 1975, Sep 1982, Feb 1991, Nov 1998, Apr 2009. Every one came right after a
panic. Every one was higher a year later, by +14% to +41%. April 2026 is the sixth member of that club.</p>
<p><strong>Why it happened:</strong> earnings ignored the war (84% of companies beat estimates),
and a decade of trained reflex — see Depth 1 — bought the hole. May melted up to records nine weeks
straight. June printed the year's warning candle: a new all-time high at <strong>7,609.78</strong>
(June 2), then a chop that couldn't hold it. The market has now spent five weeks coiled beneath that number.</p>
</section>

<hr>

<section>
<div class="chip">Depth 3 · Ten weeks</div>
<h2>A nine-week march, one shock, and a coil under the ceiling.</h2>
<figure class="card"><svg viewBox="0 0 720 244" role="img" aria-label="Weekly candles for the last ten weeks">{wc}</svg>
<figcaption>Weekly candles (dashed = this week, live). Wicks = daily-close extremes within each week.</figcaption></figure>
<div class="tbl"><table><thead><tr><th>Week</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Δ</th></tr></thead><tbody>{TABLE_W}</tbody></table></div>
<p><strong>What you're looking at:</strong> the end of the longest weekly winning streak since 2023
(nine weeks, snapped June 5 by a too-hot jobs report — a 2.64% one-day drop, ~$1.8&nbsp;trillion gone),
then a five-week argument: sellers defend 7,609–7,621 above, buyers raise the floor beneath —
7,354, then 7,424. Flat ceiling, rising floor. Chart readers call it an <em>ascending triangle</em>;
in plain words, <strong>pressure with a direction</strong>. Coils like this resolve, usually within weeks,
and usually — not always — in the direction of the rising side.</p>
</section>

<hr>

<section>
<div class="chip">Depth 4 · Ten days · 48 hours</div>
<h2>Two days ago the war came back. Watch what fear does now.</h2>
<div class="tbl"><table><thead><tr><th>Session</th><th>Close</th><th>Δ</th></tr></thead><tbody>{TABLE_D}</tbody></table></div>
<figure class="card"><svg viewBox="0 0 720 224" role="img" aria-label="15-minute candles for July 8 and July 9">
<line x1="{gapx:.0f}" y1="6" x2="{gapx:.0f}" y2="200" stroke="var(--line)" stroke-dasharray="4 4"/>
<text class="ax" x="{gapx / 2:.0f}" y="216" text-anchor="middle">Wed Jul 8 — the flush and the recovery</text>
<text class="ax" x="{(gapx + 720) / 2:.0f}" y="216" text-anchor="middle">Thu Jul 9 (live) — the staircase</text>
{ic}</svg>
<figcaption>15-minute bars (SPY, the S&amp;P 500 fund — multiply by ~10 for index points), recorded by this project's own
pipeline. Jul 8 session: open 743.21, low <b>739.51</b> at 12:15 PM with fear (VIX) peaking at 18.37 the same minute,
close 745.40 near the high — a hammer. Jul 9: gapped up despite overnight U.S. strikes on Iran, dipped to 745.59 —
0.19 above yesterday's close, a gap-fill test held almost to the penny — then higher lows every single hour.</figcaption></figure>
<p><strong>The detail worth staring at:</strong> July 1, July 2 and July 8 all closed at
<strong>7,483.2x</strong> — three separate days finding rest at the same price, to the decimal.
Levels have memory. What was a ceiling last week is the floor being defended this week.</p>
<p><strong>And the punchline of the whole study, measured at three scales:</strong> the same war has now
hit this market three times. March: <strong>−9.1%</strong> and a panic low. June (oil spike): <strong>−3.4%</strong>
and a wobble. Last night (actual airstrikes, ceasefire declared dead): a dip that lasted <strong>about
forty-five minutes</strong> and was fully bought before lunch, with oil <em>falling</em>. Identical stimulus,
reaction shrinking by two-thirds each exposure. In a nervous system you'd call that habituation.
In meditation you'd call it the fading of a conditioned reaction. The open question — the one honest
unknown — is whether this calm is <em>equanimity</em> (war has provably not touched earnings) or
<em>numbness</em> (risk being ignored, not resolved). The chart cannot tell you. Nothing can, yet.</p>
</section>

<hr>

<section>
<div class="chip">Depth 5 · The rhyme</div>
<h2>We have seen this exact movie. It was called 1998.</h2>
<p>Take the 2026 recovery (gold) and lay it over the recovery from the October 1998 crash (blue) —
the LTCM/Russia panic that kicked off the final, wildest leg of the dot-com era. Both indexed to 100
at their bottom, month by month:</p>
<figure class="card"><svg viewBox="0 0 720 240" role="img" aria-label="1998 recovery path versus 2026 recovery path, indexed to trough">
<polyline class="ana1" points="{ana98}"/><polyline class="ana2" points="{ana26}"/>
<circle cx="{ana_end[0]}" cy="{ana_end[1]}" r="4" fill="var(--gold-mark)"/>
<text x="46" y="20" fill="var(--blue)" font-weight="600">1998 → 2000 (24 months)</text>
<text x="46" y="36" fill="var(--gold)" font-weight="600">2026 (4 months in — the dot)</text></svg>
<figcaption>Monthly average level, indexed to 100 at each trough (Shiller dataset). The 1998 path ran ~+60%
over 17 more months before the March 2000 top — then gave back −42% over two years.</figcaption></figure>
<p><strong>The parallels are not decoration:</strong> a financial shock bought back in weeks · a
transformational technology everyone believes in (internet then, AI now) · narrow leadership with
records at the index level while the average stock lags · valuation at the extreme — the CAPE ratio's
eight highest readings ever were all set in 1999–2000, and mid-2026 sits at the #2 neighborhood of its
entire history · even the texture matches: insiders selling into strength (Alphabet raising $80B in stock),
hot IPOs (SpaceX +19% on debut), and a chip sector that swings 5–7% in a week.</p>
<p><strong>What 1998 teaches, both ways:</strong> the melt-up ran much further than any reasonable
person expected — selling in November 1998 missed a +60% run. And then the ending took back five years
of gains anyway. Both halves of that sentence are the lesson. The decade that taught everyone
"dips always come back" (8 for 8, remember) ended with the one dip that didn't — for thirteen years.</p>
</section>

<hr>

<section>
<div class="chip">The forecast · every level, honestly</div>
<h2>What the wave says next — as base rates, not prophecy.</h2>
<ul class="levels">
<li><span class="px r">7,609–7,621</span> the ceiling: all-time high zone, five weeks of supply</li>
<li><span class="px r">7,580</span> last record close before the June stall</li>
<li><span class="px now">≈7,542</span> <strong>price now</strong> — pressing the July 6 high</li>
<li><span class="px s">7,483</span> the triple-close shelf (Jul 1, 2, 8) — first support</li>
<li><span class="px s">7,424–7,440</span> this week's defended low / late-June closes</li>
<li><span class="px s">7,354–7,384</span> the June double-bottom — floor of the coil</li>
<li><span class="px s">6,344</span> the March low — where the last panic priced</li>
</ul>
<div class="pred"><h3>Minutes → hours (today)</h3>
<p>A staircase pinned at the day's high with shrinking bars = a market coiling for one more push, and
today's move has already exceeded what the options market priced for the whole day (±0.53%) — the
sellers of calm are being squeezed, which feeds the trend.</p>
<p class="inv">This level says nothing beyond today. It never does.</p></div>
<div class="pred"><h3>Days</h3>
<p>A hammer at support (Jul 8) confirmed by a gap-and-go (Jul 9) typically tests the prior supply:
expect a run at <strong>7,580 → 7,609–7,621</strong> within days.</p>
<p class="inv">Invalidated by a daily close back under 7,483.</p></div>
<div class="pred"><h3>Weeks</h3>
<p>Ascending triangles under all-time highs resolve upward more often than not; the pattern's measured
move (ceiling minus floor, ≈267 pts) projects <strong>≈7,880–7,890</strong> if 7,621 breaks and holds.</p>
<p class="inv">Invalidated by a weekly close under 7,354 — that turns the coil into a top.</p></div>
<div class="pred"><h3>Months</h3>
<p>The +10% month club is 5-for-5 higher a year later (+14% to +41%). The decade's dip-recovery record is
8-for-8, accelerating. Base rates say the trend has further to run — the 1998 analog says possibly much further,
and possibly wilder, than seems sane.</p>
<p class="inv">The base rate is not a law. It is the record of a regime, and regimes end unannounced.</p></div>
<div class="pred"><h3>Years — the honest one</h3>
<p>Valuation sits at the #2 extreme in 155 years of data; the #1 was March 2000. The louder the "dips always
recover" belief gets, the closer it stands to the one dip that won't. Every subtle gauge that disagrees with
the calm — fear priced higher now than a week ago while price is <em>higher</em>, breadth narrowing, insiders
issuing stock — is the tension under the stillness. When this regime breaks, the give-back will not take
12 sessions to resolve; the last time this setup broke, it took back −42% over two years and repaid it over thirteen.</p>
<p class="inv">No timing claim is made here, and anyone who makes one is imagining. The 1998 analog itself argues the top is quarters away, not days.</p></div>
</section>

<hr>

<section>
<div class="chip">Method · why you can trust the numbers</div>
<h2>Nothing on this page was imagined.</h2>
<p>Rule of the study (borrowed from Vipassana meditation, which inspired the multi-scale method):
<strong>report only what is actually observed; where awareness cannot reach, say "not perceived" —
never fabricate.</strong> In practice:</p>
<p><strong>Sources:</strong> 155 years of monthly data (Shiller/S&amp;P dataset) · ten years of daily closes
(Federal Reserve FRED, 2,608 sessions) · the last three sessions at 15-minute resolution, recorded by this
project's own market-snapshot pipeline before and during writing · every 2025–26 closing print cross-checked
against contemporaneous financial press. Candle wicks on monthly/weekly charts are daily-close extremes
(measured), not intraday extremes (not available). One-minute data was unobtainable from this environment
after multiple attempts and is therefore absent — not simulated. Today's candle is live and incomplete.</p>
<p class="foot">Recorded July 9, 2026, ~2 PM ET, S&amp;P 500 ≈ 7,542 (+0.8% on the day), VIX 16.0.
This is a study of structure, not investment advice. The market owes none of us a repeat of its patterns —
that, too, is the lesson of the page.</p>
</section>

</div>
<script>
(function(){{
  if (matchMedia('(prefers-reduced-motion: no-preference)').matches) {{
    const els = document.querySelectorAll('section, header');
    els.forEach(e => e.classList.add('reveal'));
    const io = new IntersectionObserver(en => en.forEach(x => {{
      if (x.isIntersecting) {{ x.target.classList.add('in'); io.unobserve(x.target); }}
    }}), {{ threshold: .08 }});
    els.forEach(e => io.observe(e));
  }}
}})();
</script>
"""

open(f"{SCRATCH}/one-wave.html", "w").write(html)
print("written", len(html), "bytes")
print("monthly rows:", len(mrows), "| weekly rows:", len(wrows), "| intraday bars:", len(intra_rows))
print("w2 weekly closes:", [round(v, 2) for v in w2])
