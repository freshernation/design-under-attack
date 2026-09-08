# Week 3 — Concept fence

## Allowed

**Everything from weeks 1–2**, plus:

- **Access patterns** — modelling backwards from queries, the leftmost-prefix rule,
  covering indexes, selectivity, the write cost of an index
- **B-trees** — pages, in-place update, why writes are random, page-level write
  amplification
- **LSM trees** — memtable, SSTable, tombstones, compaction, leveled against tiered
- **Amplification** — write, read and space; the three-way trade; the device-write
  multiplication
- **Write-ahead logs** — framing with length and checksum, fsync, group commit, torn
  writes, recovery as a prefix, checkpoints
- **Storage shapes named generically** — key-value, wide-column, relational, document,
  blob, time series

## Not yet

Replication of any kind · quorums, consensus, leader election · transactions and
isolation levels · distributed transactions · partitioning and resharding (week 4) ·
membership filters and caching (week 6) · secondary indexes across partitions · CDC and
change streams · anything with a vendor's name on it

---

## The rule, still

**Mechanisms yes, products no.**

This week the temptation is at its worst, because you now know enough to have opinions
about specific databases. Hold the line for two more weeks. Write:

> "a log-structured store with a one-minute memtable and leveled compaction"

not the name of the thing that does that. The first sentence says what you need; the
second says what you have heard of. In a design review, only one of them can be
discussed.

## The new rule

**Every storage decision states its access pattern first.**

From this week, "we store it in X" is not a decision in your documents. The shape is:

> *This data is written once and read in time ranges, never updated. So: ordered by
> time, log-structured, compaction cost on the read path.*

Workload, then shape, then cost. If you cannot state the workload in one sentence, you
are not ready to choose the shape.
