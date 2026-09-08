# Day 2 — B-trees and LSM trees

> **By the end of today** you can say which shape a workload wants and price the
> decision, in bytes per second on an actual device.

---

## Read first

- [ ] [**B-trees and LSM trees**](../../content/week-03/day-2/b-trees-and-lsm-trees.md) — 30 min · sources: [LevelDB implementation notes](https://github.com/google/leveldb/blob/main/doc/impl.md), [RocksDB wiki](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview), [Bigtable](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/)
- [ ] [**Amplification, and the three-way trade**](../../content/week-03/day-2/amplification.md) — 25 min · sources: [Leveled Compaction](https://github.com/facebook/rocksdb/wiki/Leveled-Compaction), [The RUM Conjecture](https://openproceedings.org/2016/conf/edbt/paper-12.pdf)

The LevelDB implementation notes are four pages and are the clearest description of an
LSM tree anywhere. Read them today; tomorrow you build a small one.

---

## The lab

`amplification.py` — six functions, all arithmetic.

```python
btree_write_amplification(page_bytes, row_bytes)
lsm_write_amplification(levels, size_ratio)
lsm_read_amplification(file_count, false_positive_rate=0.01)
space_amplification(live_bytes, obsolete_bytes)
device_write_rate(writes_per_second, bytes_per_write, amplification)
compare_compaction(strategy)
```

**Read the module docstring before you write anything.** These are models with stated
assumptions, not measurements, and the tests are careful about the difference: they
assert the *direction* of the compaction trade and never its numbers, because asserting
the numbers would teach you to trust them.

That distinction is worth more than the functions. An interviewer who has run these
systems will respect "roughly thirty, by this model, and it depends heavily on the key
distribution". They will not respect a confident wrong number.

```bash
pytest week-03/day-2 -v
```

---

## The written exercise

Two short pieces in `week-03/day-2/amplification-of-my-designs.md`:

**One.** Take the metrics store brief: 2,000,000 points a second at 32 bytes. Compute
the application write rate, then the device write rate at a plausible amplification.
State which model you used. Is the answer comfortable?

**Two.** Take your week-2 rate limiter's per-tenant state — 50,000 tenants, updated
constantly, tiny records. Which storage shape does that workload want, and why is it the
opposite answer to the metrics store?

The second one is the point of the day. Two systems in the same repo, two opposite
answers, and the reason is one sentence about the workload each time.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
