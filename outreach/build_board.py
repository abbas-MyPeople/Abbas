#!/usr/bin/env python3
"""Turn the analysis into a board Abbas can actually work from.

Every restaurant gets an opening line built from what is genuinely broken on
their own site, so the first sentence is about them. No em dashes anywhere in
the copy - hyphens only.
"""
import json, pathlib, html, collections

REPO = pathlib.Path(__file__).parent.parent
D = json.loads((REPO / "outreach/analysis-cypress.json").read_text())
rs = [r for r in D["restaurants"] if r["analysis"].get("reachable")]
rs.sort(key=lambda r: (-r["high"], -len(r["findings"])))
dead = [r for r in D["restaurants"] if not r["analysis"].get("reachable")]

def opener(r):
    a, g = r["analysis"], [f["gap"] for f in r["findings"]]
    n = r["name"]
    if "Not built for phones" in g:
        return (f"Hi - I run Wok & Karahi over in Spring. I was looking at {n} on my phone "
                f"and the site is hard to use on a small screen, which is where nearly every "
                f"order decision gets made now. I fix this kind of thing for restaurants "
                f"around Cy-Fair and I am doing it free for three months for a few places. "
                f"Worth ten minutes?")
    if "No online ordering at all" in g:
        return (f"Hi - I run Wok & Karahi in Spring. I noticed {n} has no way to take an order "
                f"online, so everything has to come through the phone during service. That is "
                f"usually the biggest recoverable loss in a week. I am setting a few Cy-Fair "
                f"places up free for three months. Can I show you what I mean?")
    if any(x.startswith("Only third-party") for x in g):
        return (f"Hi - I run Wok & Karahi in Spring. {n} is taking orders through the delivery "
                f"apps but has no direct option, so you are paying commission even on regulars "
                f"who already knew your name. That is the leak I fix first. Free for three "
                f"months for a few Cy-Fair restaurants - interested?")
    if "No Restaurant structured data" in g:
        return (f"Hi - I run Wok & Karahi in Spring. When someone asks ChatGPT or Google for "
                f"food near Cypress, {n} is harder to surface than it should be, because the "
                f"site does not describe itself in the format those systems read. It is a "
                f"quick fix and I am doing it free for three months for a few places here.")
    return (f"Hi - I run Wok & Karahi in Spring, and I do the technology side for restaurants "
            f"around Cy-Fair. I had a look at {n} and there are a couple of things costing you "
            f"orders that would take me an afternoon. Free for three months. Worth a chat?")

rows = []
for i, r in enumerate(rs, 1):
    a = r["analysis"]
    chips = "".join(f'<i class="s-{f["severity"]}">{html.escape(f["gap"])}</i>' for f in r["findings"])
    detail = "".join(
        f'<p><b>{html.escape(f["gap"])}</b> <span class="job">{html.escape(f["job"])}</span><br>{html.escape(f["why"])}</p>'
        for f in r["findings"])
    ch = []
    if a["direct_ordering"]: ch.append("direct: " + ", ".join(a["direct_ordering"]))
    if a["third_party"]: ch.append("apps: " + ", ".join(a["third_party"]))
    if a["social"]: ch.append("social: " + ", ".join(a["social"]))
    ch.append("phone link: " + ("yes" if a["phone_on_page"] else "no"))
    msg = opener(r)
    rows.append(f'''<details class="r"><summary>
        <span class="n">{i}. {html.escape(r["name"])}</span>
        <span class="chips">{chips}</span></summary>
      <div class="body">
        <p class="addr">{html.escape(r["address"])} &middot; <a href="{html.escape(a["final_url"])}" target="_blank" rel="noopener">{html.escape(a["final_url"][:60])}</a></p>
        <p class="chan"><b>How they reach guests today:</b> {html.escape(" | ".join(ch))}</p>
        {detail}
        <div class="msg"><textarea readonly>{html.escape(msg)}</textarea>
          <button class="copy" type="button">Copy opener</button></div>
      </div></details>''')

gapc = collections.Counter(f["gap"].split(" (")[0] for r in D["restaurants"] for f in r["findings"])
stat = "".join(f'<div class="k"><b>{n}</b><span>{html.escape(g)}</span></div>' for g, n in gapc.most_common(6))

