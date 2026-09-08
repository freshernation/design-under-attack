# Leaders, followers, and failover

*Week 5 · Day 1 · about 25 minutes*

> By the end of this you can describe what happens when a leader dies, name the three
> ways failover goes wrong, and say why "just promote a follower" is not a plan.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Raft**](https://raft.github.io/raft.pdf) §1–2 | 2 | Why leader-based replication is the common design, stated precisely. Wednesday is the rest of it |
| [**Spanner**](https://research.google/pubs/spanner-googles-globally-distributed-database-2/) §2 | 1 | Leader-based replication at Google, with the failover story included |
| [**Jepsen analyses**](https://jepsen.io/analyses) | 1 | Independent testing of real databases. Read one. Any one. It is a bracing experience |

---

## One writer, many readers

The overwhelmingly common arrangement, and for a good reason: **if only one node accepts
writes, most disagreements cannot happen.** Ordering is decided in one place, so there is
an order.

```
client writes  ->  leader  ->  followers (copies of the leader's decisions)
client reads   ->  leader (current) or follower (fast, maybe behind)
```

Everything difficult is in what happens when the leader is gone.

---

## Failover, and its three failures

The leader dies. Something must notice, choose a successor, and tell everyone. Three
things go wrong, and all three are worth being able to name.

### 1. Choosing a follower that is behind

Followers lag by different amounts. Promote one that is missing the last two seconds of
writes and **those writes are gone** — writes that were acknowledged, that a user was
told had succeeded.

Worse, they are not obviously gone. The new leader starts accepting writes, ids get
reused, and a week later someone finds two different records with the same identifier.

The mitigation is to promote **the most up-to-date follower**, which means knowing which
that is, which means the followers must agree on what has been written — which is
Wednesday's problem.

### 2. Deciding the leader is dead when it is not

You cannot distinguish "the leader has crashed" from "the leader is slow" or "the network
between us is broken". This is not an engineering gap; **it is a proof**, and every
system that pretends otherwise is choosing a failure mode rather than avoiding one.

So failover is triggered by a timeout, and a timeout is a guess:

| Timeout | Cost |
|---|---|
| Too short | healthy leaders get replaced under load, exactly when load is high |
| Too long | the system is unavailable for that long, every time |

There is no correct value, only a chosen point on that trade. Say which you chose and
why.

### 3. Split brain

The old leader has not crashed. It was slow, or partitioned. It is still accepting
writes. Now **two nodes each believe they are the leader**, and both are taking writes
for the same keys.

This is the worst failure in the week, because both halves look healthy from inside. It
is week 4's stale routing map again, one level worse: two nodes thinking they *own* a key
was a routing bug; two nodes thinking they may *write* it is data loss with no error
message anywhere.

The remedies are the week's real content:

- **Majorities** — a leader that cannot reach a majority stops being a leader. The old
  leader, alone on the wrong side of a partition, cannot get a majority and steps down.
  Wednesday.
- **Fencing tokens** — every leadership term gets a number, and storage rejects writes
  carrying an old one. The old leader may still believe it is leader; nothing will accept
  its writes. Friday's milestone.

Note that the second does not prevent the confusion, it makes the confusion harmless.
That distinction is a good thing to have opinions about.

---

## Reading from followers

The reason to have them, and the reason for Thursday.

| Read from | Sees | Costs |
|---|---|---|
| Leader | everything, current | leader load; no read scaling |
| Follower | whatever has arrived | stale reads, of unbounded age when lag spikes |
| Quorum of followers | the latest, if enough agree | more requests per read. Tomorrow |

The thing to notice: **staleness is unbounded.** Under normal conditions a follower is
milliseconds behind; under load, during a compaction, or after a network problem, it can
be minutes. A design that says "followers are a bit behind" has not put a number on the
worst case, and the worst case is when it matters.

A useful pattern is to make the bound explicit: a follower that is more than N seconds
behind removes itself from the read pool. You have converted an invisible correctness
problem into a visible capacity one, which is a much better problem.

---

## What goes in a design document

> Writes go to one leader per partition and replicate semi-synchronously: acknowledged
> once one follower has it. **Rejected: fully synchronous** — the slowest follower would
> set every write's latency, and a single slow machine would stop writes. **Rejected:
> asynchronous** — the envelope says no acknowledged write may be lost, and asynchronous
> loses the tail on failover. **Price:** writes cost one network round trip, and losing
> two specific machines together loses data.

Note that "which followers, and how the new leader is chosen" is not answered here. That
is Wednesday, and a document that hand-waves it has hand-waved the hard part.

---

## Today's lab

`week-05/day-1/replica.py`, on `simlib`'s network:

- `Leader` and `Follower` nodes, asynchronous replication, real message latency
- `lag_ms()` — how far behind each follower is
- a read from a follower returning a stale value, as an assertion
- killing the leader mid-replication and counting the acknowledged writes that vanished

The last one is the test to sit with. You will write an assertion that says *"three
writes were acknowledged and one of them no longer exists"*, and that is a true statement
about a correctly implemented asynchronous system.

---

> **Sources for this article**
> [Raft §1–2](https://raft.github.io/raft.pdf) — **Tier 2** ·
> [Spanner](https://research.google/pubs/spanner-googles-globally-distributed-database-2/)
> and [Jepsen](https://jepsen.io/analyses) — **Tier 1**. The three-failures framing is
> ours — **Tier 3**. The impossibility of distinguishing a crashed node from a slow one
> is a result, not an opinion, and Wednesday cites it properly.
