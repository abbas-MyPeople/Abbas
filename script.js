/* AZ Integrations — interactions + self-service tool finder */
(() => {
  const nav = document.getElementById('nav');
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 8);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  const toggle = document.getElementById('navToggle');
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  nav.querySelectorAll('.nav__links a').forEach((a) =>
    a.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    })
  );

  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }),
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  document.getElementById('year').textContent = new Date().getFullYear();

  /* ---- Lead form → emails azoeb27@gmail.com via FormSubmit ---- */
  const form = document.getElementById('leadForm');
  if (form) {
    const btn = document.getElementById('formSubmit');
    const note = document.getElementById('formNote');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (form._honey && form._honey.value) return;
      if (!form.name.value.trim() || !form.email.value.trim()) {
        note.textContent = 'Please add your name and email so I can reach you.';
        note.classList.add('error'); return;
      }
      btn.disabled = true; const original = btn.textContent; btn.textContent = 'Sending…';
      note.classList.remove('error');
      const payload = {
        name: form.name.value, restaurant: form.restaurant.value, email: form.email.value,
        phone: form.phone.value, message: form.message.value,
        _subject: 'New free-call request — AZ Integrations', _template: 'table', _captcha: 'false',
      };
      try {
        const res = await fetch('https://formsubmit.co/ajax/azoeb27@gmail.com', {
          method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('bad status');
        form.classList.add('sent');
        const ok = document.createElement('div');
        ok.className = 'form__success';
        ok.innerHTML = '<h3>Thank you — message sent.</h3>' +
          "<p>I'll personally reply to set up your free video call, usually within a day.</p>";
        form.appendChild(ok);
      } catch (err) {
        btn.disabled = false; btn.textContent = original;
        note.classList.add('error');
        note.innerHTML = 'Something went wrong sending the form. Please email me directly at ' +
          '<a href="mailto:azoeb27@gmail.com">azoeb27@gmail.com</a>.';
      }
    });
  }

  /* ============ SELF-SERVICE TOOL FINDER ============ */
  const TOOLS = [
    { n:'Slang.ai', u:'https://www.slang.ai', p:'$399–599/mo', w:'AI voice agent that answers every call 24/7 and books reservations.', t:['full-service','fast-casual','qsr'], pr:['missed-calls'], g:['guests','time'], s:['single','small','multi'], b:['modest','serious'], fit:'Recovers takeout and booking calls lost during the rush.', not:'Not worth it if your phone rarely rings.' },
    { n:'Loman.ai', u:'https://loman.ai', p:'from $199/mo', w:'AI phone agent that takes orders and payment with no per-minute fees.', t:['qsr','fast-casual','full-service'], pr:['missed-calls'], g:['guests','time'], s:['single','small','multi'], b:['lean','modest'], fit:'Captures phone orders around the clock at a flat price.', not:'Order value depends on solid POS integration.' },
    { n:'ChowNow', u:'https://www.chownow.com', p:'$99–199/mo', w:'Commission-free online ordering on your own website.', t:['qsr','fast-casual','full-service'], pr:['delivery-cost','margins'], g:['guests','costs'], s:['single','small','multi'], b:['lean','modest'], fit:'Keeps the 15–30% the delivery apps would take.', not:"It's ordering + marketing, not a recommendation engine." },
    { n:'Owner.com', u:'https://www.owner.com', p:'$249–499/mo', w:'All-in-one website, ordering, and marketing for repeat orders.', t:['qsr','fast-casual','full-service'], pr:['retention','delivery-cost'], g:['guests','costs'], s:['single','small'], b:['modest'], fit:'Built to win commission-free repeat orders for independents.', not:'Less suited to large chains.' },
    { n:'Toast', u:'https://pos.toasttab.com', p:'from $69/mo + hardware', w:'Restaurant OS: POS, online ordering, AI upsell, KDS, payroll.', t:['qsr','fast-casual','full-service'], pr:['visibility','connect','slow-service'], g:['connect','guests','time'], s:['single','small','multi'], b:['modest','serious'], fit:'One connected system instead of a dozen disconnected tools.', not:'Ecosystem lock-in; all-in cost often $1,000+/mo.' },
    { n:'Square for Restaurants', u:'https://squareup.com/us/en/point-of-sale/restaurants', p:'$0–60/mo', w:'Low-cost POS and online ordering with built-in basics.', t:['qsr','fast-casual','full-service'], pr:['visibility','connect'], g:['connect','time'], s:['single','small'], b:['lean','modest'], fit:'Easy, affordable starting point that just works.', not:'Lighter analytics than enterprise platforms.' },
    { n:'OpenTable', u:'https://www.opentable.com', p:'$149–499/mo + cover fees', w:'Reservations, waitlist, and deposit/hold policies that cut no-shows.', t:['full-service','fine-dining'], pr:['slow-service','retention'], g:['guests'], s:['single','small','multi'], b:['modest'], fit:'Biggest diner network; deposits cut no-shows sharply.', not:'Per-cover fees add up; irrelevant to QSR.' },
    { n:'SevenRooms', u:'https://sevenrooms.com', p:'enterprise, ~$499+/mo', w:'Reservations + guest data + seating AI + marketing for full-service.', t:['full-service','fine-dining'], pr:['retention'], g:['guests','connect'], s:['small','multi'], b:['serious'], fit:'Best-in-class guest profiles and personalization.', not:'Enterprise pricing; overkill for a single casual spot.' },
    { n:'Resy', u:'https://resy.com', p:'~$249/mo', w:'Reservations and waitlist with no per-cover fees.', t:['full-service','fine-dining'], pr:['retention','slow-service'], g:['guests'], s:['single','small','multi'], b:['modest'], fit:'Strong reservations without OpenTable cover fees.', not:'Smaller network in some markets.' },
    { n:'GatherUp', u:'https://gatherup.com', p:'$99/mo (single)', w:'Generates reviews and drafts on-brand replies.', t:['qsr','fast-casual','full-service','fine-dining'], pr:['reviews','retention'], g:['guests'], s:['single','small'], b:['lean','modest'], fit:'A 1★ rating lift can mean 5–9% more revenue for an independent.', not:'Big chains see less rating-to-revenue effect.' },
    { n:'Podium', u:'https://www.podium.com', p:'$399+/mo (+$99 AI)', w:'Reviews, two-way texting, and AI replies in one inbox.', t:['fast-casual','full-service'], pr:['reviews','retention'], g:['guests'], s:['single','small','multi'], b:['modest'], fit:'Consolidates reviews and guest messaging with AI.', not:'Add-ons (AI, 10DLC) push the real cost higher.' },
    { n:'Birdeye', u:'https://birdeye.com', p:'$299–449/loc', w:'Reviews, listings, and AI across many locations.', t:['fast-casual','full-service'], pr:['reviews','visibility'], g:['guests'], s:['small','multi'], b:['modest','serious'], fit:'Built to manage reputation across multiple locations.', not:'Priced per location; heavy for a single site.' },
    { n:'Klaviyo', u:'https://www.klaviyo.com', p:'free–$150/mo', w:'Email & SMS marketing that scales from free as your list grows.', t:['qsr','fast-casual','full-service'], pr:['retention'], g:['guests'], s:['single','small'], b:['lean','modest'], fit:'Powerful win-back and campaigns at a fair entry price.', not:'Someone must build the flows — it’s a tool, not done-for-you.' },
    { n:'Toast / Square Loyalty', u:'https://pos.toasttab.com/products/loyalty', p:'$45–99/mo', w:'Points/visits loyalty bundled with your POS.', t:['qsr','fast-casual','full-service'], pr:['retention'], g:['guests'], s:['single','small'], b:['lean','modest'], fit:'Simple, cheap loyalty that drives repeat visits.', not:'Basic — not AI personalization.' },
    { n:'Paytronix / Punchh', u:'https://www.paytronix.com', p:'enterprise quote', w:'AI-personalized offers and a customer data platform.', t:['qsr','fast-casual'], pr:['retention'], g:['guests'], s:['multi'], b:['serious'], fit:'One-to-one AI offers for high-frequency, multi-unit brands.', not:'Needs data scale — not for single units.' },
    { n:'7shifts', u:'https://www.7shifts.com', p:'free–$77/loc', w:'Demand-based scheduling that trims overtime and saves admin hours.', t:['qsr','fast-casual','full-service','fine-dining'], pr:['labor'], g:['costs','time'], s:['single','small','multi'], b:['lean','modest'], fit:'Fast payback from less overtime and manager time saved.', not:'Forecasting features need decent sales history.' },
    { n:'Lineup.ai', u:'https://www.lineup.ai', p:'$149/mo/loc', w:'Forecasts sales and labor by the hour from your own data.', t:['qsr','fast-casual'], pr:['labor','waste'], g:['costs'], s:['single','small','multi'], b:['modest'], fit:'Staff and prep to real demand instead of guesswork.', not:'Marginal for low-cover, reservation-driven rooms.' },
    { n:'MarginEdge', u:'https://www.marginedge.com', p:'$330/mo flat', w:'Invoice automation, live food cost, and bill pay.', t:['full-service','fast-casual','fine-dining'], pr:['margins','waste','visibility'], g:['costs','connect'], s:['single','small','multi'], b:['modest'], fit:'Kills back-office hours and 2–5% of food cost.', not:'Flat fee can outrun a tiny single QSR’s savings.' },
    { n:'xtraCHEF (by Toast)', u:'https://pos.toasttab.com/products/xtrachef', p:'free tier–$349/mo', w:'Invoice OCR and food-cost tracking, free starter tier on Toast.', t:['full-service','fast-casual'], pr:['margins','visibility'], g:['costs'], s:['single','small'], b:['lean','modest'], fit:'Low-risk way to start controlling food cost.', not:'Best value only if you’re on Toast.' },
    { n:'Otter', u:'https://www.tryotter.com', p:'$20–219/mo', w:'All delivery apps in one screen, injected into your POS.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','slow-service'], g:['costs','time','connect'], s:['single','small','multi'], b:['lean','modest'], fit:'Ends tablet chaos and re-keying during a rush.', not:'Low value if you do few delivery orders.' },
    { n:'ItsaCheckmate', u:'https://www.itsacheckmate.com', p:'$85–100/mo/loc', w:'Menu sync and order injection across delivery marketplaces.', t:['qsr','fast-casual','full-service','ghost'], pr:['delivery-cost','connect'], g:['connect','time'], s:['single','small','multi'], b:['lean','modest'], fit:'Transparent pricing; one menu pushed everywhere.', not:'Only pays back at meaningful delivery volume.' },
    { n:'Winnow', u:'https://www.winnowsolutions.com', p:'~$5k + $200–500/mo', w:'Camera-and-scale vision AI that pinpoints food waste.', t:['full-service','fine-dining'], pr:['waste','margins'], g:['costs'], s:['small','multi'], b:['serious'], fit:'Cuts food purchasing 2–8%; ~7:1 ROI in buffets/banquets.', not:'Needs high prep/buffet waste volume to pay off.' },
    { n:'Too Good To Go', u:'https://www.toogoodtogo.com', p:'$89/yr + ~$1.79/bag', w:'Sell end-of-day surplus to new customers.', t:['qsr','fast-casual','full-service'], pr:['waste'], g:['costs','guests'], s:['single','small','multi'], b:['lean'], fit:'Near-zero cost way to recover money on leftovers.', not:'Little use with minimal end-of-day inventory.' },
    { n:'GlacierGrid', u:'https://www.glaciergrid.com', p:'$30/mo + $12.50/sensor', w:'24/7 cooler/freezer temperature monitoring.', t:['qsr','fast-casual','full-service','fine-dining'], pr:['visibility','margins'], g:['costs'], s:['single','small','multi'], b:['lean','modest'], fit:'One avoided walk-in failure pays for years.', not:'Limited value with little refrigerated inventory.' },
    { n:'Fresh KDS', u:'https://fresh.technology', p:'$39/screen/mo', w:'Kitchen display that routes and times orders by station.', t:['qsr','fast-casual','full-service'], pr:['slow-service','connect'], g:['time','connect'], s:['single','small','multi'], b:['lean'], fit:'Quick payback, fewer mistakes, faster tickets.', not:'Less critical at very low ticket volume.' },
    { n:'Solink', u:'https://solink.com', p:'quote', w:'Links POS exceptions to video to catch theft and voids.', t:['fast-casual','full-service'], pr:['visibility','margins'], g:['costs'], s:['small','multi'], b:['modest'], fit:'Strong loss-prevention ROI across multiple locations.', not:'Owner-present single venues may not need it.' },
  ];

  const TYPE_LABEL = { qsr:'quick-service', 'fast-casual':'fast-casual', 'full-service':'full-service', 'fine-dining':'fine dining', ghost:'delivery-only' };
  const PROBLEM_LABEL = { 'missed-calls':'missed phone orders', 'slow-service':'slow service', labor:'labor cost', waste:'food waste', retention:'repeat business', reviews:'online reviews', 'delivery-cost':'delivery commissions', margins:'margins', visibility:'visibility into your numbers' };
  const BUDGET_RANK = { lean:0, modest:1, serious:2 };

  const finder = document.getElementById('finder');
  if (!finder) return;
  const resultsEl = document.getElementById('finderResults');
  const closeEl = document.getElementById('finderClose');
  const sels = ['f-type','f-size','f-problem','f-goal','f-comfort','f-budget'].map((id) => document.getElementById(id));

  function render() {
    const [type, size, problem, goal, comfort, budget] = sels.map((s) => s.value);

    const scored = TOOLS
      .filter((t) => t.pr.includes(problem))
      .map((t) => {
        let score = 4;
        if (t.t.includes(type)) score += 2;
        if (t.s.includes(size)) score += 1;
        if (t.g.includes(goal)) score += 1;
        if (t.b.includes(budget)) score += 1;
        return { t, score };
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);

    const lead = `<p class="finder__lead">For a ${TYPE_LABEL[type]} restaurant focused on ${PROBLEM_LABEL[problem]}, here's what's worth a look:</p>`;

    const cards = scored.map(({ t }) => {
      const cautions = [t.not];
      if (!t.t.includes(type)) cautions.push(`more commonly a fit for ${t.t.map((x) => TYPE_LABEL[x]).slice(0,2).join(' / ')}`);
      if (BUDGET_RANK[budget] < Math.min(...t.b.map((x) => BUDGET_RANK[x]))) cautions.push('may stretch a ' + budget + ' budget');
      return `<div class="tool">
        <span class="tool__name">${t.n}</span>
        <span class="tool__price">${t.p}</span>
        <p class="tool__what">${t.w}</p>
        <p class="tool__why"><span class="yes">Why it fits:</span> ${t.fit}</p>
        <p class="tool__why"><span class="no">Watch-out:</span> ${cautions.join(' · ')}</p>
        <a class="tool__link" href="${t.u}" target="_blank" rel="noopener">Visit ${t.n} →</a>
      </div>`;
    }).join('');

    resultsEl.innerHTML = scored.length
      ? lead + cards
      : '<p class="finder__empty">Adjust the sentence above and I’ll show matching tools.</p>';

    const closeMsg = {
      low: "Honestly? Wiring these together, integrating your POS, and keeping them running is a lot — and easy to get wrong. That's exactly why my team and I exist: we do it end to end, then stay with you as it evolves.",
      mid: "You could set these up yourself — the links are right there. But choosing among them, integrating your POS, and proving the ROI is the hard part. That's what my team and I do, end to end — and we stay with you for the long run.",
      high: "You could clearly wire these up yourself. The real work is making them play together, securing them, and proving the ROI over time — to a production standard. That's where my team and I turn good tools into a real edge.",
    }[comfort];

    closeEl.innerHTML = `<div class="finder__closebox">
      <h3>Do it yourself — or let us make it a game-changer.</h3>
      <p>${closeMsg}</p>
      <a href="#contact" class="btn btn--primary">Book a free video call</a>
    </div>`;
  }

  sels.forEach((s) => s.addEventListener('change', render));
  render();
})();
