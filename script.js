/* AZ Integrations — minimal, quiet interactions */
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
    { threshold: 0.14, rootMargin: '0px 0px -40px 0px' }
  );
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  document.getElementById('year').textContent = new Date().getFullYear();

  /* ---- Lead form → emails azoeb27@gmail.com via FormSubmit (no backend) ---- */
  const FORM_ENDPOINT = 'https://formsubmit.co/ajax/azoeb27@gmail.com';
  const form = document.getElementById('leadForm');
  if (form) {
    const btn = document.getElementById('formSubmit');
    const note = document.getElementById('formNote');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (form._honey && form._honey.value) return; // bot trap
      if (!form.name.value.trim() || !form.email.value.trim()) {
        note.textContent = 'Please add your name and email so I can reach you.';
        note.classList.add('error');
        return;
      }
      btn.disabled = true;
      const original = btn.textContent;
      btn.textContent = 'Sending…';
      note.classList.remove('error');

      const payload = {
        name: form.name.value,
        restaurant: form.restaurant.value,
        email: form.email.value,
        phone: form.phone.value,
        message: form.message.value,
        _subject: 'New free-call request — AZ Integrations',
        _template: 'table',
        _captcha: 'false',
      };

      try {
        const res = await fetch(FORM_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('bad status');
        form.classList.add('sent');
        const ok = document.createElement('div');
        ok.className = 'form__success';
        ok.innerHTML =
          '<h3>Thank you — message sent.</h3>' +
          "<p>I'll personally reply to set up your free video call, usually within a day.</p>";
        form.appendChild(ok);
      } catch (err) {
        btn.disabled = false;
        btn.textContent = original;
        note.classList.add('error');
        note.innerHTML =
          'Something went wrong sending the form. Please email me directly at ' +
          '<a href="mailto:azoeb27@gmail.com">azoeb27@gmail.com</a>.';
      }
    });
  }
})();
