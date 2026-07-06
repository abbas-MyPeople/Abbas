#!/usr/bin/env python3
"""AZ Restaurant Partners — guarded GA4 analytics dashboard.

A tiny, self-contained Flask app for azrestaurantpartners.com:
  • HTTP Basic auth (AUTH_USER / AUTH_PASS) on the dashboard + data API.
  • Every response is X-Robots-Tag: noindex; /robots.txt disallows all — this is a private
    internal tool that must never be indexed.
  • /health is UNauthed so the Space healthcheck works without creds.
  • Never crashes on missing creds; never fabricates numbers. When GA4 isn't configured or the
    property has no data yet, the UI shows a clean "Connect GA4" / "No data yet" state.

Deploy: Hugging Face Docker Space, gunicorn entry `app:app` on port 7860.
"""

import os
from functools import wraps

from flask import Flask, jsonify, request, Response

import az_ga4

# ── Auth ────────────────────────────────────────────────────────────────────────────────────────
AUTH_USER = os.environ.get("AUTH_USER", "az")
AUTH_PASS = os.environ.get("AUTH_PASS", "az2026")


def _check_auth(u, p):
    return u == AUTH_USER and p == AUTH_PASS


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not _check_auth(auth.username, auth.password):
            return Response(
                "Authentication required", 401,
                {"WWW-Authenticate": 'Basic realm="AZ Restaurant Partners — Analytics"'},
            )
        return f(*args, **kwargs)
    return decorated


app = Flask(__name__)


@app.after_request
def _noindex(resp):
    resp.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return resp


@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /\n", mimetype="text/plain")


@app.route("/health")
def health():
    """Unauthed liveness probe. Reports whether GA4 creds+property are configured (no data fetch)."""
    return jsonify({"ok": True, "ga4_configured": az_ga4.available()})


@app.route("/api/ga4")
@auth_required
def api_ga4():
    try:
        return jsonify(az_ga4.get())
    except Exception:
        # az_ga4.get() is designed never to raise, but guard anyway — never 500 the UI.
        return jsonify({"available": False, "connect": True,
                        "reason": "GA4 not connected yet"})


@app.route("/")
@auth_required
def index():
    return Response(DASHBOARD_HTML, mimetype="text/html")


# ════════════════════════════════════════════ FRONTEND ════════════════════════════════════════════
# Self-contained: no external CDN/scripts. Simple bar/line visuals drawn with divs + inline SVG.

