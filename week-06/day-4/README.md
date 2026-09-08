# Day 4 — Filters, and the edge

> **By the end of today** you can reject a lookup you never needed to make, and explain
> how one HTTP header can take a CDN's hit rate to zero.

---

## Read first

- [ ] [**Bloom filters**](../../content/week-06/day-4/bloom-filters.md) — 25 min · sources: [RocksDB](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview), [Facebook memcache](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [ ] [**The CDN, and the request you never receive**](../../content/week-06/day-4/cdn-and-the-edge.md) — 25 min · sources: [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111), [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching), [Cloudflare](https://developers.cloudflare.com/cache/), [Netflix Open Connect](https://openconnect.netflix.com/)

---

## The lab

`bloom.py` — the filter, and the cache-key arithmetic in the same file.

```python
BloomFilter(expected_keys, false_positive_rate)
    .add(key)   key in filter   .bits_per_key   .bytes_used
    .estimated_false_positive_rate()

cache_key(url, vary_on, request_headers)
distinct_entries(urls, vary_cardinality)
is_fresh(cached_at_ms, now_ms, max_age_s, s_maxage_s, shared)
```

Derive the `k` positions from **one** hash rather than computing k independent ones —
take a SHA-256, split it into two halves `h1` and `h2`, and use `(h1 + i * h2) % bits`.
Standard, cheap, and good enough: a bloom filter is not a security boundary and does not
need to be.

Three tests are the day:

- `test_there_is_never_a_false_negative` — the guarantee, checked over 20,000 keys
- `test_an_overfilled_filter_says_maybe_to_everything` — the failure mode nobody plans
  for. A filter needs a rebuild policy
- `test_varying_on_cookie_destroys_the_hit_rate` — one header, and a shared cache becomes
  a per-user cache while every dashboard still says the CDN is working

```bash
pytest week-06/day-4 -v
```

---

## The written exercise

`week-06/day-4/edge-plan.md`, half a page, for tomorrow's catalogue.

1. What is identical for every user, and what is personalised?
2. What is the cache key for the shared part, and what is its cardinality?
3. When a price changes, what has to be purged — and how do you know the full list?
4. How long does a purge take to propagate, and is that inside the 5-second requirement?

Question 3 is where surrogate keys come from, and question 4 is where a lot of designs
quietly fail: if a purge is slower than the freshness line, the CDN is not where that data
can live.

---

## Tomorrow

The milestone. Read `week-06/milestone/README.md` tonight and run `total_origin_qps` on
the brief's two read classes with a 5-second TTL before Friday morning. The answer changes
what you design, and you do not want to discover it at 10am.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
