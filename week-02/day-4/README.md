# Day 4 — Rate limiting

> **By the end of today** you can pick a limiting algorithm, say what it does at a
> window boundary, and prove the flaw in the obvious one with a test.

---

## Read first

- [ ] [**Rate limiting**](../../content/week-02/day-4/rate-limiting.md) — 30 min · sources: [AWS load shedding](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/), [Handling Overload](https://sre.google/sre-book/handling-overload/), [RFC 6585](https://www.rfc-editor.org/rfc/rfc6585)

---

## The lab

`token_bucket.py` — two limiters and a clock helper.

```python
advance(sim, ms)                                   # move time, do nothing else

TokenBucket(sim, rate_per_second, capacity)
    .tokens            # refilled lazily on access
    .allow(n=1)
    .retry_after_ms(n=1)

FixedWindow(sim, limit, window_ms)
    .allow()
```

**Write `FixedWindow` first**, then run `test_the_boundary_lets_through_twice_the_limit`.
Watching your own implementation permit 200 requests in half a second under a
hundred-a-minute limit is a much better argument than any article.

Two design details in `TokenBucket` worth noticing as you write them:

- **Refill lazily.** Computing tokens when someone asks, from elapsed time, avoids a
  background timer per key — and there are a lot of keys.
- **A refused request spends nothing.** Otherwise a client hammering you while over its
  limit stays over its limit for ever, which is a denial of service you built yourself.

```bash
pytest week-02/day-4 -v
```

---

## The written exercise

In `week-02/day-4/limiter-choice.md`, one page.

For each of these, say which algorithm you would use and why — and for two of them, why
the obvious answer is wrong:

1. A public API with paid tiers
2. Protecting a downstream payment gateway that allows exactly 100 calls a second
3. Stopping one customer's batch job from starving everyone else
4. An SMS provider that charges per message and has a monthly budget

Then one paragraph: **which of these is protection, which is fairness, and which is
business?** The three want different mechanisms and most systems conflate them.

---

## Tomorrow

The milestone. Read `week-02/milestone/README.md` tonight, not on Friday morning — the
brief has three constraints in it that take thinking rather than typing.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
