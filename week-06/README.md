# Week 6 — Caching and the read path

> **Destination**
> Put a cache in front of something, know exactly what it is hiding, and be able to
> say what happens when it is empty.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Turn a working set into a hit rate, and a hit rate into origin load |
| Tue | `day-2/` | Name the four write strategies and demonstrate the cache-aside race |
| Wed | `day-3/` | Collapse a thousand concurrent misses into one, in twenty lines |
| Thu | `day-4/` | Reject a lookup you never needed to make, and reason about cache keys |
| Fri | `milestone/` | Ship the catalogue read path, then defend it |

---

## The one idea

**A cache is a replica you built on purpose and gave no consistency story to.**

Say that once and week 5 does most of this week's work. Staleness bounds, read-your-writes,
the race between a write and a copy — all of it applies. The only difference is that a
cache is *allowed* to be wrong and has no protocol for becoming right. It just expires.

The second idea, which follows: **hit rate is not a performance metric, it is a capacity
dependency.** A cache dropping from 99% to 95% multiplies your origin load by five, at an
origin sized for one fifth of it.

---

## What is new

**The fence comes down on Friday.** After five weeks of forbidding product names, the
milestone lets you use them — with a rule attached. See `FENCE.md`.

**The milestone is decided by arithmetic rather than judgement.** The brief has a
five-second freshness requirement and an origin that cannot serve the load that
requirement implies. You find that out by computing it, and the way out is a mechanism
rather than a bigger machine.

---

## Milestone

A product catalogue read path: 400,000 reads a second against an origin that serves
20,000, one object with three different freshness requirements, and a long tail that a
longer TTL does nothing for. Spec in `milestone/README.md`.

---

## What this week is not about

Making things fast. Caches make things fast almost by accident; what they mostly do is
**move load**, and every interesting question this week is about where the load went and
what happens when the cache stops absorbing it.

The instinct being trained: when someone proposes a cache, ask what the hit rate will be,
what the origin does at that miss rate, and what happens when the cache is empty. Three
questions, and most proposals do not survive them.
