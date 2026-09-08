# Week 7 — Concept fence

## Allowed

**Everything from weeks 1–6**, plus:

- **Logs** — append-only partitions, offsets, consumer groups, replay, retention and
  compaction
- **Queues** — visibility timeouts, receipts, dead-letter queues, per-message retry
- **Delivery** — at-most-once, at-least-once, why exactly-once delivery is not available,
  and what products mean when they claim it
- **Idempotency** — natural idempotency, idempotency keys, deduplication windows,
  commutative effects
- **The dual write** — the outbox pattern, change data capture, and the events-versus-rows
  coupling
- **Consumers** — partition assignment, rebalancing, work reprocessed at a rebalance, lag
  per partition and against retention

## Not yet

Stream processing frameworks, windowed joins and state stores · circuit breakers,
bulkheads and load shedding (week 9) · CRDTs and operational transformation (week 10) ·
geospatial indexing (week 10) · model serving (week 10)

---

## The rule

**Every asynchronous boundary states its delivery guarantee and what makes the effect
safe.**

Two sentences, wherever a message crosses between components:

> Delivery is at-least-once; duplicates arise from producer retry, consumer crash,
> visibility timeout, rebalance and deliberate replay. The effect is idempotent because
> the aggregation recomputes a bucket rather than incrementing it.

A design that says "and then we publish an event" and stops has left the interesting half
out. From this week, that is incomplete rather than terse.
