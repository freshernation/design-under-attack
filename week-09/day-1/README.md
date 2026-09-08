# Day 1 — SLOs and error budgets

> **By the end of today** you can turn a target into a budget, alert on how fast it is
> being spent, and find out whether the target was ever achievable.

---

## Read first

- [ ] [**SLOs, and spending an error budget**](../../content/week-09/day-1/slos-and-error-budgets.md) — 30 min · sources: [SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/), [Embracing Risk](https://sre.google/sre-book/embracing-risk/), [SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)

Read *Embracing Risk* today. It is short, and it is the argument that makes the rest of
the week coherent.

---

## Predict first

Your service depends on four things, each 99.95% available.

What is the best availability you can offer on top of them? Write a number down before the
lab.

---

## The lab

`slo.py`.

```python
error_budget_minutes(target_percent, window_days=28)   budget_remaining(...)
burn_rate(observed_error_rate, target_percent)         time_to_exhaustion_hours(...)
dependency_ceiling(availabilities)                     is_reachable(target, availabilities)
should_page(rate, window_hours)
```

`dependency_ceiling` is the function to run on your own designs afterwards. It takes ten
seconds and it occasionally reveals that a target everyone agreed to was never reachable —
which is a much better thing to discover now than during a quarterly review.

```bash
pytest week-09/day-1 -v
```

---

## The written exercise

`week-09/day-1/slo-for-project-2.md`, half a page. This is the head start on Friday.

1. Write the SLI for your chat system: exactly what you count, and **where you measure it**
2. Pick the SLO, and state the error budget in minutes
3. List every dependency on the critical path with a plausible availability, and compute
   the ceiling
4. If your SLO is above the ceiling — and it probably is — write the sentence that says so

Step 4 is the exercise. It is one sentence, it is uncomfortable, and it is the most useful
thing in the document.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
