# Week 2 — Friday defence

Twenty minutes on the limiter design, three phases, then a retro.

Last week you were finding out whether they derived their numbers. This week you are
finding out whether the numbers changed their mind about anything.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-02/milestone`, and check three things:

- Did they compute **utilisation after losing one server**? It is the number the brief
  is really about, and a document that does not contain it has not engaged.
- Does every queue in the document have a bound and a full-policy? The fence requires it.
- Did they name a product anywhere? Still forbidden.

Then pick your derivation question, your mutation, and two attacks.

---

## Phase 1 — Explain (6 min)

1. *"Twelve servers, 40,000 requests a second at peak. What is the utilisation on each,
   and what is it after one dies?"* — the week's question. They should get there in
   under a minute, out loud.
2. *"Your limiter adds a decision to every request. Where does that sit in the two
   millisecond budget, and what did you decide about shared state?"*
3. *"You have a queue somewhere in this document. What is its bound and what happens
   when it is full?"* — if the answer is "it won't fill", ask what makes that true.
4. *"Over-limiting a paying tenant is worse than under-limiting. Where in the design did
   that sentence change something?"* — looking for a specific place. "I kept it in mind"
   is a fail.
5. *"Which claim here is sourced and which is you?"* — still asked, every week.

| 5 | 3 | 1 |
|---|---|---|
| Derives the utilisation numbers live and knows what they imply | Gets there with a nudge | Never computed utilisation at all |

## Phase 2 — Mutate (7 min)

Pick one. Ask which sections change **before** they design.

### A — *"A deploy restarts all twelve edge servers at once. Every token bucket starts full."*

The best mutation this week. Every tenant's burst is instantly available, on every
server, at the same moment — 50,000 tenants × their burst, arriving at a platform that
just lost its warm state. Looking for: they recognise this as the same shape as a cold
cache, and that the fix is about the *restart*, not the limiter.

A student who says "that's fine, the global limit catches it" is half right and should be
pushed: the global bucket also started full.

### B — *"One tenant now sends 40,000 requests a second, from 4,000 connections spread over all twelve servers."*

Looking for: whether their per-server enforcement can see this at all. If each server
enforces the tenant's full 500/s locally, this tenant gets 6,000/s and is inside every
local limit. The answer requires shared state or sync, which they priced in phase 1 —
so this mutation is really asking whether they believe their own budget.

### C — *"The traffic doubles. Nothing else changes."*

Looking for: they go to the utilisation table before saying anything about servers. If
peak utilisation was 0.7 and doubles, they are past 1 and the interesting question is
what gets rejected, not how many machines to add.

| 5 | 3 | 1 |
|---|---|---|
| Names affected sections first; checks against their own numbers | Gets there messily | Adds components immediately |

## Phase 3 — Break (7 min)

Two attacks, pressed until defended or conceded.

| Attack | Watching for |
|---|---|
| *"The shared state your limiter depends on is unreachable. Now what?"* | Fail open or fail closed — either is fine, **stated** is the requirement. "It's highly available" is not an answer |
| *"Every rejected client retries after exactly the `Retry-After` you sent."* | That they scattered it. Without jitter, a limiter is a synchroniser and the next second is worse than this one |
| *"Your queue's consumer has been down for an hour. It comes back."* | An hour of work compressed into minutes, aimed at whatever is downstream |
| *"Three of your twelve servers die at peak."* | The utilisation arithmetic, live. Nine servers carrying 40,000/s is a number they should be able to produce |
| *"A tenant is inside quota and is still taking the platform down."* | Whether protection exists separately from fairness at all |

| 5 | 3 | 1 |
|---|---|---|
| Reasons from their own numbers | Finds it with prompting | Adds a component to every attack |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"What did the arithmetic tell you that you did not expect?"* — almost everyone says
   the utilisation-after-losing-one number, or the bimodal cache result. If they say
   "nothing", they computed without reading.
2. *"You had to choose between over-limiting and under-limiting. Was that uncomfortable?"*
   — it should have been. Designs where nothing is uncomfortable usually have an
   unexamined assumption doing the work.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 3 is storage: access patterns, indexes, B-trees against LSM trees, and write-ahead
logs. The connection is direct and worth stating on Monday — **write amplification is a
service-time problem, and service time is what this week's curve is made of.** A student
who understands why a compaction pause hurts a p99 has understood both weeks at once.

The check: can they say, without help, why a cache makes latency better and queueing
worse? If yes, they are ready. If not, spend Monday on `bimodal_cv` before touching
storage — the same shape reappears every week from here.
