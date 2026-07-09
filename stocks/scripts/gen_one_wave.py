#!/usr/bin/env python3
"""One Wave — final version: the candle reading, written for a reader with zero context."""
from gen_one_wave_data import (rows_m, rows_w, rows_d, rows_h, rows_15, svg_m, svg_w, svg_d,
                      svg_h, svg_15, ledger, up_now, up_jul8, dn_now, lo_now,
                      CLOSE_TODAY, SCRATCH, L_ITEMS)

html = f"""<title>One Wave — the S&P 500 at every zoom level</title>
<style>
:root {{
  --ground:#f7f6f2; --surface:#fffdf9; --ink:#191714; --ink2:#524e46; --mut:#8b867c;
  --line:#e6e2d8; --gold:#a06b10; --gold-mark:#d99a2b; --up:#0e8f63; --up-mark:#1baf7a;
  --dn:#c23736; --dn-mark:#e34948; --blue:#2a78d6;
}}
@media (prefers-color-scheme: dark) {{ :root {{
  --ground:#101418; --surface:#171d23; --ink:#f2efe8; --ink2:#b9b4a8; --mut:#7d7f7a;
  --line:#262d34; --gold:#e8b04b; --gold-mark:#c98500; --up:#3ec996; --up-mark:#1baf7a;
  --dn:#ef8484; --dn-mark:#e66767; --blue:#3987e5;
}} }}
:root[data-theme="dark"] {{
  --ground:#101418; --surface:#171d23; --ink:#f2efe8; --ink2:#b9b4a8; --mut:#7d7f7a;
  --line:#262d34; --gold:#e8b04b; --gold-mark:#c98500; --up:#3ec996; --up-mark:#1baf7a;
  --dn:#ef8484; --dn-mark:#e66767; --blue:#3987e5;
}}
:root[data-theme="light"] {{
  --ground:#f7f6f2; --surface:#fffdf9; --ink:#191714; --ink2:#524e46; --mut:#8b867c;
  --line:#e6e2d8; --gold:#a06b10; --gold-mark:#d99a2b; --up:#0e8f63; --up-mark:#1baf7a;
  --dn:#c23736; --dn-mark:#e34948; --blue:#2a78d6;
}}
* {{ box-sizing:border-box }}
body {{ background:var(--ground); color:var(--ink); margin:0; font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif }}
.wrap {{ max-width:47rem; margin:0 auto; padding:0 1.25rem 6rem }}
h1,h2 {{ font-family:"Iowan Old Style",Georgia,serif; font-weight:600; text-wrap:balance }}
h1 {{ font-size:clamp(2rem,5.5vw,3.1rem); line-height:1.12; margin:.6rem 0 1rem }}
h2 {{ font-size:1.55rem; line-height:1.25; margin:0 0 .7rem }}
p {{ max-width:64ch; color:var(--ink2); margin:0 0 1.05rem }}
p strong,li strong {{ color:var(--ink) }}
.eyebrow {{ font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; color:var(--mut); margin:4rem 0 .4rem }}
.lede {{ font-size:1.12rem }}
.takeaway {{ background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--gold-mark);
  border-radius:10px; padding:.85rem 1rem; margin:0 0 1.2rem; font-size:.98rem; color:var(--ink2) }}
.takeaway b {{ color:var(--ink) }}
.chip {{ display:inline-block; font:600 .68rem/1 system-ui; letter-spacing:.12em; color:var(--gold);
  border:1px solid color-mix(in oklab, var(--gold) 45%, transparent); border-radius:999px;
  padding:.45em .9em; margin-bottom:.7rem; text-transform:uppercase }}
.card {{ background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:1.05rem 1.1rem; margin:1.3rem 0 }}
figure {{ margin:0 }} figcaption,.cap {{ font-size:.8rem; color:var(--mut); margin-top:.5rem; line-height:1.5 }}
svg {{ width:100%; height:auto; display:block }} svg text {{ font:10.5px system-ui; fill:var(--mut) }}
.cu line {{ stroke:var(--up-mark); stroke-width:1.5 }} .cu rect {{ fill:var(--up-mark) }}
.cd line {{ stroke:var(--dn-mark); stroke-width:1.5 }} .cd rect {{ fill:var(--dn-mark) }}
.live rect {{ opacity:.55; stroke:var(--gold-mark); stroke-width:1.5; stroke-dasharray:3 3 }}
.pat {{ fill:var(--gold-mark) }}
.lvl {{ stroke-dasharray:5 4; stroke-width:1.1 }} .lvl.r {{ stroke:var(--dn-mark); opacity:.7 }} .lvl.s {{ stroke:var(--up-mark); opacity:.7 }}
.diag {{ stroke-width:1.4; stroke-dasharray:7 4 }} .diag.r {{ stroke:var(--dn-mark) }} .diag.s {{ stroke:var(--up-mark) }}
.lvlt {{ font-size:9.5px }} .lvlt.r {{ fill:var(--dn) }} .lvlt.s {{ fill:var(--up) }}
.tbl {{ overflow-x:auto; margin:.9rem 0 }}
table {{ border-collapse:collapse; width:100%; font-size:.82rem; font-variant-numeric:tabular-nums }}
th,td {{ text-align:right; padding:.4em .6em; border-bottom:1px solid var(--line); white-space:nowrap; vertical-align:top }}
th:first-child,td:first-child,th:last-child,td:last-child {{ text-align:left }}
th {{ color:var(--mut); font-weight:600; font-size:.7rem; letter-spacing:.08em; text-transform:uppercase }}
td.up {{ color:var(--up) }} td.dn {{ color:var(--dn) }}
.patline {{ color:var(--gold); font-size:.76rem; white-space:normal; max-width:26ch }}
.levels {{ list-style:none; padding:0; margin:1rem 0; font-variant-numeric:tabular-nums }}
.levels li {{ display:flex; gap:.9rem; align-items:baseline; padding:.55rem 0; border-bottom:1px dashed var(--line); font-size:.92rem; color:var(--ink2) }}
.levels .px {{ font-weight:700; min-width:10.5ch; font-family:ui-monospace,Menlo,monospace; font-size:.86rem }}
.levels .r {{ color:var(--dn) }} .levels .s {{ color:var(--up) }}
.anatomy {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:.9rem; margin:1.3rem 0 }}
.anx {{ background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:.9rem; font-size:.8rem; color:var(--mut); line-height:1.5 }}
.anx b {{ color:var(--ink); display:block; font-size:.86rem; margin-bottom:.2rem }}
.inside {{ font-family:"Iowan Old Style",Georgia,serif; font-style:italic; font-size:1.05rem;
  line-height:1.7; color:var(--ink); max-width:60ch; margin:1.6rem 0 1.2rem; padding-left:1.1rem;
  border-left:2px solid var(--gold-mark) }}
.inside small {{ display:block; font:600 .64rem/1 system-ui; font-style:normal; letter-spacing:.14em;
  text-transform:uppercase; color:var(--gold); margin-bottom:.5rem }}
.pred {{ border-left:3px solid var(--gold-mark); padding:.15rem 0 .15rem 1rem; margin:1.2rem 0 }}
.pred h3 {{ margin:.2rem 0 .3rem; font-size:1.02rem }}
.pred p {{ margin-bottom:.4rem; font-size:.95rem }}
.inv {{ font-size:.8rem; color:var(--mut) }}
hr {{ border:0; border-top:1px solid var(--line); margin:3rem 0 }}
.foot {{ font-size:.8rem; color:var(--mut); line-height:1.7 }}
@media (prefers-reduced-motion: no-preference) {{
  .reveal {{ opacity:0; transform:translateY(10px); transition:opacity .7s ease, transform .7s ease }}
  .reveal.in {{ opacity:1; transform:none }}
}}
</style>

<div class="wrap">

<header class="hero">
<div class="eyebrow">S&amp;P 500 · Thursday, July 9, 2026 · closed at 7,543.64</div>
<h1>One market, five zoom levels, one story.</h1>
<p class="lede">The S&amp;P 500 is the index that tracks America's 500 largest companies — for most
people, it's what their retirement savings actually do all day. This page reads it the way you'd
examine anything carefully: <strong>from far away, then closer, then closer still</strong> — by month,
by week, by day, by hour, by quarter-hour — using only verified price data. You need no finance
background. There is exactly one concept to learn, and it takes thirty seconds:</p>
<p><strong>A candle.</strong> Take any stretch of time — a month, a day, fifteen minutes — and record four
numbers: where the price <strong>started</strong>, the <strong>highest</strong> it got, the
<strong>lowest</strong> it got, and where it <strong>ended</strong>. Drawn as a bar, the thick part (start→end)
is the <em>body</em>; the thin lines above and below are the <em>wicks</em> — the extremes that didn't hold.
Green: ended higher. Red: ended lower. That's the whole alphabet. The shapes have old names:</p>
<div class="anatomy">
<div class="anx"><b>Solid bar, no wicks</b> one side won all period long, no pushback. (Named a <i>marubozu</i>.)</div>
<div class="anx"><b>Tiny body, long wicks</b> a fight that ended where it started — a stalemate. (A <i>doji</i> or <i>spinning top</i>.)</div>
<div class="anx"><b>Long tail below</b> price plunged and was bought back up. At a bottom, a floor forming (a <i>hammer</i>); at a record high, a warning (a <i>hanging man</i>).</div>
<div class="anx"><b>Multi-bar shapes</b> one bar swallowing the previous one (<i>engulfing</i>), three drives in a row (<i>soldiers</i> / <i>crows</i>), a pause-then-reverse (<i>star</i>).</div>
</div>
<p>Every shape named on this page was assigned by <strong>measurement</strong> — the ratio of body to wicks —
by a small program, not by anyone's opinion. Hover any candle to see its four numbers and its computed read.
One honesty rule governs everything here, borrowed from a meditation discipline: <strong>report only what
was actually observed; where data couldn't be obtained, say so — never fill a gap with imagination.</strong>
Every gap on this page is labeled.</p>
</header>

<hr>

<section>
<div class="chip">Zoom 1 · By month — the last 13 months</div>
<h2>A climb, a crash, a violent recovery — and now a warning being tested.</h2>
<div class="takeaway"><b>Plain version:</b> the market climbed steadily through 2025, crashed 9% in March 2026
(an inflation scare plus a new Middle-East war), then recovered so fast that April became its best month since
2020 and June touched an all-time high of 7,609.78. But June itself is the warning: mid-month the market fell
hard — almost 350 points — and had to be pulled back up. July so far is trading entirely <em>inside</em> June's
range. The biggest picture is genuinely undecided.</div>
<figure class="card"><svg viewBox="0 0 720 254">{svg_m}</svg>
<figcaption>Each candle = one month. Wicks show the highest and lowest <i>daily close</i> in that month (measured
from the Federal Reserve's official series). ‡ = July, still in progress. Gold dots mark computed multi-candle patterns.</figcaption></figure>
{ledger(rows_m)}
<p><strong>What to notice in the table:</strong> April has a 634-point body and <em>zero</em> wick on either
end — a month where buyers never once gave ground, the most one-sided candle in the series. And June has a
small body with a 232-point tail below it — the "hanging man": at a record high, price fell far and needed
rescuing. The rescue worked, but a rescue was needed. That's the first crack after two months of total control.</p>
<div class="inside"><small>The same thing, seen from inside</small>
I climbed for five months without effort. In November I fell hard once, in the middle of the month,
and was caught before anyone watching month-ends could notice. In January I touched 7,000 for one day
and was pushed out. In March, four weeks took back everything the year had given. In April it all
returned, and more — thirty days without a single push-back. In June I stood higher than I had ever
stood, fell 343 points, and was caught again. I ended June looking calm. I was not calm.
July: I have not yet left June's shadow.</div>
<p><strong>The month-scale question is exactly two numbers.</strong> A close above <strong>7,609.78</strong>
cancels June's warning. A fall below <strong>7,266.99</strong> (the tip of June's tail) confirms it. Everything
in the rest of this page is the market deciding between those two numbers.</p>
</section>

<hr>

<section>
<div class="chip">Zoom 2 · By week — the last 12 weeks</div>
<h2>Nine straight winning weeks, one knockdown, then a five-week squeeze.</h2>
<div class="takeaway"><b>Plain version:</b> through April and May the market rose nine weeks in a row — the
longest streak in three years. In early June one bad day (a too-hot jobs report) erased an entire record week.
Since then it's been a narrowing tug-of-war: each rally peaks a little lower than 7,609, each dip bottoms a
little higher than 7,267. Squeezes like this usually end with a decisive move within a few weeks — and this
week closed right at the squeeze's upper edge.</div>
<figure class="card"><svg viewBox="0 0 720 254">{svg_w}</svg>
<figcaption>Each candle = one week. The two dashed lines are drawn through the actual highs (falling line) and
actual lows (rising line) of the squeeze — not sketched, computed. ‡ = this week, in progress until Friday's close.</figcaption></figure>
{ledger(rows_w)}
<div class="inside"><small>The same thing, seen from inside</small>
Nine weeks I only rose, and by the eighth the rising itself had become the point. The tenth week I
gave back a record in one day. Since then, each time I reach up I stop a little lower; each time I
fall I stop a little higher. The room I move in shrinks every week. This week I dipped, took all of
it back, and ended at the top edge of what room remains.</div>
<p><strong>The week-scale story in three candles:</strong> mid-May printed the first rejection — price reached
7,501, was pushed all the way back, and the week closed where it started (an 88-point wick above a 4-point
body). Early June, the knockdown: one week's candle completely swallowed the record week before it. Mid-June,
the floor: a plunge to 7,267 bought back by Friday — a 139-point tail. Rejection above, floor below: that's
the squeeze. <strong>This week closed at 7,543.64 — slightly above the falling line (≈{dn_now:,.0f})</strong>.
If Friday holds that, it's the first weekly escape from the squeeze, upward.</p>
</section>

<hr>

<section>
<div class="chip">Zoom 3 · By day — the last 16 sessions</div>
<h2>Sellers ran out of fuel, buyers took over, and one price kept catching the market.</h2>
<div class="takeaway"><b>Plain version:</b> late June was five straight down days — but look at the size of
each fall: 107 points, then 7, then 0.7, then 3.5. The selling literally decayed to nothing. Then five straight
up days. Then this week's test: on July 8 the market dropped hard in the morning and recovered by the close —
and it stopped falling at the same area where it had already found rest three times: <b>7,483.23 (Jul 1),
7,483.24 (Jul 2), 7,482.71 (Jul 8)</b>. Three separate days, the same price to within half a point. Prices
have memory, because millions of people remember them.</div>
<figure class="card"><svg viewBox="0 0 720 254">{svg_d}</svg>
<figcaption>Each candle = one trading day. Bodies (start→end) are exact for all days; the thin wicks are real
recorded extremes only for Jul 7–9, captured live by this project's own data pipeline. † = today. The rising
dashed line connects the March 30 low to the June 26 low — the "walking line" of the whole recovery.</figcaption></figure>
{ledger(rows_d)}
<div class="inside"><small>The same thing, seen from inside</small>
Five days I fell, each day with less force — 107 points, then 7, then less than one. The falling
ended not because buying arrived but because the selling was finished. Then five days up. On July 8
I was thrown down at the open and I stopped at 7,483 — not because a line exists there; nothing
exists there. It is simply where, three times now, the wish to sell ran out. Today I opened above
it, touched it once, and left.</div>
<p><strong>One more thing about July 8:</strong> draw a straight line under the recovery — from the March 30
bottom (6,343.72) through the June 26 dip (7,354.02). The market has been walking up that line for three months,
about 17 points a day. On July 8, the morning panic dropped price <em>through</em> the line (down to 7,423) —
and by the close it was back above it, resting on the 7,483 shelf. A break that fails to break is the strongest
kind of test a line can pass. Today confirmed it: up 0.81% to 7,543.64.</p>
</section>

<hr>

<section>
<div class="chip">Zoom 4 · By hour and quarter-hour — July 8 and 9</div>
<h2>Watch fear arrive, peak, and dissolve — in real time.</h2>
<div class="takeaway"><b>Plain version:</b> on July 8, panic peaked at 12:15 PM — the market's "fear gauge"
(the VIX) hit its high of 18.4 at the exact minute prices hit their low. Then four calm hours of recovery.
Overnight, the U.S. actually struck Iran and the ceasefire was declared dead — and the next morning the market
flinched for about fifteen minutes, then climbed all day. The same war caused a 9% crash in March and a 3%
wobble in June. Now: a 45-minute dip. Repeated shocks lose their power — whether that's wisdom or complacency
is the one question this page can't answer.</div>
<figure class="card"><svg viewBox="0 0 720 214">{svg_h}</svg>
<figcaption>Each candle = one hour (prices here are for SPY, the fund that tracks the index — multiply by ~10).
Jul 8: a long-tailed first hour, then recovery. Jul 9: five green hours in a row, pausing only at the day's high.</figcaption></figure>
{ledger(rows_h, " (SPY)")}
<figure class="card"><svg viewBox="0 0 720 214">{svg_15}</svg>
<figcaption>Each candle = 15 minutes, both sessions. On Jul 9, bar 3 is the war-headline flinch — answered
within fifteen minutes by a bigger green bar, and no new low for the rest of the day.</figcaption></figure>
<div class="inside"><small>The same thing, seen from inside</small>
At 12:15 on July 8 the fear was largest at the exact minute the price was lowest. That is not a
coincidence — it is one event, measured twice. The next morning the war came back and I fell for
fifteen minutes. In March the same news held me down for a month; in June, for a week. What repeats
is felt less. Whether that is understanding or numbness cannot be seen from inside the moment,
so I will not claim to know.</div>
<p><strong>And here is the discovery that makes the whole zoom exercise worth it.</strong> Go back to June's
monthly candle: its long lower tail is a single line. Zoom in, and that tail <em>is</em> the mid-June week with
its 139-point plunge-and-rescue. Zoom into that week and it's the run of shrinking red days followed by the
recovery. Zoom into July 8's daily tail and it's the hourly panic-and-recovery pictured above, which is itself
the 15-minute bars. <strong>A "moment" at one zoom level is a complete drama at the next.</strong> Big candles
aren't summaries of small ones — they <em>are</em> the small ones, seen from farther away. That's why the same
few prices keep mattering at every level: the month, the week, the day and the hour are one event, at four
magnifications.</p>
</section>

<hr>

<section>
<div class="chip">The map · every price that matters</div>
<h2>Nine numbers, and why each one earned its place.</h2>
<ul class="levels">{L_ITEMS}</ul>
<p><strong>The single most loaded spot on the map:</strong> the rising line from the March low now passes
through ≈{up_now:,.0f} — almost exactly the 7,483 shelf where three days closed. The market's trend and the
market's memory currently point at the same price. Below it there's little until 7,354; above it, the falling
line (crossed today), then 7,580, then the 7,609.78 record that decides the whole monthly picture.</p>
</section>

<hr>

<section>
<div class="chip">What happens next · with the prices that would prove it wrong</div>
<h2>Expectations, not prophecies. Each one carries its own "I was wrong" number.</h2>
<div class="inside"><small>Before the forecasts, the bare truth</small>
A level is not a wall; it is a memory of where intentions ran out. A pattern is not a promise; it is
the shape a crowd makes when it does what crowds have done before. What follows is not what I will
do. It is what bodies like mine have usually done from here — stated with the price at which
that stops being true.</div>
<p>Candle patterns are tendencies — they describe what usually followed this shape, not what must. The honest
way to state them is with the exact price at which each read fails:</p>
<div class="pred"><h3>Hours ahead</h3>
<p>Today ended with an unbroken ladder of higher lows, pausing at the day's high. Ladders like that more often
continue than reverse.</p>
<p class="inv">Wrong if: price breaks below ≈7,533 (the last rung). Genuinely bearish only below ≈7,486.</p></div>
<div class="pred"><h3>Days ahead</h3>
<p>The sequence — sellers decaying to zero, five up days, a hard test that held, today's confirmation above the
falling line — points to a run at 7,580 first, then the 7,609.78 record itself, likely within days.</p>
<p class="inv">Wrong if: any daily close back below 7,483 — that breaks both the shelf and, within a day or two, the rising line.</p></div>
<div class="pred"><h3>Weeks ahead</h3>
<p>The squeeze is 343 points tall (7,609.78 top, 7,266.99 bottom). If the market escapes upward and holds, that
height projects a move toward roughly <strong>7,900</strong>; a downward escape projects toward roughly
<strong>7,210</strong>. The recent candles — floor held below, rejection weakening above, this week closing at
the upper edge — lean upward. The squeeze itself is neutral until a Friday close leaves it.</p>
<p class="inv">Up-case wrong if: a week closes below 7,354. Everything bearish confirms below 7,266.99.</p></div>
<div class="pred"><h3>Months ahead</h3>
<p>June's hanging man remains the standing warning at the top; July, so far trading inside June's range, is the
market deciding whether to believe it. Above 7,609.78 the warning cancels and the spring trend resumes. Below
7,266.99 it confirms — and because big moves are made of small ones, that confirmation would show up
<em>first</em> as failures at the daily and hourly levels, at these same prices. The small scale always moves first.</p>
<p class="inv">Between those two numbers there is no month-scale signal. Anyone claiming one is telling a story, not reading a chart.</p></div>
</section>

<hr>

<section>
<div class="chip">Sources &amp; honesty</div>
<h2>Where every number came from, and what's missing.</h2>
<p><strong>Sources:</strong> daily closing prices from the Federal Reserve's public FRED database (2,608
sessions, ten years); today's official close (7,543.64) cross-checked against financial press; the July 7–9
intraday candles recorded live, before and during writing, by a small automated pipeline in this project that
snapshots the market every few minutes. Pattern names were assigned by a program using fixed body/wick ratio
rules; the program and the data are saved with this page so any read can be re-checked.</p>
<p><strong>Known limits, stated plainly:</strong> monthly and weekly wicks are built from daily closes, so the
true intraday extremes are slightly larger than drawn. Daily wicks are real only for July 7–9. The hourly and
15-minute candles are built from 5-minute samples, so their extremes are slightly understated, and the first
hour of July 8 wasn't captured. One-minute data could not be obtained at all and is therefore simply absent.
Nothing missing was estimated or invented.</p>
<p class="foot">S&amp;P 500, July 9, 2026: closed 7,543.64, up 0.81%. This is a reading of price structure, not
investment advice — which is why every expectation above is published together with the price that kills it.</p>
</section>

</div>
<script>
(function(){{
  if (matchMedia('(prefers-reduced-motion: no-preference)').matches) {{
    const els = document.querySelectorAll('section, header');
    els.forEach(e => e.classList.add('reveal'));
    const io = new IntersectionObserver(en => en.forEach(x => {{
      if (x.isIntersecting) {{ x.target.classList.add('in'); io.unobserve(x.target); }}
    }}), {{ threshold: .06 }});
    els.forEach(e => io.observe(e));
  }}
}})();
</script>
"""
open(f"{SCRATCH}/one-wave.html", "w").write(html)
print("written", len(html))
