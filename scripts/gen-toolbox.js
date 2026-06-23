#!/usr/bin/env node
/*
 * gen-toolbox.js — single source of truth build step for the tool directory.
 *
 * From the TOOLS array in script.js + the researched detail data in
 * data/tool-details-*.json, this:
 *   1. renders the crawlable directory + JSON-LD into toolbox.html (between markers),
 *      with each card linking to its own detail page;
 *   2. generates one detail page per tool at tools/<slug>.html (pricing, pros,
 *      cons, integrations, alternatives, verdict);
 *   3. fills the tool URLs into sitemap.xml (between markers).
 *
 * Re-run after editing TOOLS or the detail data:  node scripts/gen-toolbox.js
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const SCRIPT = path.join(ROOT, 'script.js');
const HTML = path.join(ROOT, 'toolbox.html');
const SITEMAP = path.join(ROOT, 'sitemap.xml');
const TOOLS_DIR = path.join(ROOT, 'tools');
const BASE = 'https://azrestaurantpartners.com/';
const TODAY = '2026-06-23';

// --- TOOLS array from script.js ---
const src = fs.readFileSync(SCRIPT, 'utf8');
const a = src.indexOf('const TOOLS = [');
const b = src.indexOf('\n  ];', a);
if (a === -1 || b === -1) throw new Error('Could not locate TOOLS in script.js');
const TOOLS = eval(src.slice(a + 'const TOOLS = '.length, b + 4));

// --- merge researched detail data ---
const DET = {};
for (const n of ['1', '2', '3']) {
  JSON.parse(fs.readFileSync(path.join(ROOT, `data/tool-details-${n}.json`), 'utf8'))
    .forEach((d) => { DET[d.n] = d; });
}

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
const trunc = (s, n) => { s = String(s).replace(/\s+/g, ' ').trim(); return s.length <= n ? s : s.slice(0, n - 1).replace(/\s+\S*$/, '') + '…'; };

const nameToSlug = {};
TOOLS.forEach((t) => { nameToSlug[t.n] = slug(t.n); });

// --- group by category (first-appearance order) ---
const cats = [];
const byCat = new Map();
for (const t of TOOLS) {
  if (!byCat.has(t.c)) { byCat.set(t.c, []); cats.push(t.c); }
  byCat.get(t.c).push(t);
}

/* ============================ 1. DIRECTORY ============================ */
const nav = `<nav class="tooldir__nav" aria-label="Tool categories">\n` +
  `          <span class="tooldir__nav-label">Jump to:</span>\n` +
  cats.map((c) => `          <a href="#cat-${slug(c)}">${esc(c)}</a>`).join('\n') +
  `\n        </nav>`;

const card = (t) => `          <article class="tooldir__tool">
            <div class="tooldir__tool-head">
              <h4 class="tooldir__name"><a href="tools/${slug(t.n)}.html">${esc(t.n)}</a></h4>
              <span class="tooldir__price">${esc(t.p)}</span>
            </div>
            <p class="tooldir__what">${esc(t.w)}</p>
            <p class="tooldir__fit"><span class="tooldir__tag tooldir__tag--fit">Best for</span> ${esc(t.fit)}</p>
            <p class="tooldir__watch"><span class="tooldir__tag tooldir__tag--watch">Watch out</span> ${esc(t.not)}</p>
            <a class="tooldir__more" href="tools/${slug(t.n)}.html">Pricing, pros &amp; cons →</a>
          </article>`;

const blocks = cats.map((c) => {
  const tools = byCat.get(c);
  return `        <div class="tooldir__cat" id="cat-${slug(c)}">
          <h3 class="tooldir__cat-title">${esc(c)} <span class="tooldir__count">${tools.length}</span></h3>
          <div class="tooldir__grid">
${tools.map(card).join('\n')}
          </div>
        </div>`;
}).join('\n');

const directoryHtml = `\n        ${nav}\n${blocks}\n        <p class="tooldir__foot">Prices are public list rates or research estimates (marked “est.”) as of ${new Date(TODAY).toLocaleString('en-US', { month: 'long', year: 'numeric' })} — always confirm on a live quote. Listed for reference; we take no commission from any vendor.</p>\n        `;

