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
