# Day 2 — The ring, and the alternative

> **By the end of today** you can build a hash ring, measure what virtual nodes buy,
> and choose between hashing and ranges from the access pattern.

---

## Read first

- [ ] [**Consistent hashing**](../../content/week-04/day-2/consistent-hashing.md) — 25 min · sources: [Dynamo §4.2](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Cassandra](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [ ] [**Range partitioning against hash partitioning**](../../content/week-04/day-2/range-versus-hash.md) — 20 min · sources: [Bigtable](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/), Dynamo

Two Tier 1 papers, two opposite decisions, both correct. That contrast is the day.

---

## Predict first

Three nodes, twenty thousand keys, `hash(key) % 3`. You add a fourth node.

What fraction of keys move? Write a number down before the lab tells you.

---

## The lab

`ring.py`.

```python
HashRing(nodes, virtual_nodes=100)
    .add(node) / .remove(node) / .node_for(key) / .nodes

distribution(ring, keys)          skew_of(counts)
keys_moved(before, after, keys)   modulo_keys_moved(keys, before_count, after_count)
range_partition_for(key, boundaries)
```

Build it with a sorted list of `(position, node)` and `bisect`. Each node gets
`virtual_nodes` positions, hashed from a name like `f"{node}#{i}"`. `node_for` bisects and
**wraps round to position 0** when it falls off the end — that wrap is the ring, and
forgetting it makes the highest-hashing keys homeless.

Two tests are the day:

- `test_modulo_moves_three_quarters_of_the_keys` against `test_the_ring_moves_about_a_quarter`
- `test_one_position_per_node_distributes_badly` against `test_virtual_nodes_fix_the_skew`

Both are measurements you produced, which is why they are worth more than the article.

```bash
pytest week-04/day-2 -v
```

---

## The written exercise

`week-04/day-2/hash-or-range.md`, half a page.

Four workloads. For each: hash, range, or the hybrid — and one sentence of why.

1. Chat messages, queried as "the last 50 in this channel"
2. User profiles, queried by user id only
3. Audit events, queried as "everything in this hour, across all users"
4. Shopping carts, queried by cart id, written constantly

Then one paragraph: **which of the four has no good answer, and what would you negotiate?**
One of them genuinely does not, and spotting it is the exercise.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
