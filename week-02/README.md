# Week 2 — Queues, utilisation and latency

> **Destination**
> Say what happens to a system at 90% utilisation, prove it with arithmetic, and design
> something that degrades honestly instead of collapsing quietly.

Week 1 taught you to count. This week the counting starts telling you things you did not
want to hear.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Compute what is inside your system right now, and size a pool from it |
| Tue | `day-2/` | Explain why 80% to 90% utilised roughly doubles latency |
| Wed | `day-3/` | Bound a queue, choose what happens when it fills, and measure the right thing |
| Thu | `day-4/` | Build a rate limiter and prove the flaw in the obvious one |
| Fri | `milestone/` | Ship the limiter design, then defend it |

---

## The one idea

**Idle capacity is not waste. It is the shock absorber, and a system with none of it
does not degrade gracefully — it falls off a cliff.**

Almost everything this week is a consequence of that. Headroom, backpressure, bounded
queues, rate limiting and load shedding are all the same idea approached from different
directions: decide in advance what you will refuse, or have it decided for you at the
worst possible moment.

---

## What is new this week

**The tests start simulating.** From day 3 the labs run on `simlib`, the deterministic
harness in the repo root. Time is simulated milliseconds, so a ten-second workload runs
instantly and identically every run — which is what makes a queue's behaviour something
you can assert rather than something you argue about.

Read `tests/test_simlib.py` before day 3 if you want to know what it can do. You are
using the harness, not building it.

**The fence opens slightly.** You may now name a *mechanism* — a token bucket, a bounded
queue, a thread pool. You still may not name a **product**. See `FENCE.md`.

---

## Milestone

A rate limiter for a public API platform, spec in `milestone/README.md`. Twelve edge
servers, uneven traffic, and a two-millisecond decision budget that a shared counter
will not fit inside.

---

## What this week is not about

Making things fast. Nothing here makes anything faster; it makes systems behave
predictably when they are not fast enough, which is a different and more valuable skill.

The instinct you are fighting all week is the one that says a problem of load is solved
by adding capacity. Sometimes it is. This week is about the times it is not, and about
noticing which situation you are in before you spend the money.
