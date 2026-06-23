#!/usr/bin/env node
/*
 * gen-toolbox.js — builds the crawlable tool directory (and its JSON-LD) in
 * toolbox.html from the single source of truth: the TOOLS array in script.js.
 *
 * Why: the interactive finder reads TOOLS at runtime (invisible to search
 * engines and AI answer engines). This script renders the same data as static,
 * indexable HTML so the toolbox can be found on Google and cited by AI — without
 * duplicating the data by hand. Re-run after editing TOOLS:  node scripts/gen-toolbox.js
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const SCRIPT = path.join(ROOT, 'script.js');
const HTML = path.join(ROOT, 'toolbox.html');
const SITE = 'https://abbas-mypeople.github.io/Abbas/toolbox.html';

// --- pull TOOLS array out of script.js and evaluate it ---
const src = fs.readFileSync(SCRIPT, 'utf8');
const start = src.indexOf('const TOOLS = [');
const end = src.indexOf('\n  ];', start);
if (start === -1 || end === -1) throw new Error('Could not locate TOOLS array in script.js');
const arrText = src.slice(start + 'const TOOLS = '.length, end + 4);
const TOOLS = eval(arrText); // trusted, first-party source

const esc = (s) => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');
const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

// --- group by category, preserving first-appearance order ---
const cats = [];
const byCat = new Map();
for (const t of TOOLS) {
  if (!byCat.has(t.c)) { byCat.set(t.c, []); cats.push(t.c); }
  byCat.get(t.c).push(t);
}

// --- jump nav ---
const nav = `<nav class="tooldir__nav" aria-label="Tool categories">\n` +
  `          <span class="tooldir__nav-label">Jump to:</span>\n` +
  cats.map((c) => `          <a href="#cat-${slug(c)}">${esc(c)}</a>`).join('\n') +
  `\n        </nav>`;

// --- one tool card ---
const card = (t) => `          <article class="tooldir__tool">
            <div class="tooldir__tool-head">
              <h4 class="tooldir__name"><a href="${esc(t.u)}" target="_blank" rel="nofollow noopener">${esc(t.n)}</a></h4>
              <span class="tooldir__price">${esc(t.p)}</span>
            </div>
            <p class="tooldir__what">${esc(t.w)}</p>
            <p class="tooldir__fit"><span class="tooldir__tag tooldir__tag--fit">Best for</span> ${esc(t.fit)}</p>
            <p class="tooldir__watch"><span class="tooldir__tag tooldir__tag--watch">Watch out</span> ${esc(t.not)}</p>
          </article>`;

// --- category blocks ---
const blocks = cats.map((c) => {
  const tools = byCat.get(c);
  return `        <div class="tooldir__cat" id="cat-${slug(c)}">
          <h3 class="tooldir__cat-title">${esc(c)} <span class="tooldir__count">${tools.length}</span></h3>
          <div class="tooldir__grid">
${tools.map(card).join('\n')}
          </div>
        </div>`;
}).join('\n');

const directoryHtml = `\n        ${nav}\n${blocks}\n        <p class="tooldir__foot">Prices are public list rates or research estimates (marked “est.”) as of ${new Date().toLocaleString('en-US', { month: 'long', year: 'numeric' })} — always confirm on a live quote. Listed for reference; we take no commission from any vendor.</p>\n        `;

// --- JSON-LD: ItemList of SoftwareApplication entries ---
const ld = {
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: 'Restaurant Technology Tools Directory',
  description: 'A categorized directory of 100+ software and hardware tools for independent restaurants — POS, online ordering, reservations, AI phone, loyalty, inventory, delivery, analytics and more.',
  url: SITE + '#directory',
  numberOfItems: TOOLS.length,
  itemListElement: TOOLS.map((t, i) => ({
    '@type': 'ListItem',
    position: i + 1,
    item: {
      '@type': 'SoftwareApplication',
      name: t.n,
      applicationCategory: t.c,
      description: t.w,
      url: t.u,
      offers: { '@type': 'Offer', category: t.p, priceCurrency: 'USD' },
    },
  })),
};
const ldHtml = `\n  <script type="application/ld+json">\n${JSON.stringify(ld, null, 2)}\n  </script>\n  `;

// --- splice both into toolbox.html between their markers ---
let html = fs.readFileSync(HTML, 'utf8');
const between = (s, a, b, repl) => {
  const i = s.indexOf(a), j = s.indexOf(b);
  if (i === -1 || j === -1) throw new Error(`Markers not found: ${a} / ${b}`);
  return s.slice(0, i + a.length) + repl + s.slice(j);
};
html = between(html, '<!-- TOOLDIR:START -->', '<!-- TOOLDIR:END -->', directoryHtml);
html = between(html, '<!-- TOOLDIR-LD:START -->', '<!-- TOOLDIR-LD:END -->', ldHtml);
fs.writeFileSync(HTML, html);

console.log(`Generated directory: ${TOOLS.length} tools across ${cats.length} categories.`);
