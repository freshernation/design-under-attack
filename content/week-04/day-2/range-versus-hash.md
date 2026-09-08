# Range partitioning against hash partitioning

*Week 4 · Day 2 · about 20 minutes*

> By the end of this you can choose between the two from the access pattern, and
> recognise the hotspot that sequential keys create in a range-partitioned store.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Bigtable**](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/) §2, §5.2 | 1 | Range partitioning, done by Google: tablets, splits, and why the row key ordering matters |
| [**Dynamo**](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) §4.2 | 1 | Hash partitioning, done by Amazon, for a workload with no range queries |
| [**Cassandra — Dynamo architecture**](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html) | 2 | The hybrid: a hashed partition key with an ordered clustering key inside it |

Two Tier 1 papers, two opposite decisions, both correct. That contrast is the article.

---

## The two schemes

**Hash.** Hash the key, and the hash decides the partition. Distribution is even by
construction. Adjacent keys land nowhere near each other.

**Range.** Partitions own contiguous spans of the key space — `a`–`f`, `g`–`m`, and so on.
Adjacent keys are together, so scans are cheap. Distribution depends entirely on how keys
are distributed, which is to say it is your problem.

| | Hash | Range |
|---|---|---|
| Point lookup | one partition | one partition |
| Range scan | **every partition** | one, or a few |
| Distribution | even, free | your problem |
| Sequential keys | fine | **a hotspot** |
| Rebalancing | move virtual nodes | split and merge ranges |

---

## The sequential-key hotspot

The failure mode that defines range partitioning, and it is easy to walk into.

Partition by timestamp, or by an auto-incrementing id, or by anything that grows. Every
new write has a key larger than the last, so **every write goes to the last partition**.
One machine takes 100% of the write load; the others hold history and are idle.

Worse, it is invisible in a test with a small dataset, because with one partition
everything is the last partition. It appears when you scale up, which is when you least
want it.

The standard remedies, and each has a cost you should name:

| Remedy | Cost |
|---|---|
| **Hash a prefix** — `(hash(user) % 16, timestamp)` | scans now touch 16 partitions instead of 1 |
| **Reverse the key**, so the varying part leads | ordering by time is gone |
| **Bucket by a coarser dimension** — `(day, timestamp)` | a single day is still one hot partition |

The first is the common answer and it is a genuine trade: you have converted a write
hotspot into a 16-way scatter on reads. Which is right depends on your read/write ratio,
which you computed in week 1.

---

## The hybrid, and why nearly everything uses it

Hash the **partition key**, keep the **clustering key** ordered within the partition.

```
partition key  hash(series_id)   -> spreads evenly across the fleet
clustering key timestamp          -> ordered inside one partition
```

You get even distribution across machines *and* cheap ranges within a partition. The
metrics store's 95% query — one series, last hour — is one lookup followed by one
sequential read.

The thing you do not get is a range across partitions. "All series between X and Y" or
"everything written in the last hour, across all series" still asks everybody. That
limitation is inherent, not an implementation gap, and a design that needs both usually
ends up storing the data twice — which is a decision with a price, and back to week 3.

---

## Splitting, and who does it

Range partitioning has one real advantage beyond scans: **ranges can split themselves.**
When a range grows too large or too hot, it becomes two ranges. The system adapts to the
actual distribution rather than the one you predicted. Bigtable's tablets work this way,
and Slicer is Google generalising the idea to services rather than storage.

Hash partitioning cannot do this as naturally — the hash space is uniform by
construction, so there is nothing to split unevenly. You get evenness for free and
adaptivity not at all.

Which is the better property depends on whether your load is predictable. If a few keys
can become arbitrarily hot, the ability to split them apart is worth a great deal — and
that is Wednesday.

---

## Choosing

Two questions, in this order:

1. **Does the high-volume query need a range?** If yes, you need ordering, so either
   range-partition or use a hybrid with the range inside the partition.
2. **Are the keys sequential?** If yes, plain range partitioning gives you a write
   hotspot, so hash something into the key.

Almost every real answer is the hybrid, and being able to say *which* part is hashed and
*which* is ordered, and what each buys, is the whole of this decision.

---

## Today's lab

`ring.py`, from [the previous article](consistent-hashing.md). One of its tests
demonstrates the sequential-key hotspot directly: the same keys through a hash ring and
through a range split, with the resulting distributions side by side.

---

> **Sources for this article**
> [Bigtable](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/)
> and [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) —
> **Tier 1**, and the two opposite decisions are theirs ·
> [Cassandra docs](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
> — **Tier 2** for the hybrid. The remedies table is ours — **Tier 3**.
