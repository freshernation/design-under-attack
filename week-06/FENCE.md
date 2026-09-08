# Week 6 — Concept fence

## Allowed

**Everything from weeks 1–5**, plus:

- **Caching** — working set, hit rate, effective latency, origin load, the cold-start
  multiplier, eviction, TTLs
- **Layers** — browser, CDN/edge, shared tier, in-process, buffer pool; staleness adding
  across them
- **Invalidation** — cache-aside, write-through, write-behind, write-around; the stale-set
  race; delayed double delete, leases, versioned keys
- **Stampedes** — single-flight, jitter, probabilistic early recomputation,
  `stale-while-revalidate`, negative caching
- **Membership filters** — bloom filters, sizing, false-positive rates, rebuild policy
- **HTTP caching** — cache keys, `Vary`, `max-age` and `s-maxage`, `ETag`, purging and
  surrogate keys

## Not yet

Message brokers and stream processing (week 7) · exactly-once and idempotency (week 7) ·
circuit breakers, bulkheads, load shedding (week 9) · CRDTs (week 10) · geospatial
indexing (week 10) · model serving (week 10)

---

## The rule that ends this week

**The product-name ban is lifted from the milestone onwards.**

Five weeks of writing "a store that returns one record by key in under a millisecond"
instead of a product name has done its job: you now reach for the mechanism first and the
noun second. The rule that replaces the ban is permanent:

> **A named product must come with the property you need from it.**

Not: *"we use Redis."*
But: *"an in-memory store with per-key TTLs and atomic increments — Redis, or Memcached
if we drop the increments."*

The test is unchanged from week 1: **delete every proper noun from your design. Is there
anything left?** If yes, you have named tools. If no, you had a shopping list, and now you
have one with better vocabulary.

## The new rule

**Every cache in a design states its hit rate, its TTL, and what happens when it is empty.**

Three numbers and one sentence. A design containing a cache without them has not said
whether the cache is an optimisation or a load-bearing part of its availability — and
those are very different systems that look identical on a diagram.
