# Day 3 — Breakers, bulkheads and shuffle sharding

> **By the end of today** you can stop one dependency from consuming your service, and
> one tenant from consuming everyone's.

---

## Read first

- [ ] [**Circuit breakers and bulkheads**](../../content/week-09/day-3/circuit-breakers-and-bulkheads.md) — 30 min · sources: [AWS — shuffle sharding](https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/), [SRE Book](https://sre.google/sre-book/addressing-cascading-failures/), [resilience4j](https://resilience4j.readme.io/docs/circuitbreaker), [Hystrix](https://github.com/Netflix/Hystrix/wiki/How-it-Works)

The shuffle-sharding article is the best idea in this week and the least known. Read it
properly, including the combinatorics.

---

## The lab

`breaker.py`, on `simlib`.

```python
CircuitBreaker(sim, failure_threshold, minimum_requests, cooloff_ms, half_open=True)
Bulkhead({"search": 20, "profile": 40})
shuffle_shard(customer, servers, shard_size)    overlap_probability(servers, shard_size)
```

`half_open=False` exists so one test can show what its absence costs: with it, a
recovering dependency receives one probe; without it, every waiting client resumes at once
and knocks it straight back down. **A breaker without half-open is a slower way to have
the same outage twice.**

Then run `overlap_probability(100, 5)`. One in seventy-five million, from nothing but a
different assignment function — no extra hardware, no new component, no code on the
request path.

```bash
pytest week-09/day-3 -v
```

---

## The written exercise

`week-09/day-3/isolation-plan.md`, half a page, for your chat system.

1. List every dependency and give each a pool size. What did you give up in pooling
   efficiency, and is it worth it here?
2. Which dependencies get a breaker, and at what threshold? Name one that should **not**
   have one, and why
3. Your API tier has 40 hosts. With shuffle shards of 3, what fraction of tenants does one
   abusive tenant affect?

Question 2 matters as much as the others. A breaker on a dependency with a naturally high
error rate will open constantly, and every open breaker is an outage you caused yourself.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
