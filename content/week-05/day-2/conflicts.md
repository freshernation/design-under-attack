# When copies disagree

*Week 5 · Day 2 · about 25 minutes*

> By the end of this you can say what happens when two clients write the same key at the
> same time, why "last write wins" silently deletes data, and what the alternatives cost.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Dynamo**](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) §4.4 | 1 | Version vectors and the shopping-cart argument, from the people who shipped it |
| [**Jepsen — Consistency models**](https://jepsen.io/consistency) | 1 | Where the resulting guarantees sit |
| [**Cassandra — Dynamo architecture**](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html) | 2 | Last-write-wins in production documentation, including what it does about clocks |

---

## The problem

Two clients read `x = 1`. Both write. One writes `2`, the other writes `3`. Both reach a
quorum. Now some copies say `2` and some say `3`.

**The system cannot tell which happened "first"**, because there is no global clock, and
even if there were, wall clocks on different machines disagree by milliseconds to seconds.
Something must decide, and every option is a real decision with a real cost.

---

## Last write wins

Attach a timestamp; the highest wins; the other value is discarded.

Simple, no storage overhead, no client involvement. And it **silently destroys data**:

- The two writes were concurrent, so "last" is meaningless — you are picking by clock
  reading, not by causality
- Clock skew decides. A machine one second ahead wins every race it enters
- The losing write was acknowledged. The client was told it succeeded, and it was not

Cassandra's documentation is unusually honest about this, and the honest summary is:
**last-write-wins is correct only when losing a write is acceptable.** For a cache, a
presence indicator, a "last seen" field — fine, and simple. For anything a person would
notice missing — not fine, and the failure is invisible.

---

## Version vectors and siblings

Dynamo's answer. Each write carries a version; when versions are **concurrent** rather
than one descending from the other, keep both and hand both to the reader.

```
read cart  -> [{apple}, {banana}]   two siblings, neither newer
```

The application resolves it. For a shopping cart, union the items — which is why Dynamo's
famous example is a cart, and why the failure mode is "a deleted item comes back" rather
than "your order vanished". Amazon chose the recoverable failure on purpose.

What this costs, and it is why it is not universal:

- **Every reader must handle siblings.** Not a library concern; application logic
- **Storage grows** with unresolved versions
- **Some data has no sensible merge.** Two edits to a bank balance cannot be unioned, and
  presenting both to a user is not a product

The general shape: **conflict resolution is a domain question, not a storage question.**
A storage system can only tell you *that* there is a conflict; what to do about it depends
on what the data means.

---

## Avoiding the question

Often the best answer, and usually the one available:

| Approach | How it removes the conflict |
|---|---|
| **One writer per key** | the leader arrangement. No concurrent writes, so no conflicts |
| **Immutable data** | append events rather than overwriting state. Nothing to conflict |
| **Commutative operations** | "add 1" and "add 1" merge to "add 2" regardless of order |
| **Compare-and-set** | the write states the version it read; a stale one is rejected rather than merged |

The third is worth its own note: an operation that is **commutative** — order does not
matter — has no conflicts by construction. Counters, sets, and last-seen maxima all
qualify. This is the idea CRDTs generalise, and week 10 goes there.

The fourth is what most systems actually use, and it converts a silent conflict into a
visible error that the client can retry. That is a much better failure than either
picking a winner or handing back siblings.

---

## Read repair and anti-entropy

Two mechanisms that get mentioned constantly and are worth being precise about:

**Read repair.** A read touches R nodes and notices one has an old value; the coordinator
writes the newer value back. Cheap, and it only repairs data anyone reads — so a key
nobody reads stays diverged for ever.

**Anti-entropy.** A background process compares replicas and reconciles them, usually
using hash trees so that comparing large datasets is cheap. Slower, and it covers the
keys nobody reads.

Real systems need both, for the reason implied: read repair covers the hot data cheaply,
anti-entropy covers the cold data eventually. A design with only read repair has a slow
data-loss problem in its cold tail.

---

## What goes in a design document

> Concurrent writes to one key are made impossible rather than resolved: each key has a
> single writer, and clients use compare-and-set with the version they read. **Rejected:
> last-write-wins** — a rejected write is a retry, a silently discarded one is a support
> ticket nobody can reproduce. **Price:** clients must handle a version-conflict error,
> and a hot key under contention will see retries.

---

## Today's lab

`quorum.py`, from the previous article, includes the conflict side:

- concurrent writes producing two versions
- `last_write_wins(versions)` and a test showing a **clock-skewed node winning a race it
  should have lost** — the failure that has no error message
- `siblings(versions)` returning both, and a merge function for a set-shaped value
- `compare_and_set(key, expected_version, value)` and the rejection

Write `last_write_wins` first and then run the clock-skew test. Watching a legitimate
write disappear because another machine's clock was 800 ms fast is more persuasive than
this article.

---

> **Sources for this article**
> [Dynamo §4.4](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
> — **Tier 1** for version vectors and the cart argument ·
> [Cassandra docs](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
> — **Tier 2** for last-write-wins in practice · [Jepsen](https://jepsen.io/consistency)
> — **Tier 1**. The "avoiding the question" table is ours — **Tier 3**.
