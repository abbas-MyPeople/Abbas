/* ══ MEASUREMENT ═══════════════════════════════════════════════════════════
   Shared by every v2 page. Built to match what v1's script.js already does, so
   nothing that works today stops working at cutover:

     - GA4 loads directly (data flows with no container setup)
     - GTM loads too, because pixels added in the GTM UI live there, and a page
       that quietly drops the container silently stops every one of them
     - campaign attribution is captured once and rides on every event, under
       the same sessionStorage key v1 uses, so a visitor crossing between a v1
       page and a v2 page keeps one attribution
     - one delegated listener: any element with data-track fires an event, and
       every data-track-* becomes a parameter, so a new button is measured the
       moment it is added

   Beyond v1 it also records how far people read, which sections were truly
   seen and for how long, and total time on page.

   Do NOT add a GA4 Configuration tag inside GTM while GA4 also loads directly
   here — GA4 would double-count.                                            */
(function(){
  var GA4_ID = "G-3GEL1D477G";      /* azrestaurantpartners.com — runs directly */
  var GTM_ID = "GTM-K6GTGXP9";      /* container for pixels added in the GTM UI */
  var PAGE   = "__PAGEID__";

  /* ── attribution: captured once, kept for the whole visit ──────────────── */
  var ATTR = (function(){
    var KEY="azattr", saved={};
    try{ saved=JSON.parse(sessionStorage.getItem(KEY)||"{}"); }catch(e){}
    var qs=new URLSearchParams(location.search), changed=false;
    ["utm_source","utm_medium","utm_campaign","utm_content","utm_term"].forEach(function(k){
      var v=qs.get(k); if(v&&!saved[k]){ saved[k]=v; changed=true; }
    });
    if(!saved.landing){ saved.landing=(location.pathname.split("/").pop()||"index.html"); changed=true; }
    if(!saved.referrer && document.referrer && document.referrer.indexOf(location.host)===-1){
      saved.referrer=document.referrer; changed=true;
    }
    if(changed){ try{ sessionStorage.setItem(KEY,JSON.stringify(saved)); }catch(e){} }
    return saved;
  })();

  /* ── GA4 and GTM ───────────────────────────────────────────────────────── */
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function(){ window.dataLayer.push(arguments); };

  var s=document.createElement("script");
  s.async=true; s.src="https://www.googletagmanager.com/gtag/js?id="+GA4_ID;
  document.head.appendChild(s);
  gtag("js", new Date());
  gtag("config", GA4_ID, { transport_type:"beacon" });

  window.dataLayer.push({ "gtm.start": new Date().getTime(), event:"gtm.js" });
  var g=document.createElement("script");
  g.async=true; g.src="https://www.googletagmanager.com/gtm.js?id="+GTM_ID;
  document.head.appendChild(g);

  function track(name, params){
    var p={ page:PAGE, path:location.pathname };
    ["utm_source","utm_medium","utm_campaign","utm_content","utm_term","referrer","landing"]
      .forEach(function(k){ if(ATTR[k]) p[k]=ATTR[k]; });
    if(params) for(var k in params) if(Object.prototype.hasOwnProperty.call(params,k)) p[k]=params[k];
    try{ gtag("event", name, p); }catch(e){}
  }
  window.azTrack = track;

  /* The lead email should say where the lead came from — v1 sends this and a
     lead that arrives with no source is a lead you cannot attribute. */
  window.azSource = function(){
    var parts=[];
    ["utm_source","utm_medium","utm_campaign","utm_content","utm_term"].forEach(function(k){
      if(ATTR[k]) parts.push(k.replace("utm_","")+"="+ATTR[k]);
    });
    if(ATTR.referrer) parts.push("referrer="+ATTR.referrer);
    if(ATTR.landing)  parts.push("landing="+ATTR.landing);
    return parts.length ? parts.join(" \u00b7 ") : "direct / none";
  };

  function sectionOf(el){
    var s = el.closest && el.closest("section[id], section");
    if(!s) return "";
    if(s.id) return s.id;
    var k = s.querySelector(".kick");
    return k ? k.textContent.trim().toLowerCase().replace(/\s+/g,"_").slice(0,40) : "";
  }

  /* 1 — anything carrying data-track, with its data-track-* parameters */
  document.addEventListener("click", function(e){
    var el=e.target.closest("[data-track]"); if(!el) return;
    var p={};
    for(var i=0;i<el.attributes.length;i++){
      var a=el.attributes[i];
      if(a.name.indexOf("data-track-")===0) p[a.name.slice(11).replace(/-/g,"_")]=a.value;
    }
    p.section = sectionOf(el);
    track(el.getAttribute("data-track"), p);
  }, true);

  /* 2 — every other link and button, classified, with no markup required */
  document.addEventListener("click", function(e){
    var el=e.target.closest("a, button");
    if(!el || el.hasAttribute("data-track")) return;
    var h=el.getAttribute("href")||"", name="click";
    if(/^tel:/i.test(h)) name="call_click";
    else if(/^mailto:/i.test(h)) name="email_click";
    else if(/wa\.me|whatsapp/i.test(h)) name="whatsapp_click";
    else if(/\.pdf($|\?)/i.test(h)) name="pdf_download";
    else if(/^https?:/i.test(h) && h.indexOf(location.host)===-1) name="outbound_click";
    else if(h.charAt(0)==="#") name="anchor_click";
    track(name, {
      text:(el.textContent||el.getAttribute("aria-label")||"").trim().replace(/\s+/g," ").slice(0,60),
      href:h.slice(0,120),
      section:sectionOf(el)
    });
  }, true);

  /* 3 — how far they actually read */
  (function(){
    var hit={};
    addEventListener("scroll", function(){
      var d=document.documentElement,
          pct=Math.round((scrollY+innerHeight)/d.scrollHeight*100);
      [25,50,75,90].forEach(function(m){ if(pct>=m&&!hit[m]){ hit[m]=1; track("scroll_depth",{percent:m}); } });
    }, {passive:true});
  })();

  /* 4 — which sections were genuinely seen, and for how long */
  (function(){
    if(!("IntersectionObserver" in window)) return;
    var seen={}, since={};
    var io=new IntersectionObserver(function(es){
      es.forEach(function(en){
        var id=sectionOf(en.target)||"section";
        if(en.isIntersecting){
          since[id]=Date.now();
          if(!seen[id]){ seen[id]=1; track("section_view",{section:id}); }
        }else if(since[id]){
          var secs=Math.round((Date.now()-since[id])/1000); since[id]=0;
          if(secs>=3) track("section_dwell",{section:id,seconds:secs});
        }
      });
    }, {threshold:.35});
    [].forEach.call(document.querySelectorAll("section"), function(s){ io.observe(s); });
  })();

  /* 5 — total time, reported once on the way out */
  (function(){
    var t0=Date.now(), sent=false;
    function bye(){ if(sent) return; sent=true; track("time_on_page",{seconds:Math.round((Date.now()-t0)/1000)}); }
    addEventListener("visibilitychange", function(){ if(document.visibilityState==="hidden") bye(); });
    addEventListener("pagehide", bye);
  })();
})();
