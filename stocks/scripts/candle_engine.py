#!/usr/bin/env python3
"""Candle-technique engine: anatomy, single/multi-candle patterns, pivots,
horizontal S/R zones, diagonal trendlines. Everything computed from OHLC —
no eyeballed calls. Basis of each series is declared by the caller."""
import pandas as pd


# ---------- anatomy & single-candle classification ----------
def anatomy(o, h, l, c):
    rng = h - l
    body = abs(c - o)
    uw = h - max(o, c)
    lw = min(o, c) - l
    return rng, body, uw, lw


def classify(o, h, l, c, trend=None):
    """trend: 'up'/'down'/None — context for hammer vs hanging man etc."""
    rng, body, uw, lw = anatomy(o, h, l, c)
    if rng <= 0:
        return "four-price doji"
    b, u, w = body / rng, uw / rng, lw / rng
    bull = c >= o
    if b >= 0.85:
        return f"marubozu ({'bull' if bull else 'bear'})"
    if b <= 0.12:
        if u <= 0.12 and w >= 0.6:
            return "dragonfly doji"
        if w <= 0.12 and u >= 0.6:
            return "gravestone doji"
        if u >= 0.3 and w >= 0.3:
            return "long-legged doji"
        return "doji"
    if lw >= 2 * body and u <= 0.15:
        if trend == "down":
            return "hammer"
        if trend == "up":
            return "hanging man"
        return "hammer-shape"
    if uw >= 2 * body and w <= 0.15:
        if trend == "up":
            return "shooting star"
        if trend == "down":
            return "inverted hammer"
        return "star-shape"
    if b < 0.4:
        return f"spinning top ({'bull' if bull else 'bear'})"
    return f"{'bull' if bull else 'bear'} candle"


def trend_before(closes, i, k=3):
    if i < k:
        return None
    seg = closes[i - k:i]
    if seg[-1] > seg[0]:
        return "up"
    if seg[-1] < seg[0]:
        return "down"
    return None


# ---------- multi-candle patterns ----------
def multi_patterns(rows):
    """rows: list of dicts with o,h,l,c. Returns list of (index, name)."""
    out = []
    for i in range(1, len(rows)):
        p, q = rows[i - 1], rows[i]
        pb, qb = abs(p["c"] - p["o"]), abs(q["c"] - q["o"])
        p_bull, q_bull = p["c"] >= p["o"], q["c"] >= q["o"]
        tol = q["c"] * 0.0008
        # engulfing: opposite colors, current body engulfs prior body
        if p_bull != q_bull and qb > 0 and \
           max(q["o"], q["c"]) >= max(p["o"], p["c"]) - tol / 4 and \
           min(q["o"], q["c"]) <= min(p["o"], p["c"]) + tol / 4 and qb > pb:
            out.append((i, f"{'bullish' if q_bull else 'bearish'} engulfing"))
        # harami: current body inside prior body, prior body substantial
        elif pb > 0 and max(q["o"], q["c"]) <= max(p["o"], p["c"]) and \
                min(q["o"], q["c"]) >= min(p["o"], p["c"]) and qb < pb * 0.6:
            out.append((i, f"harami ({'bull' if q_bull else 'bear'})"))
        # tweezers (needs real extremes; caller filters by basis)
        if abs(q["h"] - p["h"]) <= tol and q["h"] > q["c"] and p["h"] > p["c"]:
            out.append((i, "tweezer top"))
        if abs(q["l"] - p["l"]) <= tol:
            out.append((i, "tweezer bottom"))
        # inside / outside bar
        if q["h"] <= p["h"] and q["l"] >= p["l"]:
            out.append((i, "inside bar"))
        elif q["h"] >= p["h"] and q["l"] <= p["l"]:
            out.append((i, "outside bar"))
    for i in range(2, len(rows)):
        a, b, c3 = rows[i - 2], rows[i - 1], rows[i]
        ab, bb, cb = (abs(x["c"] - x["o"]) for x in (a, b, c3))
        arng = a["h"] - a["l"]
        if arng <= 0:
            continue
        a_bear, c_bull = a["c"] < a["o"], c3["c"] > c3["o"]
        mid_a = (a["o"] + a["c"]) / 2
        small_b = bb < ab * 0.5
        # morning star
        if a_bear and small_b and c_bull and cb > ab * 0.6 and c3["c"] > mid_a:
            out.append((i, "morning star"))
        # evening star
        if (not a_bear) and small_b and (not c_bull) and cb > ab * 0.6 and c3["c"] < mid_a:
            out.append((i, "evening star"))
        # three soldiers / crows
        if all(x["c"] > x["o"] for x in (a, b, c3)) and a["c"] < b["c"] < c3["c"] and \
           all(abs(x["c"] - x["o"]) / max(1e-9, x["h"] - x["l"]) > 0.5 for x in (a, b, c3)):
            out.append((i, "three white soldiers"))
        if all(x["c"] < x["o"] for x in (a, b, c3)) and a["c"] > b["c"] > c3["c"] and \
           all(abs(x["c"] - x["o"]) / max(1e-9, x["h"] - x["l"]) > 0.5 for x in (a, b, c3)):
            out.append((i, "three black crows"))
    return out


