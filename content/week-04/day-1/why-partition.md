# Why partition, and when not to

*Week 4 · Day 1 · about 25 minutes*

> By the end of this you can name the five reasons a system outgrows one machine, say
> which one you are actually hitting, and make the case for not partitioning yet.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Dynamo**](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) §4.2 | 1 | Amazon's own account of why they partitioned and what it cost them |
| [**Vitess — Sharding**](https://vitess.io/docs/reference/features/sharding/) | 2 | Official documentation for a sharding layer built to keep YouTube's databases alive |
| [**Slicer: Auto-Sharding for Datacenter Applications**](https://research.google/pubs/slicer-auto-sharding-for-datacenter-applications/) | 1 | Google's, OSDI 2016. §2 is unusually honest about how uneven real load is |

---

## Five different problems with one name

"It doesn't fit on one machine" is five separate statements, and they arrive in different
orders in different systems. Knowing which one you are hitting decides what you do,
because three of the five have cheaper answers than partitioning.

| The limit | You hit it when | Cheaper answers first |
|---|---|---|
| **Storage** | the dataset exceeds the disk | archive, compress, shorten retention |
| **Write throughput** | writes exceed what one machine can absorb | batch, buffer, reduce amplification |
| **Read throughput** | reads exceed one machine | replicas, cache — neither needs partitioning |
| **Working set** | the hot data no longer fits in memory | more memory is astonishingly cheap |
| **Blast radius** | one machine failing is too much to lose | this is the one where partitioning is the *point* |

Notice that **read throughput is not a reason to partition.** Read replicas solve it, and
they keep every query answerable from one machine. People partition for read load
constantly and then discover they have taken on cross-partition queries for nothing.

---

## Try the boring things first

One machine goes further than most people believe, and the number moves every year. A
single modern server can hold tens of terabytes of storage, hundreds of gigabytes of
memory, and sustain write rates that would have needed a cluster a decade ago.

The order to try things, and it is the reverse of how it is usually done:

1. **Buy a bigger machine.** Cheap next to an engineer-month, and reversible.
2. **Delete something.** Retention policy, unused indexes, columns nobody reads.
   Week 3's arithmetic makes this a conversation with numbers in it.
3. **Add read replicas**, if the problem is reads.
4. **Split by function** — the events tables and the accounts tables become separate
   databases. Every query still lives on one machine, and you have gained headroom
   without gaining a distributed system.
5. **Then, and only then, partition horizontally.**

Step 4 deserves more credit than it gets. Functional partitioning gets you a long way,
keeps joins and transactions inside one machine, and is far easier to reverse.

---

## What partitioning actually costs

Not "complexity" — that word is too vague to design with. Six specific things stop
working, and each belongs in the price line of your pass-5 decision:

| Cost | What it means in practice |
|---|---|
| **Cross-partition queries** | any query without the partition key becomes scatter-gather: ask everyone, wait for the slowest |
| **Transactions** | atomic changes across two partitions need a protocol, and that protocol is a week-5 topic with its own price |
| **Joins** | either denormalise, or fetch and join in the application |
| **Secondary indexes** | an index on a non-key column is either local to each partition (and needs scatter-gather) or global (and needs its own consistency story) |
| **Rebalancing** | adding capacity now moves data around while serving traffic |
| **Lost pooling** | week 2: ten pools at 80% behave worse than one pool of ten at 80%. Partitioning is exactly this, deliberately |

That last one is worth pausing on because nobody mentions it. Splitting one pool of
servers into ten independent partitions **loses the statistical sharing that let bursts
on one be absorbed by idleness on another.** You are trading efficiency for isolation, on
purpose, and the isolation is often worth it — but it is a trade, and a design that does
not name it has not noticed.

---

## And the scatter-gather tail

One more week-2 consequence. A query that hits all sixteen partitions finishes when the
slowest of the sixteen finishes, so its latency is roughly the p99 of a single partition
rather than the median.

**Partitioning makes the tail worse for any query that does not carry the key.** This is
the single strongest argument for choosing a key that appears in your highest-volume
query, which is tomorrow — sorry, which is [the next article](choosing-a-partition-key.md).

---

## What goes in a design document

> Writes are 2M/s, which exceeds one machine, and the dataset is 28 TB, which does not
> fit either. **Partitioning is for write throughput and storage; reads are already
> served by the partition that owns the series.** The cost is that any query spanning
> series becomes scatter-gather, and the dashboard query does exactly that — so its
> budget is set by the slowest partition, not the average one.

Which limit, why partitioning rather than the cheaper answers, and what it costs. Three
sentences.

---

## Today's lab

`week-04/day-1/keys.py` — measuring how badly a key distributes before you commit to it.

Read [choosing a partition key](choosing-a-partition-key.md) first.

---

> **Sources for this article**
> [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) and
> [Slicer](https://research.google/pubs/slicer-auto-sharding-for-datacenter-applications/)
> — **Tier 1** · [Vitess docs](https://vitess.io/docs/reference/features/sharding/) —
> **Tier 2**. The five-limits table and the "try the boring things first" ordering are
> ours — **Tier 3**.
