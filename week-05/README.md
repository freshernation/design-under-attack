# Week 5 — Replication and consistency

> **Destination**
> Keep several copies of data, know exactly what a reader is promised, and survive a
> network partition without inventing two versions of the truth.

Week 4 gave every key one home. Remove that assumption and almost everything hard in
distributed systems arrives at once.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Measure replication lag, and count the acknowledged writes a failover loses |
| Tue | `day-2/` | Pick N, W and R, and say what the overlap does and does not guarantee |
| Wed | `day-3/` | Implement leader election, and prove no term ever has two leaders |
| Thu | `day-4/` | Give a client read-your-writes without making anything linearizable |
| Fri | `milestone/` | Ship the lease service, then defend it |

---

## The one idea

**You cannot tell a crashed machine from a slow one.** Not with better engineering — it
is a proof. Everything this week is a strategy for being correct anyway.

Timeouts are guesses. Majorities are the trick that makes two answers impossible. Fencing
tokens make a confused participant harmless rather than preventing the confusion.
Session guarantees give one client what it needs without making everyone pay.

---

## What is new

**This is the hardest week so far, and the labs are the reason.** Wednesday you implement
Raft leader election and then run it through ten seeds of message loss, random crashes
and moving partitions, asserting that no term ever had two leaders. That test is the
actual safety guarantee, and you will have built the thing that provides it.

**Failure is now the normal case.** Weeks 1–4 mostly assumed things worked. From here,
every lab has something breaking in it, and the interesting behaviour is what happens
next.

---

## Milestone

A lease service. The scenario it exists for: a client acquires a lease, its host freezes
for forty seconds, the lease expires, someone else takes over — and then the first client
wakes up believing nothing happened. Spec in `milestone/README.md`.

Checking the expiry does not save you. Finding out why is the week.

---

## What this week is not about

Implementing a database. You will not write log replication, snapshots, membership
changes or any of the parts that make a real consensus system usable — those are months
of work and they are not what a design conversation turns on.

What a design conversation turns on is: what does a reader see, what does a failover
cost, and what happens on the minority side of a partition. Those you will be able to
answer precisely, from mechanisms you have built.
