# Week 4 — Concept fence

## Allowed

**Everything from weeks 1–3**, plus:

- **Why and when to partition** — the five limits, functional before horizontal, the
  costs: cross-partition queries, transactions, joins, secondary indexes, rebalancing,
  and the pooling you gave up
- **Partition keys** — cardinality, distribution, presence in the query; skew as a
  measured number; compound partition and clustering keys; bounding a partition
- **Consistent hashing** — the ring, virtual nodes, keys moved on add and remove
- **Range partitioning** — ordered ranges, splits and merges, the sequential-key hotspot
- **Hot keys** — detection by top-k and sampling, splitting, replicating, caching,
  request coalescing
- **Ids** — auto-increment, random, time-ordered, Snowflake-style; clock skew; node
  assignment
- **Routing** — client-side, proxy, any-node; stale topology and redirects

## Not yet

Replication and how copies stay in step · quorums, consensus, leader election ·
consistency models and isolation · distributed transactions and two-phase commit ·
caching (week 6) · CDC and change streams · geospatial partitioning (week 10) ·
anything with a vendor's name on it

---

## The rule, still

**Mechanisms yes, products no.** Two weeks to go.

## The new rule

**Every partitioning decision states its skew.**

From this week, a design that says "partitioned by tenant" and stops is incomplete. The
shape is:

> Partitioned by tenant. **Measured skew on a sample of real load: 5.1.** Tenants above
> 5% are split by queue, which brings it to 2.1 and costs ordering across a tenant's
> queues.

Key, number, remedy, price. If you have not measured the skew, you have chosen a key by
hoping, and hope is the thing this week exists to replace.
