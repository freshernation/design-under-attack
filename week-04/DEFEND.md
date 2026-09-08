# Week 4 — Friday defence

Twenty minutes on the job queue, three phases, then a retro.

This week's theme: whether they noticed that the brief has no free answer, and whether
they chose anyway.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-04/milestone`, and check:

- Is there a **skew number** in the document — before and after their remedy? Two
  numbers, not one.
- Did they resolve the ordering-versus-fairness conflict explicitly, or slide past it?
  Sliding past it is the failure mode of the week and it is easy to spot: the document
  will mention both requirements and never put them in the same paragraph.
- Any product names? Still forbidden.

---

## Phase 1 — Explain (6 min)

1. *"The largest tenant is a quarter of the platform and has one queue. What did you do?"*
   — the question. Any of the three positions is fine. "I split it sixteen ways" without
   mentioning ordering is not.
2. *"What is the skew of your chosen key, and what is it after your remedy?"* — two
   numbers. If they have one, ask for the other.
3. *"You have sixteen partitions and the whale is 25%. What utilisation is that partition
   running at?"* — make them do it live. It is one multiplication and it is the number
   that justifies everything else in the document.
4. *"A job is enqueued. Walk me through every hop to a worker running it."*
5. *"Which claim here is sourced and which is you?"*

| 5 | 3 | 1 |
|---|---|---|
| Names the conflict unprompted and says what they gave up | Describes the design accurately; needs prompting on the conflict | Has not noticed the conflict exists |

## Phase 2 — Mutate (7 min)

### A — *"The whale splits its work into fifty queues next month."*

The kindest mutation and still informative. Their split now works — `effective_ways` goes
from 1 to 4. Looking for: they notice the design got *better* without them doing
anything, and that this means their capacity plan depends on a customer's behaviour they
do not control. Who is watching that number?

### B — *"Ordering is relaxed: jobs must be ordered per job key, not per queue."*

The requirement moves and the whole problem dissolves. Looking for: they recognise this
was available all along, and that going back to a customer about a requirement is an
engineering option rather than a defeat. The best answers say what they would have needed
to know to make that case.

### C — *"A tenant grows from 1% to 20% over a month."*

Looking for: when does the design notice? Most documents have a static plan computed once.
The good answer has a measurement and a threshold, and says who or what acts on it.

| 5 | 3 | 1 |
|---|---|---|
| Reaches for their own numbers; treats requirements as negotiable | Gets there messily | Redesigns from scratch each time |

## Phase 3 — Break (7 min)

| Attack | Watching for |
|---|---|
| *"You add four partitions at peak. What happens in the next sixty seconds?"* | Keys move, caches go cold, and it happens while they are already busy. Did they choose a ring, and do they know it moves 1/N rather than nothing? |
| *"A worker takes a job and its host dies."* | Visibility timeouts, leases, and the fact that "at least once" means somebody's job may run twice |
| *"Two workers pull the same job."* | Their envelope says duplicates are acceptable. Push: acceptable to *whom*? Charging a customer twice is not a duplicate record |
| *"The routing tier's map is thirty seconds stale."* | Serve it anyway, forward it, or reject with the new map. Only the third is safe and it costs a round trip |
| *"Every worker restarts during a deploy."* | Two thousand workers reconnecting at once, then a compressed backlog aimed at whatever is downstream |

| 5 | 3 | 1 |
|---|---|---|
| Reasons from their own numbers | Finds it with prompting | Adds a component to every attack |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"Which of the two irreducible conflicts this week did you find harder — sortable ids,
   or splitting versus ordering?"* — both are the same shape and naming that is the
   week's real lesson.
2. *"You have now written four design documents. Which requirement, in any of them, would
   you go back and negotiate?"* — the answer should come quickly by now.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 5 is replication and consistency: quorums, leader election, Raft, and what a
partition does to a system that has to agree.

The link to say on Monday: **this week every key had exactly one home. Next week it has
several, and they can disagree.** Every hard problem in week 5 comes from removing the
assumption that made this week tractable.

The check: do they understand *why* a stale routing map is dangerous — that two nodes
believing they own a key is how data is lost? If that landed on Thursday, split brain in
week 5 will feel like the same problem rather than a new one. If it did not, ten minutes
on it before starting, because week 5 is built on top of it.
