# Day 2 — Retries, backoff and jitter

> **By the end of today** you can retry without making an outage worse, and you will
> have watched backoff alone fail to spread anything out.

---

## Read first

- [ ] [**Retries, backoff, and jitter**](../../content/week-09/day-2/retries-and-jitter.md) — 30 min · sources: [AWS — timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/), [AWS — exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), [SRE Book](https://sre.google/sre-book/addressing-cascading-failures/)

Read the Builders' Library article in full. It is the definitive practitioner account and
you will cite it in design reviews for years.

---

## The lab

`retry.py`, on `simlib`.

```python
backoff_delays(attempts, base_ms, strategy, rng, cap_ms=None)   arrival_spread(delays)
storm_peak(clients, base_ms, strategy, rng, attempt, bucket_ms)
RetryBudget(sim, window_ms, ratio)  .record_request()  .record_retry()  .allow()
total_attempts(layers, retries_each)
```

Two things to take away permanently:

- **Backoff without jitter is a synchroniser.** Ten thousand clients that all back off by
  800 ms all come back in the same instant, in a wave exactly as tall as the failure was.
  Fifth time you have met this rule.
- **A retry budget is the thing that actually bounds the damage.** It is the least famous
  mechanism in the week and the most effective, and almost nobody has one.

```bash
pytest week-09/day-2 -v
```

---

## The written exercise

`week-09/day-2/retry-audit.md`, half a page.

Go through **every** call between components in your Project 2:

1. Does it retry? How many times?
2. Is the operation idempotent? If not, retrying it is a correctness bug rather than a
   reliability feature
3. Multiply the retries across the layers. What is the total at the bottom?
4. Which single layer should keep its retries, and why that one?

Question 4's answer is usually "the one closest to the user, because it knows whether
anybody is still waiting".

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
