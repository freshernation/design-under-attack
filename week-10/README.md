# Week 10 — The deep track

> **Destination**
> Meet four domains where the general mechanisms are not enough, and learn the question
> that unlocks a domain you have never seen.

Nine weeks of mechanisms that apply everywhere. This week, four problems where they do not
quite fit — and, more importantly, a way of approaching an unfamiliar one.

---

## The week

| Day | Folder | The domain | The lab |
|---|---|---|---|
| Mon | `day-1/` | Geospatial — proximity without scanning | `geo.py` |
| Tue | `day-2/` | Collaborative editing — converging without a lock | `crdt.py` |
| Wed | `day-3/` | Matching engines — determinism as a requirement | `orderbook.py` |
| Thu | `day-4/` | Serving models and media — two expensive resources | `serving.py` |
| Fri | `milestone/` | One specialised design, from five briefs |

Thursday also carries an optional fifth topic —
[decentralised protocols](../content/week-10/day-4/decentralised-protocols.md) — as reading
without a lab, and it is the best-documented system in the course.

---

## The one question

> **What is the expensive thing here, and what is the design doing to avoid spending it?**

An accelerator. A byte crossing a network. A lock on a hot data structure. A round trip
you cannot make. Answer that and most of a specialised architecture explains itself.

It is also what to ask when you meet a domain you have never seen, which is the real
reason this week is in the course. You will not be asked to design a matching engine. You
will be asked to design something in a domain nobody taught you, and this is the way in.

---

## The second question, which is harder

> **Would a general mechanism have been good enough?**

A specialised mechanism has a fixed cost — to build, to operate, to hire for, to explain
to the next person. It pays for itself above some volume and not below it.

**The biggest risk this week is over-building**, because the specialised answer is more
interesting than the ordinary one. The milestone lab is entirely about computing the
break-even, and one of its tests is the case where no volume justifies the specialisation
at all.

---

## What you will notice

Most of what looks exotic is machinery you already have, wearing different clothes:

- A cell index is a partition key, and a dense cell is a hot key
- A CRDT is week 5's conflict resolution, made unnecessary rather than automatic
- A matching engine is week 3's write-ahead log with the ordering promoted to the centre
- Continuous batching is week 2's queue, on expensive hardware
- A federated event stream is week 7's log, published rather than internal

**The novelty is usually in the constraints, not the mechanisms.** Noticing that is what
lets you be useful in a domain you have never worked in.

---

## What this week is not about

Becoming a specialist. Four days is not enough to be trusted with an exchange or an
inference platform, and pretending otherwise would be dishonest.

It is enough to have the conversation: to know what the expensive resource is, what the
standard answer looks like, what it costs, and which questions to ask the person who does
know. That is the useful version of breadth.