# ---------- pivots, horizontal zones, diagonals ----------
def pivots(vals, k=2):
    """fractal pivots on a value list; returns (idx, val, 'H'/'L')."""
    out = []
    for i in range(k, len(vals) - k):
        w = vals[i - k:i + k + 1]
        if vals[i] == max(w) and w.count(vals[i]) == 1:
            out.append((i, vals[i], "H"))
        if vals[i] == min(w) and w.count(vals[i]) == 1:
            out.append((i, vals[i], "L"))
    return out


def hzones(pvts, tol=0.0035):
    """cluster pivot values within tol (fraction) -> zones w/ touch counts."""
    vals = sorted(v for _, v, _ in pvts)
    zones = []
    for v in vals:
        if zones and v <= zones[-1][-1] * (1 + tol):
            zones[-1].append(v)
        else:
            zones.append([v])
    return sorted(([min(z), max(z), len(z)] for z in zones if len(z) >= 2),
                  key=lambda z: -z[2])


def line_value(x1, y1, x2, y2, x):
    m = (y2 - y1) / (x2 - x1)
    return y1 + m * (x - x1)


def structure(pvts):
    """HH/HL/LH/LL sequence from alternating pivots."""
    seq = []
    lastH = lastL = None
    for i, v, t in pvts:
        if t == "H":
            seq.append(("HH" if lastH is not None and v > lastH else
                        "LH" if lastH is not None else "H", i, v))
            lastH = v
        else:
            seq.append(("HL" if lastL is not None and v > lastL else
                        "LL" if lastL is not None else "L", i, v))
            lastL = v
    return seq


def report(name, rows, basis, k=2, tol=0.0035):
    closes = [r["c"] for r in rows]
    print(f"\n{'='*74}\n{name}  (basis: {basis})\n{'='*74}")
    for i, r in enumerate(rows):
        t = trend_before(closes, i)
        cls = classify(r["o"], r["h"], r["l"], r["c"], t)
        rng, body, uw, lw = anatomy(r["o"], r["h"], r["l"], r["c"])
        print(f"  {r['label']:<16} O {r['o']:>9.2f} H {r['h']:>9.2f} L {r['l']:>9.2f} C {r['c']:>9.2f}"
              f" | body {body:7.2f} uw {uw:6.2f} lw {lw:6.2f} -> {cls}")
    mp = multi_patterns(rows)
    if mp:
        print("  -- multi-candle:")
        for i, nm in mp:
            print(f"     {rows[i]['label']}: {nm}")
    hi_p = pivots([r["h"] for r in rows], k)
    lo_p = pivots([r["l"] for r in rows], k)
    pv = sorted([(i, v, "H") for i, v, t in hi_p if t == "H"] +
                [(i, v, "L") for i, v, t in lo_p if t == "L"])
    if pv:
        print("  -- swing structure:", " ".join(f"{t}@{rows[i]['label']}:{v:.2f}" for t, i, v in
              [(x[2], x[0], x[1]) for x in pv]))
        st = structure(pv)
        print("  -- sequence:", " -> ".join(s[0] for s in st))
    z = hzones(pv, tol)
    if z:
        print("  -- horizontal zones (touches):",
              "; ".join(f"{a:.0f}-{b:.0f} ({n})" for a, b, n in z[:6]))
    return pv
