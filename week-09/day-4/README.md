# Day 4 — Shedding and degradation

> **By the end of today** you can refuse work in priority order, and you will have seen
> useful work *fall* as load rises.

---

## Read first

- [ ] [**Load shedding, and degrading on purpose**](../../content/week-09/day-4/load-shedding-and-degradation.md) — 30 min · sources: [AWS — load shedding](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/), [SRE Book — Handling Overload](https://sre.google/sre-book/handling-overload/), [AWS — health checks](https://aws.amazon.com/builders-library/implementing-health-checks/)

---

## The lab

`shedding.py`.

```python
goodput(offered_qps, capacity_qps, overload_penalty=2.0)
goodput_with_shedding(offered_qps, capacity_qps)
PriorityShedder(thresholds)  .allow(priority, utilisation)  .shed_levels(utilisation)
admit(oldest_queue_age_ms, client_timeout_ms)
healthy_fleet_fraction(hosts, failing, max_removable)
```

The goodput formula is a **stipulated model**, stated as such in the docstring, and the
tests assert its shape rather than its values. The shape is the point: past capacity, an
unprotected service does less useful work as load rises.

`admit` is the one to notice. It has no threshold to tune and no capacity to estimate — it
refuses exactly when the queue has become useless, whatever the current capacity happens to
be. Self-tuning rules like that are rare and worth collecting.

```bash
pytest week-09/day-4 -v
```

---

## The written exercise

`week-09/day-4/degraded-modes.md`, half a page.

For your chat system, write the degraded modes **in the order you would apply them**:

```
at 85% utilisation:  presence updates batch at 10s instead of 3s
at 90%:              read receipts stop being sent
at 95%:              channel member lists serve from cache, up to 5 minutes stale
at 100%:             message send only; everything else is refused
```

Four to six lines. Then one sentence on what a user actually sees at each step.

This is a product decision, and the only time it can be made is now — nobody designs a
graceful degradation at 3am.

---

## Tomorrow

The milestone: a resilience review of your own Project 2. Read
`week-09/milestone/README.md` tonight, and run `dependency_ceiling` on your critical path
before Friday morning.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
