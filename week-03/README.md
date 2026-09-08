# Week 3 — Storage and the data model

> **Destination**
> Choose how data is organised from the questions you will ask of it, and say what
> that choice costs on the other side.

Week 2 was about time. This week is about space, and about the fact that every storage
engine ever built is the same trade made in a different place.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Model backwards from queries, and say what an index costs |
| Tue | `day-2/` | Choose between update-in-place and log-structured, with numbers |
| Wed | `day-3/` | Build a log-structured store — memtable, tombstones, compaction |
| Thu | `day-4/` | Build a write-ahead log that survives a torn write |
| Fri | `milestone/` | Ship the metrics store design, then defend it |

---

## The one idea

**Sequential access is far cheaper than random access, and every storage design is an
answer to that.**

A B-tree accepts random writes to keep reads simple. A log-structured store makes writes
sequential and pays later, in background work and read complexity. A write-ahead log
turns one random write into a sequential write plus a deferred random one. Three
mechanisms, one fact.

Once you see it, the choices stop being a taxonomy to memorise and become a question you
can reason about: *where in this system would I rather pay?*

---

## What is new this week

**You build two real things.** A log-structured store on Wednesday and a crash-safe log
on Thursday. Both are small — eighty lines each — and both behave the way the production
ones do in the respects that matter.

**Thursday touches real files.** The WAL tests damage the file on disk the way a power
cut damages one: truncated mid-record, a byte flipped. That is the only honest way to
test crash safety and it is worth seeing.

**The week-2 connection is live all week.** Compaction is a service-time spike, which is
a variability increase, which is a queueing increase at the same utilisation. If that
sentence does not yet mean anything to you, go back to `bimodal_cv` before Wednesday.

---

## Milestone

A metrics store: two million points a second, three query shapes, and a storage ceiling
that the retention policy only just fits inside. Spec in `milestone/README.md`.

One line of the brief — *an average over any window must be right* — rules out the
obvious implementation. Finding out why takes four seconds in the lab and is the point
of the week.

---

## What this week is not about

Databases. You will not learn which database to pick, and that is deliberate: the answer
changes every two years and the reasoning does not. What you learn is what to ask of one,
which survives.

Nor is it about implementing storage engines for a living. It is about being able to say
*"this workload is append-heavy with range reads, so a log-structured store fits and the
cost is compaction pauses on the read path"* — one sentence, and it is worth more in a
design review than any amount of product knowledge.
