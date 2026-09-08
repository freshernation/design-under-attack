# Milestone — A resilience review of Project 2

> A different shape of week. You are not designing something new; you are taking the
> chat system you designed last week and finding out how it degrades.

| File | What |
|---|---|
| `REVIEW.md` | The review — a document about a document |
| `resilience.py` | The arithmetic that turns "we added a circuit breaker" into a number |

Must pass `pytest week-09/milestone` and `python3 tools/check_sources.py`.

---

## Why a review rather than a design

Because reviewing is the job.

Most of your career will be spent making an existing system better rather than designing
a new one, and a resilience review is the highest-leverage version of that: it needs no
migration, no new component, and it usually finds two or three things that would each
have caused an incident.

It is also the honest test of last week's work. A design nobody has attacked is a draft,
and this week you are the one attacking it.

---

## The subject

**Your own Project 2 design document**, unchanged. Do not fix it as you go — write the
review first, then decide what to change.

If your Project 2 came out badly, review it anyway. A review of a weak design finds more
and teaches more.

---

## `REVIEW.md`

Five sections. Two to four pages.

### 1. The envelope, restated as an SLO

Your Project 2 had a latency and availability target. Turn it into a measured objective:

- the SLI: exactly what you count, and **where you measure it**
- the SLO, over a window, and the error budget in minutes
- **`dependency_ceiling` for everything on the critical path.** If your target is above the
  ceiling, say so plainly — it is the most valuable sentence in the review
- the burn-rate alerts, with windows and thresholds

### 2. Failure inventory

For every component in the design, all three cases: **dead, slow, lying.**

Slow is the one to spend time on. Week 2 said most outages are a slow dependency rather
than a dead one, and a design that handles "dead" and not "slow" has covered the easy case.

For each: what does a user see, and how long until anyone knows?

### 3. Protections, with numbers

For each of the five, either the setting and its justification, or an explicit "not
needed, because…":

| | The number that justifies it |
|---|---|
| Timeouts | derived from the latency budget, per hop |
| Retries | attempts, jitter strategy, **and the retry budget ratio** |
| Circuit breakers | threshold, minimum requests, cool-off — per dependency |
| Bulkheads | pool sizes, and what you gave up in pooling efficiency |
| Shedding | priorities, thresholds, and the degraded modes in order |

"We would add a circuit breaker" is not a review finding. "A breaker on the presence
service at 50% over 20 requests, cooling off for 10 seconds, because presence is
best-effort and its failure must not delay message sends" is.

### 4. The amplification audit

Two numbers, computed:

- **Retry amplification** — `total_attempts` across every layer that retries. If it is
  above 3, name the layers and say which one keeps its retries
- **Fan-out amplification** — the largest number of downstream calls one user action can
  produce, from week 8

### 5. The three findings

Rank everything you found. Take the top three and, for each:

- what fails, and what a user sees
- the smallest change that fixes it
- **what that change costs** — latency, complexity, availability elsewhere

Three, ranked, with costs. A review with fifteen undifferentiated findings has not
prioritised, and prioritising is the part that requires judgement.

---

## `resilience.py`

The arithmetic behind section 3, composing this week's three days:

```python
effective_offered(offered_qps, retries, has_retry_budget, budget_ratio=0.1)
effective_capacity(base_capacity_qps, dependency_failing, dependent_fraction,
                   has_breaker, has_bulkhead)
incident_goodput(offered_qps, capacity_qps, has_shedding)
run_incident(offered_qps, base_capacity_qps, dependency_failing,
             dependent_fraction, protections)   -> dict
```

Run `run_incident` on your own numbers with every protection off, then turn them on one at
a time. **The order in which they help is not the order people add them**, and finding that
out is the point of the lab.

---

## The five questions to have answers to

1. Your dependency ceiling is X. Your SLO is Y. Which is larger, and what will you do?
2. A dependency slows to 5 seconds. How long until your service is fully consumed, and
   what does Little's Law say the number is?
3. Every layer in your design retries three times. How many requests does one user action
   produce at the bottom?
4. At 150% of capacity, what is still working and who decided?
5. Your deep health check depends on the message store. The store has a bad minute. How
   many hosts leave the load balancer?

Question 5 is the one that turns a small problem into a total outage, and almost every
design has it.

---

## Before you submit

```bash
pytest week-09/milestone -v
python3 tools/check_sources.py
```

Then run `ai/editor.md` on `REVIEW.md` — the editor role is built for exactly this, and a
review of a review is a fair use of it.
