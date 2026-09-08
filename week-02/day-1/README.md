# Day 1 — Little's Law

> **By the end of today** you can compute how many requests are inside your system,
> size a pool from a latency target, and explain why one slow dependency caps your
> throughput without anything being wrong with your code.

---

## Read first

- [ ] [**Little's Law**](../../content/week-02/day-1/littles-law.md) — 25 min · sources: [Google SRE Book — Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/), [AWS Builders' Library](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [ ] [**Concurrency, pools, and where the queue actually is**](../../content/week-02/day-1/concurrency-and-pools.md) — 20 min

---

## Predict first

Before the lab, write down your answers:

1. A service handles 500 requests a second, each taking 200 ms. How many are inside it
   at any moment?
2. Its database calls slow from 10 ms to 30 ms. The connection pool is unchanged. What
   happens to throughput?

Most people are out by a factor of five on the first and have no answer to the second.
Both are one multiplication.

---

## The lab

`littles.py` — five functions, one line each. The value is not the code, it is having
committed to what each term means.

```python
concurrency(throughput, latency_s)
wait_seconds(queue_depth, drain_rate)
max_throughput(concurrency_limit, latency_s)
pool_size(throughput, latency_s, headroom=1.5)
throughput_retained(old_latency_s, new_latency_s)
```

`wait_seconds` raises `ValueError` for a drain rate of zero or less — a queue that is
not draining does not have a long wait, it has an unbounded one, and returning a number
would be a lie.

```bash
pytest week-02/day-1 -v
```

---

## The written exercise

Take **your week-1 milestone** — the link shortener — and add a section called
`## Queues`. Find every place a request waits. There are more than you put in the
document: the client's connection pool, the accept backlog, your worker pool, the pool
to the store, and the store's own workers.

For each: what is its bound, and what happens when it is full?

Half a page, in `week-02/day-1/queues-in-my-shortener.md`. You will not be able to
answer all of them, and the ones you cannot answer are the point.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