DASHBOARD_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>AZ Restaurant Partners — Analytics</title>
<style>
  :root{
    --bg:#0e1116; --panel:#161b22; --panel2:#1c2230; --line:#28303d;
    --ink:#e8edf4; --muted:#8b97a8; --gold:#e08a2b; --gold2:#f2a44a;
    --green:#3fb950; --blue:#4a9eff; --violet:#a371f7;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  a{color:var(--gold2);text-decoration:none}
  .wrap{max-width:1080px;margin:0 auto;padding:22px 18px 60px}
  header{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:8px;
    padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:20px}
  h1{font-size:20px;margin:0;letter-spacing:.2px}
  h1 .em{color:var(--gold)}
  .sub{color:var(--muted);font-size:12.5px}
  .status{font-size:12px;color:var(--muted)}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle}
  .dot.ok{background:var(--green)} .dot.warn{background:var(--gold)} .dot.off{background:#586172}

  .banner{background:var(--panel);border:1px solid var(--line);border-radius:12px;
    padding:22px 20px;margin-bottom:22px}
  .banner h2{margin:0 0 6px;font-size:16px}
  .banner p{margin:0;color:var(--muted);font-size:13.5px}
  .banner code{background:var(--panel2);padding:1px 6px;border-radius:5px;color:var(--gold2);font-size:12px}

  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:22px}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
  .kpi .label{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
  .kpi .val{font-size:26px;font-weight:700;margin-top:4px;line-height:1}
  .kpi .sub2{font-size:11.5px;color:var(--muted);margin-top:5px}
  .kpi.conv{border-color:#3a2c14;background:linear-gradient(180deg,#1b1710,var(--panel))}
  .kpi.conv .val{color:var(--gold2)}

  .grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  @media(max-width:720px){.grid{grid-template-columns:1fr}}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:16px}
  .card h3{margin:0 0 14px;font-size:13.5px;letter-spacing:.3px}
  .card h3 .n{color:var(--muted);font-weight:400;font-size:12px}

  /* horizontal bars */
  .bars .row{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:13px}
  .bars .nm{flex:0 0 42%;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .bars .track{flex:1;background:var(--panel2);border-radius:6px;height:16px;position:relative;overflow:hidden}
  .bars .fill{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--gold),var(--gold2))}
  .bars .fill.b{background:linear-gradient(90deg,#2f6fbf,var(--blue))}
  .bars .fill.v{background:linear-gradient(90deg,#6b45c0,var(--violet))}
  .bars .vv{flex:0 0 auto;color:var(--muted);font-variant-numeric:tabular-nums;min-width:42px;text-align:right}

  /* line/area trend as inline SVG */
  .trend svg{width:100%;height:120px;display:block}
  .legend{font-size:11.5px;color:var(--muted);margin-top:8px;display:flex;gap:14px}
  .legend b{font-weight:600}
  .sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;vertical-align:middle}

  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:6px 4px;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-weight:500;font-size:11.5px;text-transform:uppercase;letter-spacing:.5px}
  td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
  .empty{color:var(--muted);font-size:13px;padding:8px 0}
  footer{color:var(--muted);font-size:11.5px;margin-top:24px;text-align:center}
  .hide{display:none}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>AZ Restaurant Partners <span class="em">·</span> Analytics</h1>
      <div class="sub">azrestaurantpartners.com — private, noindex</div>
    </div>
    <div class="status" id="status"><span class="dot off"></span>loading…</div>
  </header>

  <div id="banner" class="banner hide"></div>

  <div id="dash" class="hide">
    <div class="kpis" id="kpis"></div>

    <div class="card trend">
      <h3>Traffic trend <span class="n">· last 28 days</span></h3>
      <div id="trend"></div>
      <div class="legend">
        <span><span class="sw" style="background:var(--gold2)"></span>Active users</span>
        <span><span class="sw" style="background:var(--blue)"></span>Sessions</span>
      </div>
    </div>

    <div class="card">
      <h3>Conversion funnel <span class="n">· section_view by section</span></h3>
      <div class="bars" id="sections"><div class="empty">No section views yet.</div></div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Top pages <span class="n">· by pageviews</span></h3>
        <div class="bars" id="pages"><div class="empty">No page data yet.</div></div>
      </div>
      <div class="card">
        <h3>Traffic sources <span class="n">· by channel</span></h3>
        <div class="bars" id="sources"><div class="empty">No source data yet.</div></div>
      </div>
    </div>

    <div class="card">
      <h3>All events <span class="n">· last 28 days</span></h3>
      <table id="events"><thead><tr><th>Event</th><th class="n">Count</th></tr></thead>
        <tbody><tr><td class="empty" colspan="2">No events yet.</td></tr></tbody></table>
    </div>
  </div>

  <footer id="foot"></footer>
</div>

<script>
const $ = id => document.getElementById(id);
const fmt = n => (n==null?'—':Number(n).toLocaleString());
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function bars(el, items, nameKey, valKey, cls){
  const box = $(el);
  if(!items || !items.length){ return; }  // keep the empty placeholder
  const max = Math.max(...items.map(i=>i[valKey]), 1);
  box.innerHTML = items.map(i=>{
    const w = Math.max(2, Math.round(i[valKey]/max*100));
    return `<div class="row"><div class="nm" title="${esc(i[nameKey])}">${esc(i[nameKey])}</div>`
      + `<div class="track"><div class="fill ${cls||''}" style="width:${w}%"></div></div>`
      + `<div class="vv">${fmt(i[valKey])}</div></div>`;
  }).join('');
}

function trend(series){
  const box = $('trend');
  if(!series || series.length<2){ box.innerHTML = '<div class="empty">Not enough days of data to chart yet.</div>'; return; }
  const W=720, H=120, pad=6;
  const xs = series.map((_,i)=> pad + i*(W-2*pad)/(series.length-1));
  const maxU = Math.max(...series.map(d=>d.activeUsers), 1);
  const maxS = Math.max(...series.map(d=>d.sessions), 1);
  const mx = Math.max(maxU, maxS);
  const y = v => H-pad - (v/mx)*(H-2*pad);
  const path = key => series.map((d,i)=> (i?'L':'M')+xs[i].toFixed(1)+' '+y(d[key]).toFixed(1)).join(' ');
  const area = key => 'M'+xs[0].toFixed(1)+' '+(H-pad)+' '
      + series.map((d,i)=>'L'+xs[i].toFixed(1)+' '+y(d[key]).toFixed(1)).join(' ')
      + ' L'+xs[series.length-1].toFixed(1)+' '+(H-pad)+' Z';
  box.innerHTML = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#e08a2b" stop-opacity=".35"/>
      <stop offset="1" stop-color="#e08a2b" stop-opacity="0"/></linearGradient></defs>
    <path d="${area('activeUsers')}" fill="url(#g)"/>
    <path d="${path('sessions')}" fill="none" stroke="#4a9eff" stroke-width="2" opacity=".9"/>
    <path d="${path('activeUsers')}" fill="none" stroke="#f2a44a" stroke-width="2.2"/>
  </svg>`;
}

function connect(reason){
  $('status').innerHTML = '<span class="dot off"></span>GA4 not connected';
  const b = $('banner'); b.classList.remove('hide');
  b.innerHTML = '<h2>Connect GA4</h2><p>' + esc(reason||'GA4 is not configured.')
    + ' Set <code>GA4_PROPERTY_ID</code> and <code>GA4_SA_JSON</code> as Space secrets, and add the'
    + ' service account as a Viewer on the GA4 property.</p>';
}

function noData(){
  const b = $('banner'); b.classList.remove('hide');
  b.innerHTML = '<h2>No data yet</h2><p>GA4 is connected, but the property is new — no traffic has '
    + 'been recorded in the last 28 days. Numbers will appear here as visits come in.</p>';
}

function render(d){
  $('dash').classList.remove('hide');
  const t7=d.totals_7d||{}, t28=d.totals_28d||{}, cv=d.conversions||{};
  const kpis = [
    {label:'Active users · 7d', val:t7.activeUsers, sub:`${fmt(t28.activeUsers)} in 28d`},
    {label:'Sessions · 7d', val:t7.sessions, sub:`${fmt(t28.sessions)} in 28d`},
    {label:'New users · 7d', val:t7.newUsers, sub:`${fmt(t28.newUsers)} in 28d`},
    {label:'Pageviews · 7d', val:t7.screenPageViews, sub:`${fmt(t28.screenPageViews)} in 28d`},
    {label:'Leads · 28d', val:cv.lead_submit, sub:'lead_submit', conv:true},
    {label:'Calls · 28d', val:cv.call_click, sub:'call_click', conv:true},
    {label:'Finder captures · 28d', val:cv.finder_capture, sub:'finder_capture', conv:true},
  ];
  $('kpis').innerHTML = kpis.map(k=>
    `<div class="kpi ${k.conv?'conv':''}"><div class="label">${esc(k.label)}</div>`
    + `<div class="val">${fmt(k.val)}</div><div class="sub2">${esc(k.sub)}</div></div>`).join('');

  trend(d.trend);
  bars('sections', d.sections, 'section', 'count', 'v');
  bars('pages', d.top_pages, 'path', 'views', '');
  bars('sources', d.sources, 'channel', 'sessions', 'b');

  const ev = d.events||[];
  if(ev.length){
    $('events').querySelector('tbody').innerHTML = ev.map(e=>
      `<tr><td>${esc(e.event)}</td><td class="n">${fmt(e.count)}</td></tr>`).join('');
  }

  const fresh = d.has_data;
  $('status').innerHTML = `<span class="dot ${fresh?'ok':'warn'}"></span>`
    + (fresh ? `Live · property ${esc(d.property_id)}` : 'Connected · awaiting first data');
  if(!fresh) noData();
  $('foot').textContent = (d.basis||'') + (d.fetched_at? ' · fetched '+d.fetched_at : '');
}

fetch('/api/ga4').then(r=>r.json()).then(d=>{
  if(!d || d.available===false){ connect(d && d.reason); return; }
  render(d);
}).catch(()=>connect('Could not reach the analytics API.'));
</script>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
