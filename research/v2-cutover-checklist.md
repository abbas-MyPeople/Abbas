# v2 cutover — what is done and what is left

Written 2026-08-17 after rendering both pages at real viewports for the first time.

## Backup (done)

    tag     live-pre-v2-20260817-1931      (pushed to origin)
    branch  backup/live-pre-v2-20260817-1931
    files   .backup/index.pre-v2.html, .backup/robots.pre-v2.txt

Instant revert, no git knowledge needed:

    cp .backup/index.pre-v2.html index.html && git commit -am "revert to pre-v2"

## Bugs that only rendering caught

Static analysis passed all three of these. They were found by looking.

1. **`.rise` could hide the whole page.** It animated `opacity:0 → 1` on an
   `animation-timeline: view()` with `fill: both`. Anywhere the view timeline does
   not advance — an iframe, an unusual scroll container — every section stays at
   opacity 0 permanently and the page renders blank. It now animates transform
   only, so the worst case is content that does not slide.
2. **The rotating headline rendered grey.** A leftover `.hero h1 span{color:var(--ink-3)}`
   out-specified `.rot{color:var(--ticket)}`. Removed.
3. **The rotator phrases ghosted over each other.** A symmetric 0.38s crossfade left
   two lines of 3rem type both legible. The outgoing phrase now leaves in 0.16s and
   the incoming arrives over 0.34s after a beat.
4. **The pinned call to action covered the form it points at.** Two earlier versions
   of the hide logic looked right and did nothing: an `IntersectionObserver` against
   a target taller than the viewport, then a `requestAnimationFrame` throttle whose
   `ticking` flag latched shut the moment a frame callback was deferred. It is now a
   single `getBoundingClientRect` read run inline on scroll, and the bar clears the
   moment the form crosses 92% of viewport height.

## Header and the pinned action

The header is the brand and the scroll rail, nothing else. The only call to action on
the page is a bar pinned to the bottom of the screen, which hides itself whenever the
form is visible so it never sits on top of the fields.

Note for anyone testing this: **programmatic scrolling in the Chrome automation
context does not dispatch scroll events at all** — a listener added by hand records
zero hits after `window.scrollTo`. Verify by scrolling, then dispatching
`new Event('scroll')` by hand, or the behaviour will look broken when it is not.

## Verified

- 390 / 768 / 1512 px: no horizontal overflow, nothing wider than the viewport,
  nothing invisible, every image has alt text, exactly one h1
- Tap targets at 44px+ on mobile
- CSS balanced, base rules confirmed at depth 0 (not trapped inside a media query)
- JS parses clean
- **All 41 content pages linked** from the new footer (index and onepager excluded
  by design), so nothing indexed gets orphaned

## Still open before cutover

- [ ] **Form endpoint untested.** It posts to the same `formsubmit.co` address the
      live site uses, but no test message has been sent end to end.
- [ ] **Language toggles.** The live site offers EN / HI / UR; v2 does not.
- [ ] **Meta + Open Graph into `<head>`.** They exist but must sit in the head when
      this becomes a real document.
- [ ] **Stage at a preview URL** for a click-through before replacing index.html.

## The pinned button

Edge to edge at every width, with a 12px gutter on each side and no maximum. An
earlier version capped it at the page's content measure to keep it aligned with the
rest of the layout on a desktop; that was wrong — it read as a button that had failed
to fill its bar. The cap is gone and cannot bind at any viewport.

The border is live: a solid fill painted on the padding box, a conic gradient painted
on the border box, and a transparent 2px border letting the gradient through as a rim.
A registered `@property --sweep` rotates the gradient, so a warm highlight travels the
perimeter every 4.6s. Where `@property` is unsupported the angle simply never moves and
the rim renders as a static two-tone border, which is why the resting colours are set to
look deliberate on their own. The site's global reduced-motion rule already stops it.

Checked against DoorDash first, since that was the reference: **DoorDash does not do
this.** doordash.com has zero animated elements and zero gradient buttons;
merchants.doordash.com has only `fadeIn` keyframes. Whatever the reference was, it is
not on their web surfaces.

## Video

Two clips, deliberately different in weight:

    assets/video/founder-pitch.mp4   848x478  1:41  3.8MB   homepage, secondary
    assets/video/yc-pitch.mp4        478x850  0:51  5.5MB   investors page, hero

Both were re-encoded from the WhatsApp originals (15MB and 9.4MB) at CRF 28 with
faststart and 64k mono audio. Posters are single frames picked by eye from a contact
sheet, not the first frame.

On the homepage the founder clip sits directly above the enquiry form, under "Who
you'd be working with" — the last thing before someone fills anything in, not the
centrepiece. On the investors page the YC pitch is the hero, in its own column at a
phone's proportions beside the thesis; below 860px the hero stacks and the video lands
between the thesis and the numbers.

Neither preloads. Both are click-to-load behind a poster and a play button, so the
page costs nothing until someone asks.

### The build, and why it exists

`v2/build.py` renders both pages from `v2/*-src.html` in one of two modes:

    python3 v2/build.py site        # videos as assets/video/… paths
    python3 v2/build.py artifact    # videos as base64 payloads, decoded to Blob URLs

The artifact viewer's CSP allows no external requests, so the preview has to carry its
own media. **Do not inline video as a `data:` URI** — Chrome will not stream media from
one, and a 5MB `data:` URI leaves the element at `readyState 0` indefinitely with no
error event. The page ships the clip as base64 inside an inert
`<script type="text/plain">` and converts it to a Blob URL on click instead.

### What could not be tested here

Playback. This Chrome never fires `loadedmetadata` or `error` for any video, from a
file URL, a data URI, or a Blob URL. Two things were ruled out: `canPlayType` reports
H.264 as "probably", and a byte-for-byte check proved the base64 round trip is exact
(4,003,377 bytes in and out, valid `ftyp` box). Also note `python -m http.server`
answers a Range request with **200, not 206**, so no local file-URL video will ever
play against it. Both clips still need a human to press play once.
