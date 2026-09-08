# Day 4 — Ordering, consumers and lag

> **By the end of today** you can say what a partitioned log actually orders, what a
> rebalance costs, and which lag alert almost nobody has.

---

## Read first

- [ ] [**Ordering, consumers, and rebalancing**](../../content/week-07/day-4/ordering-and-consumers.md) — 25 min · sources: [Kafka — Design](https://kafka.apache.org/documentation/#design), [consumer configuration](https://kafka.apache.org/documentation/#consumerconfigs), [Google Pub/Sub](https://cloud.google.com/pubsub/docs/subscription-overview)

---

## The lab

`consumers.py` — no simulation today; this is about assignment and arithmetic.

```python
assign(partitions, consumers)            Group(partitions).join/.leave/.assignment/.idle
reprocessed_on_rebalance(committed_offset, processed_offset)
lag(end_offsets, committed)              total_lag(...)
at_risk_of_data_loss(lag_records, retention_records)
rebalances_during_deploy(consumers, rolling=True)
```

Two results worth carrying out of the day:

- **You cannot have more consumers than partitions.** The idle ones are permanently idle,
  and partition count is a ceiling you set when the topic was created.
- **A rolling deploy is two rebalances per instance**, not one — a leave and a join. Twenty
  instances is forty rebalances, which is why throughput dips after every release.

```bash
pytest week-07/day-4 -v
```

`test_the_total_hides_the_hot_partition` is week 4 arriving in a monitoring dashboard: the
total says a modest backlog, one partition holds all of it.

---

## The written exercise

`week-07/day-4/partition-plan.md`, half a page, for tomorrow's aggregator.

1. What is the partition key, and what ordering does that give you?
2. How many partitions, and what does that cap consumer parallelism at?
3. The largest campaign is 15% of clicks. What rate does its partition see?
4. What is the session timeout against your p99 batch time, and what happens if a batch
   occasionally takes longer?

Question 4 is the one that produces the "continuous rebalancing with no progress" failure,
which looks like a broken broker and is a timeout shorter than the work.

---

## Tomorrow

The milestone. Read `week-07/milestone/README.md` tonight and compute the
replay-depth deduplication window before Friday morning. The number is the reason the
milestone is interesting.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
