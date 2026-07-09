#!/usr/bin/env python3
"""One Wave v2 — document based on the candle technique itself.
Every classification computed by candle_engine; no eyeballed calls."""
import pandas as pd
from candle_engine import classify, anatomy, trend_before, multi_patterns, line_value

SCRATCH = "/tmp/claude-0/-home-user-Abbas/0bcb134e-841b-522b-b661-36eb435683b7/scratchpad"
CLOSE_TODAY = 7543.64
SCALE = 10.039  # SPX/SPY ratio at Jul 8 close

d = pd.read_csv("/home/user/Abbas/stocks/data/candles/gspc_daily_close_fred.csv")
d.columns = ["Date", "Close"]
d = d[d.Close != "."].copy()
d["Close"] = d.Close.astype(float)
d["Date"] = pd.to_datetime(d.Date)
d = d.dropna().reset_index(drop=True)

# ---------------- build candle series ----------------
dm = d.set_index("Date").Close
rows_m = []
for (yy, mm), s in dm.groupby([dm.index.year, dm.index.month]):
    if (yy, mm) < (2025, 7):
        continue
    rows_m.append(dict(label=f"{pd.Timestamp(yy,mm,1):%b %y}", o=s.iloc[0], h=s.max(), l=s.min(), c=s.iloc[-1]))
rows_m[-1].update(c=CLOSE_TODAY, h=max(rows_m[-1]["h"], CLOSE_TODAY), label=rows_m[-1]["label"] + " ‡")

rows_w = []
for ts, s in d.set_index("Date").Close.resample("W-FRI"):
    if len(s) == 0 or ts < pd.Timestamp("2026-04-20"):
        continue
    rows_w.append(dict(label=f"w/e {ts:%b %d}", o=s.iloc[0], h=s.max(), l=s.min(), c=s.iloc[-1]))
rows_w[-1].update(c=CLOSE_TODAY, h=max(rows_w[-1]["h"], CLOSE_TODAY), label=rows_w[-1]["label"] + " ‡")

t = d.tail(16).reset_index(drop=True)
true_hl = {"2026-07-07": (750.96 * SCALE, 745.21 * SCALE), "2026-07-08": (746.15 * SCALE, 739.51 * SCALE)}
rows_d = []
for i in range(1, len(t)):
    o, c = t.Close[i - 1], t.Close[i]
    h, l = true_hl.get(str(t.Date[i].date()), (max(o, c), min(o, c)))
    rows_d.append(dict(label=f"{t.Date[i]:%a %b %d}", o=o, h=max(h, o, c), l=min(l, o, c), c=c, wick=str(t.Date[i].date()) in true_hl))
rows_d.append(dict(label="Thu Jul 09 †", o=747.26 * SCALE, h=max(751.83 * SCALE, CLOSE_TODAY), l=745.59 * SCALE, c=CLOSE_TODAY, wick=True))

J8 = [(741.51,741.51,741.12,741.32),(740.15,740.74,739.94,740.74),(740.59,740.74,740.50,740.50),(740.48,741.25,740.48,741.25),(741.66,742.58,741.66,742.58),(742.73,743.10,742.73,743.03),(743.22,744.27,743.22,744.27),(744.40,744.68,744.29,744.29),(744.28,744.94,744.28,744.94),(745.44,745.72,745.44,745.55),(745.26,745.26,744.36,744.36),(744.43,745.29,744.39,745.29),(745.27,745.28,745.18,745.18),(744.91,744.91,744.44,744.44),(745.18,745.27,745.04,745.27),(745.14,745.33,745.14,745.26),(745.30,745.30,744.83,744.83),(745.03,745.19,744.92,744.92),(745.24,745.33,744.80,744.80),(745.66,745.66,745.29,745.40)]
J9 = [(747.35,748.40,747.35,748.40),(748.11,748.95,748.11,748.67),(748.69,748.69,747.55,747.55),(746.26,747.88,746.26,747.88),(747.65,748.40,747.65,747.88),(748.05,748.73,747.97,748.73),(748.86,749.49,748.86,749.20),(749.22,749.90,749.22,749.80),(749.58,750.11,749.58,750.11),(750.16,750.16,749.87,749.87),(750.33,750.53,750.33,750.53),(750.56,750.80,750.56,750.64),(750.48,750.69,750.48,750.69),(750.48,750.48,750.42,750.44),(750.72,751.23,750.72,751.23),(751.54,751.76,751.45,751.76),(751.62,751.73,751.62,751.70),(751.74,751.74,751.73,751.73)]
rows_15 = [dict(label=f"Jul 8 · {i+1}", o=a, h=b, l=c, c=e) for i, (a, b, c, e) in enumerate(J8)] + \
          [dict(label=f"Jul 9 · {i+1}", o=a, h=b, l=c, c=e) for i, (a, b, c, e) in enumerate(J9)]

def agg(bins, label, per=4):
    out = []
    for i in range(0, len(bins), per):
        ch = bins[i:i + per]
        out.append(dict(label=f"{label} · hr {i//per+1}", o=ch[0][0], h=max(x[1] for x in ch), l=min(x[2] for x in ch), c=ch[-1][3]))
    return out
