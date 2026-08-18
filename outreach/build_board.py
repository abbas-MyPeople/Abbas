#!/usr/bin/env python3
"""Board built from the dossiers. Evidence tier is visible on every claim."""
import json, pathlib, html, collections

REPO = pathlib.Path(__file__).parent.parent
ds = [json.loads(p.read_text()) for p in sorted((REPO/"outreach/dossiers").glob("*.json"))]
E = lambda s: html.escape(str(s), quote=False)
V = lambda f: (f or {}).get("value")

real = [d for d in ds if V(d["site"]["status"]) in ("STATIC", "STATIC_AFTER_RENDER")]
check = [d for d in ds if V(d["site"]["status"]) not in ("STATIC", "STATIC_AFTER_RENDER")]

def score(d):
    n = 0
    if not V(d["discovery"]["restaurant_schema"]): n += 2
    if V(d["ordering"]["channel_state"]) == "none online": n += 3
    if V(d["ordering"]["channel_state"]) == "third-party only": n += 3
    if V(d["catering"]["state"]) in ("ABSENT", "MENTIONED_ONLY"): n += 2
    if not V(d["discovery"]["mobile_viewport"]): n += 3
    if not V(d["discovery"]["tel_link"]): n += 1
    if V(d["discovery"]["menu_is_pdf"]): n += 1
    if V(d["discovery"].get("ai_crawlers_blocked")): n += 2
    return n
real.sort(key=score, reverse=True)

CAT = {"ABSENT":"no catering anywhere","MENTIONED_ONLY":"named, no way to order it",
       "PAGE_NO_PRICING":"page exists, no minimums or pricing","OPERATIONAL":"real order path"}

def tier(f):
    t = (f or {}).get("tier","")
    return f'<em class="t t-{t.lower()}">{t}</em>' if t else ""

def card(d, i):
    r, s, dis, o, c, m = d["restaurant"], d["site"], d["discovery"], d["ordering"], d["catering"], d.get("menu",{})
    chips = []
    if V(o["channel_state"]) in ("none online","third-party only"): chips.append(("hot", V(o["channel_state"])))
    if not V(dis["restaurant_schema"]): chips.append(("hot","invisible to AI answers"))
    if not V(dis["mobile_viewport"]): chips.append(("hot","not built for phones"))
    if V(c["state"]) in ("ABSENT","MENTIONED_ONLY"): chips.append(("warn", CAT[V(c["state"])]))
    if V(dis["menu_is_pdf"]): chips.append(("warn","menu is a PDF"))
    if not V(dis["tel_link"]): chips.append(("cool","no tap-to-call"))
    if V(dis.get("ai_crawlers_blocked")): chips.append(("hot","blocks AI crawlers"))
    chipsh = "".join(f'<i class="c-{k}">{E(v)}</i>' for k,v in chips) or '<i class="c-ok">nothing obvious</i>'

    price = ""
    if V(m.get("price_median")):
        price = (f'<tr><td>Menu prices</td><td>{V(m["prices_found"])} parsed, '
                 f'${V(m["price_min"]):.2f} to ${V(m["price_max"]):.2f}, median '
                 f'${V(m["price_median"]):.2f}, {E(V(m["pricing_style"]))} pricing '
                 f'{tier(m["pricing_style"])}</td></tr>')
    gifts = "".join(f"<li>{E(g)}</li>" for g in d.get("first_gift",[]))
    return f'''<details class="r"><summary><span class="n">{i}. {E(r["name"])}</span>
      <span class="chips">{chipsh}</span></summary><div class="b">
      <p class="a">{E(r["address"])} &middot; <a href="{E(V(s["final_url"]))}" target="_blank" rel="noopener">{E(str(V(s["final_url"]))[:58])}</a></p>
      <table>
        <tr><td>Site</td><td>{E(V(s["status"]))}, {V(s["words"])} words across {V(s["pages_crawled"])} pages
            {"<b>(only readable after rendering)</b>" if V(s["rendered_with_browser"]) else ""} {tier(s["status"])}</td></tr>
        <tr><td>Ordering</td><td>{E(V(o["channel_state"]))}{(" &middot; " + ", ".join(V(o["direct_platforms"]))) if V(o["direct_platforms"]) else ""}{(" &middot; apps: " + ", ".join(V(o["third_party"]))) if V(o["third_party"]) else ""} {tier(o["channel_state"])}</td></tr>
        <tr><td>Catering</td><td>{E(CAT.get(V(c["state"]),V(c["state"])))} {tier(c["state"])}<br><span class="w">{E(V(c["state"]) and c["state"].get("note",""))}</span></td></tr>
        <tr><td>AI readable</td><td>Restaurant schema: <b>{"yes" if V(dis["restaurant_schema"]) else "no"}</b>
            &middot; menu as PDF: {"yes" if V(dis["menu_is_pdf"]) else "no"}
            &middot; crawlers blocked: {E(V(dis.get("ai_crawlers_blocked")) or "none")} {tier(dis["restaurant_schema"])}</td></tr>
        {price}
      </table>
      <p class="g"><b>First gift</b> - what we can do before they owe us anything, no access needed:</p>
      <ul>{gifts}</ul></div></details>'''

cards = "".join(card(d,i) for i,d in enumerate(real,1))
noschema = sum(1 for d in real if not V(d["discovery"]["restaurant_schema"]))
noorder  = sum(1 for d in real if V(d["ordering"]["channel_state"])=="none online")
nocater  = sum(1 for d in real if V(d["catering"]["state"]) in ("ABSENT","MENTIONED_ONLY"))
byst = collections.Counter(V(d["site"]["status"]) for d in ds)

