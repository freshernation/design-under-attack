# Day 3 — Stampedes

> **By the end of today** you can turn a thousand concurrent misses into one origin
> request, and you will never ship a uniform TTL again.

---

## Read first

- [ ] [**Stampedes, and the misses you can avoid**](../../content/week-06/day-3/stampedes.md) — 30 min · sources: [Facebook §3.2.1](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf), [Vattani et al., VLDB 2015](https://cseweb.ucsd.edu/~avattani/papers/cache_stampede.pdf), [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111)

---

## The lab

`stampede.py`, on `simlib` — the requests have to genuinely overlap in simulated time or
none of this means anything.

```python
SingleFlight(sim)   .do(key, loader, on_done, load_ms)   .loads   .in_flight
jittered_ttl(base_ms, fraction, rng)
should_refresh_early(now_ms, expires_at_ms, recompute_ms, beta, rng)
NegativeCache(sim, ttl_ms)   .mark_absent(key)   .known_absent(key)   .forget(key)
```

`SingleFlight` is about twenty lines and it is the most under-used mechanism in this
course. It generalises far past caches: a config fetch, a token refresh, a schema lookup —
anywhere many callers want the same expensive thing at the same instant.

One honest limitation to keep in mind: it is per process. A thousand servers each
coalescing their own misses still send a thousand requests. Facebook's leases live in the
shared tier for exactly that reason.

```bash
pytest week-06/day-3 -v
```

---

## The written exercise

`week-06/day-3/jitter-audit.md`, half a page.

Go through **all** of your designs so far and list every place where many things are
scheduled to happen at the same moment:

- TTLs written together
- lease renewals
- retries after a failure
- health checks
- cron and scheduled jobs
- clients reconnecting after a deploy

For each: is there jitter? If not, what happens at the moment they all fire?

You will find several. This is the audit that makes the rule stick, and week 9 will
assume you have already internalised it.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
