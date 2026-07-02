/* ==========================================================================
   TradingView embed helpers.
   Charts are near-real-time and free (no API key, no CORS headaches).
   We drive the seven required timeframes through the advanced-chart widget.
   ========================================================================== */

export const TIMEFRAMES = [
  { id: '1',  label: '1m',  hint: 'scalp' },
  { id: '5',  label: '5m',  hint: 'intraday' },
  { id: '15', label: '15m', hint: 'intraday' },
  { id: '60', label: '1h',  hint: 'swing' },
  { id: 'D',  label: '1D',  hint: 'trend' },
  { id: 'W',  label: '1W',  hint: 'position' },
  { id: 'M',  label: '1Mo', hint: 'macro' }
];

function theme() {
  return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
}

/* Mount the full advanced chart for a given interval. Rebuilds cleanly on
   each call so timeframe tabs just re-invoke it. */
export function mountAdvancedChart(containerId, tvSymbol, interval) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = '<div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>';
  const s = document.createElement('script');
  s.type = 'text/javascript';
  s.async = true;
  s.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
  s.innerHTML = JSON.stringify({
    autosize: true,
    symbol: tvSymbol,
    interval,
    timezone: 'America/New_York',
    theme: theme(),
    style: '1',                 // candles
    locale: 'en',
    enable_publishing: false,
    backgroundColor: theme() === 'light' ? '#ffffff' : '#0f1524',
    gridColor: 'rgba(120,130,160,0.10)',
    hide_top_toolbar: false,
    allow_symbol_change: false,
    save_image: false,
    calendar: false,
    studies: ['STD;VWAP', 'Volume@tv-basicstudies'],
    support_host: 'https://www.tradingview.com'
  });
  el.querySelector('.tradingview-widget-container__widget').appendChild(s);
}

/* Build the timeframe tab bar wired to the advanced chart. */
export function mountTimeframeChart(tabsId, chartId, tvSymbol, initial = 'D') {
  const tabs = document.getElementById(tabsId);
  tabs.innerHTML = TIMEFRAMES.map(t =>
    `<button data-int="${t.id}" title="${t.hint}" class="${t.id === initial ? 'active' : ''}">${t.label}</button>`
  ).join('');
  const render = (int) => {
    tabs.querySelectorAll('button').forEach(b => b.classList.toggle('active', b.dataset.int === int));
    mountAdvancedChart(chartId, tvSymbol, int);
  };
  tabs.addEventListener('click', e => {
    const b = e.target.closest('button');
    if (b) render(b.dataset.int);
  });
  render(initial);
  // Re-render on theme change so the chart matches
  const obs = new MutationObserver(() => {
    const active = tabs.querySelector('button.active')?.dataset.int || initial;
    mountAdvancedChart(chartId, tvSymbol, active);
  });
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
}

/* A compact single-symbol overview widget (live price + mini chart). */
export function mountSymbolOverview(containerId, tvSymbol) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = '<div class="tradingview-widget-container__widget"></div>';
  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-info.js';
  s.innerHTML = JSON.stringify({
    symbol: tvSymbol, width: '100%', locale: 'en',
    colorTheme: theme(), isTransparent: true
  });
  el.querySelector('.tradingview-widget-container__widget').appendChild(s);
}

/* Technical-analysis gauge (buy/sell) for a symbol + interval. */
export function mountTechnicals(containerId, tvSymbol, interval = '1D') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = '<div class="tradingview-widget-container__widget"></div>';
  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js';
  s.innerHTML = JSON.stringify({
    interval, width: '100%', height: 400, symbol: tvSymbol,
    showIntervalTabs: true, locale: 'en', colorTheme: theme(), isTransparent: true
  });
  el.querySelector('.tradingview-widget-container__widget').appendChild(s);
}
