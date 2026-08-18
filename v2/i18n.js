/* ══ हिंदी · اردو ══════════════════════════════════════════════════════════
   English ⇄ Hindi, matched on text rather than on hand-placed keys, so a new
   paragraph is translatable the moment its Hindi is added to hi.json and
   nothing has to be tagged in the markup.

   Same shape as v1's engine and the same localStorage key ("azlang"), so a
   visitor who picked a language on an old page lands in it here too.

   The tables are injected at build time from v2/hi.json and v2/ur.json, with
   their keys normalised to what innerHTML actually returns: the browser
   re-escapes only & < >, and turns every other entity into its literal
   character. Urdu additionally flips the document to right-to-left.        */
(function(){
  var TX = __LANG_TABLES__;
  var RTL = {ur:1};

  var SEL = "h1,h2,h3,h4,p,li,figcaption,summary,label,button,a,span,em,b,strong";
  function norm(s){ return s.replace(/\s+/g," ").trim(); }

  /* Text that sits beside a child element belongs to no leaf, so it would never
     be translated — the headline's "Stop worrying about" sits next to the
     rotator span. Wrapping those loose runs in <t9n> once at startup turns each
     into a leaf of its own. A custom element is used deliberately: no stylesheet
     rule can match it, so wrapping cannot disturb the layout. */
  function split(){
    [].forEach.call(document.querySelectorAll(SEL), function(el){
      if(!el.children.length) return;
      [].slice.call(el.childNodes).forEach(function(n){
        if(n.nodeType!==3 || !n.nodeValue.trim()) return;
        var w=document.createElement("t9n");
        w.textContent=n.nodeValue;
        n.parentNode.replaceChild(w,n);
      });
    });
  }

  /* Only leaves: an element that contains another translatable element is a
     container, and rewriting its innerHTML would blow away its children. */
  function leaves(){
    var all=[].slice.call(document.querySelectorAll(SEL+",t9n")), set=new Set(all), out=[];
    all.forEach(function(el){
      for(var i=0;i<el.children.length;i++) if(set.has(el.children[i])) return;
      out.push(el);
    });
    return out;
  }

  function apply(lang){
    leaves().forEach(function(el){
      if(el.dataset.en===undefined) el.dataset.en=el.innerHTML;
      var tbl=TX[lang], hit=tbl && tbl[norm(el.dataset.en)];
      el.innerHTML = hit || el.dataset.en;
    });
    /* placeholders are attributes, not text, so they need their own pass */
    [].forEach.call(document.querySelectorAll("[placeholder]"),function(el){
      if(el.dataset.enPh===undefined) el.dataset.enPh=el.placeholder;
      var tbl=TX[lang], hit=tbl && tbl[norm(el.dataset.enPh)];
      el.placeholder = hit || el.dataset.enPh;
    });
  }

  function setLang(lang){
    apply(lang);
    var h=document.documentElement;
    h.setAttribute("lang", lang);
    h.setAttribute("dir", RTL[lang] ? "rtl" : "ltr");
    h.classList.toggle("lang-hi", lang==="hi");
    h.classList.toggle("lang-ur", lang==="ur");
    [].forEach.call(document.querySelectorAll("#lang [data-lang]"),function(b){
      var on=b.getAttribute("data-lang")===lang;
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", on?"true":"false");
    });
    try{ localStorage.setItem("azlang", lang); }catch(e){}
    if(window.azTrack) window.azTrack("lang_switch",{lang:lang});
  }
  window.azSetLang = setLang;

  document.addEventListener("click",function(e){
    var b=e.target.closest("#lang [data-lang]"); if(!b) return;
    e.preventDefault();
    setLang(b.getAttribute("data-lang"));
  });

  split();

  var saved="en";
  try{ saved=localStorage.getItem("azlang")||"en"; }catch(e){}
  if(saved!=="en" && !TX[saved]) saved="en";
  setLang(saved);
})();
