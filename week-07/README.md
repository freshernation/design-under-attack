# Week 7 — Logs, queues and idempotency

> **Destination**
> Move work between systems knowing it will arrive more than once, out of order, or an
> hour late — and design so that none of those matter.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Say what a log gives you that a queue cannot, and what it costs |
| Tue | `day-2/` | Choose a delivery guarantee, and know why the third one is not on offer |
| Wed | `day-3/` | Make an effect safe to repeat, and remove a dual write with a table |
| Thu | `day-4/` | Reason about ordering, rebalancing and lag in a consumer group |
| Fri | `milestone/` | Ship the click aggregator, then defend it |

---

## The one idea

**Exactly-once delivery is impossible. Exactly-once effect is a design choice, and it is
usually yours to make.**

A sender cannot distinguish "you never received it" from "your reply was lost", so it must
choose between resending and not. That is the terrain, not a gap. Everything this week is
about building on it: at-least-once delivery, plus an effect that does not care.

---

## What is new

**You have built this before.** Week 3 day 4 was an append-only log with framed records,
read forward, stopping at the first bad one. This week is the same structure with the
readers moved outside, and every idea transfers.

**The failures are now familiar.** "You cannot tell a crash from a slowdown" was week 5.
"A monotonic token makes a confused participant harmless" was week 5 and again week 6.
By Wednesday you should be recognising shapes rather than learning them.

---

## Milestone

An ad-click aggregator, where advertisers are billed from the numbers. At-least-once
delivery, exactly-once counting, and a 24-hour replay requirement whose obvious
implementation needs 690 GB of event ids. Spec in `milestone/README.md`.

The way out is a mechanism you build on Wednesday, applied somewhere you would not
immediately think to apply it.

---

## What this week is not about

Message brokers. You will not learn how to operate one, tune one, or choose between them,
and the differences that dominate those conversations are not the ones that decide a
design.

What decides a design is: which guarantee do I have, where do duplicates come from, and
what makes the effect safe to repeat. Three questions, answerable without knowing anyone's
product name.
