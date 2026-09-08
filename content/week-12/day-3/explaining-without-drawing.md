# Explaining without drawing

*Week 12 · Day 3 · about 20 minutes*

> By the end of this you can explain any mechanism in this course out loud, in under a
> minute, without a diagram.

---

## Why this is a separate skill

A large share of design conversations happen without a whiteboard: a phone screen, a
corridor, a video call where nobody shares a screen, a colleague asking what you are
working on.

And **explaining without drawing is a harder test of understanding**, because a diagram
lets you gesture at a relationship you have not articulated. Speech does not.

It is also the version that comes up most in the first round, which is the round that
decides whether anybody reads your document.

---

## The shape of a good verbal explanation

Four parts, in this order, in under a minute:

1. **The problem it solves**, in one sentence, with no jargon
2. **How it works**, in two or three sentences
3. **What it costs** — always. This is the part that signals you have used it
4. **When you would not use it**

Worked:

> "A circuit breaker stops you calling something that is already failing. You count
> failures, and past a threshold you stop attempting the call and fail instantly instead —
> then after a cool-off you let one request through to see if it has recovered. What it
> costs is that you refuse some requests that would have succeeded, and if the threshold is
> too sensitive you cause an outage yourself. I wouldn't put one on a dependency with a
> naturally high error rate, because it would open constantly."

Fifty-five seconds. Problem, mechanism, price, limit.

**The third and fourth parts are what distinguish the answer.** Anybody can recite a
mechanism; a person who names its cost has used it, and a person who names where it does
not apply has thought about it.

---

## The ones you will be asked

Rehearse these until they are boring. Out loud, timed, and preferably while walking.

| | Where it came from |
|---|---|
| Why 80% to 90% utilisation roughly doubles latency | week 2 |
| What a bounded queue does that an unbounded one does not | week 2 |
| B-tree against LSM, and which workload wants which | week 3 |
| Why a write-ahead log makes a database faster, not slower | week 3 |
| Consistent hashing, and what virtual nodes buy | week 4 |
| Why a hot key is not fixed by adding machines | week 4 |
| What a quorum guarantees, and what it does not | week 5 |
| Why a majority prevents two leaders | week 5 |
| Why checking a lease before writing does not protect storage | week 5 |
| The cache-aside race, and one fix | week 6 |
| Why a longer TTL does nothing for a long tail | week 6 |
| Why exactly-once delivery is impossible | week 7 |
| What an idempotency key does, and who generates it | week 7 |
| The dual-write problem, and what an outbox converts it into | week 7 |
| Fan-out on write against on read, and why real systems do both | week 8 |
| Why a retry budget matters more than backoff | week 9 |
| Why goodput falls past capacity | week 9 |
| What a dependency ceiling is | week 9 |

Eighteen. If any of them is not fluent, that is where tonight goes.

---

## The trap: reciting

There is a version of each of these that sounds like a textbook and demonstrates nothing.
The tell is that it contains no number, no cost, and no example.

> **Weak:** "A bounded queue applies backpressure to prevent unbounded memory growth."
>
> **Strong:** "If the queue has no bound, a slow consumer means everything gets late and
> then the process dies of memory exhaustion — and every dashboard shows traffic being
> accepted normally the whole time. With a bound you have to choose: block the producer,
> reject, or drop the oldest. Rejecting is usually right at an edge, and dropping oldest is
> right for telemetry where fresh beats complete."

The second one cannot be recited from a blog post, and that is the point.

---

## Today

Take the eighteen. Explain each out loud, timed, to a phone recording or a person.

Then listen to three of them. You will hear the ones you have understood and the ones you
have memorised, and the difference is audible in a way it is not on paper.

---

> **Sources for this article**
> **None. Ours.** The list is a summary of this course, and every item on it has a
> primary source in the week it came from — which is where to go if one of them turns out
> to be memorised rather than understood.
