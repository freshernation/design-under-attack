# The decision record

*Week 11 · Day 3 · about 20 minutes*

> By the end of this you have the artefact this course was actually building: a
> collection of decisions you can defend, and reuse.

---

## The decision, as a unit

Ten weeks of writing them. The shape, one more time, because it is the thing that
transfers:

> **What we chose.** Partition by tenant, splitting tenants above 5% of load by queue.
>
> **What we rejected, and why.** A dedicated partition per large tenant — it needs manual
> intervention as tenants grow and shrink, and we expect them to.
>
> **What it costs.** Reads for split tenants fan out sixteen ways, so their p99 is the
> slowest of sixteen.
>
> **What would change our mind.** If a single tenant exceeded 30% of platform load, the
> split stops being sufficient and the tenant needs isolation rather than sharding.

Four parts. The fourth is the one nobody writes and the one that makes a decision
**reviewable a year later** — because the person reading it then does not want to know what
you thought, they want to know whether it still holds.

---

## The library

You have now made somewhere between thirty and fifty of these. Collected, they are the most
valuable thing you will take out of this course.

Not because you will look them up — you mostly will not. Because **you can design a system
you have never seen** by recognising which decisions it needs, and that recognition comes
from having made them before, with prices attached.

That is the difference the course was aiming at. Somebody who memorised fifteen
architectures can answer fifteen questions. Somebody with fifty priced decisions can answer
a question nobody has written up.

### Assembling it

One page. For each decision: the choice, the rejected alternative, the price, the condition
that flips it, and where you first met it.

```
Fan-out on write below a threshold, read above it
  rejected: uniform fan-out on write — one post becomes 200M writes
  price:    a read is a lookup plus a merge of a few dozen sources
  flips if: the follower distribution stops being heavy-tailed
  week 8, and the same shape as week 4's whale and week 6's tail
```

The last line matters more than it looks. **Decisions that recur across domains are the
ones worth carrying**, and noticing that four of your decisions are the same decision is
worth more than having four.

---

## The recurring ones

By now you should recognise most of these without effort. If any is unfamiliar, that is
where to spend an evening before week 12:

| The shape | Where it appeared |
|---|---|
| Two populations, two strategies | weeks 4, 6, 7, 8, 10 |
| A monotonic token makes a confused participant harmless | weeks 5, 6 |
| Anything synchronised needs jitter | weeks 6, 8, 9 |
| Store it, then deliver it as an optimisation | weeks 7, 8 |
| Absolute assignments are idempotent; increments are not | weeks 7, 10 |
| Idle capacity is the shock absorber | weeks 2, 9 |
| A prefix is a state; a subset with a hole is not | weeks 3, 7 |
| The expensive resource explains the architecture | week 10, and every week in hindsight |

Eight ideas. They cover a very large fraction of the design questions you will be asked,
and none of them is about a product.

---

## Today

Finish Project 3's decisions, then assemble the library. Both are milestone deliverables.

Take the library into week 12 — it is what you will revise from, and it is much better
revision than rereading eleven documents.

---

> **Sources for this article**
> **Tier 3 — ours.** The decision-record format resembles the architecture-decision-record
> convention, which is a widely-used community practice with no single authoritative
> source. The recurring-shapes table is a summary of this course and is an argument rather
> than a finding.
