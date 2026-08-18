# Local SEO and AEO

## What is here

    geo.json        the cities and services — all the content that differs per page
    build_geo.py    renders 17 pages from it
    indexnow.json   the key and the URL list submitted for crawling
    <32-hex>.txt    (repo root) the IndexNow key file — must stay reachable

## Why these pages exist

The site had 42 pages and exactly one was geo-targeted. Everything else is
national informational content: "Toast vs Clover" pulls a reader in Ohio who
will never hire us. Nothing addressed what a Houston-area owner actually types
when they have a problem — *restaurant POS Katy*, *AI phone answering Houston
restaurant*, *who fixes restaurant tech in Sugar Land*.

12 city pages across the Houston metro, 5 service pages for the highest
commercial-intent searches.

## The rule that shapes the content

**Near-identical city pages are doorway pages. They get filtered and they
deserve to be.** The first draft came out 82–88% identical between cities. It
was rewritten so each city carries its own county, its own real commercial
corridors, its own read on what trades there, its own "what we would look at
first", and its own FAQ. That brought it to 57% median / 70% max, where the
shared remainder is the offer — which legitimately is the same everywhere.

Check it after any change:

    python3 seo/build_geo.py --check

If similarity climbs back above roughly 70%, the shared block has grown too
large or a city has lost its specifics. Fix the content, not the threshold.

## Nothing invented

Counties are correct, corridors are real roads, and the only statistic used
across the pages is attributed on every page it appears:

> 119 restaurants closed across the Houston metro in H1 2026 — more than any
> other city in the US or Canada, Harris County leading every county.
> https://restaurantdata.com/first-half-2026-restaurant-closure-report/

## Adding a city

Add an entry to `geo.json` with `slug, name, county, drive, corridors, scene,
angle, first, q, a`, then:

    python3 seo/build_geo.py

Then add it to `sitemap.xml`, `llms.txt`, the homepage footer column in
`v2/az-v2-src.html`, and `seo/indexnow.json` — and rebuild the homepage with
`python3 v2/build.py site`.

## Asking for a crawl

Google retired its ping endpoint, so for Google the only lever is Search
Console (owner account). For Bing and its partners, IndexNow works:

    curl -X POST https://api.indexnow.org/IndexNow \
      -H "Content-Type: application/json; charset=utf-8" \
      -d @seo/indexnow.json

`202` means accepted. Submitted 2026-08-18 with 20 URLs.

## Still owner-only

- **Google Business Profile** for AZ Restaurant Partners. The single biggest
  local ranking factor and it needs the owner's Google account to claim.
- **Search Console** — verification is already on the homepage via the
  `google-site-verification` meta tag, but submitting the sitemap and watching
  what actually ranks needs the account.

## Honest expectation

These pages need to be indexed and then earn position. That takes weeks, and
more pages does not shorten it. The fast levers are the Business Profile and
direct outreach; the pages are what compounds afterwards.
