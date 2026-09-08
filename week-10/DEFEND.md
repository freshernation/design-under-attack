# Week 10 — Friday defence

Twenty-five minutes, three phases, then a retro. Longer than a normal week because the
domain is unfamiliar to you as well — and that is useful, because it forces the student to
explain rather than perform.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-10/milestone`, and check:

- Is there a **break-even volume** for the specialised mechanism, and are they past it?
- Is `binding_constraint` computed over at least three resources, and is the answer the
  one the brief emphasised or a different one?
- Is there a `headroom_months` number? *When* matters as much as whether.
- Does the `Break` table have a row for **the specialised mechanism itself failing**?
- For path 5 only: is every protocol claim cited to the specification?

You will not know their domain as well as they do by Friday. Say so, and lean on it — a
student who can explain a specialised design to a competent person who does not share their
context is doing the thing this course is for.

---

## Phase 1 — Explain (8 min)

1. *"What is the expensive thing in this system, and what does the design do to avoid
   spending it?"* — the week's question. It should be answerable in two sentences.
2. *"What is the binding constraint? What is second, and what happens when they swap?"*
3. *"At what volume would the general answer have been enough, and how far are you from
   it?"* — a number, from their own lab.
4. *"What did you have to leave out because it did not fit the specialised model?"* —
   every specialisation makes something else awkward. If they cannot name it, they have not
   found the edge of their design.
5. *"Which claim here is sourced and which is you?"* — sharper than usual this week. Four
   of the five paths have thin public records.

| 5 | 3 | 1 |
|---|---|---|
| Names the expensive resource and the break-even without prompting; knows what the specialisation cost them | Describes the design accurately | Adopted the specialised mechanism because it is the one for this domain |

## Phase 2 — Mutate (8 min)

Choose by path.

**Dispatch —** *"The service area expands to a region with a thousandth of the density."*
Looking for: one resolution cannot serve both, and the answer is two populations again.

**Editor —** *"Documents must now be full-text searchable while being edited."*
Looking for: the CRDT's stored form is not the text, so the index is derived and must be
kept in step — a materialised view with a lag, which is week 7.

**Matching —** *"The venue must run in two datacentres and survive losing one."*
Looking for: a replicated sequencer, and the realisation that failover must not change the
fill sequence — which is week 5, at a latency budget that forbids the usual answer.

**Inference —** *"The batch workload triples and must still not delay interactive traffic."*
Looking for: priority classes and token-based admission, from week 9 and Thursday, not more
hardware.

**Federated —** *"A server you consume from starts publishing invalid records."*
Looking for: self-verifying records mean you can reject them, and the interesting question
is what your index does about the ones you already ingested.

| 5 | 3 | 1 |
|---|---|---|
| Reaches for an earlier week's mechanism unprompted | Gets there messily | Treats it as a new problem |

## Phase 3 — Break (7 min)

| Attack | Watching for |
|---|---|
| *"Your specialised component is unavailable for an hour."* | Is there a degraded path, or is the product simply down? |
| *"The thing you optimised for stops being the constraint."* | Would they notice? What measurement would tell them? |
| *"Somebody joins the team who has never seen this mechanism."* | The fixed cost they did not count. It is a real cost and it recurs |
| *"Your growth rate doubles."* | `headroom_months`, live |
| *"The general mechanism improves — hardware gets faster, the library gets better."* | The break-even moves against them. Specialisations decay |

| 5 | 3 | 1 |
|---|---|---|
| Treats the specialisation as a decision with an expiry date | Defends it | Assumes it is permanent |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"Which earlier week did you use most in this design?"* — usually 2, 4 or 7, which
   surprises people who expected the answer to be "week 10".
2. *"If you had to work in this domain on Monday, what would you need to learn first?"* —
   a good answer is specific and short.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 11 is **Project 3**: a full design, from a one-line brief, with no scaffolding.

The framing for Monday: **every brief so far told you the scale. Next week's does not, and
you have to ask.** Pass 1 stops being a warm-up and becomes the hardest part.

The check: can they say what their specialisation cost them, unprompted? A student who can
only list what a mechanism enables will, next week, produce a design with four impressive
components and no acknowledgement of what any of them made worse.
