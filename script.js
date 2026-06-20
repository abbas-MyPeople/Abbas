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
  // c = category · t = restaurant types · pr = problems it addresses · g = goals · s = sizes · b = budget tiers it fits
  const TOOLS = [
    // ---------- POS ----------
    { n:'Toast', c:'POS', u:'https://pos.toasttab.com', p:'from $69/mo + hardware', w:'All-in-one restaurant OS: POS, ordering, KDS, payroll.', t:['qsr','fast-casual','full-service','fine-dining','ghost'], pr:['visibility','connect','slow-service'], g:['connect','time'], s:['single','small','multi'], b:['modest','serious'], fit:'One connected system instead of a dozen disconnected tools.', not:'Hardware lock-in; all-in cost often $1,000+/mo.' },
    { n:'Square for Restaurants', c:'POS', u:'https://squareup.com/us/en/point-of-sale/restaurants', p:'$0–149/mo', w:'iPad POS unified with Square payments and ecosystem.', t:['qsr','fast-casual','full-service','ghost'], pr:['visibility','connect'], g:['connect','time'], s:['single','small'], b:['lean','modest','serious'], fit:'Affordable, easy starting point that just works.', not:'Locked to Square processing; thin for complex coursing.' },
    { n:'Lightspeed Restaurant', c:'POS', u:'https://www.lightspeedhq.com/pos/restaurant', p:'$69–399/mo + payments', w:'Cloud POS with deep inventory, analytics, multi-location tools.', t:['full-service','fine-dining','fast-casual'], pr:['visibility','connect'], g:['connect','costs'], s:['small','multi'], b:['modest','serious'], fit:'Strong inventory and reporting for serious operators.', not:'Higher tiers pricey for a tiny shop.' },
    { n:'SpotOn', c:'POS', u:'https://www.spoton.com/restaurant-pos', p:'$0–135/mo + payments', w:'Restaurant POS plus marketing, loyalty, reviews and strong support.', t:['qsr','fast-casual','full-service'], pr:['visibility','connect','retention'], g:['connect','guests'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'POS bundled with guest-marketing and great support.', not:'Must use SpotOn hardware/processing; early-switch fee.' },
    { n:'TouchBistro', c:'POS', u:'https://www.touchbistro.com', p:'from $69/mo', w:'iPad POS purpose-built for tableside full-service.', t:['full-service','fine-dining','fast-casual'], pr:['visibility','slow-service'], g:['connect','time'], s:['single','small'], b:['modest','serious'], fit:'Built for tableside, coursing, and floor management.', not:'Add-ons inflate cost; weak for high-volume QSR.' },
    // ---------- Online ordering ----------
    { n:'ChowNow', c:'Online ordering', u:'https://www.chownow.com', p:'$119–328/mo', w:'Commission-free branded online ordering, app and marketing.', t:['qsr','fast-casual','full-service'], pr:['delivery-cost','retention'], g:['guests','costs'], s:['single','small'], b:['modest','serious'], fit:'Keeps the 15–30% the delivery apps would take.', not:'Subscription owed even in slow months.' },
    { n:'Owner.com', c:'Online ordering', u:'https://www.owner.com', p:'$499/mo + 5% guest fee', w:'AI-built website, app, ordering, loyalty and marketing in one.', t:['fast-casual','full-service','qsr'], pr:['retention','delivery-cost'], g:['guests','costs'], s:['single','small'], b:['serious'], fit:'Built to win commission-free repeat orders for independents.', not:'Flat $499 steep at low volume; 5% fee passed to guests.' },
    { n:'Square Online', c:'Online ordering', u:'https://squareup.com/us/en/online-store', p:'$0–149/mo', w:'Free site builder with pickup/delivery ordering on Square.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost'], g:['guests','costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Zero-cost way to launch commission-free ordering.', not:'Generic commerce tool; lighter restaurant upsell.' },
    { n:'BentoBox', c:'Online ordering', u:'https://www.getbento.com', p:'~$149–479/mo', w:'Premium restaurant website/CMS plus commission-free ordering & catering.', t:['full-service','fine-dining','fast-casual'], pr:['delivery-cost','retention'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Best-looking brand site with ordering built in.', not:'Strength is website/brand, not high-volume ordering.' },
    { n:'Slice', c:'Online ordering', u:'https://slice.com', p:'$69/mo + ~$2.25/order', w:'Commission-free online ordering and marketing built for pizzerias.', t:['qsr','fast-casual'], pr:['delivery-cost'], g:['guests','costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Purpose-built, low-cost ordering for pizza shops.', not:'Pizza-only — not for other concepts.' },
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
    { n:'SoundHound Dynamic Drive-Thru', c:'AI drive-thru', u:'https://www.soundhound.com/voice-ai-products/dynamic-drive-thru/', p:'enterprise quote', w:'GenAI voice ordering for drive-thru lanes, POS-integrated.', t:['qsr','fast-casual'], pr:['slow-service','labor'], g:['time','guests'], s:['multi'], b:['serious'], fit:'Speeds the lane and never forgets to upsell.', not:'Enterprise/brand-level deals; overkill for one store.' },
    { n:'ConverseNow', c:'AI drive-thru', u:'https://conversenow.ai', p:'enterprise quote', w:'Voice AI for phone and drive-thru ordering with upsell.', t:['qsr','fast-casual','ghost'], pr:['slow-service','missed-calls','labor'], g:['guests','time'], s:['multi'], b:['serious'], fit:'Handles peak ordering volume across many lanes/lines.', not:'Quote-only; built for large chains.' },
    { n:'Presto (Phoenix)', c:'AI drive-thru', u:'https://presto.com', p:'enterprise quote', w:'Drive-thru voice AI live across hundreds of lanes.', t:['qsr'], pr:['slow-service','labor'], g:['time'], s:['multi'], b:['serious'], fit:'Proven drive-thru automation at scale.', not:'Vendor recovering from past financial distress.' },
    // ---------- Chatbot & social ----------
    { n:'Popmenu', c:'Chatbot & social', u:'https://get.popmenu.com', p:'~$200–499/mo', w:'AI phone + text answering plus interactive menu and marketing.', t:['qsr','fast-casual','full-service'], pr:['missed-calls','retention'], g:['guests'], s:['single','small','multi'], b:['modest','serious'], fit:'Engaging menu + AI answering in one bundle.', not:'Bundled suite; hard to buy a la carte.' },
    { n:'ChatFood (Deliverect)', c:'Chatbot & social', u:'https://www.deliverect.com/en/integrations/chatfood', p:'quote', w:'Ordering via Instagram, Facebook, WhatsApp plus QR dine-in pay.', t:['qsr','fast-casual','ghost'], pr:['retention','delivery-cost'], g:['guests'], s:['small','multi'], b:['modest','serious'], fit:'Turns social channels into ordering channels.', not:'Strongest in EMEA; best if already on Deliverect.' },
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
    { n:'Paytronix', c:'Loyalty & CRM', u:'https://paytronix.com', p:'enterprise quote', w:'Loyalty, CRM, ordering and AI personalization suite.', t:['qsr','fast-casual','full-service'], pr:['retention'], g:['guests'], s:['multi'], b:['serious'], fit:'One-to-one AI offers for high-frequency, multi-unit brands.', not:'Enterprise-oriented; pricing opaque.' },
    { n:'Bikky', c:'Loyalty & CRM', u:'https://bikky.com', p:'enterprise quote', w:'Restaurant-only CDP unifying POS/ordering/payments/loyalty data.', t:['qsr','fast-casual'], pr:['retention','visibility'], g:['guests','connect'], s:['multi'], b:['serious'], fit:'The data backbone for serious multi-unit marketing.', not:'CDP/analytics, multi-unit only — not for single units.' },
    // ---------- Inventory & purchasing ----------
    { n:'MarketMan', c:'Inventory & purchasing', u:'https://www.marketman.com', p:'~$199/mo + setup', w:'Inventory, purchasing and recipe costing with POS sync.', t:['full-service','fast-casual','qsr'], pr:['margins','waste','visibility'], g:['costs','connect'], s:['small','multi'], b:['modest','serious'], fit:'Tightens ordering and food cost across vendors.', not:'Install fee + per-loc cost stings tiny single shops.' },
    { n:'MarginEdge', c:'Inventory & purchasing', u:'https://www.marginedge.com', p:'~$330/mo flat', w:'Invoice automation, live food cost and bill pay.', t:['full-service','fast-casual','fine-dining'], pr:['margins','waste','visibility'], g:['costs','connect'], s:['single','small','multi'], b:['modest','serious'], fit:'Kills back-office hours and 2–5% of food cost.', not:'Flat fee can outrun a tiny single QSR’s savings.' },
    { n:'BlueCart', c:'Inventory & purchasing', u:'https://www.bluecart.com', p:'$10–200/mo', w:'B2B wholesale ordering/procurement plus inventory.', t:['full-service','fast-casual','ghost'], pr:['margins','visibility'], g:['costs','connect'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Streamlines supplier ordering at a low entry price.', not:'Procurement-first; lighter on costing depth.' },
    { n:'Crunchtime', c:'Inventory & purchasing', u:'https://www.crunchtime.com', p:'enterprise quote', w:'Enterprise inventory, ordering and food-cost (AvT) for chains.', t:['qsr','fast-casual','full-service'], pr:['margins','waste','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Gold-standard control at scale.', not:'Built for large chains, not small shops.' },
    // ---------- Forecasting ----------
    { n:'Lineup.ai', c:'Forecasting', u:'https://www.lineup.ai', p:'~$149/mo/loc', w:'AI sales/labor/item forecasts from weather, events, history.', t:['qsr','fast-casual','full-service'], pr:['labor','waste'], g:['costs'], s:['single','small','multi'], b:['modest','serious'], fit:'Staff and prep to real demand, not guesswork.', not:'Forecasting-only; needs ~6 months of data.' },
    { n:'Tenzo', c:'Forecasting', u:'https://www.gotenzo.com', p:'from ~$600/yr', w:'Analytics plus demand forecasting across locations.', t:['fast-casual','full-service','ghost'], pr:['labor','waste','visibility'], g:['costs'], s:['small','multi'], b:['modest','serious'], fit:'Forecasts plus a unified ops dashboard.', not:'Needs ~90 days history; analytics-led.' },
    { n:'5-Out', c:'Forecasting', u:'https://www.5out.io', p:'quote', w:'ML demand forecasting feeding labor and purchasing decisions.', t:['full-service','fast-casual','qsr'], pr:['labor','waste'], g:['costs'], s:['small','multi'], b:['modest','serious'], fit:'Turns forecasts into concrete staffing/ordering calls.', not:'No public pricing; newer/smaller vendor.' },
    // ---------- Scheduling ----------
    { n:'7shifts', c:'Scheduling', u:'https://www.7shifts.com', p:'free–$150/mo/loc', w:'Scheduling, forecasting, tips and team chat.', t:['qsr','fast-casual','full-service','fine-dining'], pr:['labor'], g:['costs','time'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Fast payback from less overtime and saved admin time.', not:'Add-ons (tips, tasks) stack cost per location.' },
    { n:'Homebase', c:'Scheduling', u:'https://www.joinhomebase.com', p:'free–$99.95/mo/loc', w:'Scheduling, time tracking, payroll and hiring for SMBs.', t:['qsr','fast-casual','full-service'], pr:['labor'], g:['costs','time'], s:['single','small'], b:['lean','modest','serious'], fit:'Free for one location; covers the basics well.', not:'Per-location pricing jumps fast for multi-unit.' },
    { n:'Deputy', c:'Scheduling', u:'https://www.deputy.com', p:'$5–9/user/mo', w:'Scheduling, demand forecasting and biometric clock-ins.', t:['fast-casual','full-service'], pr:['labor'], g:['costs','time'], s:['small','multi'], b:['lean','modest','serious'], fit:'Demand-based auto-scheduling at a low per-user price.', not:'Per-user cost rises with large hourly teams.' },
    { n:'Sling', c:'Scheduling', u:'https://getsling.com', p:'free–$3.40/user/mo', w:'Shift scheduling, time-off and labor-cost management.', t:['qsr','fast-casual','ghost'], pr:['labor'], g:['costs','time'], s:['single','small'], b:['lean','modest','serious'], fit:'Free tier covers small teams; cheap to grow.', not:'Lighter forecasting/analytics than rivals.' },
    // ---------- KDS ----------
    { n:'Fresh KDS', c:'Kitchen display (KDS)', u:'https://www.fresh.technology', p:'$15–39/screen/mo', w:'Tablet-based kitchen display; works with Square/Clover and more.', t:['qsr','fast-casual','ghost'], pr:['slow-service','connect'], g:['time','connect'], s:['single','small'], b:['lean','modest','serious'], fit:'Quick payback, fewer mistakes, faster tickets.', not:'Fewer enterprise/multi-unit controls.' },
    { n:'Toast KDS', c:'Kitchen display (KDS)', u:'https://pos.toasttab.com/products/kitchen-display-system', p:'quote + hardware', w:'KDS routing POS/online/handheld orders to kitchen screens.', t:['qsr','fast-casual','full-service'], pr:['slow-service','connect'], g:['time','connect'], s:['single','small','multi'], b:['modest','serious'], fit:'Deeply integrated if you run Toast.', not:'Locked to Toast POS; opaque pricing.' },
    { n:'QSR Automations ConnectSmart', c:'Kitchen display (KDS)', u:'https://qsrautomations.com/connectsmart/kitchen', p:'enterprise quote', w:'Enterprise KDS, ticket routing, prep timing and analytics.', t:['full-service','fine-dining'], pr:['slow-service','connect'], g:['time'], s:['multi'], b:['serious'], fit:'Sophisticated kitchen coordination at scale.', not:'Cost/complexity high for small shops.' },
    // ---------- Robotics ----------
    { n:'Miso Robotics Flippy', c:'Robotics', u:'https://www.misorobotics.com', p:'~$3,500/mo + install', w:'AI robot arm that fries and hot-holds food.', t:['qsr','fast-casual'], pr:['labor','slow-service'], g:['costs','time'], s:['multi'], b:['serious'], fit:'Frees crew from the fryer at high volume.', not:'High-volume frying only; ROI needs heavy throughput.' },
    { n:'Hyphen Makeline', c:'Robotics', u:'https://www.hyphen.ai', p:'$50k–100k', w:'Automated under-counter makeline assembling bowls/salads.', t:['fast-casual','ghost'], pr:['labor','slow-service'], g:['costs','time'], s:['multi'], b:['serious'], fit:'Speeds bowl/salad assembly at scale.', not:'Big capex; bowl format only; not plated service.' },
    { n:'Bear Robotics Servi', c:'Robotics', u:'https://www.bearrobotics.ai', p:'$11,990 or ~$293/mo', w:'Autonomous food-running and bussing robot.', t:['full-service','fast-casual'], pr:['labor','slow-service'], g:['time','costs'], s:['small','multi'], b:['modest','serious'], fit:'Takes running/bussing off your servers.', not:'Runs food, doesn’t cook; needs open floor layout.' },
    // ---------- Recipe & food cost ----------
    { n:'meez', c:'Recipe & food cost', u:'https://www.getmeez.com', p:'quote', w:'Recipe digitization, scaling and costing for chefs.', t:['fine-dining','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small'], b:['modest','serious'], fit:'Keeps plate costs and prep consistent across the team.', not:'Lighter on inventory; costing is an add-on.' },
    { n:'Parsley', c:'Recipe & food cost', u:'https://www.parsleycooks.com', p:'$99–299/mo', w:'Recipe management, costing, inventory and nutrition.', t:['full-service','fine-dining'], pr:['margins','visibility'], g:['costs'], s:['single','small'], b:['modest','serious'], fit:'Affordable plate-costing for independents.', not:'Limited for large multi-unit chains.' },
    { n:'xtraCHEF (by Toast)', c:'Recipe & food cost', u:'https://pos.toasttab.com/products/xtrachef', p:'free tier–$349/mo', w:'Invoice OCR, line-item food cost and recipe analytics.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Low-risk way to start controlling food cost.', not:'Best value only if you’re on Toast.' },
    // ---------- Accounting & payroll ----------
    { n:'Restaurant365', c:'Accounting & payroll', u:'https://www.restaurant365.com', p:'$249–469/mo/loc + setup', w:'Accounting + inventory + scheduling unified for restaurants.', t:['full-service','fast-casual','qsr'], pr:['margins','visibility'], g:['costs','connect'], s:['multi'], b:['serious'], fit:'One ledger across many locations.', not:'Heavy/pricey; overkill for a single independent.' },
    { n:'Ottimate (Plate IQ)', c:'Accounting & payroll', u:'https://ottimate.com', p:'from ~$200/mo', w:'AP automation: AI invoice coding, approvals and payments.', t:['full-service','fast-casual'], pr:['margins','visibility'], g:['costs','time'], s:['small','multi'], b:['modest','serious'], fit:'Turns the invoice pile into automated, coded payments.', not:'AP-only; needs separate accounting/payroll.' },
    { n:'Gusto', c:'Accounting & payroll', u:'https://gusto.com', p:'$49/mo + $6/employee', w:'Full-service payroll, benefits and HR.', t:['qsr','fast-casual','full-service','ghost'], pr:['margins'], g:['time','costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Painless payroll and tax filing.', not:'Generic; lacks tips/POS-native restaurant features.' },
    { n:'DAVO by Avalara', c:'Accounting & payroll', u:'https://www.davosalestax.com', p:'~$57.99/mo/loc', w:'Auto-sets aside daily sales tax, files and pays it.', t:['qsr','fast-casual','full-service'], pr:['margins'], g:['time','costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Never scramble for sales-tax money again.', not:'Single-purpose (sales tax only).' },
    // ---------- Loss prevention ----------
    { n:'Solink', c:'Loss prevention', u:'https://solink.com', p:'from ~$175/mo/loc', w:'Pairs camera video with POS data to review suspect transactions.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small','multi'], b:['modest','serious'], fit:'Catch theft/voids with video tied to the receipt.', not:'Needs compatible cameras.' },
    { n:'Delaget', c:'Loss prevention', u:'https://www.delaget.com', p:'enterprise quote', w:'QSR loss prevention plus back-office analytics; flags exceptions.', t:['qsr','fast-casual'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Surfaces theft and anomalies across many stores.', not:'Built for franchise/multi-unit; overkill for one store.' },
    { n:'DTiQ', c:'Loss prevention', u:'https://www.dtiq.com', p:'enterprise quote', w:'Managed video surveillance plus POS exception analytics.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['small','multi'], b:['serious'], fit:'Outsourced video + analytics with human review.', not:'Managed service + hardware; contract-based, higher cost.' },
    // ---------- Energy & maintenance ----------
    { n:'Ecotrak', c:'Energy & maintenance', u:'https://www.ecotrak.com', p:'from $25/mo/loc', w:'Facility/asset CMMS: work orders, preventive maintenance, vendors.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Cheap way to track assets and stop surprise repairs.', not:'Maintenance mgmt, not real-time energy metering.' },
    { n:'Powerhouse Dynamics Open Kitchen', c:'Energy & maintenance', u:'https://powerhousedynamics.com/food-service-solutions/', p:'enterprise quote', w:'IoT software unifying HVAC/lighting/equipment with AI energy mgmt.', t:['qsr','fast-casual','full-service'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Cuts the energy bill 10–20% across a portfolio.', not:'Built for chains; overkill for a single location.' },
    { n:'Verdigris', c:'Energy & maintenance', u:'https://verdigris.co', p:'enterprise quote', w:'Circuit-level energy monitoring with AI power/cooling optimization.', t:['full-service','fine-dining','fast-casual'], pr:['margins','visibility'], g:['costs'], s:['multi'], b:['serious'], fit:'Pinpoints exactly where power and money leak.', not:'Panel-level install; multi-site focus.' },
    // ---------- Food safety ----------
    { n:'Therma', c:'Food safety', u:'https://www.hellotherma.com', p:'from $10/mo/sensor', w:'Wireless temp/humidity sensors with 24/7 spoilage alerts.', t:['full-service','fine-dining','ghost'], pr:['visibility','margins'], g:['costs'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'One avoided walk-in failure pays for years.', not:'Monitoring only, not a full HACCP workflow.' },
    { n:'FreshCheq', c:'Food safety', u:'https://www.freshcheq.com', p:'$60/mo or $629/yr', w:'Paperless mobile food-safety checklists and logs.', t:['qsr','fast-casual'], pr:['visibility'], g:['time','costs'], s:['single','small'], b:['lean','modest','serious'], fit:'Cheapest way to digitize line checks and logs.', not:'Manual entry; no built-in temp sensors.' },
    { n:'Jolt', c:'Food safety', u:'https://www.jolt.com', p:'~$80–200/mo/loc', w:'Digital checklists, temp logging, label printing and tasks.', t:['qsr','fast-casual','full-service'], pr:['visibility'], g:['time','costs'], s:['single','small','multi'], b:['modest','serious'], fit:'Operations + food safety in one daily app.', not:'Manual temps unless you add sensors.' },
    { n:'SmartSense by Digi', c:'Food safety', u:'https://www.smartsense.co/food-service/restaurants/', p:'enterprise quote', w:'Wire-free temp sensors plus HACCP compliance and alerts.', t:['qsr','fast-casual','full-service'], pr:['visibility','margins'], g:['costs'], s:['multi'], b:['serious'], fit:'Enterprise-grade monitoring and audit trails.', not:'Sales-led; no self-serve pricing.' },
    // ---------- Delivery & aggregators ----------
    { n:'Otter', c:'Delivery & aggregators', u:'https://www.tryotter.com', p:'~$100+/mo/loc', w:'All delivery apps in one screen, injected into your POS.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','slow-service','connect'], g:['costs','time','connect'], s:['single','small','multi'], b:['lean','modest','serious'], fit:'Ends tablet chaos and re-keying during a rush.', not:'Upsells a broad suite; low value at low volume.' },
    { n:'ItsaCheckmate', c:'Delivery & aggregators', u:'https://www.itsacheckmate.com', p:'~$85–100/mo/loc', w:'Connects 30+ delivery/ordering channels to your POS.', t:['qsr','fast-casual','full-service','ghost'], pr:['delivery-cost','connect'], g:['connect','time'], s:['small','multi'], b:['modest','serious'], fit:'One menu pushed everywhere; orders into the POS.', not:'Only pays back at meaningful delivery volume.' },
    { n:'Deliverect', c:'Delivery & aggregators', u:'https://www.deliverect.com/en-us', p:'~$99+/mo/loc', w:'Order injection from delivery apps into POS, menu sync, dispatch.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','connect'], g:['connect','time'], s:['small','multi'], b:['modest','serious'], fit:'Robust multi-channel sync for delivery-heavy operators.', not:'Add-on stacking raises the true cost.' },
    { n:'Chowly', c:'Delivery & aggregators', u:'https://chowly.com', p:'quote', w:'Delivery middleware with AI pricing/menu/marketing for independents.', t:['qsr','fast-casual','full-service'], pr:['delivery-cost','connect'], g:['connect','costs'], s:['single','small'], b:['modest','serious'], fit:'Aggregation plus smart pricing for independents.', not:'Opaque pricing; feature creep beyond aggregation.' },
    // ---------- Analytics & BI ----------
    { n:'Avero', c:'Analytics & BI', u:'https://averoinc.com', p:'quote', w:'Sales, labor and server-performance analytics and benchmarking.', t:['full-service','fine-dining'], pr:['visibility','margins'], g:['costs','connect'], s:['small','multi'], b:['modest','serious'], fit:'Deep operational analytics for full-service groups.', not:'Quote-only; strongest at multi-unit scale.' },
    { n:'Tenzo', c:'Analytics & BI', u:'https://www.gotenzo.com', p:'from ~$600/yr', w:'Unifies sales/labor/inventory/reviews into one dashboard.', t:['fast-casual','full-service','ghost'], pr:['visibility','margins'], g:['costs','connect'], s:['small','multi'], b:['modest','serious'], fit:'One pane of glass across your whole operation.', not:'Per-module + per-location pricing climbs.' },
    // ---------- Emerging AI ----------
    { n:'Loop AI', c:'Emerging AI', u:'https://www.loopai.com', p:'quote', w:'AI agent that reconciles third-party delivery errors and chargebacks.', t:['qsr','fast-casual','ghost'], pr:['delivery-cost','margins'], g:['costs'], s:['small','multi'], b:['modest','serious'], fit:'Recovers money the delivery apps quietly owe you.', not:'Value tied to high delivery volume.' },
    { n:'Toast Sous Chef', c:'Emerging AI', u:'https://pos.toasttab.com', p:'bundled with Toast', w:'AI assistant that surfaces insights from your sales and labor data.', t:['qsr','fast-casual','full-service'], pr:['visibility'], g:['time'], s:['single','small','multi'], b:['modest','serious'], fit:'Turns your Toast data into plain-language answers.', not:'Toast-only; an assistant, not an autonomous agent.' },
    { n:'Agot AI', c:'Emerging AI', u:'https://www.agot.ai', p:'quote', w:'Kitchen-camera computer vision for real-time order accuracy.', t:['qsr','fast-casual'], pr:['slow-service','margins'], g:['time'], s:['multi'], b:['serious'], fit:'Catches order errors before they reach the guest.', not:'Chain-scale; integration heavy.' },
    { n:'PreciTaste', c:'Emerging AI', u:'https://precitaste.com', p:'quote', w:'AI + computer vision for kitchen task and production management.', t:['qsr','fast-casual'], pr:['labor','waste'], g:['costs','time'], s:['multi'], b:['serious'], fit:'Predicts prep so the line stays ahead of demand.', not:'Enterprise/chain focus; complex BOH integration.' },
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

  function card(t, type, budget) {
    const cautions = [t.not];
    if (!t.t.includes(type)) cautions.push(`more commonly a fit for ${t.t.map((x) => TYPE_LABEL[x]).slice(0, 2).join(' / ')}`);
    if (BUDGET_RANK[budget] < Math.min(...t.b.map((x) => BUDGET_RANK[x]))) cautions.push('may stretch a ' + budget + ' budget');
    return `<div class="tool">
        <span class="tool__name">${t.n}</span>
        <span class="tool__price">${t.p}</span>
        <p class="tool__what">${t.w}</p>
        <p class="tool__why"><span class="yes">Why it fits:</span> ${t.fit}</p>
        <p class="tool__why"><span class="no">Watch-out:</span> ${cautions.join(' · ')}</p>
        <a class="tool__link" href="${t.u}" target="_blank" rel="noopener">Visit ${t.n} →</a>
      </div>`;
  }

  function render() {
    const [type, size, problem, goal, comfort, budget] = sels.map((s) => s.value);
    const category = catSel.value;

    let list, lead;
    if (category !== 'any') {
      list = TOOLS
        .filter((t) => t.c === category)
        .map((t) => ({ t, score: (t.t.includes(type) ? 2 : 0) + (t.s.includes(size) ? 1 : 0) + (t.b.includes(budget) ? 1 : 0) }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 8);
      lead = `<p class="finder__lead">${category} — options worth a look (sorted for a ${TYPE_LABEL[type]} restaurant):</p>`;
    } else {
      list = TOOLS
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
      lead = `<p class="finder__lead">For a ${TYPE_LABEL[type]} restaurant focused on ${PROBLEM_LABEL[problem]}, here's what's worth a look:</p>`;
    }

    const cards = list.map(({ t }) => card(t, type, budget)).join('');
    resultsEl.innerHTML = list.length
      ? lead + cards
      : '<p class="finder__empty">Adjust the options above and I’ll show matching tools.</p>';

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
  catSel.addEventListener('change', render);
  render();
})();