const ld = {
  '@context': 'https://schema.org', '@type': 'ItemList',
  name: 'Restaurant Technology Tools Directory',
  description: 'A categorized directory of 100+ software and hardware tools for independent restaurants — POS, online ordering, reservations, AI phone, loyalty, inventory, delivery, analytics and more.',
  url: BASE + 'toolbox.html#directory', numberOfItems: TOOLS.length,
  itemListElement: TOOLS.map((t, i) => ({
    '@type': 'ListItem', position: i + 1,
    item: { '@type': 'SoftwareApplication', name: t.n, applicationCategory: t.c, description: t.w, url: BASE + 'tools/' + slug(t.n) + '.html', sameAs: t.u },
  })),
};
const ldHtml = `\n  <script type="application/ld+json">\n${JSON.stringify(ld, null, 2)}\n  </script>\n  `;

let html = fs.readFileSync(HTML, 'utf8');
const splice = (s, m1, m2, repl) => {
  const i = s.indexOf(m1), j = s.indexOf(m2);
  if (i === -1 || j === -1) throw new Error(`Markers not found: ${m1}/${m2}`);
  return s.slice(0, i + m1.length) + repl + s.slice(j);
};
html = splice(html, '<!-- TOOLDIR:START -->', '<!-- TOOLDIR:END -->', directoryHtml);
html = splice(html, '<!-- TOOLDIR-LD:START -->', '<!-- TOOLDIR-LD:END -->', ldHtml);
fs.writeFileSync(HTML, html);

/* ========================= 2. DETAIL PAGES ========================= */
const ICON = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231b1a17'/%3E%3Ctext x='50%25' y='55%25' font-family='Georgia,serif' font-size='30' font-weight='700' fill='%23c0492b' text-anchor='middle' dominant-baseline='middle'%3EA%3C/text%3E%3C/svg%3E`;
const FONTS = `https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=Inter:wght@400;500;600&display=swap`;

if (!fs.existsSync(TOOLS_DIR)) fs.mkdirSync(TOOLS_DIR);
// clear stale generated pages
fs.readdirSync(TOOLS_DIR).filter((f) => f.endsWith('.html')).forEach((f) => fs.unlinkSync(path.join(TOOLS_DIR, f)));

const li = (x) => `              <li>${esc(x)}</li>`;
const detailPage = (t) => {
  const d = DET[t.n] || {};
  const s = slug(t.n);
  const cslug = slug(t.c);
  const url = BASE + 'tools/' + s + '.html';
  const pros = (d.pros || []).map(li).join('\n');
  const cons = (d.cons || []).map(li).join('\n');
  const alts = (d.alternatives || []).map((x) => nameToSlug[x] ? `<a href="${nameToSlug[x]}.html">${esc(x)}</a>` : esc(x)).join(' · ');
  const desc = trunc(`${t.w} ${t.n} pricing, pros, cons and alternatives for restaurants.`, 158);
  const jsonld = {
    '@context': 'https://schema.org',
    '@graph': [
      { '@type': 'SoftwareApplication', name: t.n, applicationCategory: t.c, operatingSystem: 'Web', description: t.w, url: url, sameAs: t.u,
        offers: { '@type': 'Offer', priceCurrency: 'USD', category: d.pricing || t.p },
        review: { '@type': 'Review', author: { '@type': 'Organization', name: 'AZ Restaurant Partners' }, reviewBody: d.verdict || t.fit } },
      { '@type': 'BreadcrumbList', itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Toolbox', item: BASE + 'toolbox.html' },
        { '@type': 'ListItem', position: 2, name: t.c, item: BASE + 'toolbox.html#cat-' + cslug },
        { '@type': 'ListItem', position: 3, name: t.n, item: url } ] },
    ],
  };
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(trunc(t.n + ': Pricing, Pros & Cons', 60))}</title>
  <meta name="description" content="${esc(desc)}" />
  <meta name="theme-color" content="#f4eee2" />
  <link rel="canonical" href="${url}" />
  <meta property="og:title" content="${esc(t.n)} — pricing, pros &amp; cons" />
  <meta property="og:description" content="${esc(desc)}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="${url}" />
  <meta property="og:image" content="${BASE}assets/og.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="${ICON}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="${FONTS}" rel="stylesheet" />
  <link rel="stylesheet" href="../styles.css" />
  <script type="application/ld+json">
${JSON.stringify(jsonld, null, 2)}
  </script>
