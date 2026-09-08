# Day 1 — Why caches work, and where to put them

> **By the end of today** you can turn a working set into a hit rate, a hit rate into
> origin load, and say what your origin sees when the cache is empty.

---

## Read first

- [ ] [**Why caches work, and what they hide**](../../content/week-06/day-1/why-caches-work.md) — 25 min · sources: [Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf), [Redis eviction](https://redis.io/docs/latest/develop/reference/eviction/)
- [ ] [**Where to cache**](../../content/week-06/day-1/where-to-cache.md) — 20 min · sources: [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching), [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111)

Read §1–3 of the Facebook paper today. It is the best primary source on caching that
exists and you will use it all week.

---

## Predict first

A service takes 400,000 reads a second. Its cache has a 99% hit rate.

1. How much load reaches the origin?
2. The cache tier restarts. How much load reaches the origin in the next second?

Write both down. The second number is the one that decides whether the cache is an
optimisation or a load-bearing part of your availability.

---

## The lab

`cache.py` — an LRU with TTLs, plus the arithmetic.

```python
LRUCache(sim, capacity)   .get(key)   .put(key, value, ttl_ms)   .hit_rate   .stats
effective_latency_ms(hit_rate, hit_ms, miss_ms)
origin_qps(total_qps, hit_rate)          cold_start_multiplier(hit_rate)
total_staleness_ms(layer_ttls_ms)
working_set_bytes(hot_keys, bytes_per_key)   fits_in(working_set, memory_bytes)
```

Two details that are not fussiness:

- **An expired entry is a miss**, and is removed when found. A cache that counted expiries
  as hits would report a hit rate with no relationship to the load reaching your origin.
- **`__contains__` must not touch the statistics.** Inspecting a cache should not change
  what it reports, or every dashboard built on it lies.

```bash
pytest week-06/day-1 -v
```

---

## The written exercise

`week-06/day-1/caches-in-my-designs.md`, half a page.

Every design you have written so far has at least one cache in it, named or implied. For
each of your five:

1. What is the working set, in bytes?
2. What hit rate would you expect, and what does the origin see at that rate?
3. What is the cold-start multiplier, and what happens at a deploy?

Three numbers each. The third one is the question this course keeps returning to, and it
is the one that turns "we'll add a cache" into a design decision.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
