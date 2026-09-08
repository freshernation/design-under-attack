# Day 1 — Why partition, and on what key

> **By the end of today** you can say which limit you are actually hitting, and
> measure a candidate key's skew before you are committed to it.

---

## Read first

- [ ] [**Why partition, and when not to**](../../content/week-04/day-1/why-partition.md) — 25 min · sources: [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) §4.2, [Slicer](https://research.google/pubs/slicer-auto-sharding-for-datacenter-applications/), [Vitess](https://vitess.io/docs/reference/features/sharding/)
- [ ] [**Choosing a partition key**](../../content/week-04/day-1/choosing-a-partition-key.md) — 25 min · source: [Cassandra — Dynamo architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)

---

## Predict first

A hundred tenants. Ninety-nine send one unit of load each; one sends 231.

Across eight partitions, keyed by tenant:

1. What is the skew?
2. If you double to sixteen partitions, does the skew go up, down, or stay the same?

Write both down. The second answer is the reason "add more machines" is not a fix.

---

## The lab

`keys.py` — five functions, all arithmetic, and the whole point is that you run them on
your own candidate keys afterwards.

```python
partition_for(key, partitions)
distribute(weighted_keys, partitions)
skew(loads)
utilisation_of_busiest(loads, fleet_utilisation)
partitions_needed(total_load, per_partition_capacity, skew_factor=1.0)
```

Use `zlib.crc32`, not the built-in `hash()`. Python randomises string hashing per process,
so a partition function built on `hash()` gives a different answer after every restart —
which is the kind of bug that only shows up after a deploy.

```bash
pytest week-04/day-1 -v
```

---

## The written exercise

`week-04/day-1/keys-for-my-designs.md`, half a page.

For each of your four designs so far — link shortener, rate limiter, metrics store, and
the job queue you are about to design — name the partition key you would choose and
answer three questions:

1. Does the highest-volume query carry it?
2. What is the plausible skew? Estimate it; you do not need real data to know that one
   tenant will be ten times the next.
3. Which query have you just made a scatter-gather?

Four keys, twelve answers, half a page. The metrics store is the interesting one, because
you already chose there and may not have noticed.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
