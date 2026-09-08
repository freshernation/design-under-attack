# Day 4 — Ids, and finding the right machine

> **By the end of today** you can generate ids without coordination and show, with
> numbers, what sortability does to your partition distribution.

---

## Read first

- [ ] [**Ids, and finding the right machine**](../../content/week-04/day-4/ids-and-routing.md) — 30 min · sources: [Twitter Snowflake](https://github.com/twitter-archive/snowflake), [Vitess](https://vitess.io/docs/reference/features/sharding/), [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Slicer](https://research.google/pubs/slicer-auto-sharding-for-datacenter-applications/)

---

## The lab

`ids.py` — a Snowflake-style generator on `simlib`'s clock.

```python
SnowflakeGenerator(sim, node_id, epoch_ms=0).next_id()
decode(snowflake, epoch_ms=0) -> (timestamp_ms, node, sequence)
hash_partitions(ids, partitions)
range_partitions(ids, partitions, low, high)
```

Layout, high bits first: 41 bits of milliseconds, 10 bits of node, 12 bits of sequence.
Shifting is the whole implementation.

Two failure modes are part of the lab, and both are choices rather than bugs:

- **`ClockWentBackwards`** — refuse to issue. A generator that stops is an incident; one
  that issues duplicates is a data-loss bug found weeks later.
- **`SequenceExhausted`** — 4,096 in one millisecond and no more. A real generator spins
  until the next millisecond; this one raises, because busy-waiting on a simulated clock
  never returns.

The last three tests are the day. Same ids, two partitioning schemes: range puts every
single one on one partition, hash spreads them evenly and loses the range scan.

```bash
pytest week-04/day-4 -v
```

---

## The written exercise

`week-04/day-4/ids-and-routing-choices.md`, half a page.

For the job queue you design tomorrow:

1. Which id scheme, and what does it do to your partition distribution?
2. Which routing model — client-side, proxy, or any-node — and what does it cost in your
   20 ms enqueue budget?
3. A worker's view of the partition map is thirty seconds stale and it pulls from a
   partition that has moved. What should happen, and what would happen in your design?

Question 3 is next week's material arriving early, and having tried to answer it makes
week 5 land much harder.

---

## Tomorrow

The milestone. Read `week-04/milestone/README.md` tonight — the brief has a conflict in
it that has no free answer, and you want to have slept on it.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
