# Week 11 — Friday defence (Project 3)

**Forty minutes.** The longest defence of the course, and the closest thing to a real
design interview the student will have had.

Four phases: explain, mutate, break, and reflect.

---

## Before they arrive

Read `DESIGN.md`, `DECISIONS.md` and `SOURCES.yml`. Run their own linter over their
document. Then check the three things that separate a Project 3 from a week-4 milestone:

- **Do the assumptions carry consequences?** "We assume peak is 5x" is a disclaimer. "We
  assume peak is 5x; at 20x the queue tier triples" is a design artefact.
- **Is there a "what we do not know" section**, and is it honest? Anybody can write three
  unknowns. Look for the one that would actually hurt.
- **Is the decision library grouped by shape** rather than by week? Somebody who has noticed
  that four of their decisions are the same decision has learned the transferable thing.

---

## Phase 1 — Explain (10 min)

1. *"Walk me through the brief you were given, and the brief you designed to."* — the gap
   between them is the whole of pass 1, and it should be a page.
2. *"Which of your numbers were given, which estimated, and which invented?"* — the answer
   should come immediately and without embarrassment.
3. *"Walk me through a share, end to end. Every hop."*
4. *"What is your dependency ceiling, and is your availability below it?"*
5. *"What is in this design that is not needed?"* — asked every Friday since week 1. It has
   never once had the answer "nothing", and a student who says "nothing" now has stopped
   reviewing their own work.

| 5 | 3 | 1 |
|---|---|---|
| Distinguishes given, estimated and invented instantly; names something to cut | Describes the design accurately | Presents assumptions as facts |

## Phase 2 — Mutate (10 min)

Two mutations, not one. Pick from these, or invent one from a weakness you spotted.

**"Files are now shared with 50,000 people at a time, not 5."** The fan-out design breaks;
the permission check moves from per-recipient to per-link. This is the fork they should
have named on Monday, and the best answers say "I flagged this — here is what changes."

**"Every file must be encrypted such that we cannot read it."** Almost everything they
built for search, deduplication, thumbnails and virus scanning stops working. Looking for:
they identify what dies rather than proposing a cryptographic scheme.

**"Regulators require that a deleted file is provably gone within 24 hours."** Deletion
across caches, replicas, backups and a CDN — weeks 5, 6 and 8 arriving together, and most
designs have no story at all.

**"Halve the budget."** What comes out? A student who cannot cut has not priced anything.

| 5 | 3 | 1 |
|---|---|---|
| Identifies what dies, and prices the change | Redesigns competently | Adds components |

## Phase 3 — Break (12 min)

Twelve minutes, and go hard. This is the closest they will get to a real interview before
they are in one.

| Attack | Watching for |
|---|---|
| *"Your cache is empty and traffic is at peak."* | The cold-start multiplier, week 6 |
| *"The metadata store is up and taking four seconds per query."* | Slow, not dead. Week 9 |
| *"Two users share the same file at the same millisecond."* | Week 5, and whether the answer is idempotence rather than locking |
| *"Your deploy restarts everything."* | Reconnects, cold caches, retry storms, all at once |
| *"An entire region is unreachable for an hour, then returns."* | The return is worse than the outage |
| *"One customer is 40% of your traffic."* | Two populations, sixth time |
| *"How would you know any of this was happening?"* | The metric, and the threshold. Most designs have neither |

The last one is worth reserving for the end. A design with no answer to "how would you
know" is a design that has only been thought about in the present tense.

| 5 | 3 | 1 |
|---|---|---|
| Reasons from their own numbers under sustained pressure | Finds most of it with prompting | Reaches for a component each time |

## Phase 4 — Reflect (8 min)

Not scored. This is the conversation the whole course was for.

1. *"Which week's material did you use most in this design?"* — almost never week 10, and
   very often week 2.
2. *"Which of your eleven documents would you now rewrite, and what would you change?"*
3. *"You have a decision library. Which decision in it are you least sure of?"*
4. *"If somebody asked you to design something in a domain you know nothing about on
   Monday, what would you do first?"* — the answer should be a question, not a mechanism.

---

## Instructor: what next week is

Week 12 is the interview: ten scored mocks, and no new material.

Say this on Friday, plainly, because it changes how the weekend is spent: **the design work
is finished.** Next week nothing improves except them. Students will want to add a feature
to Project 3; the honest answer is that a person who can build and cannot explain gets
rejected in round one and their repository is never opened.

The check going into week 12: is the decision library grouped by shape? That page is what
they revise from. If it is a list of eleven weeks in order, it will not help them under
pressure, and half an hour of regrouping on Sunday is the best-value work available.
