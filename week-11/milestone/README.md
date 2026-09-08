# Project 3 — The full design

> One line of brief. Four to six pages of document. No scaffolding.

| File | What |
|---|---|
| `DESIGN.md` | The design document |
| `DECISIONS.md` | Your decision library — every priced decision from the whole course |
| `SOURCES.yml` | Sources for every claim about a real system, in `content/sources/` format |

Must pass `python3 tools/check_sources.py`, and your own `design_lint.review()` must come
back clean.

---

## The brief

> **"Let people share files with each other."**

That is all of it.

The numbers exist — somebody knows them, or nobody does and you must assume them. Getting
them, or deciding them, is the work. Your instructor will answer questions in the Monday
hour and will not volunteer anything.

---

## Why the brief is one line

Every brief for ten weeks had a table of numbers. That was scaffolding.

A real brief is a sentence, and **pass 1 stops being a warm-up and becomes the hardest part
of the week.** The single most common failure in this milestone is a document whose
requirements were written after the boxes were drawn, and it is visible from across a room:
the numbers are round, the non-goals are missing, and every assumption is the one that made
the chosen design work.

---

## What is required

### `DESIGN.md`

Four to six pages, following the seven passes. Beyond the usual requirements:

- **Assumptions carry consequences.** Not "we assume peak is 5x" but "we assume peak is 5x;
  if it is 20x the queue tier triples". An assumption without a consequence is decoration
- **A "what we do not know" section**, applying the sourced/inferred/unknown split from
  week 1 to your own design. Which numbers are given, which are estimated, which are
  guesses
- **At least five decisions**, each with a rejected alternative, a price, and the condition
  that would flip it
- **A dependency ceiling**, from week 9, against your stated availability
- **Degraded modes in order**, from week 9

### `DECISIONS.md`

The decision library. Every priced decision you have made in eleven weeks, one page,
grouped by the recurring shape rather than by week.

This is the artefact the course was building, and it is what you revise from in week 12 —
much better revision than rereading eleven documents.

### `SOURCES.yml`

Any claim you make about how a real system works goes in here, in the same format as
`content/sources/`, and `tools/check_sources.py` must pass.

If your design makes no claims about real systems, the file says so and explains why —
which is a legitimate answer and a rarer one than you would think.

---

## Running your own linter on it

You built `design_lint.py` on Tuesday. Run it on this document before anybody else reads
it:

```bash
python3 -c "
import sys; sys.path.insert(0, 'week-11/day-2')
from design_lint import review
print('\n'.join(review(open('week-11/milestone/DESIGN.md').read())) or 'clean')
"
```

A clean result is not the same as a good document — the linter finds tells, not thinking —
but a document that fails its own author's linter has not been read by its author.

---

## The week

| Day | |
|---|---|
| Mon | Pass 1 only. Requirements, envelope, assumptions with consequences, non-goals. **No architecture.** One page |
| Tue | Passes 2–4: sizing, contract, paths. Build `design_lint.py` |
| Wed | Passes 5–7: decisions, failure modes, growth. Assemble the decision library |
| Thu | Run the linter, run `ai/editor.md`, revise. **Do not add features** |
| Fri | Defend it |

Thursday's instruction is the one people ignore. By Thursday the document will feel thin
and the temptation is to add a component. **Revise instead** — the fastest improvement
available on Thursday is deleting the third rejected alternative that was a straw man and
replacing it with one honest one.

---

## The five questions to have answers to

1. Which of your numbers were given, which estimated, and which invented?
2. What is your dependency ceiling, and is your stated availability below it?
3. Which decision was closest? What nearly won, and what would flip it?
4. What is in this design that is not needed?
5. If you had one more week, what would you do — and why is it not in the document?

Question 4 is asked every Friday and it has never once had the answer "nothing".

---

## Before you submit

```bash
python3 tools/check_sources.py
pytest week-11 -v
```

Then `ai/defend.md`, and then `ai/interviewer.md` on the same design. Week 12 will use this
document, so it is worth the extra hour now.