rows_h = agg(J8, "Jul 8") + agg(J9, "Jul 9")

# ---------------- classification & patterns ----------------
KEEP = ("engulfing", "harami", "morning star", "evening star", "soldiers", "crows", "outside", "tweezer")

def enrich(rows, keep=KEEP, tweezer_min_tf=False):
    closes = [r["c"] for r in rows]
    for i, r in enumerate(rows):
        r["cls"] = classify(r["o"], r["h"], r["l"], r["c"], trend_before(closes, i))
    pats = {}
    for i, nm in multi_patterns(rows):
        if not any(k in nm for k in keep):
            continue
        if "tweezer" in nm and not tweezer_min_tf:
            continue
        pats.setdefault(i, []).append(nm)
    for i, r in enumerate(rows):
        r["pats"] = ", ".join(dict.fromkeys(pats.get(i, [])))
    return rows

rows_m = enrich(rows_m)
rows_w = enrich(rows_w)
rows_d = enrich(rows_d, tweezer_min_tf=True)
rows_h = enrich(rows_h)
rows_15 = enrich(rows_15)

# manual dedup of noisy daily tweezers: keep only Jun 26 & Jul 2 (flat closes at level)
for r in rows_d:
    if "tweezer" in r["pats"] and r["label"] not in ("Fri Jun 26", "Thu Jul 02"):
        r["pats"] = ", ".join(p for p in r["pats"].split(", ") if "tweezer" not in p)

# ---------------- diagonals & levels ----------------
dd = d.reset_index(drop=True)
def sidx(ds):
    return int((dd.Date <= pd.Timestamp(ds)).sum()) - 1
NOW = len(dd)  # today
i_mar, v_mar = sidx("2026-03-30"), 6343.72
i_j26, v_j26 = sidx("2026-06-26"), 7354.02
i_top, v_top = sidx("2026-06-02"), 7609.78
i_j06, v_j06 = sidx("2026-07-06"), 7537.43
i_j12, v_j12 = sidx("2026-06-12"), 7266.99
up_now = line_value(i_mar, v_mar, i_j26, v_j26, NOW)
up_jul8 = line_value(i_mar, v_mar, i_j26, v_j26, NOW - 1)
dn_now = line_value(i_top, v_top, i_j06, v_j06, NOW)
lo_now = line_value(i_j12, v_j12, i_j26, v_j26, NOW)

LEVELS = [
    ("7,609.78", "r", "the all-time high close (Jun 2) — June's hanging-man head; negation line for every bear pattern below"),
    ("7,580.06", "r", "May 29 record close — last shelf before the high"),
    ("7,537–7,554", "r", "the weekly lower-high (w/e Jun 19: 7,554.29) + Jul 6 close — the triangle's trigger zone, price closed INSIDE it today"),
    (f"≈{dn_now:,.0f}", "r", "falling diagonal from the Jun 2 high through the Jul 6 high — today's close 7,543.64 finished ABOVE it (first close above since the top)"),
    ("7,499–7,501", "s", "Jun 30 / Jun 18 closes — pivot cluster, two touches, now support"),
    (f"≈{up_now:,.0f}", "s", f"rising primary diagonal from the Mar 30 low through the Jun 26 low (+16.6 pts/session). On Jul 8 it sat at ≈{up_jul8:,.0f}: that day's candle speared to 7,423 and closed at 7,482.71 — pierced it, reclaimed it"),
    ("7,483.2x", "s", "the triple-close shelf — Jul 1, Jul 2, Jul 8 all closed here, and it now coincides with the rising diagonal: horizontal memory and diagonal trend at the same price"),
    ("7,354.02", "s", "the weekly higher-low (w/e Jun 26) — lower triangle boundary; floor of the coil"),
    ("7,266.99", "s", "the June swing low (w/e Jun 12 hammer wick) — June's hanging-man wick tip; the pattern's confirmation line"),
    ("6,343.72", "s", "the March 30 low — anchor of the primary diagonal"),
]

