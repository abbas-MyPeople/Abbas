/* ============================================================
   AZ Integrations — interaction engine (vanilla, no deps)
   ============================================================ */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const lerp = (a, b, n) => a + (b - a) * n;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  /* ---------- Nav: scroll state + mobile menu ---------- */
  const nav = $('#nav');
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 12);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  const toggle = $('#navToggle');
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  $$('.nav__links a').forEach((a) =>
    a.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    })
  );

  /* ---------- Scroll progress bar ---------- */
  const bar = $('#scrollProgress');
  const progress = () => {
    const h = document.documentElement;
    const p = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
    bar.style.width = clamp(p, 0, 1) * 100 + '%';
  };
  progress();
  addEventListener('scroll', progress, { passive: true });
  addEventListener('resize', progress);

  /* ---------- Reveal on scroll (staggered) ---------- */
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -50px 0px' }
  );
  $$('.reveal').forEach((el, i) => {
    el.style.transitionDelay = `${Math.min(i % 4, 3) * 80}ms`;
    io.observe(el);
  });

  /* ---------- Count-up stats ---------- */
  const countIO = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        const el = e.target;
        const target = +el.dataset.count;
        const suffix = el.dataset.suffix || '';
        const dur = 1400;
        const t0 = performance.now();
        const tick = (now) => {
          const p = clamp((now - t0) / dur, 0, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased) + suffix;
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        countIO.unobserve(el);
      });
    },
    { threshold: 0.6 }
  );
  $$('[data-count]').forEach((el) => (reduce ? (el.textContent = el.dataset.count + (el.dataset.suffix || '')) : countIO.observe(el)));

  /* ---------- Rotating headline word ---------- */
  const rot = $('#rotator');
  if (rot) {
    const words = $$('span', rot);
    let i = 0;
    words[0].classList.add('active');
    if (!reduce && words.length > 1) {
      setInterval(() => {
        words[i].classList.remove('active');
        i = (i + 1) % words.length;
        words[i].classList.add('active');
      }, 2200);
    }
  }

  /* ---------- Spotlight cards ---------- */
  $$('[data-spotlight]').forEach((el) => {
    el.addEventListener('mousemove', (e) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${e.clientX - r.left}px`);
      el.style.setProperty('--my', `${e.clientY - r.top}px`);
    });
  });

  /* ---------- 3D tilt (desktop only) ---------- */
  if (fine && !reduce) {
    $$('[data-tilt]').forEach((el) => {
      const max = 7;
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(900px) rotateY(${px * max}deg) rotateX(${-py * max}deg) translateY(-4px)`;
      });
      el.addEventListener('mouseleave', () => (el.style.transform = ''));
    });
  }

  /* ---------- Magnetic buttons + custom cursor ---------- */
  if (fine && !reduce) {
    document.body.classList.add('cursor-on');
    const cur = $('#cursor');
    const dot = $('#cursorDot');
    let cx = innerWidth / 2, cy = innerHeight / 2, tx = cx, ty = cy;
    addEventListener('mousemove', (e) => {
      tx = e.clientX; ty = e.clientY;
      dot.style.transform = `translate(${tx}px, ${ty}px) translate(-50%, -50%)`;
      cur.style.opacity = dot.style.opacity = '1';
    });
    const ring = () => {
      cx = lerp(cx, tx, 0.18); cy = lerp(cy, ty, 0.18);
      cur.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`;
      requestAnimationFrame(ring);
    };
    ring();

    const interactive = '[data-magnetic], a, button, input, textarea';
    $$(interactive).forEach((el) => {
      el.addEventListener('mouseenter', () => cur.classList.add('hover'));
      el.addEventListener('mouseleave', () => cur.classList.remove('hover'));
    });

    $$('[data-magnetic]').forEach((el) => {
      const strength = 0.32;
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - (r.left + r.width / 2);
        const y = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
      });
      el.addEventListener('mouseleave', () => (el.style.transform = ''));
    });
  }

  /* ---------- Footer year ---------- */
  $('#year').textContent = new Date().getFullYear();

  /* ============================================================
     WebGL aurora shader background (graceful CSS fallback)
     ============================================================ */
  const canvas = $('#gl');
  const cssFallback = () => {
    canvas.style.background =
      'radial-gradient(60% 80% at 30% 20%, rgba(56,225,196,0.22), transparent 60%),' +
      'radial-gradient(60% 80% at 75% 30%, rgba(106,139,255,0.26), transparent 60%),' +
      'radial-gradient(70% 90% at 50% 100%, rgba(176,123,255,0.18), transparent 60%),' +
      '#070a12';
  };

  // Skip the shader on reduced-motion, data-saver, or low-memory devices.
  const lowEnd =
    (navigator.connection && navigator.connection.saveData) ||
    (navigator.deviceMemory && navigator.deviceMemory < 4);

  let gl;
  if (!canvas) return;
  try { gl = canvas.getContext('webgl', { antialias: true, alpha: false, powerPreference: 'low-power' }); } catch (_) {}
  if (!gl || reduce || lowEnd) { cssFallback(); return; }

  const vsrc = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;
  const fsrc = `
  precision highp float;
  uniform vec2 u_res; uniform float u_time; uniform vec2 u_mouse;
  vec3 mod289(vec3 x){return x - floor(x*(1.0/289.0))*289.0;}
  vec2 mod289(vec2 x){return x - floor(x*(1.0/289.0))*289.0;}
  vec3 permute(vec3 x){return mod289(((x*34.0)+1.0)*x);}
  float snoise(vec2 v){
    const vec4 C = vec4(0.211324865405187,0.366025403784439,-0.577350269189626,0.024390243902439);
    vec2 i  = floor(v + dot(v, C.yy));
    vec2 x0 = v -   i + dot(i, C.xx);
    vec2 i1 = (x0.x > x0.y) ? vec2(1.0,0.0) : vec2(0.0,1.0);
    vec4 x12 = x0.xyxy + C.xxzz; x12.xy -= i1;
    i = mod289(i);
    vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
    vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
    m = m*m; m = m*m;
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;
    m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
    vec3 g;
    g.x  = a0.x  * x0.x  + h.x  * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
  }
  float fbm(vec2 p){ float v=0.0, a=0.5; for(int i=0;i<5;i++){ v += a*snoise(p); p*=2.0; a*=0.5; } return v; }
  void main(){
    vec2 uv = gl_FragCoord.xy / u_res.xy;
    vec2 p = uv; p.x *= u_res.x / u_res.y;
    float t = u_time * 0.05;
    vec2 m = (u_mouse - 0.5) * 0.5;
    float n  = fbm(p*1.5 + vec2(t, -t*0.7) + m);
    float n2 = fbm(p*2.3 - vec2(t*0.8, t) + n*0.6);
    vec3 c1 = vec3(0.027,0.039,0.071);
    vec3 c2 = vec3(0.22,0.88,0.77);
    vec3 c3 = vec3(0.42,0.55,1.0);
    vec3 c4 = vec3(0.69,0.48,1.0);
    vec3 col = c1;
    col = mix(col, c3, smoothstep(0.0,0.95, n*0.5+0.5) * 0.7);
    col = mix(col, c2, smoothstep(0.25,1.0, n2*0.5+0.5) * 0.55);
    col = mix(col, c4, smoothstep(0.45,1.0, (n+n2)*0.35+0.5) * 0.45);
    float vig = smoothstep(1.25, 0.15, length(uv-0.5));
    col *= 0.5 + 0.75 * vig;
    gl_FragColor = vec4(col, 1.0);
  }`;

  const compile = (type, src) => {
    const s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { console.warn(gl.getShaderInfoLog(s)); return null; }
    return s;
  };
  const vs = compile(gl.VERTEX_SHADER, vsrc);
  const fs = compile(gl.FRAGMENT_SHADER, fsrc);
  if (!vs || !fs) { cssFallback(); return; }
  const prog = gl.createProgram();
  gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { cssFallback(); return; }
  gl.useProgram(prog);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 3,-1, -1,3]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  const uRes = gl.getUniformLocation(prog, 'u_res');
  const uTime = gl.getUniformLocation(prog, 'u_time');
  const uMouse = gl.getUniformLocation(prog, 'u_mouse');

  let mx = 0.5, my = 0.5, tmx = 0.5, tmy = 0.5;
  addEventListener('mousemove', (e) => { tmx = e.clientX / innerWidth; tmy = 1 - e.clientY / innerHeight; }, { passive: true });

  // Mobile renders at a lower internal resolution (gradient upscales cleanly) to save battery/GPU.
  const mobile = innerWidth < 820 || !fine;
  const pxr = Math.min(devicePixelRatio || 1, mobile ? 1 : 1.5) * (mobile ? 0.7 : 1);
  const resize = () => {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    canvas.width = Math.max(1, Math.floor(w * pxr)); canvas.height = Math.max(1, Math.floor(h * pxr));
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(uRes, canvas.width, canvas.height);
  };
  resize();
  addEventListener('resize', resize);

  /* pause when hero off-screen for performance */
  let visible = true;
  const hero = canvas.closest('.hero');
  new IntersectionObserver((e) => (visible = e[0].isIntersecting), { threshold: 0 }).observe(hero);

  const start = performance.now();
  const render = (now) => {
    if (visible) {
      mx = lerp(mx, tmx, 0.05); my = lerp(my, tmy, 0.05);
      gl.uniform1f(uTime, (now - start) / 1000);
      gl.uniform2f(uMouse, mx, my);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    requestAnimationFrame(render);
  };
  requestAnimationFrame(render);
})();
