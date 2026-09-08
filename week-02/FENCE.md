# Week 2 — Concept fence

## Allowed

**Everything from week 1**, plus:

- **Little's Law** — `L = λW`, in all three directions; concurrency, pools, queue age
- **Utilisation** — `ρ`, the M/M/1 wait curve, the knee, headroom, what losing one
  instance does to the survivors
- **Variability** — coefficients of variation, Kingman's approximation, the tail at
  scale, hedged and tied requests as *named ideas* you may cite but not design with yet
- **Queues** — bounded and unbounded, backpressure, reject / drop-oldest / grow, queue
  age as the metric, LIFO under overload
- **Rate limiting** — fixed window, sliding window log and counter, token bucket, leaky
  bucket; 429 and `Retry-After`
- **`simlib`** — `Simulation`, `schedule`, `run(until_ms=...)`. Not `Network` or `Node`
  yet, and not partitions

## Not yet

Load shedding by priority · circuit breakers and bulkheads · retry budgets and jitter
(named this week, designed in week 9) · autoscaling policy · replication and quorums ·
consistency models · caching · partitioning and hot keys · anything about storage
internals

---

## The rule that changes this week

Week 1 forbade naming anything. That rule now relaxes by exactly one step:

> **You may name a mechanism. You may not name a product.**

"A token bucket per tenant, plus a bounded queue with a drop-oldest policy" — allowed,
because every one of those words describes behaviour you could implement and defend.

"Redis for the counters, SQS for the queue" — still forbidden, and will be until week 6.

The distinction matters more than it looks. A mechanism is a decision you made; a
product is a decision somebody else made, which you have adopted without yet saying what
properties of it you need. The second one always *sounds* more concrete and is usually
less.

## The other rule

**Every queue in your design has a stated bound and a stated policy for being full.**

From this week on, a design document containing a queue with neither is incomplete, and
your instructor will treat it that way.
