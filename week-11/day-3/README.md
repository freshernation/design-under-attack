# Day 3 — Decisions, failures, growth — and the library

> **By the end of today** the document is complete, and the decision library exists.

---

## Read first

- [ ] [**The decision record**](../../content/week-11/day-3/the-decision-record.md) — 20 min

---

## The design work

Passes 5, 6 and 7:

- **Decisions.** At least five. Each with the rejected alternative, the price, and **the
  condition that would flip it**. That fourth part is the one nobody writes and the one
  that makes a decision reviewable a year later
- **Failure modes.** Dead, slow and lying, per component. Slow is the one to spend time on
- **Growth.** What breaks first at 10x, and which metric shows it

---

## `DECISIONS.md`

The library. Every priced decision from eleven weeks, on one page, **grouped by shape
rather than by week**:

```
Two populations, two strategies
  weeks 4, 6, 7, 8, 10 — whale tenants, long tails, hot campaigns, large channels, dense cells
  the boundary is always derived from a budget, never round
  flips if: the distribution stops being heavy-tailed, which it does not

A monotonic token makes a confused participant harmless
  weeks 5, 6 — fencing tokens, cache leases
  price: storage must enforce it; by convention it enforces nothing
```

Grouping by shape rather than by week is the exercise. **Noticing that four of your
decisions are the same decision is worth more than having four**, and it is what lets you
answer a question about a system nobody has written up.

---

## No lab today

The library is the work.

---

## Tomorrow

Lint, edit, revise. **Do not add features.** By tomorrow the document will feel thin and
the temptation is to add a component; the fastest improvement available is deleting the
straw-man alternative and replacing it with an honest one.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
