# Concurrency, pools, and where the queue actually is

*Week 2 · Day 1 · about 20 minutes*

> By the end of this you can find every queue in a request path — including the three
> you did not know were there — and say which one fills first.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Google SRE Book — Addressing Cascading Failures**](https://sre.google/sre-book/addressing-cascading-failures/) | 1 | How a queue in one place takes down a system somewhere else |
| [**AWS Builders' Library — Timeouts, retries and backoff with jitter**](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | 1 | Why an unbounded wait is a design decision, whether or not you made it deliberately |

---

## Every limit is a queue

A "pool" is a queue with a nicer name. So is a semaphore, a thread pool, a connection
pool, a socket accept backlog, and a channel with a buffer.

Whenever you cap concurrency at `L`, requests beyond `L` do not vanish. They wait. And
the place they wait is a queue you now own, whether or not you wrote it.

Here is a request path with the queues marked. Most designs draw four boxes and none of
these:

| Where | The queue | Bounded by |
|---|---|---|
| Client | connection pool to your service | pool size |
| Network | TCP accept backlog | `somaxconn`, and it is small |
| Your process | thread pool / event loop task queue | pool size, or memory |
| Your process | connection pool to the database | pool size |
| Database | its own worker pool | its config, which you did not set |
| Downstream | HTTP client pool per host | usually a default you have never read |

Six queues in a path most people would describe as "the app talks to the database".

**When something slows down, one of these fills first.** Which one it is decides what
your failure looks like — a timeout, a rejection, a hang, or a memory graph going
vertical — and knowing which is most of debugging an overload.

---

## Sizing a pool

From Little's Law: `L = λW`, plus headroom.

```
throughput 500/s, latency 200 ms  ->  L = 100
with 1.5x headroom                ->  pool of 150
```

Headroom is not padding. It absorbs the variance that the average hides — some requests
take much longer than 200 ms, and a pool sized exactly at the average is at 100%
utilisation half the time. Tomorrow's article is entirely about why that is fatal.

### Too small and too large both hurt, differently

| | Symptom |
|---|---|
| **Too small** | requests queue outside the pool; latency rises; throughput is capped below what the hardware can do |
| **Too large** | everything is admitted, the real constraint saturates, all requests slow down together, and nothing is rejected until memory runs out |

The second is worse and less obvious. A large pool does not add capacity — it moves the
queue from a place where you could have shed load to a place where you cannot. **A
system that rejects 10% of requests quickly is usually healthier than one that accepts
100% of them and serves them all past their timeout**, because in the second case nobody
gets an answer they can still use.

That sentence is one of the harder ideas in the course, and it is the whole reason week
9 exists.

---

## The unbounded queue

The default in most languages: an unbounded work queue, a list you append to, a channel
with no capacity.

An unbounded queue does not remove the limit. It converts a fast, visible failure
(rejection) into a slow, invisible one (everything is late, then the process dies of
memory exhaustion). And it does so while every dashboard shows the service accepting
traffic normally.

**Every queue in a design should have a stated bound**, and "what happens when it is
full" should be a decision written in your document rather than a default you inherited.

---

## Where the queue is, matters

Two systems with identical capacity behave completely differently depending on where
the waiting happens:

**Queue at the edge, one shared pool.** A slow dependency backs up one pool, that pool
is shared, and every request type is now slow — including ones that never touch the slow
dependency. This is how a failure in a minor feature takes out a checkout page.

**Queue per dependency, separate pools.** The slow dependency backs up its own pool.
Requests that need it fail; requests that do not are unaffected.

The second is bulkheading, and it is a week 9 topic — but notice that the difference is
not extra capacity or better code. It is *where the queue is*, which is a design
decision available to you in pass 4, for free, if you drew the queues.

---

## What to do with this today

When you write pass 4 — the path — mark every queue. Ask for each:

1. What is its bound?
2. What happens when it is full?
3. Which one fills first as the system slows?

Three questions. Most design documents cannot answer any of them, and being able to
answer all three about your own design is a large fraction of what week 2 is for.

---

## Today's lab

`littles.py`, from the previous article. Pay attention to
`throughput_after_slowdown` — it is the shape of most incidents you will ever read
about.

---

> **Sources for this article**
> [Google SRE Book](https://sre.google/sre-book/addressing-cascading-failures/) and
> [AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/),
> both **Tier 1**. The six-queue table and the "where the queue is" framing are ours —
> **Tier 3**.