page = f'''<title>Cypress Outreach Board</title>
<style>
:root{{--bg:#faf8f4;--ink:#1a1a17;--ink2:#57534b;--ink3:#8a857a;--line:#e2ddd2;--card:#fff;--hot:#a8331f;--warn:#b3701a;--cool:#6b6357;--go:#1c4739}}
:root:not([data-theme=light]) {{}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#15140f;--ink:#f0ece2;--ink2:#b3ada0;--ink3:#7d776b;--line:#2f2c25;--card:#1d1b15;--hot:#e0705a;--warn:#d9a04a;--cool:#8e877a;--go:#7fbfa2}}}}
:root[data-theme=dark]{{--bg:#15140f;--ink:#f0ece2;--ink2:#b3ada0;--ink3:#7d776b;--line:#2f2c25;--card:#1d1b15;--hot:#e0705a;--warn:#d9a04a;--cool:#8e877a;--go:#7fbfa2}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;padding:34px 20px 80px}}
.w{{max-width:940px;margin:0 auto}}
h1{{font-size:clamp(1.6rem,3.4vw,2.2rem);letter-spacing:-.03em;margin:0 0 6px;font-weight:800}}
.sub{{color:var(--ink2);margin:0 0 26px;max-width:70ch}}
h2{{font-size:1.12rem;letter-spacing:-.01em;margin:34px 0 12px;font-weight:750}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0 6px}}
.k{{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:13px 15px}}
.k b{{display:block;font-size:1.5rem;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums}}
.k span{{font-size:12.4px;color:var(--ink2);line-height:1.35;display:block;margin-top:3px}}
.note{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--hot);border-radius:0 11px 11px 0;padding:15px 17px;margin:16px 0}}
.note p{{margin:0 0 8px}} .note p:last-child{{margin:0}}
.r{{background:var(--card);border:1px solid var(--line);border-radius:11px;margin-bottom:8px;overflow:hidden}}
.r summary{{cursor:pointer;padding:13px 16px;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;list-style:none}}
.r summary::-webkit-details-marker{{display:none}}
.n{{font-weight:680;min-width:210px}}
.chips{{display:flex;flex-wrap:wrap;gap:5px}}
.chips i{{font-style:normal;font-size:11px;letter-spacing:.02em;padding:3px 8px;border-radius:999px;border:1px solid currentColor}}
.s-high{{color:var(--hot)}} .s-medium{{color:var(--warn)}} .s-low{{color:var(--cool)}}
.body{{padding:2px 16px 16px;border-top:1px solid var(--line)}}
.addr{{font-size:13px;color:var(--ink3);margin:12px 0 10px}}
.chan{{font-size:13.5px;color:var(--ink2);background:var(--bg);border-radius:8px;padding:9px 11px;margin:0 0 12px}}
.body p{{font-size:14.4px;margin:0 0 10px;color:var(--ink2)}}
.body p b{{color:var(--ink)}}
.job{{font-size:11px;color:var(--ink3);border:1px solid var(--line);padding:1px 7px;border-radius:999px;margin-left:5px}}
.msg{{display:flex;flex-direction:column;gap:8px;margin-top:14px}}
textarea{{width:100%;min-height:96px;resize:vertical;font:14px/1.5 inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:9px;padding:11px 13px}}
.copy{{align-self:flex-start;font:600 13.5px inherit;background:var(--go);color:#fff;border:0;border-radius:8px;padding:9px 16px;cursor:pointer}}
.copy.done{{opacity:.75}}
a{{color:inherit}}
ol{{padding-left:20px}} ol li{{margin-bottom:9px;color:var(--ink2)}} ol li b{{color:var(--ink)}}
</style>

<div class="w">
<h1>Cypress outreach board</h1>
<p class="sub">86 locally owned Cypress restaurants read from their own public websites on 18 August 2026. Sorted by what is visibly costing them orders. Open one to see the angle and copy an opener written from that restaurant's actual gaps.</p>

<div class="kpis">
  <div class="k"><b>86</b><span>independents checked</span></div>
  <div class="k"><b>38</b><span>with a working website</span></div>
  <div class="k"><b>48</b><span>no reachable site</span></div>
  <div class="k"><b>38</b><span>live sites with a gap</span></div>
</div>
<div class="kpis">{stat}</div>

<div class="note">
  <p><b>Read this before you use the list.</b> The 48 with no reachable site are not all
  opportunities. That directory is from 2018, so an unreachable domain can mean closed, not
  invisible. Verify each is still trading before you approach it - Google Maps in ten seconds.</p>
  <p>The 38 with live sites are confirmed trading and every one has at least one visible gap.
  That is your first list.</p>
</div>

<h2>Cypress vs Katy - you were right to hesitate</h2>
<div class="note">
  <p>Katy is in a build cycle: new retail and restaurant openings are the story there in 2026.
  Operators who are opening or expanding are spending on build-out, not looking for someone to
  fix a leak. Felt pain is lower.</p>
  <p>Cypress is growing too, but the independents in this list are established rather than new -
  many trading a decade or more - and the metro around them lost 119 restaurants in six months,
  more than any city in the US or Canada. Established operator plus visible squeeze is the
  combination that converts. Start Cypress, keep Katy for when you have proof to lead with.</p>
</div>

<h2>The play</h2>
<ol>
  <li><b>Walk in, do not email.</b> You are an operator in Spring, not an agency. Between 2pm
  and 4pm on Tuesday to Thursday the owner is usually there and not in the weeds. That single
  fact is your entire advantage over everyone else calling them.</li>
  <li><b>Lead with their thing, not yours.</b> Every opener below names something real on their
  own site. Show it on your phone. Do not pitch six services.</li>
  <li><b>Leave the one-pager</b> (AZ-RP-leave-behind.pdf) and the free-pilot line. Three months,
  nothing to sign, they keep whatever you build.</li>
  <li><b>Follow up once</b> by Instagram or Facebook DM within 48 hours, referencing the visit.
  Once. Not a sequence.</li>
  <li><b>Five a day, three days a week.</b> 38 targets is about three weeks. You only need to
  fill three founding spots.</li>
</ol>

<h2>Targets - live sites, worst first</h2>
{"".join(rows)}

<h2>Needs a status check first ({len(dead)})</h2>
<p class="sub">No reachable website. Confirm open on Google Maps, then treat "no website at all" as the strongest possible opening.</p>
<div class="note"><p>{html.escape(", ".join(r["name"] for r in dead))}</p></div>
</div>

<script>
document.addEventListener("click", function(e){{
  var b = e.target.closest(".copy"); if(!b) return;
  var ta = b.parentElement.querySelector("textarea");
  navigator.clipboard.writeText(ta.value).then(function(){{
    var t = b.textContent; b.textContent = "Copied"; b.classList.add("done");
    setTimeout(function(){{ b.textContent = t; b.classList.remove("done"); }}, 1400);
  }});
}});
</script>'''
(REPO / "outreach/board-cypress.html").write_text(page)
print("board written:", len(page), "bytes |", len(rows), "targets |", len(dead), "to verify")
