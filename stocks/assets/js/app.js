/* ==========================================================================
   Shared dashboard utilities: paths, formatting, market clock, theme,
   nav shell, and a resilient data loader (live source -> committed snapshot).
   Loaded by every page.
   ========================================================================== */

// Resolve the /stocks base regardless of nesting depth (/stocks/, /stocks/spy/,
// /stocks/spy/options/). Everything references data via BASE.
export const BASE = (() => {
  const m = location.pathname.match(/^(.*\/stocks)\//);
  if (m) return m[1];
  // running from a nested page without trailing match, or local file
  const parts = location.pathname.split('/');
  const i = parts.lastIndexOf('stocks');
  return i >= 0 ? parts.slice(0, i + 1).join('/') : '/stocks';
})();

/* ---------- Formatting ---------- */
export const fmt = {
  usd(n, d = 2) {
    if (n == null || isNaN(n)) return '—';
    return n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  },
  money(n, d = 2) { return n == null || isNaN(n) ? '—' : '$' + fmt.usd(n, d); },
  pct(n, d = 2) {
    if (n == null || isNaN(n)) return '—';
    const s = n >= 0 ? '+' : '';
    return s + n.toFixed(d) + '%';
  },
  signed(n, d = 2) {
    if (n == null || isNaN(n)) return '—';
    return (n >= 0 ? '+' : '') + n.toFixed(d);
  },
  compact(n) {
    if (n == null || isNaN(n)) return '—';
    return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n);
  },
  cls(n) { return n > 0 ? 'up' : n < 0 ? 'down' : 'flat'; },
  arrow(n) { return n > 0 ? '▲' : n < 0 ? '▼' : '▪'; },
  when(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (isNaN(d)) return iso;
    return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
  },
  ago(iso) {
    if (!iso) return '';
    const s = (Date.now() - new Date(iso).getTime()) / 1000;
    if (s < 60) return 'just now';
    if (s < 3600) return Math.floor(s / 60) + 'm ago';
    if (s < 86400) return Math.floor(s / 3600) + 'h ago';
    return Math.floor(s / 86400) + 'd ago';
  }
};

/* ---------- US market clock (NYSE regular session, ET) ---------- */
export function marketStatus(now = new Date()) {
  // Convert to America/New_York wall clock
  const et = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
  const day = et.getDay(); // 0 Sun .. 6 Sat
  const mins = et.getHours() * 60 + et.getMinutes();
  const open = 9 * 60 + 30, close = 16 * 60;
  const weekday = day >= 1 && day <= 5;
  let state = 'closed', label = 'Closed';
  if (weekday) {
    if (mins >= open && mins < close) { state = 'open'; label = 'Market open'; }
    else if (mins >= 4 * 60 && mins < open) { state = 'pre'; label = 'Pre-market'; }
    else if (mins >= close && mins < 20 * 60) { state = 'post'; label = 'After hours'; }
  }
  return { state, label, et };
}

/* ---------- Resilient JSON loader ----------
   Tries the primary path (committed snapshot). Live overrides can be layered
   later without touching callers. Returns null on failure (pages degrade). */
