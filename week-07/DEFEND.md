# Week 7 — Friday defence

Twenty minutes on the click aggregator, three phases, then a retro.

This week's theme: whether they found the trap, and whether the way out is stated as a
mechanism rather than a hope.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-07/milestone`, and check:

- Did they compute the **replay-sized deduplication window** and notice it is 690 GB?
  A document that proposes deduplication over 24 hours has not done the arithmetic.
- Is the **replay-by-recomputation** decision explicit, with its alternative?
- Does every asynchronous boundary state its guarantee? The new rule.
- Is there a row for "an event arrives 3 hours late"?

---

## Phase 1 — Explain (6 min)

1. *"Delivery is at-least-once and counting must be exactly once. How?"* — the question.
2. *"You need a 24-hour replay. How big is a deduplication window that covers it?"* —
   690 GB. If they have not computed it, do it with them and watch the design change.
3. *"So how does the replay produce a correct result without one?"* — recomputation.
   Assignment is idempotent; addition is not. They proved it on Wednesday in two lines.
4. *"An event arrives three hours late. What happens, and who finds out?"* — dropped,
   counted, and alerted. A silent drop here is money.
5. *"Which claim here is sourced and which is you?"*

| 5 | 3 | 1 |
|---|---|---|
| Reaches recomputation unprompted and can say why it is idempotent | Has the mechanism, needs prompting on why | Proposes a 24-hour deduplication window |

## Phase 2 — Mutate (7 min)

### A — *"Advertisers can now query their spend in real time, and it must match the invoice exactly."*

Looking for: they notice that a bucket inside the late window is **not final**, so a
real-time number and a billed number are different things. The good answer surfaces that
to the product — "provisional" versus "final" — rather than pretending a watermark can be
zero.

### B — *"The late window goes from 10 minutes to 6 hours."*

Looking for: the deduplication memory grows 36x, and buckets stay open 36x longer. They
should go to `dedup_window_bytes` rather than reasoning qualitatively, and then notice
that the *counts* are unaffected — only the deduplication state is transient.

### C — *"One campaign becomes 40% of all clicks during a sporting event."*

Week 4 in a week 7 design. Looking for: one partition takes 40% of 500,000/s, its consumer
is now the bottleneck, and splitting the key would break the per-campaign ordering they
relied on — except that **the aggregation is commutative**, so ordering does not actually
matter here and the key can be split. A student who spots that has understood both weeks.

| 5 | 3 | 1 |
|---|---|---|
| Reaches for their numbers; spots the commutativity in C | Gets there messily | Redesigns from scratch |

## Phase 3 — Break (7 min)

| Attack | Watching for |
|---|---|
| *"Your aggregator crashes with 40 seconds of counts in memory."* | Where the counts are durable, and whether the answer is "we replay", which is now cheap |
| *"A consumer is rebalanced mid-batch."* | Reprocessing between the commit and the crash — a duplicate source with a name |
| *"A consumer was down all weekend and the log keeps 24 hours."* | Data loss at the retention edge, silently, with no error. Is that alert present? |
| *"Two aggregator instances both hold the same partition for ten seconds."* | Double counting, unless the effect is idempotent per bucket — which it is, if they built it |
| *"Billing runs at 02:00. Is yesterday's number final?"* | A watermark, not a time of day. This is question 5 and it separates a pipeline from a billing system |

| 5 | 3 | 1 |
|---|---|---|
| Reasons from watermarks and idempotency | Finds it with prompting | Adds a component to every attack |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"Where else in your designs is there a dual write?"* — everyone has at least two, and
   week 6's cache invalidation is one of them.
2. *"Which of your five earlier designs would survive a deliberate replay?"* — usually
   none, and noticing that is worth more than the milestone.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 8 is realtime and fan-out: push against pull, presence, and timelines.

The link for Monday: **a timeline is a materialised view over a log, and fan-out is when
you compute it.** Everything from this week applies — ordering per key, at-least-once
delivery, idempotent application — and the new question is only *when* the work happens.

The check: can they say why the aggregation being commutative made the hot-key split safe?
If yes, week 8's fan-out-on-write material lands as a variation. If not, ten minutes on
`apply_absolute` against `apply_increment`, because week 8 is full of the same choice.
