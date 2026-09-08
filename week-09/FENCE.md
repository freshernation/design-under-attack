# Week 9 — Concept fence

## Allowed

**Everything from weeks 1–8**, plus:

- **SLIs, SLOs, error budgets** — burn rate, multi-window alerting, dependency ceilings
- **Retries** — what is safe to retry, exponential backoff, full and decorrelated jitter,
  retry budgets, the layer multiplication
- **Circuit breakers** — closed, open, half-open; thresholds and minimum request counts
- **Bulkheads** — per-dependency pools, and the pooling efficiency you give up
- **Shuffle sharding** — and the combinatorics that make it work
- **Load shedding** — goodput, priority levels, admission control on queue age, LIFO under
  overload
- **Degradation** — degraded modes chosen in advance, serving stale on error
- **Health checks** — liveness, shallow, deep, and capping how much of a fleet may be
  removed

## Not yet

CRDTs and collaborative editing (week 10) · geospatial indexing (week 10) · media
pipelines (week 10) · model serving (week 10) · incident command and postmortem practice —
worth learning, and not a design skill

---

## The rule

**Every dependency in a design has a stated behaviour when it is slow.**

Not when it is down — when it is *slow*. Dead is the easy case: it is obvious, it pages
somebody, it gets fixed. Slow holds your connections, fills your pools, triggers retries
that add load, and takes down healthy things around it.

From this week, a design that says what happens when a dependency fails and not what
happens when it degrades has covered the easy half.
