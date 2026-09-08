# Day 2 — Invalidation

> **By the end of today** you can drive the cache-aside race deliberately, and pick a
> scheme that does not have it.

---

## Read first

- [ ] [**Invalidation**](../../content/week-06/day-2/invalidation.md) — 30 min · sources: [Scaling Memcache at Facebook §3.2](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf), [Redis](https://redis.io/docs/latest/develop/reference/eviction/), [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111)

---

## The lab

`invalidation.py` — four approaches to the same problem.

```python
Store()                       .read(key)   .write(key, value)   .reads
CacheAside(sim, store, ttl)   .read(key)   .write(key, value)
                              .load(key)   .set_after_load(key, value)
LeasedCache(sim, store, ttl)  .read_or_lease(key)   .set_with_lease(key, value, token)
VersionedKeys(sim, store, ttl) .read(key)  .write(key, value)  .entries_held()  .purge_expired()
```

`CacheAside.load` and `set_after_load` exist so a test can put a write between them —
which is exactly what a slow reader does in production. That is not a testing trick; it
is the race, made reproducible.

Write `CacheAside` first and run `test_the_cache_aside_race`. Watching correct code cache
a wrong price, with the delete having happened, is the day.

Then notice the shape of the lease fix: **a monotonic token that makes a confused
participant harmless.** You built that last week and called it fencing.

```bash
pytest week-06/day-2 -v
```

---

## The written exercise

`week-06/day-2/invalidation-choice.md`, half a page.

For each, pick a strategy and say what its failure looks like **to a user**:

1. A product price
2. A user's own profile, edited by that user
3. A leaderboard recomputed every minute
4. A feature flag read on every request by 500 servers

Number 2 is the interesting one: it is a read-your-writes problem wearing a caching
costume, and the answer is a session guarantee rather than a cache setting. Number 4 is
the in-process trap — 500 caches that all disagree and cannot be invalidated together.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