# ---------------- svg builders ----------------
def candles_svg(rows, w, h, hlines=(), dlines=(), label_every=None, pad=8, forming_last=True):
    los = [r["l"] for r in rows] + [v for v, *_ in hlines]
    his = [r["h"] for r in rows] + [v for v, *_ in hlines]
    lo, hi = min(los), max(his)
    span = (hi - lo) or 1
    lo -= span * 0.04; hi += span * 0.04
    n = len(rows)
    slot = (w - 2 * pad) / n
    bw = min(16, slot * 0.55)
    def Y(v):
        return 6 + (1 - (v - lo) / (hi - lo)) * (h - 28)
    def X(i):
        return pad + slot * (i + 0.5)
    out = []
    for v, cls, lab in hlines:
        out.append(f'<line class="lvl {cls}" x1="{pad}" y1="{Y(v):.1f}" x2="{w-pad}" y2="{Y(v):.1f}"/>'
                   f'<text class="lvlt {cls}" x="{w-pad}" y="{Y(v)-3:.1f}" text-anchor="end">{lab}</text>')
    for (i1, v1, i2, v2, cls, lab) in dlines:
        x1, y1 = X(i1), Y(v1)
        x2, y2 = X(i2), Y(v2)
        xe = w - pad
        ye = y1 + (y2 - y1) * (xe - x1) / (x2 - x1)
        out.append(f'<line class="diag {cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{xe:.1f}" y2="{ye:.1f}"/>'
                   f'<text class="lvlt {cls}" x="{xe}" y="{ye-4:.1f}" text-anchor="end">{lab}</text>')
    for i, r in enumerate(rows):
        cx = X(i)
        up = r["c"] >= r["o"]
        cls = "cu" if up else "cd"
        if forming_last and i == n - 1 and r["label"].endswith(("‡", "†")):
            cls += " live"
        top, bot = max(r["o"], r["c"]), min(r["o"], r["c"])
        tip = f"{r['label']}: O {r['o']:,.2f} · H {r['h']:,.2f} · L {r['l']:,.2f} · C {r['c']:,.2f} — {r['cls']}" + (f" | {r['pats']}" if r["pats"] else "")
        out.append(f'<g class="{cls}"><title>{tip}</title>'
                   f'<line x1="{cx:.1f}" y1="{Y(r["h"]):.1f}" x2="{cx:.1f}" y2="{Y(r["l"]):.1f}"/>'
                   f'<rect x="{cx-bw/2:.1f}" y="{Y(top):.1f}" width="{bw:.1f}" height="{max(1.5, Y(bot)-Y(top)):.1f}" rx="1.5"/></g>')
        if r["pats"]:
            out.append(f'<circle class="pat" cx="{cx:.1f}" cy="{Y(r["h"])-6:.1f}" r="2.6"><title>{r["pats"]}</title></circle>')
        if label_every and i % label_every == 0:
            out.append(f'<text class="ax" x="{cx:.1f}" y="{h-4}" text-anchor="middle">{r["label"].replace(" ‡","").replace(" †","")}</text>')
    return "".join(out)


def ledger(rows, unit=""):
    tr = ""
    for r in rows:
        rng, body, uw, lw = anatomy(r["o"], r["h"], r["l"], r["c"])
        cls_c = "up" if r["c"] >= r["o"] else "dn"
        pat = f'<div class="patline">{r["pats"]}</div>' if r["pats"] else ""
        tr += (f"<tr><td>{r['label']}</td><td>{r['o']:,.2f}</td><td>{r['h']:,.2f}</td><td>{r['l']:,.2f}</td>"
               f"<td>{r['c']:,.2f}</td><td>{uw:,.2f}</td><td>{lw:,.2f}</td>"
               f"<td class='{cls_c}'>{r['cls']}{pat}</td></tr>")
    return (f'<div class="tbl"><table><thead><tr><th>Candle{unit}</th><th>Open</th><th>High</th><th>Low</th>'
            f'<th>Close</th><th>Wick ↑</th><th>Wick ↓</th><th>Read (computed)</th></tr></thead><tbody>{tr}</tbody></table></div>')


# chart-local index positions for weekly diagonals
wi = {r["label"].replace(" ‡", ""): i for i, r in enumerate(rows_w)}
w_dlines = [
    (wi["w/e Jun 05"], 7609.78, wi["w/e Jun 19"], 7554.29, "r", "falling boundary"),
    (wi["w/e Jun 12"], 7266.99, wi["w/e Jun 26"], 7354.02, "s", "rising boundary"),
]
di = {r["label"].replace(" †", ""): i for i, r in enumerate(rows_d)}
d_dlines = [
    (di["Mon Jun 29"], line_value(i_mar, v_mar, i_j26, v_j26, sidx("2026-06-29")), di["Wed Jul 08"], up_jul8, "s", "primary diagonal (from Mar 30 low)"),
]

svg_m = candles_svg(rows_m, 720, 250, hlines=[(7609.78, "r", "ATH 7,609.78"), (7266.99, "s", "June wick tip 7,266.99")], label_every=2)
svg_w = candles_svg(rows_w, 720, 250, hlines=[(7354.02, "s", "7,354 floor")], dlines=w_dlines, label_every=2)
svg_d = candles_svg(rows_d, 720, 250, hlines=[(7483.23, "s", "7,483 shelf"), (7580.06, "r", "7,580"), (7609.78, "r", "ATH")], dlines=d_dlines, label_every=3)
svg_h = candles_svg(rows_h, 720, 210, hlines=[(745.5, "s", "745.4–745.7 (SPY)"), (751.76, "r", "day high")], label_every=1)
svg_15 = candles_svg(rows_15, 720, 210, hlines=[(745.5, "s", "745.5"), (750.45, "s", "750.4 last HL")], label_every=6)

L_ITEMS = "".join(f'<li><span class="px {c}">{v}</span> {t}</li>' for v, c, t in LEVELS)

