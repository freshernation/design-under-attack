# Week 9 — Friday defence

Twenty minutes on the review, three phases, then a retro.

Different from other weeks: the artefact is a **review of their own earlier work**, so the
question is not "is this design good" but "did they find what is actually wrong with it".

---

## Before they arrive

Read their `REVIEW.md` alongside their Project 2, run `pytest week-09/milestone`, and
check:

- Is there a **dependency ceiling**, and does it sit above or below their SLO? If they did
  not compute it, that is the first question.
- Does the failure inventory cover **slow** as well as dead? Most cover dead only.
- Are the three findings **ranked, with costs**? Fifteen undifferentiated findings is not a
  review.
- Did they run `run_incident` on their own numbers, or reason qualitatively?

---

## Phase 1 — Explain (6 min)

1. *"What is your dependency ceiling, and what is your SLO?"* — if the SLO is above the
   ceiling, the review should say so plainly. It is the most valuable sentence in it.
2. *"A dependency slows to 5 seconds. How long until your service is fully consumed?"* —
   Little's Law. They should reach for concurrency = throughput × latency without help.
3. *"How many requests does one user action produce at the bottom of your stack?"*
4. *"At 150% of capacity, what is still working, and who decided that?"* — the priority
   order is a product decision, and if nobody made it, it was made by accident.
5. *"Which of your three findings would you do first, and what does it cost?"*

| 5 | 3 | 1 |
|---|---|---|
| Computed the ceiling and acted on it; findings ranked with costs | Found real problems, ranking is soft | Listed mechanisms without numbers |

## Phase 2 — Mutate (7 min)

### A — *"You may add exactly one protection. Which, and why?"*

The best question of the week. Their lab says the order in which protections help is not
the order people add them — shedding alone can beat a breaker and a retry budget together.
Looking for: they answer from their own `run_incident` output rather than from the famous
one.

### B — *"Your SLO is 99.9% and your dependency ceiling is 99.8%. Product will not accept 99.8%."*

Looking for: the three real options — remove a dependency from the critical path, make
failures survivable so the dependency's availability stops mattering, or change the
number. And that the third is a legitimate engineering answer, not a defeat.

### C — *"A deep health check on the message store. The store has a bad minute."*

Looking for: every host reports unhealthy simultaneously and the fleet empties. The cap on
removable hosts is the answer, and almost nobody has it.

| 5 | 3 | 1 |
|---|---|---|
| Answers from their own numbers; treats requirements as negotiable | Gets there messily | Adds every protection at once |

## Phase 3 — Break (7 min)

| Attack | Watching for |
|---|---|
| *"Your circuit breaker opens during a normal traffic spike."* | Threshold and minimum-request tuning. An over-sensitive breaker is an outage you caused |
| *"Your retry budget is exhausted and the dependency recovers."* | Does the budget refill fast enough to use the recovery? |
| *"Every client backs off 30 seconds and returns together."* | Jitter, fifth time. If it is missing here it is missing everywhere |
| *"You shed best-effort work. Those clients retry immediately."* | Retries must inherit the priority of what they retry, or shedding is theatre |
| *"Your bulkheads mean you cannot use spare capacity."* | Do they know they bought isolation with efficiency, deliberately? |

| 5 | 3 | 1 |
|---|---|---|
| Knows what each protection costs, not only what it prevents | Finds it with prompting | Treats protections as free |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"What did the review find that you would not have found by rereading the document?"* —
   usually the dependency ceiling or the retry multiplication, and both are arithmetic.
2. *"Which protection did you expect to matter most, and which actually did?"*
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 10 is the deep track: two specialised areas from six.

The framing for Monday: **nine weeks of general mechanisms, and now two problems where the
general answer is not enough.** Geospatial, collaborative editing, matching engines, media
pipelines, model serving, decentralised protocols — each needs something the course has
not yet given them.

The check: can they say what a protection *costs*, not only what it prevents? Week 10's
specialised material is full of expensive mechanisms, and a student who evaluates them
only on what they enable will over-build every one.
