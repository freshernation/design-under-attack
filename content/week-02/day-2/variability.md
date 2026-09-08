# Variability, and why the average lies twice

*Week 2 · Day 2 · about 25 minutes*

> By the end of this you can name where the variance in your system comes from, and
> explain why two services with identical average load can have wildly different p99s.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Dean & Barroso — The Tail at Scale**](https://research.google/pubs/the-tail-at-scale/) | 1 | Google engineers on where tail latency comes from and what to do about it. The single best paper on this subject |
| [**Google SRE Book — Addressing Cascading Failures**](https://sre.google/sre-book/addressing-cascading-failures/) | 1 | The operational view of the same thing |

Read *The Tail at Scale*. It is about ten pages, it is written for engineers rather than
theorists, and you will cite it for the rest of your career.

---

## The optimistic case was optimistic

Yesterday's curve assumed random arrivals and random service times — the textbook case.
Real systems are worse, and the reason has a name.

For a general queue, the waiting time is roughly

```
wait  ≈  ρ/(1−ρ)  ×  (Ca² + Cs²)/2  ×  service time
                     └────┬────┘
                  the variability term
```

The first term is yesterday's curve. The second is new: **`Ca`** is how variable the
arrivals are, **`Cs`** is how variable the service times are, each measured as the
standard deviation divided by the mean.

When both are 1 — the textbook case — the term is 1 and you get yesterday's numbers.
Double the variability of service times and the term is roughly 2.5, so **the wait more
than doubles at the same utilisation.** No extra load, no code change, no slower
hardware. Just more spread.

This is the second way the average lies. The first was that the average response time
hides the tail; the second is that the average *load* hides the variance that creates
the tail.

---

## Where the variance comes from

Nearly all of it is one of these, and every one is a design decision you can revisit.

| Source | What it looks like |
|---|---|
| **Request size skew** | one customer's query returns 100,000 rows, everyone else's returns 12 |
| **Cache misses** | a hit is 1 ms and a miss is 40 ms, so your service time is bimodal, not spread |
| **Garbage collection / compaction** | the process stops for 200 ms at unpredictable moments |
| **Noisy neighbours** | someone else's job on the same host takes the CPU |
| **Retries** | arrivals are not independent; they cluster exactly when things are bad |
| **The top of the hour** | crons, reminders and scheduled jobs all fire together |
| **Queueing upstream** | a burst absorbed by one component leaves it as a burst for the next |

Look at the second row. **A cache is not just a latency improvement, it is a variance
increase** — you have replaced one steady service time with two very different ones, and
the queueing consequence is worse than the average suggests. A cache that takes the mean
from 40 ms to 5 ms while making the distribution bimodal can leave the p99 unchanged or
worse. This is a real and common surprise, and it is invisible if you only look at
averages.

---

## Fan-out turns variance into the median

The result from week 1 day 2, now with a mechanism behind it.

If a request waits on 100 parallel calls, it finishes when the **slowest** finishes. With
100 samples you are essentially sampling the 99th percentile every time. So your
service's typical response inherits your dependency's tail — and the more you fan out,
the further into the tail you go.

*The Tail at Scale* is largely about this, and it is why the paper's remedies are what
they are:

- **Hedged requests** — send to a second replica if the first has not answered by p95,
  take whichever returns first. Costs a few percent extra load, cuts the tail sharply
- **Tied requests** — send to two, and have them cancel each other on start
- **Micro-partitioning** — many small partitions per machine, so hot ones can be moved
- **Selective replication** — more copies of the items that are hot

You are not building any of these this week. You are learning that "reduce the tail" has
concrete techniques behind it, so that in a design discussion it is a decision rather
than a wish.

---

## Reducing variability is a design lever

Because the variability term multiplies the queueing term, **halving your service-time
variance is worth about as much as a large amount of extra hardware.** Ways to do it,
roughly in order of how often they are available:

| Technique | What it does |
|---|---|
| **Bound the work per request** | page results, cap the rows, reject the pathological query |
| **Separate heavy work** | a different pool for the expensive endpoints, so their variance is not everyone's |
| **Timeouts** | truncate the tail deliberately, at a value derived from the budget |
| **Batching** | fewer, more uniform units of work — often reduces both mean and variance |
| **Admission control** | keep λ steady rather than letting it spike |

The first one is the most under-used. A single endpoint that occasionally returns a
million rows will dominate the tail of an entire service, and the fix is a limit
parameter rather than a cluster.

---

## What to do with this in a design

In pass 2, alongside the average, ask: **what is the biggest single unit of work this
system can be asked to do?** Not the average request — the worst legitimate one. That
number drives the tail, and it usually turns out that nobody has ever bounded it.

In pass 6, "slow" is now a thing you can be precise about: which component's service
time has the widest spread, and what happens to everything queued behind it?

---

## Today's lab

`queueing.py` includes the variability side:

- `kingman_wait(service_time_s, rho, ca, cs)` — the formula above
- `variability_penalty(ca, cs)` — the multiplier on its own
- `bimodal_cv(fast_s, slow_s, slow_fraction)` — the coefficient of variation of a
  cache-shaped service time, which is the number that makes the cache surprise concrete

Run `bimodal_cv` on a 1 ms hit, a 40 ms miss and a 5% miss rate before you read its
test. The answer is larger than almost anyone guesses.

---

> **Sources for this article**
> [Dean & Barroso, *The Tail at Scale*](https://research.google/pubs/the-tail-at-scale/),
> Google, 2013 — **Tier 1**, and the source for hedged requests, tied requests and
> micro-partitioning. Kingman's approximation is standard queueing theory (Kingman,
> 1961 — **Tier 2**). The variance-source table is ours — **Tier 3**.
