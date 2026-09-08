# Week 5 — Friday defence

Twenty minutes on the lease service, three phases, then a retro.

This week's theme: whether they understand that safety and availability were traded
against each other on purpose, and can say where.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-05/milestone`, and check:

- Is there a **lease duration** with the trade stated in both directions? A number with
  no justification is the failure mode of the week.
- Does the document say what happens on the **minority side of a partition**? The
  envelope decides it; a document that hedges has not read the envelope.
- Does it distinguish **preventing** the confusion from **making it harmless**?
- Any product names? Last week of the fence.

---

## Phase 1 — Explain (6 min)

1. *"A holder's host freezes for forty seconds. Walk me through every write it attempts
   on waking."* — the question. A strong answer gets to fencing without prompting.
2. *"Why does checking the lease expiry before writing not fix this?"* — the check-then-act
   race. If they cannot articulate it, they have implemented fencing without understanding
   why it is necessary.
3. *"You chose a 10-second lease. Why not 2, and why not 60?"* — both directions. Shorter:
   more renewal traffic and spurious expiries under load, which is when load is high.
   Longer: a crashed holder blocks the resource for that long.
4. *"200,000 leases renewed halfway through a 10-second lease. What is the renewal rate?"*
   — 40,000/second, eight times the brief's stated peak. Make them notice.
5. *"Which claim here is sourced and which is you?"*

| 5 | 3 | 1 |
|---|---|---|
| Reaches fencing unprompted and can explain why expiry checks fail | Describes the design accurately, needs a nudge on the race | Believes checking the expiry is sufficient |

## Phase 2 — Mutate (7 min)

### A — *"The storage you are protecting does not support fencing tokens. It is a system you do not control."*

The honest mutation, and the one worth running. Three defensible answers — a proxy in
front that enforces tokens, making the operations idempotent so a duplicate is harmless,
or accepting the risk and shortening the lease — and **none of them is as good as
fencing**. Looking for: they name at least two and say what each actually guarantees.

A student who says "then we'd be fine because the lease is short" has missed the whole
week: the pause can be longer than any lease you choose.

### B — *"The lease service is partitioned 3–2 and a client is talking to the minority."*

Looking for: the minority refuses, and the client must treat "I cannot reach the service"
as "I do not hold the lease" — which means it must stop working, not carry on hoping.
That second half is what people miss.

### C — *"Leases now have to work across two regions, 80 ms apart."*

Looking for: they notice that every acquire is now a cross-region round trip, that the
lease duration must exceed several of those, and that a region-isolating partition makes
one side unable to acquire anything at all.

| 5 | 3 | 1 |
|---|---|---|
| Names several options and what each guarantees | Finds one and defends it | Assumes the problem away |

## Phase 3 — Break (7 min)

| Attack | Watching for |
|---|---|
| *"Your lease service's leader fails while 200,000 leases are held. What happens?"* | Do the leases survive the failover, or does everything expire at once and stampede? |
| *"A client's clock is 30 seconds fast."* | Whose clock decides expiry? If it is the client's, the design is broken |
| *"Every holder renews at exactly the same moment after a service restart."* | Synchronisation. Jitter belongs on renewals, same as on retries |
| *"A holder finishes and crashes before releasing."* | The resource is blocked for a full lease duration. That is the cost of the number they chose |
| *"Two clients both acquire, because a network glitch made the service issue two leases."* | Fencing again: even if the service is buggy, tokens order the writers |

| 5 | 3 | 1 |
|---|---|---|
| Reasons from their own numbers and the token ordering | Finds it with prompting | Adds a component to every attack |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"You wrote a test asserting that acknowledged writes disappeared on Monday, and one
   asserting no term ever has two leaders on Wednesday. What is the difference between
   those two kinds of guarantee?"* — one is a bill, one is a promise. Naming that is the
   week.
2. *"Which of your four earlier designs needs read-your-writes, and does it have it?"* —
   usually at least two do and none say so.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 6 is caching: the read path, invalidation, stampedes, and CDNs.

The link for Monday: **a cache is a replica you built on purpose and gave no consistency
story to.** Everything from this week applies — staleness bounds, read-your-writes, the
invalidation race — and students who see that arrive at week 6 already knowing the hard
parts.

The check: can they say, unprompted, why "eventually consistent" is not an answer to
"what does a reader see?" If yes, week 6's invalidation material lands as a special case
of something they know. If not, ten minutes on the day-4 lab before starting.
