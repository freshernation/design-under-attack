# The CDN, and the request you never receive

*Week 6 · Day 4 · about 25 minutes*

> By the end of this you can reason about cache keys, say why a personalised response
> destroys a hit rate, and name the mechanism that lets you purge without waiting.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**RFC 9111 — HTTP Caching**](https://www.rfc-editor.org/rfc/rfc9111) | 2 | The specification: freshness, revalidation, `Vary`, `stale-while-revalidate` |
| [**MDN — HTTP caching**](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching) | 2 | The same, readable, with what browsers actually do |
| [**Cloudflare — Cache**](https://developers.cloudflare.com/cache/) | 1 | A CDN operator documenting cache keys, purge, and tiered caching |
| [**Netflix Open Connect**](https://openconnect.netflix.com/) | 1 | What it looks like when the cached objects are enormous and the economics invert |

---

## The best request is the one you never receive

A CDN is a cache in hundreds of places, near users. Two things follow, and the second is
the one people underrate.

**Latency.** From week 1: a cross-ocean round trip is 150 ms of physics that no
engineering removes. A CDN removes the trip, not the physics.

**Load.** Every hit at the edge is a request your origin never sees. For static assets the
hit rate is well above 99%, which means your origin handles a small fraction of traffic —
and that fraction is the number your capacity plan should be built on, with the cold-start
multiplier from Monday sitting next to it.

For media it goes further. Netflix's Open Connect exists because the bandwidth cost of
serving video from a central origin is larger than everything else in the system put
together — at that scale the CDN is not an optimisation, it is the architecture, and the
application is what arranges it.

---

## The cache key is the design

An edge cache stores a response against a **key**. Everything about your hit rate follows
from what goes into it.

By default the key is the URL. Add anything that varies per user and your hit rate
collapses:

| Key includes | Distinct entries | Hit rate |
|---|---|---|
| URL | one per page | high |
| URL + country | one per page per country | still fine |
| URL + user id | one per page **per user** | approximately zero |

`Vary: Cookie` is the classic way to do this by accident. One header, and a shared cache
becomes a per-user cache with a hit rate near zero — while every dashboard still says the
CDN is working.

**The fix is architectural rather than a setting.** Split the response:

```
GET /product/42            cached at the edge, same for everybody
GET /api/me/cart-summary   never cached, small, per user
```

The page is assembled from a cached shell and an uncached fragment. This is why so many
sites load a page instantly and then fill in the personalised corner a moment later — it
is not laziness, it is the cache key.

---

## Freshness, revalidation, and the useful directives

Four things worth knowing precisely, because they are the vocabulary of any CDN
conversation:

| | What it does |
|---|---|
| `max-age=300` | fresh for 300 s. Serve without asking anyone |
| `s-maxage=3600` | as above, but for shared caches only — so a CDN may hold it far longer than a browser |
| `stale-while-revalidate=60` | serve the stale copy immediately and refresh in the background |
| `ETag` + `If-None-Match` | ask the origin "has it changed?" and get a 304 with no body |

`s-maxage` is the one that matters most in practice: it lets you keep a long TTL where you
*can* purge (the CDN) and a short one where you cannot (the browser). That asymmetry is
the whole reason for the separate directive.

`stale-while-revalidate` is yesterday's early-recomputation idea, standardised. A user
never waits for a refresh; one background request does the work.

---

## Purging, and why surrogate keys exist

A TTL says when a value becomes wrong. A purge says it is wrong *now*.

Purging by URL is fine until a change affects many URLs. A price change touches the
product page, the category listing, the search results, the home page carousel — and you
do not have a list.

**Surrogate keys** — tags attached to cached responses:

```
response for /product/42        tagged: product-42, category-shoes
response for /category/shoes    tagged: category-shoes
purge tag: category-shoes       ->  both, and everything else tagged that way
```

You invalidate by *meaning* rather than by URL, which is the only version of this that
survives a growing site. If a design purges at all, it should say what its tags are.

And a number to keep in mind: **a purge is not instant.** It propagates to hundreds of
locations and takes seconds. If your freshness requirement is tighter than a purge's
propagation, the CDN is not where that data lives — which is a real constraint and it
belongs in your envelope rather than in a surprise.

---

## What goes in a design document

> The product page shell is cached at the edge with `s-maxage=3600` and tagged with the
> product and category ids; the personalised block is a separate uncached request.
> **Rejected: `Vary: Cookie` on the page** — it would give one cache entry per user and a
> hit rate near zero. Price changes purge by surrogate key, which propagates in about 5
> seconds; **the 5-second freshness line is therefore met by the purge, not by the TTL**,
> and if purge propagation degrades, prices are stale rather than wrong-and-fast.

That last clause — what happens when the mechanism you rely on is slow — is what makes it
a design rather than a configuration.

---

## Today's lab

`bloom.py`, from the previous article, plus a short CDN piece in the same file:

- `cache_key(url, vary_headers, request_headers)` — what actually gets stored against
- `distinct_entries(urls, vary_on, cardinality)` — the table above, computed, so the
  `Vary: Cookie` cliff is a number rather than a warning
- `is_fresh(cached_at, now, max_age, s_maxage, shared)` — the freshness rules, including
  the shared-versus-private asymmetry

---

> **Sources for this article**
> [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111) and
> [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching) — **Tier 2** ·
> [Cloudflare](https://developers.cloudflare.com/cache/) and
> [Netflix Open Connect](https://openconnect.netflix.com/) — **Tier 1**, both operators
> documenting their own systems. Purge propagation times vary by provider and we have not
> quoted one — check your provider's documentation and put their number in your envelope.