export async function loadJSON(relPath) {
  try {
    const res = await fetch(`${BASE}/${relPath}?t=${Math.floor(Date.now() / 60000)}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(res.status);
    return await res.json();
  } catch (e) {
    console.warn('loadJSON failed:', relPath, e.message);
    return null;
  }
}

/* ---------- Silent auto-refresh ----------
   Re-runs `tick` on a cadence that adapts to the market session (fast while
   open, relaxed off-hours), pauses while the tab is hidden, and fires
   immediately when the tab becomes visible again. `tick` is responsible for
   patching the DOM ONLY when data actually changed — no blinks, no reloads. */
export function autoRefresh(tick, { openMs = 60_000, extMs = 120_000, closedMs = 600_000 } = {}) {
  let timer = null;
  let inFlight = false;   // a slow tick must never pile up behind a fast cadence
  const delay = () => {
    const { state } = marketStatus();
    return state === 'open' ? openMs : (state === 'closed' ? closedMs : extMs);
  };
  const loop = async () => {
    if (!document.hidden && !inFlight) {
      inFlight = true;
      try { await tick(); } catch (e) { console.warn('refresh tick failed:', e); }
      finally { inFlight = false; }
    }
    timer = setTimeout(loop, delay());
  };
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) { clearTimeout(timer); loop(); }
  });
  timer = setTimeout(loop, delay());
  return () => clearTimeout(timer);
}

/* Patch helpers: touch the DOM only when content actually differs, so
   repaints never happen on unchanged data. */
export function setText(el, txt) {
  if (el && el.textContent !== txt) el.textContent = txt;
}
export function setHTML(el, html) {
  if (el && el.innerHTML !== html) el.innerHTML = html;
}

/* ---------- Theme ---------- */
export function initTheme() {
  const saved = localStorage.getItem('stx-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
}
export function toggleTheme() {
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'light' ? 'dark' : 'light';
  if (next === 'light') document.documentElement.setAttribute('data-theme', 'light');
  else document.documentElement.removeAttribute('data-theme');
  localStorage.setItem('stx-theme', next);
}

/* ---------- Shared navigation shell ---------- */
export function mountNav(active) {
  const { state, label } = marketStatus();
  const dotClass = state === 'open' ? 'live' : (state === 'closed' ? 'closed' : '');
  const links = [
    { href: `${BASE}/`, id: 'home', label: 'Dashboard' },
    { href: `${BASE}/spy/`, id: 'spy', label: 'SPY' },
    { href: `${BASE}/spy/options/`, id: 'spy-options', label: 'SPY Options' },
    { href: `${BASE}/spy/#research`, id: 'research', label: 'Morning Brief' }
  ];
  const nav = document.createElement('div');
  nav.className = 'topbar';
  nav.innerHTML = `
    <div class="topbar-inner">
      <a class="brand" href="${BASE}/">
        <span class="logo">AZ</span>
        <span>Stocks<br><small>abbaszoeb.com/stocks</small></span>
      </a>
      <nav class="nav-links">
        ${links.map(l => `<a href="${l.href}" class="${l.id === active ? 'active' : ''}">${l.label}</a>`).join('')}
      </nav>
      <div class="spacer"></div>
      <span class="pill" title="US market session (ET)"><span class="dot ${dotClass}"></span>${label}</span>
      <button class="icon-btn" id="themeBtn" title="Toggle light / dark">◐</button>
    </div>`;
  document.body.prepend(nav);
  document.getElementById('themeBtn').addEventListener('click', toggleTheme);
}

/* ---------- Tiny inline SVG sparkline ---------- */
export function sparkline(values, { w = 220, h = 42, up = 'var(--up)', down = 'var(--down)' } = {}) {
  if (!values || values.length < 2) return '';
  const min = Math.min(...values), max = Math.max(...values);
  const span = max - min || 1;
  const step = w / (values.length - 1);
  const pts = values.map((v, i) => `${(i * step).toFixed(1)},${(h - ((v - min) / span) * (h - 6) - 3).toFixed(1)}`);
  const rising = values[values.length - 1] >= values[0];
  const color = rising ? up : down;
  const area = `M0,${h} L${pts.join(' L')} L${w},${h} Z`;
  const line = `M${pts.join(' L')}`;
  const id = 'g' + Math.random().toString(36).slice(2, 8);
  return `<svg class="sparkline" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
    <defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${color}" stop-opacity="0.28"/>
      <stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>
    <path d="${area}" fill="url(#${id})"/>
    <path d="${line}" fill="none" stroke="${color}" stroke-width="1.8" stroke-linejoin="round"/>
  </svg>`;
}

/* ---------- Semicircular gauge (0..100), for volatility / sentiment ---------- */
export function gauge(value, { label = '', bands = null } = {}) {
  const v = Math.max(0, Math.min(100, value ?? 0));
  const r = 70, cx = 90, cy = 90;
  const ang = Math.PI * (1 - v / 100);
  const x = cx + r * Math.cos(ang), y = cy - r * Math.sin(ang);
  const track = `M20,90 A70,70 0 0 1 160,90`;
  const val = `M20,90 A70,70 0 0 1 ${x.toFixed(1)},${y.toFixed(1)}`;
  let color = 'var(--up)';
  if (v >= 66) color = 'var(--down)'; else if (v >= 33) color = 'var(--accent)';
  return `<svg viewBox="0 0 180 108" style="width:100%;max-width:220px">
    <path d="${track}" fill="none" stroke="var(--surface-3)" stroke-width="12" stroke-linecap="round"/>
    <path d="${val}" fill="none" stroke="${color}" stroke-width="12" stroke-linecap="round"/>
    <circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="6" fill="${color}"/>
    <text x="90" y="82" text-anchor="middle" font-family="var(--mono)" font-size="26" font-weight="700" fill="var(--text)">${Math.round(v)}</text>
    <text x="90" y="100" text-anchor="middle" font-size="11" fill="var(--text-3)">${label}</text>
  </svg>`;
}

/* ---------- Footer ---------- */
export function mountFooter() {
  const f = document.createElement('footer');
  f.className = 'site';
  f.innerHTML = `<div class="wrap">
    <div class="disclaimer">
      <strong>Personal research tool — not financial advice.</strong>
      Data is sourced from free/near-real-time feeds and may be delayed. Options analytics are model
      estimates (Black-Scholes) for education only. Nothing here is a recommendation to buy or sell any security.
      You alone are responsible for your trades.
    </div>
    <p class="note" style="margin-top:14px">Built for Abbas · <span class="mono">abbaszoeb.com/stocks</span> · updates commit automatically each morning.</p>
  </div>`;
  document.body.appendChild(f);
}
