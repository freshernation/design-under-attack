# Week 9 — Failure and operations

> **Destination**
> Take a design you have already written, find out how it degrades, and make it degrade
> by only the part that is actually broken.

Everything until now assumed the failure was somewhere else. This week your own service is
the one failing, and the question is what it does about it.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Turn a target into a budget, and find out whether it was ever reachable |
| Tue | `day-2/` | Retry without making the outage worse |
| Wed | `day-3/` | Stop one dependency, and one tenant, from consuming everything |
| Thu | `day-4/` | Refuse work on purpose, in priority order |
| Fri | `milestone/` | **Review Project 2** and find its three worst failures |

---

## The one idea

**Refusing work is how you protect the work you accepted.**

Past capacity, an unprotected service does *less* useful work as load rises — every
response arrives after its client gave up. A service that serves 80% and rejects 20%
quickly has done its job far better than one that accepts everything and completes
nothing in time.

That is uncomfortable to design deliberately, and it is the whole difference between a
system that degrades and one that collapses.

---

## The four shapes you will keep meeting

By Friday these should be reflexes rather than techniques:

| | The failure it prevents |
|---|---|
| **Retry budgets** | retries tripling the load on a service that is already failing |
| **Jitter** | everything synchronised coming back at the same instant. Fifth time this course |
| **Breakers and bulkheads** | one dependency's slowness becoming your total outage |
| **Shedding by priority** | doing work nobody is waiting for while critical work queues |

---

## Milestone

Not a new design. **A resilience review of your own Project 2** — the SLO restated with a
dependency ceiling, a dead/slow/lying inventory, the protections with numbers, the
amplification audit, and three ranked findings.

Reviewing is the job. Most of your career is spent making an existing system better, and
this is the highest-leverage version of that.

---

## What this week is not about

Monitoring tools, alerting platforms, or incident process. Those matter and they are
learned on the job in a week.

What is learned here and nowhere else is the arithmetic: what a target costs, what a
dependency ceiling is, how far a retry multiplies, and what a service actually produces at
150% of capacity. Those numbers turn "we should be more resilient" into a decision.
