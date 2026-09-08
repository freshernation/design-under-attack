# Day 1 — Access patterns and indexes

> **By the end of today** you can write a data model backwards from its queries, and
> say in one sentence what each index costs.

---

## Read first

- [ ] [**Access patterns first**](../../content/week-03/day-1/access-patterns-first.md) — 25 min · sources: [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) §1–2, [Bigtable](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/) §2
- [ ] [**Indexes**](../../content/week-03/day-1/indexes.md) — 20 min · source: [PostgreSQL — Indexes](https://www.postgresql.org/docs/current/indexes.html)

Read Dynamo §1–2 properly. Four pages, and it is where most of this week comes from.

---

## Predict first

An index on `(tenant, created_at)`. Which of these does it serve without a scan?

1. `WHERE tenant = 'acme'`
2. `WHERE created_at > '2026-01-01'`
3. `WHERE tenant = 'acme' ORDER BY created_at`
4. `WHERE tenant = 'acme' AND status = 'open'`

Write your four answers down before the lab. Number 3 catches people who think an index
only finds rows, and number 4 catches everyone else.

---

## The lab

`access.py` — the rules as code.

```python
can_serve(index, equalities, range_column=None, order_by=None)
is_covering(index, selected)
selectivity(distinct_values, rows)
write_amplification(index_count)
```

`can_serve` is the leftmost-prefix rule and it is the only one with any subtlety. The
docstring states the exact rule; the tests walk every row of the article's table.

You are implementing a simplification, and knowing that is part of the exercise — real
planners handle index merges, skip scans and backwards scans. The leftmost-prefix rule
is the part that transfers to every ordered structure you will ever meet.

```bash
pytest week-03/day-1 -v
```

---

## The written exercise

In `week-03/day-1/model-for-my-metrics.md`, half a page — this is the head start on
Friday, so do it properly.

For the metrics store in `milestone/README.md`:

1. Write the three query shapes as questions in plain words, with their volumes
2. For each, say what the data would have to be ordered by to serve it as a lookup
3. Say which single ordering serves the 95% query, and what that costs the other two
4. One sentence: **what query is this model deliberately bad at?**

Step 4 is the one that matters. Every model makes something expensive; a document that
says which has made a decision, and one that does not has made the same decision
accidentally.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
