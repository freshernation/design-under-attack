# Indexes

*Week 3 · Day 1 · about 20 minutes*

> By the end of this you can say what an index costs, what a composite index can and
> cannot serve, and why the fastest query is the one that never touches the row.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**PostgreSQL — Indexes**](https://www.postgresql.org/docs/current/indexes.html) | 2 | Official documentation for one real implementation, including multi-column and index-only scans |
| [**Bigtable §2**](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/) | 1 | What you get when there is exactly one index and it is the row key |

---

## An index is a sorted copy

That is the whole idea. An index on `(tenant, created_at)` is a second structure holding
just those two columns plus a pointer back to the row, kept in sorted order.

Everything follows from "sorted copy":

- **It makes reads fast** — binary search instead of a scan
- **It makes writes slower** — a second structure to update, in order
- **It costs storage** — sometimes a lot; indexes on a write-heavy table can approach the
  size of the table
- **It only helps queries that match its ordering** — see the leftmost-prefix rule

---

## Composite indexes, and the order of columns

`(tenant, created_at)` and `(created_at, tenant)` are different indexes with different
capabilities, and picking the wrong order is the most common indexing mistake there is.

| Query | `(tenant, created_at)` | `(created_at, tenant)` |
|---|---|---|
| `tenant = 'acme'` | lookup | scan |
| `tenant = 'acme' AND created_at > T` | lookup | scan |
| `created_at > T` | scan | lookup |
| `created_at > T AND tenant = 'acme'` | scan | lookup, then filter |
| `tenant = 'acme' ORDER BY created_at` | free — already sorted | sort required |

Read the last row twice. **An index does not just find rows, it delivers them in an
order** — and an `ORDER BY` that matches the index costs nothing, while one that does not
costs a sort of the whole result set, in memory, on every request.

The rule: **equality columns first, then the one range or sort column.** Everything after
a range column in the index is no longer usefully ordered, so there is at most one of
them and it goes last.

---

## Covering indexes

If the index contains every column the query needs, the database never touches the row
at all.

```sql
-- index on (tenant, created_at, status)
SELECT status FROM watches WHERE tenant = 'acme' ORDER BY created_at
```

Everything the query wants is in the index, so this is one sequential read of a small
sorted structure — no random access to rows, no second lookup per row.

The difference is larger than it sounds. A non-covering index gives you a sorted list of
pointers, and following a thousand pointers is a thousand random reads. Making the index
cover turns that into one scan of contiguous data, and the ratio between random and
sequential access is the single biggest lever in storage performance.

The price is that the index is now wider, so it costs more to store and more to update.
Same trade as always: **you are moving cost from the read path to the write path**, and
your read/write ratio says whether that is a good deal.

---

## Selectivity: when an index does nothing

An index helps in proportion to how much it narrows the search.

```
selectivity = distinct values / rows
```

| Column | Distinct | Rows | Selectivity | Useful? |
|---|---|---|---|---|
| `email` | 10,000,000 | 10,000,000 | 1.0 | perfect |
| `product_id` | 10,000,000 | 100,000,000 | 0.1 | good |
| `status` | 3 | 100,000,000 | 0.00000003 | useless alone |

An index on `status` narrows 100 million rows to 33 million. Reading 33 million rows via
an index — one random access each — is *slower* than scanning the table sequentially, and
a competent query planner will ignore your index and scan. This surprises people who
added the index specifically to avoid the scan.

Low-selectivity columns are useful as the **leading** column of a composite index —
`(status, created_at)` is a fine index — because there the low cardinality is a grouping
rather than a filter.

---

## The other cost nobody counts

Indexes make writes slower in two ways, and only the first is obvious.

**The direct cost:** each index is another structure to update. Four indexes means five
writes per insert.

**The indirect cost:** those updates are at *random* positions — you are inserting into
the middle of a sorted structure, in a different place for each index. Random writes are
far more expensive than sequential ones on every storage medium ever built, and this is
the specific problem that LSM trees exist to solve. That is tomorrow.

---

## What goes in a design document

Not "we will index the right things". This:

| Query | Volume | Index | Covering? |
|---|---|---|---|
| watches by product | 5k/s | `(product_id)` | no — needs the email |
| watches by shopper | 20/s | `(email, created_at)` | yes |

Plus one line: **"writes touch N structures"**, and one line saying which query is
deliberately left as a scan.

That table is the difference between a data model and a list of entities.

---

## Today's lab

`access.py`, from the previous article. `can_serve` is the leftmost-prefix rule and the
tests walk through every row of the composite-index table above.

---

> **Sources for this article**
> [PostgreSQL documentation](https://www.postgresql.org/docs/current/indexes.html) —
> **Tier 2**, official documentation for one implementation ·
> [Bigtable](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/)
> — **Tier 1**. The selectivity table is illustrative arithmetic, ours — **Tier 3**.
