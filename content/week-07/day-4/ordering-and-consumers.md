# Ordering, consumers, and rebalancing

*Week 7 · Day 4 · about 25 minutes*

> By the end of this you can say what ordering a partitioned log actually gives you, and
> what happens to in-flight work when a consumer joins or leaves.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Kafka — Design**](https://kafka.apache.org/documentation/#design) | 1 | Partitions, consumer groups, and the ordering guarantee stated precisely |
| [**Kafka — consumer configuration**](https://kafka.apache.org/documentation/#consumerconfigs) | 1 | The knobs: session timeout, max poll interval, auto-commit. Every one of them is a decision |
| [**Google Pub/Sub — subscriptions**](https://cloud.google.com/pubsub/docs/subscription-overview) | 1 | Ordering keys, which is the same idea arrived at from the other direction |

---

## The ordering you get

**Records within one partition are ordered. Records in different partitions have no
relationship.** That is the whole guarantee, and every ordering question reduces to what
your partition key is.

```
key = user_id     ->  one user's events are ordered
key = order_id    ->  one order's events are ordered
key = null        ->  nothing is ordered, and the throughput is even
```

Two consequences worth stating plainly, because they get argued about:

**Total ordering means one partition**, which means one machine's throughput and no
horizontal scaling at all. When somebody asks for global ordering, that is what they are
asking for. Say it as a number: "that caps us at one partition, which is about N events a
second".

**Ordering and parallelism trade against each other, per key.** The finer your partition
key, the more parallelism and the less you can order. Week 4's milestone was exactly this
conflict, and the log makes it a property of the primitive rather than something you build.

---

## Consumer groups

Several consumers share the work of a topic: each partition is assigned to exactly one
consumer in the group.

```
6 partitions, 3 consumers  ->  2 partitions each
6 partitions, 6 consumers  ->  1 each
6 partitions, 8 consumers  ->  2 consumers idle, permanently
```

The last line is the one people meet in production. **You cannot have more consumers than
partitions**, so partition count is a ceiling on parallelism that you set when you created
the topic and can usually only increase — and increasing it changes which keys land where,
which reorders things relative to what came before.

That makes partition count a decision with the same weight as week 4's partition key:
easy to get wrong, awkward to change, and it belongs in the design document with a
justification.

---

## Rebalancing, and the work in flight

When a consumer joins, leaves or is presumed dead, partitions are reassigned. Three
things happen that a design should account for:

**Processing stops during the rebalance.** In simple implementations every consumer in the
group stops until the assignment settles. It is usually short; under a rolling deploy it
happens once per instance.

**In-flight work is orphaned.** A consumer processing a batch loses the partition; the new
owner starts from the last **committed** offset, which may be behind. So the records
between the last commit and the crash are processed twice — a duplicate source you now
have a name for.

**A slow consumer looks dead.** The group decides membership by heartbeat and by how long
a consumer takes between polls. A consumer doing 30 seconds of work per batch with a 10
second poll timeout is ejected mid-batch, its partitions are reassigned, its work is
redone by somebody else, and it rejoins — and then does it again. Forever.

That last failure is worth recognising by its symptom: **continuous rebalancing with no
progress**, which looks like a broken broker and is a timeout that is shorter than the
work.

---

## Lag, and the two ways to read it

`lag = log_end_offset − committed_offset`, per partition.

Two things to watch, and most teams watch only the first:

**The absolute number**, and whether it is returning to zero. Week 2's distinction between
a queue that is absorbing and one that is losing, unchanged.

**Lag against the retention edge.** A consumer that falls further behind than the
retention window **loses data**, and does so silently — the records are simply gone when
it gets there. That alert is rarely present, and it is the one that catches a consumer
that was down over a weekend.

And the per-partition view matters as much as the total: one partition lagging while five
are fine is a hot key, and the aggregate hides it completely. That is week 4's lesson
arriving in a monitoring dashboard.

---

## What goes in a design document

> Clicks are partitioned by `campaign_id` across 64 partitions. **Ordering is guaranteed
> per campaign and nowhere else**, which is all the aggregation needs. 64 caps consumer
> parallelism at 64; at 500,000 events/s that is 7,800 per consumer, against a measured
> capacity of 20,000. Session timeout is 45 s against a p99 batch time of 3 s, so a slow
> batch does not trigger a rebalance. **Lag is alerted per partition, and against the
> retention edge as well as against a threshold.**

---

## Today's lab

`week-07/day-4/consumers.py`:

- `ConsumerGroup` — assignment, joining, leaving, and idle consumers when there are more
  than partitions
- `rebalance()` and a test showing records between the last commit and the reassignment
  being processed **twice**
- `lag(...)` per partition and in total, and a test where the total looks fine and one
  partition is drowning
- `at_risk_of_data_loss(lag, retention)` — the alert nobody has

---

> **Sources for this article**
> [Kafka documentation](https://kafka.apache.org/documentation/#design) and
> [consumer configuration](https://kafka.apache.org/documentation/#consumerconfigs) —
> **Tier 1** · [Google Pub/Sub](https://cloud.google.com/pubsub/docs/subscription-overview)
> — **Tier 1**. The "slow consumer looks dead" failure and the two-ways-to-read-lag framing
> are ours — **Tier 3**, though both are directly implied by the configuration
> documentation.