</head>
<body>
  <header class="nav" id="nav">
    <div class="wrap nav__inner">
      <a href="../index.html" class="brand" aria-label="AZ Restaurant Partners">AZ&nbsp;Restaurant&nbsp;Partners</a>
      <nav class="nav__links" aria-label="Primary">
        <a href="../index.html">Home</a>
        <a href="../toolbox.html">Toolbox</a>
        <a href="../guides.html">Guides</a>
        <a href="../details.html">Full details</a>
        <a href="../index.html#contact" class="nav__cta">Book a free call</a>
      </nav>
      <button class="nav__toggle" id="navToggle" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
    </div>
  </header>

  <main id="top">
    <article class="section guide tool-detail">
      <div class="wrap">
        <div class="guide__head">
          <p class="guide__crumb"><a href="../toolbox.html">Toolbox</a> · <a href="../toolbox.html#cat-${cslug}">${esc(t.c)}</a></p>
          <p class="kicker">${esc(t.c)}</p>
          <h1>${esc(t.n)}</h1>
          <p class="guide__lead">${esc(t.w)}</p>
          <p class="tool-detail__price"><strong>${esc(t.p)}</strong></p>
          <p><a class="btn btn--primary" href="${esc(t.u)}" target="_blank" rel="nofollow noopener">Visit ${esc(t.n)} website →</a></p>
        </div>

        <div class="guide__body">
          <h2>What it costs</h2>
          <p>${esc(d.pricing || t.p)}</p>

          <h2>Best for</h2>
          <p>${esc(d.bestFor || t.fit)}</p>
${pros ? `
          <h2>Pros</h2>
          <ul class="tool-detail__list tool-detail__pros">
${pros}
          </ul>` : ''}
${cons ? `
          <h2>Cons</h2>
          <ul class="tool-detail__list tool-detail__cons">
${cons}
          </ul>` : ''}
${d.integrations ? `
          <h2>Integrations</h2>
          <p>${esc(d.integrations)}</p>` : ''}
${alts ? `
          <h2>Alternatives</h2>
          <p>${alts}</p>` : ''}

          <div class="guide__callout">
            <p><strong>Our take:</strong> ${esc(d.verdict || t.fit)}</p>
          </div>
          <p class="tool-detail__disc">Pricing is the public list rate or a research estimate as of June 2026 — always confirm on a live quote. We take no commission from any vendor; this is for reference.</p>
        </div>

        <div class="guide__next">
          <p class="guide__next-label">Keep exploring</p>
          <a href="../toolbox.html#cat-${cslug}">More ${esc(t.c)} tools →</a>
          <a href="../toolbox.html">Browse the full toolbox — 100+ tools →</a>
          <a href="../index.html#contact">Not sure what fits? Book a free call →</a>
        </div>
      </div>
    </article>

    <section class="ctaband">
      <div class="wrap ctaband__inner">
        <p>Want the right tools picked, set up, and proven in your numbers? We only get paid once you're saving.</p>
        <a href="../index.html#contact" class="btn btn--primary">Book your free call</a>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="wrap footer__inner">
      <span class="brand">AZ&nbsp;Restaurant&nbsp;Partners</span>
      <p><strong>Keep more of what you earn.</strong> For independent, family-run restaurants — a restaurant family + an engineering team · Spring &amp; Greater Houston, TX.</p>
      <p class="footer__copy">© <span id="year"></span> AZ Restaurant Partners · <a href="../index.html">Home</a> · <a href="../toolbox.html">Toolbox</a> · <a href="../guides.html">Guides</a></p>
    </div>
  </footer>

  <div class="mobilecta" id="mobilecta">
    <a href="../index.html#contact" class="btn btn--primary btn--full">Book your free call</a>
  </div>

  <script src="../script.js"></script>
</body>
</html>
`;
};

TOOLS.forEach((t) => fs.writeFileSync(path.join(TOOLS_DIR, slug(t.n) + '.html'), detailPage(t)));

/* ========================= 3. SITEMAP ========================= */
let sm = fs.readFileSync(SITEMAP, 'utf8');
const toolUrls = '\n' + TOOLS.map((t) =>
  `  <url>\n    <loc>${BASE}tools/${slug(t.n)}.html</loc>\n    <lastmod>${TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>`
).join('\n') + '\n  ';
sm = splice(sm, '<!-- TOOLS:START -->', '<!-- TOOLS:END -->', toolUrls);
fs.writeFileSync(SITEMAP, sm);

console.log(`Directory + ${TOOLS.length} detail pages generated across ${cats.length} categories; sitemap updated.`);
