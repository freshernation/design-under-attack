# Day 1 — Pass 1, and nothing else

> **By the end of today** you have one page: requirements, envelope, assumptions with
> consequences, and non-goals. No architecture.

---

## Read first

- [ ] [**Designing from one line**](../../content/week-11/day-1/from-a-one-line-brief.md) — 25 min
- [ ] [**Writing the document**](../../content/week-11/day-2/writing-the-document.md) — 25 min

Both are **Tier 3 — ours**. There is no authority on this and anybody claiming otherwise is
selling a template. Read them as arguments.

---

## The brief

> **"Let people share files with each other."**

Your instructor will answer questions in the live hour and will not volunteer anything.
Sort your questions first — load-bearing and knowable, load-bearing and unknowable, or not
load-bearing — and only ask the first kind.

---

## Today's output

One page in `week-11/milestone/DESIGN.md`:

```
## Problem and non-goals
## Envelope
## Assumptions
## Scale
```

That is all. **No components, no diagram, no storage choice.**

The rule is not arbitrary. The most common failure in this milestone is a document whose
requirements were written after the boxes were drawn, and it is visible from across a room:
round numbers, missing non-goals, and every assumption exactly the one that made the chosen
design work.

---

## The assumptions section is the exercise

Every assumption gets a consequence:

```
ASSUMED (not given):
- peak is 5x average                        if 20x, the upload tier triples
- median file 400 KB, p99 20 MB             if p99 is 2 GB, this is a different system
- 99% of shares reach fewer than 10 people  the fan-out design depends on this
- shares are permanent unless revoked       if they expire, there is a sweeper and a new failure mode
```

Four to eight of these. **An assumption without a consequence is decoration**, and the
right-hand column is what makes this a design artefact rather than a disclaimer.

---

## No lab today

Deliberately. Today is a page of prose, and the temptation to open an editor and start
sketching components is exactly what the day exists to resist.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
