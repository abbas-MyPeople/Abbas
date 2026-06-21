/* AZ Restaurant Partners — interactions + self-service tool finder */
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
        note.textContent = 'Please add your name and email so we can reach you.';
        note.classList.add('error'); return;
      }
      btn.disabled = true; const original = btn.textContent; btn.textContent = 'Sending…';
      note.classList.remove('error');
      const payload = {
        name: form.name.value, restaurant: form.restaurant.value, email: form.email.value,
        phone: form.phone.value, message: form.message.value,
        _subject: 'New free-call request — AZ Restaurant Partners', _template: 'table', _captcha: 'false',
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
          "<p>We'll personally reply to set up your free call, usually within a day.</p>";
        form.appendChild(ok);
      } catch (err) {
        btn.disabled = false; btn.textContent = original;
        note.classList.add('error');
        note.innerHTML = 'Something went wrong sending the form. Please email us directly at ' +
          '<a href="mailto:azoeb27@gmail.com">azoeb27@gmail.com</a>.';
      }
    });
  }

  /* ============ SELF-SERVICE TOOL FINDER ============ */
  // c = category · t = restaurant types · pr = problems · g = goals · s = sizes · b = budget tiers
  // Prices marked "est." are estimates (vendor publishes quote-only pricing) — confirm on a live quote.
  const TOOLS = [
    // ---------- POS ----------
    { n:'Toast', c:'POS', u:'https://pos.toasttab.com', p:'from $69/mo + hardware', w:'All-in-one restaurant OS: POS, ordering, KDS, payroll.', t:['qsr','fast-casual','full-service','fine-dining','ghost'], pr:['visibility','connect','slow-service'], g:['connect','time'], s:['single','small','multi'], b:['modest','serious'], fit:'One connected system instead of a dozen disconnected tools.', not:'Hardware lock-in; all-in cost often $1,000+/mo.' },
    { n:'Square for Restaurants', c:'POS', u:'https://squareup.com/us/en/point-of-sale/restaurants', p:'$0–149/mo', w:'iPad POS unified with Square payments and ecosystem.', t:['qsr','fast-casual','full-service','ghost'], pr:['visibility','connect'], g:['connect','time'], s:['single','small'], b:['lean','modest','serious'], fit:'Affordable, easy starting point that just works.', not:'Locked to Square processing; thin for complex coursing.' },
    { n:'Lightspeed Restaurant', c:'POS', u:'https://www.lightspeedhq.com/pos/restaurant', p:'$69–399/mo + payments', w:'Cloud POS with deep inventory, analytics, multi-location tools.', t:['full-service','fine-dining','fast-casual'], pr:['visibility','connect'], g:['connect','costs'], s:['small','multi'], b:['modest','serious'], fit:'Strong inventory and reporting for serious operators.', not:'Higher tiers pricey for a tiny shop.' },
    { n:'SpotOn', c:'POS', u:'https://www.spoton.com/restaurant-pos', p:'$0–135/mo + payments', w:'Restaurant POS plus marketing, loyalty, reviews and strong support.', t:['qsr','fast-casual','full-service'], pr:['visibility','connect','retention'], g:['connect','guests'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'POS bundled with guest-marketing and great support.', not:'Must use SpotOn hardware/processing; early-switch fee.' },
    { n:'TouchBistro', c:'POS', u:'https://www.touchbistro.com', p:'from $69/mo', w:'iPad POS purpose-built for tableside full-service.', t:['full-service','fine-dining','fast-casual'], pr:['visibility','slow-service'], g:['connect','time'], s:['single','small'], b:['modest','serious'], fit:'Built for tableside, coursing, and floor management.', not:'Add-ons inflate cost; weak for high-volume QSR.' },
    { n:'Clover', c:'POS', u:'https://www.clover.com', p:'~$15–90/mo/device + processing', w:'Flexible POS hardware and app marketplace, sold via banks/resellers.', t:['qsr','fast-casual','full-service'], pr:['visibility','connect'], g:['connect'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Affordable, customizable POS with a big app store.', not:'Reseller pricing varies wildly; rates depend on merchant account.' },
    { n:'Revel Systems', c:'POS', u:'https://revelsystems.com', p:'from $99/mo/terminal + ~$674 install', w:'iPad POS for high-volume and multi-unit QSR/chains.', t:['qsr','fast-casual','full-service'], pr:['visibility','connect'], g:['connect'], s:['small','multi'], b:['modest','serious'], fit:'Robust POS built for volume and many locations.', not:'3-yr contract + 2-terminal minimum; high setup.' },
    // ---------- Online ordering ----------
    { n:'ChowNow', c:'Online ordering', u:'https://www.chownow.com', p:'$119–328/mo', w:'Commission-free branded online ordering, app and marketing.', t:['qsr','fast-casual','full-service'], pr:['delivery-cost','retention'], g:['guests','costs'], s:['single','small'], b:['modest','serious'], fit:'Keeps the 15–30% the delivery apps would take.', not:'Subscription owed even in slow months.' },
    { n:'Owner.com', c:'Online ordering', u:'https://www.owner.com', p:'$499/mo + 5% guest fee', w:'AI-built website, app, ordering, loyalty and marketing in one.', t:['fast-casual','full-service','qsr'], pr:['retention','delivery-cost'], g:['guests','costs'], s:['single','small'], b:['serious'], fit:'Built to win commission-free repeat orders for independents.', not:'Flat $499 steep at low volume; 5% fee passed to guests.' },
    { n:'Square Online', c:'Online ordering', u:'https://squareup.com/us/en/online-store', p:'$0–149/mo', w:'Free site builder with pickup/delivery ordering on Square.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost'], g:['guests','costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Zero-cost way to launch commission-free ordering.', not:'Generic commerce tool; lighter restaurant upsell.' },
    { n:'BentoBox', c:'Online ordering', u:'https://www.getbento.com', p:'~$149–479/mo', w:'Premium restaurant website/CMS plus commission-free ordering & catering.', t:['full-service','fine-dining','fast-casual'], pr:['delivery-cost','retention'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Best-looking brand site with ordering built in.', not:'Strength is website/brand, not high-volume ordering.' },
    { n:'Slice', c:'Online ordering', u:'https://slice.com', p:'$69/mo + ~$2.25/order', w:'Commission-free online ordering and marketing built for pizzerias.', t:['qsr','fast-casual'], pr:['delivery-cost'], g:['guests','costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Purpose-built, low-cost ordering for pizza shops.', not:'Pizza-only — not for other concepts.' },
    { n:'Olo', c:'Online ordering', u:'https://www.olo.com', p:'est. ~$149–600+/mo/loc + setup', w:'Enterprise digital ordering, delivery dispatch and channel management.', t:['fast-casual','full-service','ghost'], pr:['delivery-cost','retention','connect'], g:['guests','connect'], s:['multi'], b:['serious'], fit:'Powers ordering across channels for big multi-unit brands.', not:'Built for chains; overkill for a single independent.' },
    // ---------- Reservations ----------
    { n:'OpenTable', c:'Reservations', u:'https://www.opentable.com', p:'$149–499/mo + cover fees', w:'Reservations and waitlist on the largest US diner network.', t:['full-service','fine-dining'], pr:['slow-service','retention'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Biggest diner network; deposits cut no-shows sharply.', not:'Per-cover fees add up; irrelevant to QSR.' },
    { n:'Resy', c:'Reservations', u:'https://resy.com', p:'from ~$249/mo', w:'Reservations, waitlist and table management (Amex).', t:['full-service','fine-dining'], pr:['retention','slow-service'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Strong reservations without per-cover fees.', not:'Skews trendy/urban; weak for QSR.' },
    { n:'Tock', c:'Reservations', u:'https://www.exploretock.com', p:'$199–699/mo (+2% prepaid)', w:'Reservations with prepaid deposits and event ticketing.', t:['fine-dining','full-service','ghost'], pr:['retention','slow-service'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Deposits/prepaid experiences crush no-shows.', not:'Prepaid model overkill for casual walk-in venues.' },
    { n:'Yelp Guest Manager', c:'Reservations', u:'https://business.yelp.com/restaurants/products/yelp-guest-manager/', p:'~$199–299/mo, no cover fees', w:'Reservations and waitlist across Yelp/Google/Apple.', t:['fast-casual','full-service'], pr:['slow-service','retention'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Wide discovery, no per-cover fees.', not:'Tied to the Yelp ecosystem.' },
    { n:'SevenRooms', c:'Reservations', u:'https://sevenrooms.com', p:'~$795–2,500/mo', w:'Reservations + CRM, marketing and loyalty; you own the data.', t:['full-service','fine-dining'], pr:['retention'], g:['guests','connect'], s:['small','multi'], b:['serious'], fit:'Best-in-class guest profiles and personalization.', not:'Pricey/complex for a single small venue.' },
    { n:'Waitwhile', c:'Reservations', u:'https://waitwhile.com', p:'free–~$31+/mo', w:'Waitlist and queue management for walk-in-heavy venues.', t:['qsr','fast-casual'], pr:['slow-service'], g:['guests','time'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Simple, cheap waitlist that cuts the door line.', not:'Not a diner-network reservation platform.' },
    // ---------- AI phone ----------
    { n:'Slang.ai', c:'AI phone', u:'https://www.slang.ai', p:'$399–599/mo', w:'AI voice agent answers calls and books reservations 24/7.', t:['full-service','fine-dining','fast-casual'], pr:['missed-calls'], g:['guests','time'], s:['single','small','multi'], b:['modest','serious'], fit:'Recovers booking and FAQ calls lost during the rush.', not:'Texts an order link rather than taking orders.' },
    { n:'Loman.ai', c:'AI phone', u:'https://loman.ai', p:'from $199/mo', w:'AI phone agent that takes orders, payment and reservations.', t:['qsr','fast-casual','full-service','ghost'], pr:['missed-calls'], g:['guests','time'], s:['single','small','multi'], b:['modest','serious'], fit:'Captures phone orders around the clock.', not:'Base-minute caps; younger vendor.' },
    { n:'Newo.ai', c:'AI phone', u:'https://newo.ai', p:'free–$799/mo', w:'AI voice + text agent for calls, reservations, delivery/catering.', t:['full-service','fast-casual','fine-dining'], pr:['missed-calls'], g:['guests','time'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Flexible voice+text across many use cases.', not:'Conversation caps per tier; horizontal, less specialized.' },
    { n:'Goodcall', c:'AI phone', u:'https://www.goodcall.com', p:'$59–199/mo', w:'AI phone agent / virtual receptionist for service businesses.', t:['full-service','fast-casual'], pr:['missed-calls'], g:['guests','time'], s:['single','small'], b:['lean','modest','serious'], fit:'Cheap way to stop sending callers to voicemail.', not:'Per-unique-caller pricing balloons; not restaurant-native.' },
    // ---------- AI drive-thru ----------
    { n:'SoundHound Dynamic Drive-Thru', c:'AI drive-thru', u:'https://www.soundhound.com/voice-ai-products/dynamic-drive-thru/', p:'est. ~$300–500/mo/loc', w:'GenAI voice ordering for drive-thru lanes, POS-integrated.', t:['qsr','fast-casual'], pr:['slow-service','labor'], g:['time','guests'], s:['multi'], b:['serious'], fit:'Speeds the lane and never forgets to upsell.', not:'Enterprise/brand-level deals; overkill for one store.' },
    { n:'ConverseNow', c:'AI drive-thru', u:'https://conversenow.ai', p:'est. ~$750–2,000/mo/loc', w:'Voice AI for phone and drive-thru ordering with upsell.', t:['qsr','fast-casual','ghost'], pr:['slow-service','missed-calls','labor'], g:['guests','time'], s:['multi'], b:['serious'], fit:'Handles peak ordering volume across many lanes/lines.', not:'Quote-only; built for large chains.' },
    { n:'Hi Auto', c:'AI drive-thru', u:'https://hi.auto', p:'est. ~$500–1,500/mo/loc', w:'Voice AI for drive-thru and phone ordering for QSR chains.', t:['qsr','fast-casual'], pr:['slow-service','labor','missed-calls'], g:['time'], s:['multi'], b:['serious'], fit:'Automates high-volume ordering with upsell.', not:'Chain-focused; limited fit for full-service/single.' },
    // ---------- Chatbot & social ----------
    { n:'Popmenu', c:'Chatbot & social', u:'https://get.popmenu.com', p:'~$200–499/mo', w:'AI phone + text answering plus interactive menu and marketing.', t:['qsr','fast-casual','full-service'], pr:['missed-calls','retention'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Engaging menu + AI answering in one bundle.', not:'Bundled suite; hard to buy a la carte.' },
    { n:'ChatFood (Deliverect)', c:'Chatbot & social', u:'https://www.deliverect.com/en/integrations/chatfood', p:'est. ~$50–150/mo', w:'Ordering via Instagram, Facebook, WhatsApp plus QR dine-in pay.', t:['qsr','fast-casual','ghost'], pr:['retention','delivery-cost'], g:['guests'], s:['small','multi'], b:['modest','serious'], fit:'Turns social channels into ordering channels.', not:'Strongest in EMEA; best if already on Deliverect.' },
    { n:'Tillster', c:'Chatbot & social', u:'https://www.tillster.com', p:'est. enterprise (~$ per loc)', w:'Digital ordering across web/app/kiosk/call-center with AI tools.', t:['qsr','fast-casual'], pr:['retention','delivery-cost'], g:['guests'], s:['multi'], b:['serious'], fit:'Omnichannel ordering for high-volume brands.', not:'Enterprise/chain-focused; overkill for single sites.' },
    // ---------- Marketing ----------
    { n:'Klaviyo', c:'Marketing', u:'https://www.klaviyo.com', p:'free–$150+/mo', w:'Unified email + SMS with deep segmentation and POS integrations.', t:['fast-casual','full-service','ghost'], pr:['retention'], g:['guests'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Powerful win-back and campaigns; starts free.', not:'Active-profile billing inflates on big lists.' },
    { n:'Attentive', c:'Marketing', u:'https://www.attentive.com', p:'$300+/mo + per-SMS', w:'Enterprise SMS (and email) marketing at scale.', t:['qsr','fast-casual'], pr:['retention'], g:['guests'], s:['multi'], b:['serious'], fit:'High-volume SMS that drives repeat traffic.', not:'High minimums + contracts; too costly for single sites.' },
    { n:'SlickText', c:'Marketing', u:'https://www.slicktext.com', p:'free–$139+/mo', w:'SMS/text marketing with keywords and automation.', t:['qsr','fast-casual','full-service'], pr:['retention'], g:['guests'], s:['single','small'], b:['lean','modest','serious'], fit:'Simple, affordable text marketing.', not:'SMS-only (light email); per-credit penalizes high volume.' },
    { n:'Marsello', c:'Marketing', u:'https://www.marsello.com', p:'from ~$60/mo/site', w:'Loyalty + email + SMS for hospitality, POS-connected.', t:['fast-casual','full-service'], pr:['retention'], g:['guests'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Loyalty and marketing in one connected tool.', not:'Marketing/SMS are paid add-ons that stack.' },
    // ---------- Reviews ----------
    { n:'GatherUp', c:'Reviews', u:'https://gatherup.com', p:'$99/mo (single)', w:'Generates reviews and drafts on-brand replies.', t:['qsr','fast-casual','full-service','fine-dining'], pr:['reviews','retention'], g:['guests'], s:['single','small'], b:['lean','modest','serious'], fit:'A 1★ lift can mean 5–9% more revenue for an independent.', not:'Big chains see less rating-to-revenue effect.' },
    { n:'Ovation', c:'Reviews', u:'https://ovationup.com', p:'$79–259/mo/loc', w:'SMS 2-question survey that drives reviews and guest recovery.', t:['qsr','fast-casual','full-service'], pr:['reviews','retention'], g:['guests'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Catches unhappy guests privately, sends happy ones public.', not:'Lower tiers gate review-response/insights.' },
    { n:'Marqii', c:'Reviews', u:'https://marqii.com', p:'$74.99–149.99/mo/loc', w:'Listings + reviews + menu sync across 50+ platforms.', t:['qsr','fast-casual','full-service','fine-dining'], pr:['reviews','visibility'], g:['guests'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Keeps listings accurate and reviews answered everywhere.', not:'Listings-focused; lighter on guest surveys.' },
    { n:'Podium', c:'Reviews', u:'https://www.podium.com', p:'$399+/mo (+$99 AI)', w:'SMS review requests + customer messaging and AI replies.', t:['fast-casual','full-service'], pr:['reviews','retention'], g:['guests'], s:['single','small','multi'], b:['serious'], fit:'Consolidates reviews and guest messaging with AI.', not:'Add-ons (AI, 10DLC) push the real cost higher.' },
    { n:'Birdeye', c:'Reviews', u:'https://birdeye.com', p:'$299–449/mo/loc', w:'Multi-site review generation/monitoring with AI replies.', t:['fast-casual','full-service','fine-dining'], pr:['reviews','visibility'], g:['guests'], s:['small','multi'], b:['modest','serious'], fit:'Built to manage reputation across many locations.', not:'Per-location + onboarding cost; heavy for one site.' },
    { n:'Tattle', c:'Reviews', u:'https://get.tattleapp.com', p:'from $59/mo/loc', w:'Causation-based guest surveys integrated with POS/loyalty.', t:['fast-casual','full-service'], pr:['reviews','visibility'], g:['guests'], s:['small','multi'], b:['lean','modest','serious'], fit:'Pinpoints exactly what to fix to lift satisfaction.', not:'Feedback focus, not public-review generation.' },
    // ---------- Loyalty & CRM ----------
    { n:'Toast / Square Loyalty', c:'Loyalty & CRM', u:'https://pos.toasttab.com/products/loyalty', p:'$45–185/mo', w:'Simple points/visits loyalty bundled with your POS.', t:['qsr','fast-casual','full-service'], pr:['retention'], g:['guests'], s:['single','small'], b:['lean','modest','serious'], fit:'Cheap, easy loyalty that drives repeat visits.', not:'Basic — not AI personalization; POS lock-in.' },
    { n:'TapMango', c:'Loyalty & CRM', u:'https://tapmango.com', p:'from ~$79/mo', w:'Loyalty + promotions, mobile ordering and surveys for SMBs.', t:['qsr','fast-casual'], pr:['retention'], g:['guests'], s:['single','small'], b:['modest','serious'], fit:'Feature-rich loyalty for independents.', not:'Real cost climbs with add-ons.' },
    { n:'Incentivio', c:'Loyalty & CRM', u:'https://incentivio.com', p:'from ~$249/mo', w:'Ordering + loyalty + marketing with white-label apps.', t:['fast-casual','full-service','qsr'], pr:['retention'], g:['guests'], s:['small','multi'], b:['modest','serious'], fit:'Branded app + loyalty + marketing together.', not:'Depth/cost overshoots single-unit operators.' },
    { n:'Como', c:'Loyalty & CRM', u:'https://como.com', p:'est. ~$100–300/mo/loc', w:'AI-personalized loyalty with branded apps and deep POS integration.', t:['qsr','fast-casual','full-service'], pr:['retention'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Personalized loyalty + app without enterprise scale.', not:'Quote-only; needs a sales process to evaluate.' },
    { n:'Paytronix', c:'Loyalty & CRM', u:'https://paytronix.com', p:'est. ~$500–2,000/mo/loc', w:'Loyalty, CRM, ordering and AI personalization suite.', t:['qsr','fast-casual','full-service'], pr:['retention'], g:['guests'], s:['multi'], b:['serious'], fit:'One-to-one AI offers for high-frequency, multi-unit brands.', not:'Enterprise-oriented; pricing opaque.' },
    { n:'Thanx', c:'Loyalty & CRM', u:'https://www.thanx.com', p:'est. ~$ enterprise (3-yr)', w:'Loyalty + CRM + agentic AI marketing for chains.', t:['fast-casual','full-service'], pr:['retention'], g:['guests'], s:['multi'], b:['serious'], fit:'Autonomous AI campaigns across many locations.', not:'Enterprise-priced; not aimed at single independents.' },
    { n:'Bikky', c:'Loyalty & CRM', u:'https://bikky.com', p:'est. ~$200/mo/loc', w:'Restaurant-only CDP unifying POS/ordering/payments/loyalty data.', t:['qsr','fast-casual'], pr:['retention','visibility'], g:['guests','connect'], s:['multi'], b:['serious'], fit:'The data backbone for serious multi-unit marketing.', not:'CDP/analytics, multi-unit only — not for single units.' },
    // ---------- Inventory & purchasing ----------
    { n:'MarketMan', c:'Inventory & purchasing', u:'https://www.marketman.com', p:'~$199/mo + setup', w:'Inventory, purchasing and recipe costing with POS sync.', t:['full-service','fast-casual','qsr'], pr:['margins','waste','visibility'], g:['costs','connect'], s:['small','multi'], b:['modest','serious'], fit:'Tightens ordering and food cost across vendors.', not:'Install fee + per-loc cost stings tiny single shops.' },
    { n:'MarginEdge', c:'Inventory & purchasing', u:'https://www.marginedge.com', p:'~$330/mo flat', w:'Invoice automation, live food cost and bill pay.', t:['full-service','fast-casual','fine-dining'], pr:['margins','waste','visibility'], g:['costs','connect'], s:['single','small','multi'], b:['modest','serious'], fit:'Kills back-office hours and 2–5% of food cost.', not:'Flat fee can outrun a tiny single QSR’s savings.' },
    { n:'BlueCart', c:'Inventory & purchasing', u:'https://www.bluecart.com', p:'$10–200/mo', w:'B2B wholesale ordering/procurement plus inventory.', t:['full-service','fast-casual','ghost'], pr:['margins','visibility'], g:['costs','connect'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Streamlines supplier ordering at a low entry price.', not:'Procurement-first; lighter on costing depth.' },
    { n:'Notch', c:'Inventory & purchasing', u:'https://www.notch.financial', p:'est. ~$ quote', w:'Digital supplier ordering, invoicing and AP across the supply chain.', t:['full-service','fast-casual','ghost'], pr:['margins','visibility'], g:['costs','connect'], s:['small','multi'], b:['modest','serious'], fit:'Centralizes supplier ordering and invoices.', not:'Strongest in Canada; ordering-focused, opaque pricing.' },
    { n:'Crunchtime', c:'Inventory & purchasing', u:'https://www.crunchtime.com', p:'est. ~$400–800/mo/loc', w:'Enterprise inventory, ordering and food-cost (AvT) for chains.', t:['qsr','fast-casual','full-service'], pr:['margins','waste','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Gold-standard control at scale.', not:'Built for large chains, not small shops.' },
    // ---------- Forecasting ----------
    { n:'Lineup.ai', c:'Forecasting', u:'https://www.lineup.ai', p:'~$149/mo/loc', w:'AI sales/labor/item forecasts from weather, events, history.', t:['qsr','fast-casual','full-service'], pr:['labor','waste'], g:['costs'], s:['single','small','multi'], b:['modest','serious'], fit:'Staff and prep to real demand, not guesswork.', not:'Forecasting-only; needs ~6 months of data.' },
    { n:'Tenzo', c:'Forecasting', u:'https://www.gotenzo.com', p:'from ~$600/yr', w:'Analytics plus demand forecasting across locations.', t:['fast-casual','full-service','ghost'], pr:['labor','waste','visibility'], g:['costs'], s:['small','multi'], b:['modest','serious'], fit:'Forecasts plus a unified ops dashboard.', not:'Needs ~90 days history; analytics-led.' },
    { n:'5-Out', c:'Forecasting', u:'https://www.5out.io', p:'est. ~$150–400/mo', w:'ML demand forecasting feeding labor and purchasing decisions.', t:['full-service','fast-casual','qsr'], pr:['labor','waste'], g:['costs'], s:['small','multi'], b:['modest','serious'], fit:'Turns forecasts into concrete staffing/ordering calls.', not:'No public pricing; newer/smaller vendor.' },
    // ---------- Scheduling ----------
    { n:'7shifts', c:'Scheduling', u:'https://www.7shifts.com', p:'free–$150/mo/loc', w:'Scheduling, forecasting, tips and team chat.', t:['qsr','fast-casual','full-service','fine-dining'], pr:['labor'], g:['costs','time'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Fast payback from less overtime and saved admin time.', not:'Add-ons (tips, tasks) stack cost per location.' },
    { n:'Homebase', c:'Scheduling', u:'https://www.joinhomebase.com', p:'free–$99.95/mo/loc', w:'Scheduling, time tracking, payroll and hiring for SMBs.', t:['qsr','fast-casual','full-service'], pr:['labor'], g:['costs','time'], s:['single','small'], b:['lean','modest','serious'], fit:'Free for one location; covers the basics well.', not:'Per-location pricing jumps fast for multi-unit.' },
    { n:'Deputy', c:'Scheduling', u:'https://www.deputy.com', p:'$5–9/user/mo', w:'Scheduling, demand forecasting and biometric clock-ins.', t:['fast-casual','full-service'], pr:['labor'], g:['costs','time'], s:['small','multi'], b:['lean','modest','serious'], fit:'Demand-based auto-scheduling at a low per-user price.', not:'Per-user cost rises with large hourly teams.' },
    { n:'Sling', c:'Scheduling', u:'https://getsling.com', p:'free–$3.40/user/mo', w:'Shift scheduling, time-off and labor-cost management.', t:['qsr','fast-casual','ghost'], pr:['labor'], g:['costs','time'], s:['single','small'], b:['lean','modest','serious'], fit:'Free tier covers small teams; cheap to grow.', not:'Lighter forecasting/analytics than rivals.' },
    // ---------- KDS ----------
    { n:'Fresh KDS', c:'Kitchen display (KDS)', u:'https://www.fresh.technology', p:'$15–39/screen/mo', w:'Tablet-based kitchen display; works with Square/Clover and more.', t:['qsr','fast-casual','ghost'], pr:['slow-service','connect'], g:['time','connect'], s:['single','small'], b:['lean','modest','serious'], fit:'Quick payback, fewer mistakes, faster tickets.', not:'Fewer enterprise/multi-unit controls.' },
    { n:'Toast KDS', c:'Kitchen display (KDS)', u:'https://pos.toasttab.com/products/kitchen-display-system', p:'est. ~$ + hardware (Toast)', w:'KDS routing POS/online/handheld orders to kitchen screens.', t:['qsr','fast-casual','full-service'], pr:['slow-service','connect'], g:['time','connect'], s:['single','small','multi'], b:['modest','serious'], fit:'Deeply integrated if you run Toast.', not:'Locked to Toast POS; opaque pricing.' },
    { n:'QSR Automations ConnectSmart', c:'Kitchen display (KDS)', u:'https://qsrautomations.com/connectsmart/kitchen', p:'est. ~$50–150/mo/screen', w:'Enterprise KDS, ticket routing, prep timing and analytics.', t:['full-service','fine-dining'], pr:['slow-service','connect'], g:['time'], s:['multi'], b:['serious'], fit:'Sophisticated kitchen coordination at scale.', not:'Cost/complexity high for small shops.' },
    // ---------- Robotics ----------
    { n:'Miso Robotics Flippy', c:'Robotics', u:'https://www.misorobotics.com', p:'~$3,500/mo + install', w:'AI robot arm that fries and hot-holds food.', t:['qsr','fast-casual'], pr:['labor','slow-service'], g:['costs','time'], s:['multi'], b:['serious'], fit:'Frees crew from the fryer at high volume.', not:'High-volume frying only; ROI needs heavy throughput.' },
    { n:'Hyphen Makeline', c:'Robotics', u:'https://www.hyphen.ai', p:'$50k–100k', w:'Automated under-counter makeline assembling bowls/salads.', t:['fast-casual','ghost'], pr:['labor','slow-service'], g:['costs','time'], s:['multi'], b:['serious'], fit:'Speeds bowl/salad assembly at scale.', not:'Big capex; bowl format only; not plated service.' },
    { n:'Bear Robotics Servi', c:'Robotics', u:'https://www.bearrobotics.ai', p:'$11,990 or ~$293/mo', w:'Autonomous food-running and bussing robot.', t:['full-service','fast-casual'], pr:['labor','slow-service'], g:['time','costs'], s:['small','multi'], b:['modest','serious'], fit:'Takes running/bussing off your servers.', not:'Runs food, doesn’t cook; needs open floor layout.' },
    { n:'Chef Robotics', c:'Robotics', u:'https://www.chefrobotics.ai', p:'est. ~$3,000+/mo (RaaS)', w:'AI robot for high-volume meal/tray assembly.', t:['fast-casual','ghost'], pr:['labor','slow-service'], g:['costs','time'], s:['multi'], b:['serious'], fit:'Consistent high-volume assembly without staffing it.', not:'Aimed at commissary/manufacturing, not in-store lines.' },
    // ---------- Recipe & food cost ----------
    { n:'meez', c:'Recipe & food cost', u:'https://www.getmeez.com', p:'est. ~$49–150/mo', w:'Recipe digitization, scaling and costing for chefs.', t:['fine-dining','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Keeps plate costs and prep consistent across the team.', not:'Lighter on inventory; costing is an add-on.' },
    { n:'Parsley', c:'Recipe & food cost', u:'https://www.parsleycooks.com', p:'$99–299/mo', w:'Recipe management, costing, inventory and nutrition.', t:['full-service','fine-dining'], pr:['margins','visibility'], g:['costs'], s:['single','small'], b:['modest','serious'], fit:'Affordable plate-costing for independents.', not:'Limited for large multi-unit chains.' },
    { n:'ReciPal', c:'Recipe & food cost', u:'https://www.recipal.com', p:'from $59/mo', w:'Recipe costing plus FDA nutrition labels.', t:['ghost','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Cheapest path to costing + compliant labels.', not:'Label/CPG-leaning; not a full ops suite.' },
    { n:'xtraCHEF (by Toast)', c:'Recipe & food cost', u:'https://pos.toasttab.com/products/xtrachef', p:'free tier–$349/mo', w:'Invoice OCR, line-item food cost and recipe analytics.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Low-risk way to start controlling food cost.', not:'Best value only if you’re on Toast.' },
    // ---------- Accounting & payroll ----------
    { n:'Restaurant365', c:'Accounting & payroll', u:'https://www.restaurant365.com', p:'$249–469/mo/loc + setup', w:'Accounting + inventory + scheduling unified for restaurants.', t:['full-service','fast-casual','qsr'], pr:['margins','visibility'], g:['costs','connect'], s:['multi'], b:['serious'], fit:'One ledger across many locations.', not:'Heavy/pricey; overkill for a single independent.' },
    { n:'Ottimate (Plate IQ)', c:'Accounting & payroll', u:'https://ottimate.com', p:'from ~$200/mo', w:'AP automation: AI invoice coding, approvals and payments.', t:['full-service','fast-casual'], pr:['margins','visibility'], g:['costs','time'], s:['small','multi'], b:['modest','serious'], fit:'Turns the invoice pile into automated, coded payments.', not:'AP-only; needs separate accounting/payroll.' },
    { n:'Gusto', c:'Accounting & payroll', u:'https://gusto.com', p:'$49/mo + $6/employee', w:'Full-service payroll, benefits and HR.', t:['qsr','fast-casual','full-service','ghost'], pr:['margins'], g:['time','costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Painless payroll and tax filing.', not:'Generic; lacks tips/POS-native restaurant features.' },
    { n:'Toast Payroll', c:'Accounting & payroll', u:'https://pos.toasttab.com/products/payroll-team-management', p:'~$69–90/mo + ~$9/employee', w:'POS-integrated payroll and scheduling with tip pooling.', t:['qsr','fast-casual','full-service'], pr:['margins'], g:['time','costs'], s:['single','small','multi'], b:['modest','serious'], fit:'Payroll that pulls hours and tips straight from the POS.', not:'Locked to the Toast ecosystem.' },
    { n:'DAVO by Avalara', c:'Accounting & payroll', u:'https://www.davosalestax.com', p:'~$57.99/mo/loc', w:'Auto-sets aside daily sales tax, files and pays it.', t:['qsr','fast-casual','full-service'], pr:['margins'], g:['time','costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Never scramble for sales-tax money again.', not:'Single-purpose (sales tax only).' },
    // ---------- Loss prevention ----------
    { n:'Solink', c:'Loss prevention', u:'https://solink.com', p:'from ~$175/mo/loc', w:'Pairs camera video with POS data to review suspect transactions.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small','multi'], b:['modest','serious'], fit:'Catch theft/voids with video tied to the receipt.', not:'Needs compatible cameras.' },
    { n:'Delaget', c:'Loss prevention', u:'https://www.delaget.com', p:'est. ~$300–600/mo/loc', w:'QSR loss prevention plus back-office analytics; flags exceptions.', t:['qsr','fast-casual'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Surfaces theft and anomalies across many stores.', not:'Built for franchise/multi-unit; overkill for one store.' },
    { n:'DTiQ', c:'Loss prevention', u:'https://www.dtiq.com', p:'est. ~$300–700/mo/loc', w:'Managed video surveillance plus POS exception analytics.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['small','multi'], b:['serious'], fit:'Outsourced video + analytics with human review.', not:'Managed service + hardware; contract-based, higher cost.' },
    { n:'Agilence', c:'Loss prevention', u:'https://www.agilenceinc.com', p:'est. ~$ enterprise', w:'Exception-based reporting / loss analytics across thousands of sites.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Deep exception reporting at enterprise scale.', not:'Overkill for a single site.' },
    // ---------- Energy & maintenance ----------
    { n:'Ecotrak', c:'Energy & maintenance', u:'https://www.ecotrak.com', p:'from $25/mo/loc', w:'Facility/asset CMMS: work orders, preventive maintenance, vendors.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Cheap way to track assets and stop surprise repairs.', not:'Maintenance mgmt, not real-time energy metering.' },
    { n:'Powerhouse Dynamics Open Kitchen', c:'Energy & maintenance', u:'https://powerhousedynamics.com/food-service-solutions/', p:'est. ~$150–400/mo/loc', w:'IoT software unifying HVAC/lighting/equipment with AI energy mgmt.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Cuts the energy bill 10–20% across a portfolio.', not:'Built for chains; overkill for a single location.' },
    { n:'GridPoint', c:'Energy & maintenance', u:'https://www.gridpoint.com/industries/food-beverage/', p:'est. ~$ enterprise + install', w:'Energy intelligence with HVAC/freezer predictive alerts.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Monitors equipment and trims energy across sites.', not:'Enterprise-leaning; hardware install, opaque pricing.' },
    { n:'Verdigris', c:'Energy & maintenance', u:'https://verdigris.co', p:'est. ~$200–500/mo/loc', w:'Circuit-level energy monitoring with AI power/cooling optimization.', t:['full-service','fine-dining','fast-casual'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Pinpoints exactly where power and money leak.', not:'Panel-level install; multi-site focus.' },
    // ---------- Food safety ----------
    { n:'Therma', c:'Food safety', u:'https://www.hellotherma.com', p:'from $10/mo/sensor', w:'Wireless temp/humidity sensors with 24/7 spoilage alerts.', t:['full-service','fine-dining','ghost'], pr:['visibility','margins'], g:['costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'One avoided walk-in failure pays for years.', not:'Monitoring only, not a full HACCP workflow.' },
    { n:'FreshCheq', c:'Food safety', u:'https://www.freshcheq.com', p:'$60/mo or $629/yr', w:'Paperless mobile food-safety checklists and logs.', t:['qsr','fast-casual'], pr:['visibility'], g:['time','costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Cheapest way to digitize line checks and logs.', not:'Manual entry; no built-in temp sensors.' },
    { n:'Jolt', c:'Food safety', u:'https://www.jolt.com', p:'~$80–200/mo/loc', w:'Digital checklists, temp logging, label printing and tasks.', t:['qsr','fast-casual','full-service'], pr:['visibility'], g:['time','costs'], s:['single','small','multi'], b:['modest','serious'], fit:'Operations + food safety in one daily app.', not:'Manual temps unless you add sensors.' },
    { n:'ComplianceMate', c:'Food safety', u:'https://www.compliancemate.com', p:'est. ~$70–160/mo', w:'Wireless temp monitoring plus automated HACCP workflows.', t:['qsr','fast-casual','full-service'], pr:['visibility','margins'], g:['costs'], s:['small','multi'], b:['modest','serious'], fit:'Automated temp logs that satisfy inspectors.', not:'Requires sensor hardware; pricing not public.' },
    { n:'SmartSense by Digi', c:'Food safety', u:'https://www.smartsense.co/food-service/restaurants/', p:'est. ~$100–300/mo/loc', w:'Wire-free temp sensors plus HACCP compliance and alerts.', t:['qsr','fast-casual','full-service'], pr:['visibility','margins'], g:['costs'], s:['multi'], b:['serious'], fit:'Enterprise-grade monitoring and audit trails.', not:'Sales-led; no self-serve pricing.' },
    { n:'Squadle', c:'Food safety', u:'https://www.crunchtime.com/squadle', p:'est. ~$ quote', w:'Digital food-safety checklists plus remote temp monitoring.', t:['qsr','fast-casual','full-service'], pr:['visibility'], g:['time','costs'], s:['small','multi'], b:['modest','serious'], fit:'Checklists + sensors in one food-safety suite.', not:'Custom pricing; suite may exceed single-site needs.' },
    // ---------- Delivery & aggregators ----------
    { n:'Otter', c:'Delivery & aggregators', u:'https://www.tryotter.com', p:'~$100+/mo/loc', w:'All delivery apps in one screen, injected into your POS.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','slow-service','connect'], g:['costs','time','connect'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Ends tablet chaos and re-keying during a rush.', not:'Upsells a broad suite; low value at low volume.' },
    { n:'ItsaCheckmate', c:'Delivery & aggregators', u:'https://www.itsacheckmate.com', p:'~$85–100/mo/loc', w:'Connects 30+ delivery/ordering channels to your POS.', t:['qsr','fast-casual','full-service','ghost'], pr:['delivery-cost','connect'], g:['connect','time'], s:['small','multi'], b:['modest','serious'], fit:'One menu pushed everywhere; orders into the POS.', not:'Only pays back at meaningful delivery volume.' },
    { n:'Deliverect', c:'Delivery & aggregators', u:'https://www.deliverect.com/en-us', p:'~$99+/mo/loc', w:'Order injection from delivery apps into POS, menu sync, dispatch.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','connect'], g:['connect','time'], s:['small','multi'], b:['modest','serious'], fit:'Robust multi-channel sync for delivery-heavy operators.', not:'Add-on stacking raises the true cost.' },
    { n:'Chowly', c:'Delivery & aggregators', u:'https://chowly.com', p:'est. ~$150–300/mo/loc', w:'Delivery middleware with AI pricing/menu/marketing for independents.', t:['qsr','fast-casual','full-service'], pr:['delivery-cost','connect'], g:['connect','costs'], s:['single','small'], b:['modest','serious'], fit:'Aggregation plus smart pricing for independents.', not:'Opaque pricing; feature creep beyond aggregation.' },
    { n:'CloudKitchens', c:'Delivery & aggregators', u:'https://cloudkitchens.com', p:'est. ~$ lease + fees (quote)', w:'Ghost-kitchen real estate plus tech to run delivery brands.', t:['ghost'], pr:['delivery-cost'], g:['guests','costs'], s:['single','small','multi'], b:['serious'], fit:'Turnkey delivery-only kitchen space and tooling.', not:'Requires committing to their facilities; opaque fees.' },
    // ---------- Analytics & BI ----------
    { n:'Avero', c:'Analytics & BI', u:'https://averoinc.com', p:'est. ~$300–1,200/mo', w:'Sales, labor and server-performance analytics and benchmarking.', t:['full-service','fine-dining'], pr:['visibility','margins'], g:['costs','connect'], s:['small','multi'], b:['modest','serious'], fit:'Deep operational analytics for full-service groups.', not:'Quote-only; strongest at multi-unit scale.' },
    { n:'Tenzo (BI)', c:'Analytics & BI', u:'https://www.gotenzo.com', p:'from ~$600/yr', w:'Unifies sales/labor/inventory/reviews into one dashboard.', t:['fast-casual','full-service','ghost'], pr:['visibility','margins'], g:['costs','connect'], s:['small','multi'], b:['modest','serious'], fit:'One pane of glass across your whole operation.', not:'Per-module + per-location pricing climbs.' },
    { n:'Mirus', c:'Analytics & BI', u:'https://www.mirus.com', p:'est. ~$ enterprise', w:'Custom multi-unit data warehousing and report building.', t:['full-service'], pr:['visibility','margins'], g:['costs','connect'], s:['multi'], b:['serious'], fit:'Tailored reporting across complex multi-unit data.', not:'Needs analyst time; chain-oriented.' },
    // ---------- Emerging AI ----------
    { n:'Loop AI', c:'Emerging AI', u:'https://www.loopai.com', p:'est. ~% of recovered funds', w:'AI agent that reconciles third-party delivery errors and chargebacks.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','margins'], g:['costs'], s:['small','multi'], b:['modest','serious'], fit:'Recovers money the delivery apps quietly owe you.', not:'Value tied to high delivery volume.' },
    { n:'Toast Sous Chef', c:'Emerging AI', u:'https://pos.toasttab.com', p:'bundled with Toast', w:'AI assistant that surfaces insights from your sales and labor data.', t:['qsr','fast-casual','full-service'], pr:['visibility'], g:['time'], s:['single','small','multi'], b:['modest','serious'], fit:'Turns your Toast data into plain-language answers.', not:'Toast-only; an assistant, not an autonomous agent.' },
    { n:'Voosh', c:'Emerging AI', u:'https://www.voosh.ai', p:'est. ~$ quote', w:'AI review responder plus delivery-app dispute and recovery.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','reviews'], g:['costs','guests'], s:['small','multi'], b:['modest','serious'], fit:'Recovers delivery disputes and answers reviews with AI.', not:'More delivery-ops tool than guest chatbot.' },
    { n:'Agot AI', c:'Emerging AI', u:'https://www.agot.ai', p:'est. ~$500–1,500/mo/loc', w:'Kitchen-camera computer vision for real-time order accuracy.', t:['qsr','fast-casual'], pr:['slow-service','margins'], g:['time'], s:['multi'], b:['serious'], fit:'Catches order errors before they reach the guest.', not:'Chain-scale; integration heavy.' },
    { n:'PreciTaste', c:'Emerging AI', u:'https://precitaste.com', p:'est. ~$1,000+/mo/loc', w:'AI + computer vision for kitchen task and production management.', t:['qsr','fast-casual'], pr:['labor','waste'], g:['costs','time'], s:['multi'], b:['serious'], fit:'Predicts prep so the line stays ahead of demand.', not:'Enterprise/chain focus; complex BOH integration.' },
  ];

  const TYPE_LABEL = { qsr:'quick-service', 'fast-casual':'fast-casual', 'full-service':'full-service', 'fine-dining':'fine dining', ghost:'delivery-only' };
  const PROBLEM_LABEL = { 'missed-calls':'missed phone orders', 'slow-service':'slow service', labor:'labor cost', waste:'food waste', retention:'repeat business', reviews:'online reviews', 'delivery-cost':'delivery commissions', margins:'margins', visibility:'visibility into your numbers' };
  const BUDGET_RANK = { lean:0, modest:1, serious:2 };

  const finder = document.getElementById('finder');
  if (!finder) return;
  const resultsEl = document.getElementById('finderResults');
  const closeEl = document.getElementById('finderClose');
  const catSel = document.getElementById('f-category');
  const sels = ['f-type','f-size','f-problem','f-goal','f-comfort','f-budget'].map((id) => document.getElementById(id));

  // Populate the "browse by category" dropdown from the dataset
  [...new Set(TOOLS.map((t) => t.c))].sort().forEach((cat) => {
    const o = document.createElement('option');
    o.value = cat; o.textContent = cat;
    catSel.appendChild(o);
  });

  // Price shown as a tier ($ / $$ / $$$), derived from the cheapest budget the tool fits.
  // (Exact figures change constantly; tiers stay accurate and carry no per-vendor liability.)
  const TIERS = ['$', '$$', '$$$'];
  const TIER_WORD = { '$':'budget-friendly', '$$':'mid-range', '$$$':'premium / enterprise' };
  const tierOf = (t) => TIERS[Math.min(...t.b.map((x) => BUDGET_RANK[x]))];

  let captured = false; // once a visitor shares an email, the finder stays unlocked for them

  const SIZE_LABEL = { single:'one location', small:'a few locations', multi:'many locations' };

  // Plain-language diagnosis per challenge — speaks money & outcomes, not brand names.
  const DIAG = {
    'missed-calls': {
      whats: "When the phone rings mid-rush nobody can grab it — and most callers won't leave a message or try again. What feels like a slow night is often just demand you never saw.",
      cost: "Missing even a few order or reservation calls a week quietly adds up — for a busy independent that's often hundreds to a few thousand dollars a month.",
      fix: "Every call answered 24/7 — orders taken, tables booked, questions handled — so the demand you already create actually lands, and you can see exactly how many calls were saved.",
    },
    'slow-service': {
      whats: "Slow service is usually a symptom, not the cause — it traces back to kitchen workflow, ticket routing, or a clunky payment step, not your team not trying.",
      cost: "Every extra minute per table caps how many guests you can serve at peak — on a full night that's real covers and tips left on the floor.",
      fix: "Tighten the actual bottleneck so tickets flow and tables turn — more covers in the same hours, with less stress on the line.",
    },
    labor: {
      whats: "High labor cost is rarely lazy scheduling — it's scheduling by gut instead of by demand, so you're overstaffed on slow shifts and slammed on busy ones.",
      cost: "Trimming labor by even a point or two of sales is real money on a restaurant's thin margins — plus the manager hours lost building schedules by hand.",
      fix: "Staff to predicted demand hour by hour — fewer dead payroll hours, fewer understaffed rushes, and hours of admin off your plate.",
    },
    waste: {
      whats: "Food waste hides in over-prep and over-ordering — you can't fix what you can't see, and most kitchens are guessing.",
      cost: "Waste commonly runs a few percent of food cost straight into the bin — on real food spend that's thousands a year.",
      fix: "See exactly what's wasted and why, and order and prep to actual demand — lower food cost without touching the menu.",
    },
    retention: {
      whats: "If guests come once and don't return, the leak isn't traffic — it's the lack of a reason and a nudge to come back.",
      cost: "Most first-timers never return, yet regulars drive the bulk of sales — winning back even a slice of lapsed guests is found money.",
      fix: "Capture guests and bring them back automatically with offers that fit how they actually order — more repeat visits without discount-dumping.",
    },
    reviews: {
      whats: "Your rating quietly decides whether a stranger walks in. Thin or slipping reviews lose you bookings before anyone tastes the food.",
      cost: "For an independent, a one-star rating increase is linked to roughly 5–9% more revenue — reputation moves real money.",
      fix: "Steadily earn more genuine reviews and answer them on time, so your rating climbs and more searches turn into visits.",
    },
    'delivery-cost': {
      whats: "If delivery feels busy but unprofitable, the apps' 15–30% commissions are eating the order — you're renting customers you could own.",
      cost: "On thin margins a 25–30% commission can mean the platform makes more on an order than your kitchen does.",
      fix: "Move repeat customers to your own commission-free ordering and tame the apps — keep more of every order you're already making.",
    },
    margins: {
      whats: "Shrinking margins on steady sales means a leak you can't see — food-cost creep, delivery dilution, or money walking out the back — not a sales problem.",
      cost: "A couple of points of margin is the difference between a good year and a scary one at restaurant-level profitability.",
      fix: "Find the real leak — food cost, channel mix, or loss — and close it, so steady sales finally turn into steady profit.",
    },
    visibility: {
      whats: "Flying blind on your numbers means problems surface on the P&L a month too late — by then the money's already gone.",
      cost: "Decisions made on gut instead of data quietly cost you across labor, food, and pricing every single week.",
      fix: "One clear view of what's working, what's costing you, and where the next dollar of profit is — so you act in time, not after.",
    },
  };

  const DIY = {
    low: "Spotting this is one thing; fixing it properly is another — and that's exactly what we do, end to end.",
    mid: "You could tackle parts of this yourself — but pinning down the real number and wiring the fix into your POS is where it gets hard. That's where we come in.",
    high: "You could likely build the fix yourself — the real work is doing it to a production standard and proving the ROI. That's where our team turns it into an edge.",
  };

  const miniTool = (t) => {
    const tier = tierOf(t);
    return `<div class="tool tool--mini">
        <span class="tool__name">${t.n}</span>
        <span class="tool__price" title="${TIER_WORD[tier]}">${tier}</span>
        <p class="tool__what">${t.w}</p>
        <a class="tool__link" href="${t.u}" target="_blank" rel="noopener nofollow">Visit ${t.n} →</a>
      </div>`;
  };

  const matchList = (type, size, problem, goal, budget) =>
    TOOLS
      .filter((t) => t.pr.includes(problem))
      .map((t) => {
        let score = 4;
        if (t.t.includes(type)) score += 2;
        if (t.s.includes(size)) score += 1;
        if (t.g.includes(goal)) score += 1;
        if (t.b.includes(budget)) score += 1;
        return { t, score };
      })
      .sort((a, b) => b.score - a.score);

  function render() {
    const [type, size, problem, goal, comfort, budget] = sels.map((s) => s.value);
    const category = catSel.value;

    if (category !== 'any') {
      const list = TOOLS
        .filter((t) => t.c === category)
        .map((t) => ({ t, score: (t.t.includes(type) ? 2 : 0) + (t.s.includes(size) ? 1 : 0) + (t.b.includes(budget) ? 1 : 0) }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 8);
      resultsEl.innerHTML =
        `<p class="finder__lead">${category} — the toolbox (sorted for a ${TYPE_LABEL[type]} restaurant):</p>` +
        list.map(({ t }) => miniTool(t)).join('');
    } else {
      const d = DIAG[problem];
      const leadin = `<p class="diag__leadin">For a ${TYPE_LABEL[type]} restaurant with ${SIZE_LABEL[size]}, focused on ${PROBLEM_LABEL[problem]} —</p>`;
      const diag = `<div class="diag">
          <div class="diag__row"><p class="diag__label">What's likely really going on</p><p>${d.whats}</p></div>
          <div class="diag__row"><p class="diag__label">What it's probably costing you</p><p>${d.cost}</p><p class="diag__cost-note">Illustrative — we pin down your real number on the call.</p></div>
          <div class="diag__row"><p class="diag__label">What fixing it looks like</p><p>${d.fix}</p></div>
          <p class="diag__diy">${DIY[comfort]}</p>
        </div>`;

      if (!captured) {
        resultsEl.innerHTML = leadin + diag +
          `<form class="lead-capture" id="leadCapture" novalidate>
             <p class="lead-capture__pitch">Want the full breakdown — a closer estimate for your restaurant, plus the kinds of tools that solve this? Enter your email and we'll send it and set up your free call.</p>
             <div class="lead-capture__row">
               <input type="email" id="leadEmail" required placeholder="you@restaurant.com" aria-label="Your email" />
               <button type="submit" class="btn btn--primary" id="leadBtn">Send my breakdown</button>
             </div>
             <p class="lead-capture__note" id="leadNote">Free. No spam. We read every one personally.</p>
           </form>`;
        const lf = document.getElementById('leadCapture');
        lf.addEventListener('submit', async (e) => {
          e.preventDefault();
          const email = document.getElementById('leadEmail').value.trim();
          const note = document.getElementById('leadNote');
          const lb = document.getElementById('leadBtn');
          if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { note.textContent = 'Please enter a valid email.'; note.classList.add('error'); return; }
          lb.disabled = true; lb.textContent = 'Sending…'; note.classList.remove('error');
          const payload = {
            email,
            profile: `${TYPE_LABEL[type]} · ${SIZE_LABEL[size]} · challenge: ${PROBLEM_LABEL[problem]} · goal: ${goal} · tech comfort: ${comfort} · budget: ${budget}`,
            matched_tools: matchList(type, size, problem, goal, budget).slice(0, 5).map((x) => x.t.n).join(', '),
            _subject: 'Finder lead — AZ Restaurant Partners', _template: 'table', _captcha: 'false',
          };
          try {
            const res = await fetch('https://formsubmit.co/ajax/azoeb27@gmail.com', {
              method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
              body: JSON.stringify(payload),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok || data.success === false || data.success === 'false') throw new Error('x');
            captured = true; render();
          } catch (err) {
            lb.disabled = false; lb.textContent = 'Send my breakdown';
            note.classList.add('error');
            note.innerHTML = 'Couldn’t send just now — email us at <a href="mailto:azoeb27@gmail.com">azoeb27@gmail.com</a> and we’ll send it.';
          }
        });
      } else {
        const tools = matchList(type, size, problem, goal, budget).slice(0, 4);
        resultsEl.innerHTML = leadin + diag +
          '<p class="finder__sent">Sent — check your inbox. The kinds of tools that solve this:</p>' +
          tools.map(({ t }) => miniTool(t)).join('');
      }
    }

    const closeMsg = {
      low: "Honestly? Wiring this up, integrating your POS, and keeping it running is a lot — and easy to get wrong. That's exactly why we exist: we do it end to end, then stay on as your team.",
      mid: "You could set this up yourself — but choosing the right fix, integrating your POS, and proving the ROI is the hard part. That's what we do, end to end — and we stay with you for the long run.",
      high: "You could clearly build this yourself. The real work is making it production-grade, secure, and ROI-proven over time. That's where our team turns a good idea into a real edge.",
    }[comfort];

    closeEl.innerHTML = `<div class="finder__closebox">
      <h3>Do it yourself — or let us make it a game-changer.</h3>
      <p>${closeMsg}</p>
      <a href="#contact" class="btn btn--primary">Book a free video call</a>
    </div>`;
  }

  sels.forEach((s) => s.addEventListener('change', render));
  catSel.addEventListener('change', render);
  // Collapsed by default to keep the page short — reveal the diagnosis on demand
  resultsEl.innerHTML = '<div class="finder__hint"><p>Set the sentence above to match your place — then see what fits.</p><button type="button" class="btn btn--primary" id="finderGo">See what fits my restaurant →</button></div>';
  document.getElementById('finderGo').addEventListener('click', render);
})();

/* ===== Persona toggle (strategies) — tailors intro + flags "start here" cards ===== */
(() => {
  const wrap = document.getElementById('who');
  if (!wrap) return;
  const msgEl = document.getElementById('whoMsg');
  const grid = document.getElementById('possible');
  const MSG = {
    p1: "For a single neighborhood spot, the fastest money is defensive: turn the customers the apps bring you into your own repeat orders, get every call answered, and end the tablet chaos — wins you feel within weeks. <strong>Start with the three marked below.</strong>",
    p2: "For an established family restaurant, the money is in your regulars and your reputation: bring lapsed guests back, lift your reviews, and grow a higher-margin catering channel. <strong>Start with the three marked below.</strong>",
    p3: "For 2–10 locations, it's visibility and consistency: recover what the apps owe you across stores, get found everywhere new guests look, and win the customers the apps send you. <strong>Start with the three marked below.</strong>",
  };
  const apply = (who) => {
    msgEl.innerHTML = MSG[who] || MSG.p1;
    if (grid) grid.querySelectorAll('.poss').forEach((c) => {
      c.classList.toggle('poss--first', (c.dataset.who || '').split(' ').includes(who));
    });
  };
  wrap.querySelectorAll('.who__opt').forEach((btn) => {
    btn.addEventListener('click', () => {
      wrap.querySelectorAll('.who__opt').forEach((b) => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      apply(btn.dataset.who);
    });
  });
  apply('p1');
})();

/* ===== Sticky mobile CTA + strategies "see all plays" ===== */
(() => {
  const mcta = document.getElementById('mobilecta');
  const contact = document.getElementById('contact');
  if (mcta) {
    const onScroll = () => {
      let reached = false;
      if (contact) reached = contact.getBoundingClientRect().top < window.innerHeight * 0.9;
      mcta.classList.toggle('show', window.scrollY > 520 && !reached);
    };
    onScroll();
    addEventListener('scroll', onScroll, { passive: true });
    mcta.querySelector('a').addEventListener('click', () => mcta.classList.remove('show'));
  }
  const grid = document.querySelector('#possible .possible');
  const moreBtn = document.getElementById('moreplays');
  if (grid && moreBtn) {
    moreBtn.addEventListener('click', () => {
      const open = grid.classList.toggle('show-all');
      moreBtn.textContent = open ? 'Show fewer' : 'See all plays';
    });
  }
})();