page = f'''<title>Cypress Dossiers</title>
<style>
:root{{--bg:#faf8f4;--ink:#1a1a17;--ink2:#4f4b43;--ink3:#8a857a;--line:#e4dfd4;--card:#fff;--hot:#a8331f;--warn:#b3701a;--cool:#6f6859;--ok:#2f6b4f;--go:#1c4739;--soft:#f2eee5}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#14130f;--ink:#f0ece2;--ink2:#b6b0a3;--ink3:#7c766a;--line:#2e2b24;--card:#1c1a15;--hot:#e0705a;--warn:#d9a04a;--cool:#8d8578;--ok:#7fbfa2;--go:#7fbfa2;--soft:#201e18}}}}
:root[data-theme=dark]{{--bg:#14130f;--ink:#f0ece2;--ink2:#b6b0a3;--ink3:#7c766a;--line:#2e2b24;--card:#1c1a15;--hot:#e0705a;--warn:#d9a04a;--cool:#8d8578;--ok:#7fbfa2;--go:#7fbfa2;--soft:#201e18}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);padding:36px 20px 90px;font:16px/1.55 ui-sans-serif,system-ui,-apple-system,sans-serif}}
.w{{max-width:900px;margin:0 auto}}
h1{{font-size:clamp(1.6rem,3.5vw,2.2rem);font-weight:820;letter-spacing:-.03em;margin:0 0 6px}}
.sub{{color:var(--ink2);margin:0 0 24px;max-width:72ch}}
h2{{font-size:1.1rem;font-weight:750;margin:34px 0 12px}}
.k{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:16px 0}}
.k div{{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:12px 14px}}
.k b{{display:block;font-size:1.45rem;font-weight:800;letter-spacing:-.03em;font-variant-numeric:tabular-nums}}
.k span{{font-size:12.3px;color:var(--ink2);display:block;margin-top:3px;line-height:1.35}}
.note{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--hot);border-radius:0 11px 11px 0;padding:14px 16px;margin:16px 0;color:var(--ink2)}}
.note b{{color:var(--ink)}}
.r{{background:var(--card);border:1px solid var(--line);border-radius:11px;margin-bottom:8px}}
.r summary{{cursor:pointer;padding:13px 15px;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;list-style:none}}
.r summary::-webkit-details-marker{{display:none}}
.n{{font-weight:680;min-width:205px}}
.chips{{display:flex;flex-wrap:wrap;gap:5px}}
.chips i{{font-style:normal;font-size:11px;padding:3px 8px;border-radius:999px;border:1px solid currentColor}}
.c-hot{{color:var(--hot)}} .c-warn{{color:var(--warn)}} .c-cool{{color:var(--cool)}} .c-ok{{color:var(--ok)}}
.b{{padding:4px 15px 16px;border-top:1px solid var(--line)}}
.a{{font-size:12.6px;color:var(--ink3);margin:11px 0 10px}}
table{{width:100%;border-collapse:collapse;font-size:14px;margin-bottom:12px}}
td{{padding:7px 0;border-bottom:1px solid var(--line);color:var(--ink2);vertical-align:top}}
td:first-child{{width:112px;color:var(--ink3);font-size:12.4px;text-transform:uppercase;letter-spacing:.05em;padding-right:12px}}
.w{{color:var(--ink3);font-size:13px}}
.t{{font-style:normal;font-size:9.5px;letter-spacing:.08em;padding:1px 5px;border-radius:4px;background:var(--soft);color:var(--ink3);margin-left:4px}}
.t-inferred{{color:var(--warn)}} .t-unknown{{color:var(--hot)}}
.g{{font-size:13.6px;margin:14px 0 6px;color:var(--ink)}}
.b ul{{margin:0;padding-left:20px}} .b li{{font-size:14px;color:var(--ink2);margin-bottom:6px}}
a{{color:inherit}}
</style>
<div class="w">
<h1>Cypress dossiers</h1>
<p class="sub">86 locally owned Cypress restaurants, collected 18 August 2026. Site classified and rendered where needed, menu and catering read from their own pages. Every claim shows its evidence tier. Sorted by how much is visibly broken.</p>

<div class="k">
  <div><b>86</b><span>collected</span></div>
  <div><b>{len(real)}</b><span>real, readable sites</span></div>
  <div><b>{noschema}</b><span>invisible to AI answers</span></div>
  <div><b>{noorder}</b><span>no online ordering at all</span></div>
  <div><b>{nocater}</b><span>catering absent or unorderable</span></div>
</div>

<div class="note">
  <p><b>Correcting my own earlier number.</b> The first pass reported 38 working websites by
  treating HTTP 200 as a site. Reading them properly gives <b>{len(real)}</b>. The rest are
  {byst.get("DEAD",0)} dead, {byst.get("NO_SITE_LISTED",0)} with no site listed,
  {byst.get("PARKED",0)} parked and {byst.get("JS_SHELL",0)} JavaScript shells that would not
  render. Edojin looked empty to a static read and has 98 words once rendered - that class of
  false negative is exactly what would have embarrassed us in front of an owner.</p>
</div>

<div class="note">
  <p><b>Still provisional.</b> This is the free, automatable half: site, menu, catering,
  crawler access. Winnability, access, reviews, the guest journey and the AI-answer check are
  not in here yet, so no verdict is final. The directory is from 2018, so anything without a
  live site needs confirming as still trading before you go near it.</p>
</div>

<h2>Readable sites, worst first</h2>
{cards}

<h2>Needs a status check first ({len(check)})</h2>
<div class="note"><p>{E(", ".join(d["restaurant"]["name"] for d in check))}</p></div>
</div>'''
(REPO/"outreach/board-cypress.html").write_text(page)
print("board:", len(page), "bytes |", len(real), "real |", len(check), "to verify")
