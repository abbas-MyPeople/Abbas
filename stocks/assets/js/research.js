/* ==========================================================================
   Renders the automated morning research briefing from a JSON document.
   The JSON is produced each morning by the research GitHub Action.
   ========================================================================== */
import { fmt, gauge } from './app.js';

const CONF = { high: 'high', med: 'med', medium: 'med', low: 'low' };
const confBadge = (c) => `<span class="badge ${CONF[c] || 'low'}">${(c || 'low').toUpperCase()} confidence</span>`;

function biasChip(bias) {
  if (!bias) return '';
  const dir = (bias.direction || 'neutral').toLowerCase();
  const cls = dir === 'bullish' ? 'up' : dir === 'bearish' ? 'down' : 'flat';
  const arrow = dir === 'bullish' ? '▲' : dir === 'bearish' ? '▼' : '▪';
  return `<span class="chip ${cls}">${arrow} ${dir.toUpperCase()}</span>`;
}

function driverCard(d) {
  const type = (d.type || 'macro').toLowerCase();
  const impactPct = { high: 100, med: 60, medium: 60, low: 30 }[d.impact] || 40;
  const tags = (d.tags || []).map(t => `<span class="tag info">${t}</span>`).join(' ');
  return `<div class="driver ${type}">
    <div class="meta">
      <span class="tag ${type === 'bull' ? 'call' : type === 'bear' ? 'put' : 'info'}">${type.toUpperCase()}</span>
      ${d.inferred ? '<span class="tag gold" title="Not explicitly reported — inferred from related signals">INFERRED</span>' : ''}
      ${confBadge(d.confidence)}
    </div>
    <h4>${d.title}</h4>
    <p>${d.detail || ''}</p>
    <div>
      <div class="note" style="display:flex;justify-content:space-between"><span>Price impact</span><span>${d.impact || '—'}</span></div>
      <div class="meter" style="margin-top:4px"><span style="width:${impactPct}%;background:${type === 'bull' ? 'var(--up)' : type === 'bear' ? 'var(--down)' : 'var(--c1)'}"></span></div>
    </div>
    <div class="meta">${tags}${d.source ? `<a href="${d.source}" target="_blank" rel="noopener" class="dim">source ↗</a>` : ''}</div>
  </div>`;
}

export function renderBrief(el, r, { compact = false } = {}) {
  if (!r) {
    el.innerHTML = `<div class="card"><div class="card-head"><h3>Morning brief</h3></div>
      <p class="muted">No briefing yet. The research job commits <span class="mono">data/spy/research/latest.json</span> before the open each trading day.</p></div>`;
    return;
  }
  const vol = r.volatility || {};
  const em = r.expectedMove || {};
  const lv = r.keyLevels || {};

  const drivers = (r.drivers || []).slice().sort((a, b) => {
    const w = { high: 3, med: 2, medium: 2, low: 1 };
    return (w[b.impact] || 0) - (w[a.impact] || 0);
  });

  el.innerHTML = `
    <div class="card">
      <div class="card-head">
        <div>
          <div class="eyebrow">Morning brief · ${r.symbol || 'SPY'} · ${r.session || 'pre-open'}</div>
          <h2 style="margin-top:6px">${r.headline || 'Daily briefing'}</h2>
        </div>
        <div style="text-align:right">
          ${biasChip(r.bias)}
          <div class="note" style="margin-top:6px">${fmt.when(r.generatedAt)} · ${fmt.ago(r.generatedAt)}</div>
        </div>
      </div>
      <p style="font-size:15px;color:var(--text);max-width:820px">${r.summary || ''}</p>
      ${r.bias?.note ? `<p class="muted" style="font-size:13.5px">${r.bias.note} ${confBadge(r.bias.confidence)}</p>` : ''}
    </div>

    <div class="grid cols-3" style="margin-top:16px">
      <div class="card">
        <div class="card-head"><h3>Expected move (today)</h3><span class="hint">${em.basis || 'options-implied'}</span></div>
        <div class="stat"><div class="v" style="font-size:26px">±${fmt.pct(em.pct)}</div>
          <div class="sub">${em.dollarLow != null ? fmt.money(em.dollarLow) + ' – ' + fmt.money(em.dollarHigh) : 'range pending'}</div></div>
        <p class="note" style="margin-top:8px">One standard-deviation band the tape is pricing for the session. Break outside it = a surprise.</p>
      </div>
      <div class="card" style="text-align:center">
        <div class="card-head" style="justify-content:center"><h3>Volatility regime</h3></div>
        ${gauge(vol.score ?? 0, { label: (vol.regime || '').toUpperCase() })}
        <div class="note">VIX ${fmt.usd(vol.vix, 1)} <span class="${fmt.cls(vol.vixChg)}">${fmt.signed(vol.vixChg, 1)}</span> · IV rank ${vol.ivRank ?? '—'}</div>
      </div>
      <div class="card">
        <div class="card-head"><h3>Key levels</h3><span class="hint">pivot ${fmt.usd(lv.pivot)}</span></div>
        <div style="display:flex;flex-direction:column;gap:6px;font-family:var(--mono);font-size:13px">
          ${(lv.resistance || []).map(x => `<div class="down">R · ${fmt.usd(x)}</div>`).join('')}
          <div style="height:1px;background:var(--border);margin:2px 0"></div>
          ${(lv.support || []).map(x => `<div class="up">S · ${fmt.usd(x)}</div>`).join('')}
        </div>
      </div>
    </div>

    <div class="section" style="padding-top:20px">
      <div class="card-head"><h2>What's moving price ${r.symbol ? '· ' + r.symbol : ''}</h2>
        <span class="hint">sorted by confident price impact · surfaced &amp; inferred</span></div>
      <div class="grid cols-2">${drivers.map(driverCard).join('') || '<p class="muted">No drivers listed.</p>'}</div>
    </div>

    ${(r.calendar && r.calendar.length) ? `
    <div class="card">
      <div class="card-head"><h3>Today's catalysts</h3><span class="hint">ET</span></div>
      <div style="display:flex;flex-direction:column;gap:8px">
        ${r.calendar.map(c => `<div style="display:flex;gap:12px;align-items:center">
          <span class="mono" style="min-width:78px;color:var(--text-2)">${c.time}</span>
          <span class="badge ${c.importance === 'high' ? 'high' : c.importance === 'med' ? 'med' : 'low'}">${(c.importance || 'low').toUpperCase()}</span>
          <span>${c.event}</span></div>`).join('')}
      </div>
    </div>` : ''}

    ${(r.watch && r.watch.length) ? `
    <div class="card" style="margin-top:16px">
      <div class="card-head"><h3>On watch</h3></div>
      <ul style="margin:0;padding-left:18px;color:var(--text-2);font-size:14px">${r.watch.map(w => `<li>${w}</li>`).join('')}</ul>
    </div>` : ''}

    ${(r.sources && r.sources.length) ? `
    <p class="note" style="margin-top:14px">Sources: ${r.sources.map(s => `<a href="${s.url}" target="_blank" rel="noopener" class="dim">${s.title} ↗</a>`).join(' · ')}</p>` : ''}
  `;
}
