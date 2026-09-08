# Day 3 — Build a log-structured store

> **By the end of today** you have written one, and you know why the read order is a
> correctness property rather than an optimisation.

---

## Read first

- [ ] [**Inside an LSM store**](../../content/week-03/day-3/inside-an-lsm.md) — 25 min · sources: [LevelDB implementation notes](https://github.com/google/leveldb/blob/main/doc/impl.md), [RocksDB wiki](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview)

---

## The lab

`memtable.py` — `LSMStore`, about eighty lines.

```python
LSMStore(memtable_limit=4)
    .put(key, value)      # flushes automatically when the memtable is full
    .delete(key)          # writes a tombstone
    .get(key)             # None when absent or tombstoned
    .flush()
    .compact()
    .keys()
    .sstables             # newest first
    .stats                # flushes, compactions, sstables_read
```

Write it in this order and it stays simple:

1. `put`, `get`, `flush` with no deletes at all — get the newest-wins ordering right
2. `delete` and the tombstone, and fix `get` to treat a tombstone as a hit
3. `compact`, and only then think about when a tombstone may be dropped

**The mistake to expect** is `get` treating a tombstone as "not here, keep looking". It
then finds the older value underneath and returns it — a deleted record coming back from
the dead. The tests catch it, but catching it yourself is better.

`stats["sstables_read"]` is read amplification, counted. One test uses it to show that
compaction makes reads cheaper as well as smaller, which is the half people forget.

```bash
pytest week-03/day-3 -v
```

---

## The written exercise

`week-03/day-3/lsm-costs.md`, half a page.

Suppose your week-2 rate limiter's per-tenant counters lived in a store like the one you
just built, with 50,000 tenants updated constantly.

- What is the read path for one limiter decision? How many files might it touch?
- How many versions of one tenant's counter exist between compactions?
- **Would you use this store for that workload?** One sentence, with the reason.

The answer is no. Being able to say precisely why — updates to hot keys are exactly what
a log-structured store is worst at — is the exercise.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
