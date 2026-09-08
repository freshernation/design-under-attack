# Milestone — Design a product catalogue read path

> Seven passes. A design document, and a working split-TTL cache with the economics
> worked out.

| File | What |
|---|---|
| `DESIGN.md` | Your design document |
| `catalogue.py` | Per-field TTLs, and the arithmetic that decides whether any of it fits |

Must pass `pytest week-06/milestone` and `python3 tools/check_sources.py`.

---

## The brief

The read path for a retail catalogue. Product pages, category listings, and the API
behind both.

**Scale**

| | |
|---|---|
| Products | 50,000,000 |
| Viewed in any hour | about 2,000,000 |
| Reads | 400,000/second at peak |
| Writes | 2,000/second — price changes, stock updates, description edits |
| **Read distribution** | 20,000 products take 380,000 reads/s; the remaining ~2M take 20,000/s |
| **Origin capacity** | **20,000 queries/second, and it is not negotiable this quarter** |
| Cache memory | 200 GB across the tier |

**Envelope**

| | |
|---|---|
| Latency | p99 under 80 ms |
| **Price freshness** | **a price change must be visible within 5 seconds** |
| Description freshness | 1 hour is fine |
| Stock band ("in stock" / "low" / "out") | 30 seconds |
| Availability | 99.95% |

**Not building**

Search · recommendations · checkout · inventory reservation · image delivery · the
catalogue's write path

---

## What this brief is about

**1. The origin capacity does the deciding.** 400,000 reads against a 20,000 origin means
a hit rate of at least 95%, and at 95% the cold-start multiplier is 20 — an empty cache
sends 400,000/s at something that serves 20,000. Your document has to say what happens
during a deploy.

**2. One object, three freshness requirements.** Price at 5 seconds, stock at 30,
description at an hour. Cache them as one object and the shortest one applies to all
three. Cache them separately and you have three lookups per page. Both are real costs.

**3. The five-second price TTL does not fit, and finding out why is the milestone.**
Run `total_origin_qps` on the brief's two read classes with a 5-second TTL before you
design anything. The answer is above the origin's capacity, and the reason is not the
one most people guess.

**4. A long tail is not helped by a longer TTL — until it is.** Compute
`ttl_that_starts_helping_ms` for both read classes. For the hot products it is about 50
milliseconds; for the tail it is **99 seconds**, because a key read once every 99 seconds
gains nothing from a 60-second TTL. Every read of it is a miss regardless.

That number surprises people, and it changes what you do about the tail.

---

## `catalogue.py`

```python
required_hit_rate(total_qps, origin_capacity_qps)
origin_qps_for_class(products, class_read_qps, ttl_ms, class_write_qps=0.0)
total_origin_qps(classes)
ttl_that_starts_helping_ms(products, class_read_qps)
memory_bytes(entries, bytes_per_entry)     cold_start_seconds(entries, warm_rate_per_s)

SplitCache(sim, capacity, field_ttls_ms)
    .read(product_id, field, loader)
    .invalidate(product_id, field=None)
```

The model behind `origin_qps_for_class` is worth understanding rather than just calling:

```
fetches per key per second = min(read rate for that key, 1 / ttl + write rate for that key)
```

A key is refetched when its entry expires **or** when a write invalidates it — whichever
happens more often — but never more often than it is actually read. That last clause is
the one that makes the long tail behave the way it does.

---

## The decision the arithmetic is pushing you towards

Do the sums before reading further, then come back.

At 2,000 writes a second against 400,000 reads, **a TTL is the wrong instrument for
freshness.** A TTL refreshes every key on a schedule whether or not anything changed; an
invalidation refreshes only what actually changed. Pass the write rate into
`origin_qps_for_class` and watch what happens to the number.

That does not make the problem disappear — invalidation has its own costs, which you met
on Tuesday and Wednesday, and your document has to price them:

- the cache-aside race, and which of the three fixes you chose
- invalidation delivery: how does the write reach every cache node, and what is the
  latency of that? **The 5-second requirement is now a property of your invalidation
  path, not of a TTL**, and it can fail in ways a TTL cannot
- what happens to freshness when invalidation delivery is broken but reads still work

---

## `DESIGN.md`

The week-1 template. **The fence is now lifted** — see `FENCE.md`. You may name products
this week, and the rule that replaces the ban is that a named product must come with the
property you need from it.

Your **Size** section must include:

- the required hit rate, and the cold-start multiplier that follows
- `total_origin_qps` for your chosen TTLs, against the 20,000 capacity
- `ttl_that_starts_helping_ms` for both read classes, and what you did about the tail
- memory for your cache entries against the 200 GB budget — remembering that splitting
  fields multiplies the entry count
- `cold_start_seconds` for a full warm at a rate the origin can actually serve

Your **Break** table needs rows for: the cache tier is empty · invalidation delivery is
delayed by two minutes · one product becomes 60% of all traffic.

---

## The five questions to have answers to

1. A deploy empties the cache tier at peak. Walk through the next sixty seconds.
2. A flash sale makes one product 60% of all reads. What breaks, and what does not?
3. Invalidation is delivered but one cache node misses it. How long is that node wrong
   for, and how would anybody find out?
4. The 5-second price requirement now applies to all 50 million products, not just the
   2 million viewed this hour. What changes?
5. You have 200 GB. What are you choosing not to cache, and how did you decide?

Question 2 is week 4 arriving in a week 6 design, and question 5 is the one most
documents never answer.

---

## Before you submit

```bash
pytest week-06/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md` on your own document.
