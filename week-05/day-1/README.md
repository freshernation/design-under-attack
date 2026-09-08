# Day 1 — Leaders, followers, and lag

> **By the end of today** you can measure replication lag in milliseconds and count
> exactly how many acknowledged writes a failover throws away.

---

## Read first

- [ ] [**Why copies, and what they cost**](../../content/week-05/day-1/why-copies.md) — 25 min · sources: [Dynamo §4](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Spanner](https://research.google/pubs/spanner-googles-globally-distributed-database-2/), [Jepsen — consistency models](https://jepsen.io/consistency)
- [ ] [**Leaders, followers, and failover**](../../content/week-05/day-1/leaders-and-followers.md) — 25 min · sources: [Raft §1–2](https://raft.github.io/raft.pdf), [Jepsen analyses](https://jepsen.io/analyses)

Read one Jepsen analysis in full this week. Any one. It is a bracing experience and it
permanently changes how you read a database's marketing page.

---

## The lab

`replica.py`, on `simlib`'s network — real latency, real jitter, real message loss.

```python
Follower(name, sim)      .receive(...)  .read(key)  .applied_version  .pending
Leader(name, sim, follower_names)   .write(key, value) -> version   .read(key)

build(sim, followers=2, latency_ms=(10, 40), loss=0.0)
entries_behind(leader, follower)      lag_ms(sim, leader, follower)
most_current(followers)               acknowledged_writes_lost(leader, promoted)
```

The detail that matters: **a replication stream is buffered and applied in order.** Jitter
reorders messages, and a follower that applied entry 7 before entry 6 would be in a state
the leader was never in. Buffer into `pending` and drain whatever is contiguous.

Two tests are the day:

- `test_one_lost_message_stalls_everything_behind_it` — one dropped message and the
  follower stops applying anything, for ever, while thirteen later entries sit in memory.
  It is not corrupt and not complaining. Only a lag metric would ever tell you.
- `test_acknowledged_writes_disappear_on_failover` — you will assert that writes the
  system said were saved no longer exist anywhere. That is a true statement about a
  correctly implemented asynchronous system, and it is the bill for not waiting.

```bash
pytest week-05/day-1 -v
```

---

## The written exercise

`week-05/day-1/replication-in-my-designs.md`, half a page.

For your metrics store and your job queue:

1. Which of the four reasons are you replicating for? Be specific — it is usually two.
2. Synchronous, semi-synchronous or asynchronous, and what does that choose about lost
   writes?
3. What is the worst-case staleness a reader can see, in seconds? Not "small" — a number.
4. Does anything in either design read from a replica without caring? Should it?

Question 3 is the one most designs cannot answer, and the answer is almost never bounded
unless somebody bounded it.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
