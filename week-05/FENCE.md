# Week 5 — Concept fence

## Allowed

**Everything from weeks 1–4**, plus:

- **Replication** — the four reasons; synchronous, semi-synchronous, asynchronous;
  replication lag measured in time; applying a stream in order
- **Failover** — promoting the most current follower, the timeout guess, split brain
- **Quorums** — N, W, R; `W + R > N` and what it does not give you; sloppy quorums and
  hinted handoff
- **Conflicts** — concurrent versions, last-write-wins and its cost, siblings, merging,
  compare-and-set, read repair and anti-entropy
- **Consensus** — terms, votes, majorities, randomised election timeouts, check-quorum;
  FLP by name
- **Consistency** — linearizable, sequential, causal, session guarantees, eventual;
  read-your-writes and monotonic reads; CAP and PACELC; consistency against isolation
- **Leases and fencing tokens**
- **`simlib` in full** — `Network`, `Node`, partitions, crashes, loss

## Not yet

Log replication and snapshotting in detail · membership changes · distributed
transactions and two-phase commit · CRDTs and operational transformation (week 10) ·
caching (week 6) · message brokers and stream processing (week 7) · clock synchronisation
and TrueTime · anything with a vendor's name on it

---

## The rule, still

**Mechanisms yes, products no.** One more week. Next week the fence opens and you will
find that you reach for products later, and with reasons attached.

## The new rule

**Every design states what a reader is promised.**

Not "eventually consistent". Not "strongly consistent". This:

> A user always sees their own writes; other users see them within 2 seconds at p99;
> there is no ordering guarantee between two different users' writes, and the product
> does not need one.

Per-client guarantees, a staleness bound with a number, and the guarantee you have
deliberately not bought. Any design document from this week onward that describes its
consistency with a single adjective is incomplete.
