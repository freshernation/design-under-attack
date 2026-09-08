# Milestone — Design a multi-tenant job queue

> Seven passes. A design document, and a working partition planner and scheduler.

| File | What |
|---|---|
| `DESIGN.md` | Your design document — the week-1 template |
| `jobqueue.py` | Partition planning, ordering-safe splitting, and a fair scheduler |

Must pass `pytest week-04/milestone` and `python3 tools/check_sources.py`.

---

## The brief

A background-job queue for a platform that runs customers' work. Tenants enqueue jobs
into named queues; a pool of workers pulls and runs them.

**Scale**

| | |
|---|---|
| Tenants | 30,000 |
| Enqueue rate | 400,000 jobs/second at peak |
| Job payload | about 2 KB |
| Workers | 2,000 |
| **Skew** | the largest tenant is about **25%** of all jobs; the top ten are about 60% |
| Queues per tenant | median 3. The largest tenant has **one** |

**Envelope**

| | |
|---|---|
| Enqueue latency | p99 under 20 ms |
| Durability | an acknowledged job survives one host dying. **Losing a job is unacceptable; running one twice is not** |
| **Ordering** | **jobs in the same (tenant, queue) must run in the order they were enqueued** |
| **Fairness** | **no starvation: a small tenant's job must start within 30 seconds even while the largest tenant is saturating the platform** |
| Retention | a completed job's record kept 7 days |
| Availability | 99.95% for enqueue |

**Not building**

Retry policy and dead-letter queues (week 9) · cron and scheduled jobs · storing job
results · a UI · cross-tenant priorities · exactly-once execution

---

## The tension this brief is built around

Read these three lines together:

- One tenant is **25%** of all jobs
- Jobs in the same (tenant, queue) must be **ordered**
- That tenant has **one queue**

Splitting a hot key is Wednesday's answer, and ordering is what splitting destroys. Split
that tenant sixteen ways and its jobs run out of order; do not split it and one partition
carries a quarter of the platform.

**There is no answer that costs nothing.** Your document has to pick one and say what it
gave up. Three defensible positions, and there are others:

- Split by **queue**, so ordering holds within each queue — and accept that a tenant with
  one queue cannot be split at all
- Keep the whale whole on a dedicated partition sized for it — and accept manual
  intervention as tenants grow
- Weaken the ordering guarantee to "ordered per job key rather than per queue" — and go
  back to the customer about it

The third is a legitimate engineering answer and people forget it is available.
Requirements are negotiable if you say what you are buying.

---

## `jobqueue.py`

### Planning the partitions

```python
split_ways(tenant_share, partitions)            # how many ways to bring one tenant under an even share
plan_splits(tenant_loads, partitions, threshold)  # {tenant: ways}, only for tenants over the threshold
projected_loads(tenant_loads, plan, partitions)   # what the fleet looks like afterwards
```

Run `projected_loads` before and after and compare the skew. That comparison is the
argument for the plan, and it belongs in your document as two numbers.

### Splitting without losing ordering

```python
shard_key(tenant, queue, ways)      # which shard this (tenant, queue) belongs to
effective_ways(queue_count, ways)   # how many shards a tenant can actually occupy
```

`shard_key` must send **every job for the same (tenant, queue) to the same shard**, every
time. That is what preserves ordering, and it is why the split is by queue rather than at
random.

`effective_ways` is the honest part: a tenant with three queues cannot occupy sixteen
shards no matter what the plan says. One test uses it on the whale — one queue — and the
answer is 1. There is nothing to fix in the code when that test passes; it is telling you
something about the brief.

### Fairness

```python
fifo_schedule(pending, limit)     # strictly by arrival — and watch what happens
fair_schedule(pending, limit)     # round-robin across tenants
position_of(schedule, tenant)     # where a tenant's first job lands
```

`pending` is `{tenant: [job, ...]}`, each list in arrival order.

Both schedulers preserve each tenant's own order — that is not negotiable. They differ in
how they interleave tenants, and the tests show a small tenant waiting behind ten thousand
whale jobs under one and being served almost immediately under the other.

---

## `DESIGN.md`

The week-1 template. **The fence still forbids product names.**

This week your **Size** section must include:

- jobs per second and bytes per second at peak, and per partition
- the skew of the natural key, and the skew after your plan — both numbers
- `utilisation_of_hot_partition` for the whale, before your remedy
- how many partitions you need, using `partitions_needed` with a real skew factor
- storage for 7 days of job records, including replicas

And your **Decide** section must contain the ordering-versus-fairness decision, with the
alternative you rejected and its price.

---

## The five questions to have answers to

1. The whale's single queue is 25% of the platform. What have you actually done about it,
   and what did it cost?
2. A worker takes a job and dies. What happens to that job, and how long until anyone
   notices?
3. A tenant grows from 1% to 20% of the platform over a month. When does your design
   notice, and who does something about it?
4. Every worker restarts during a deploy. What does the queue look like a second later?
5. Two workers pull the same job. Your envelope says duplicates are acceptable — does
   that mean the *customer's* job is safe to run twice, or only your record of it?

Question 5 is the one that separates a design document from an engineering one.

---

## Before you submit

```bash
pytest week-04/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md` on your own document.
