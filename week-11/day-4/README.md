# Day 4 — Revise

> **By the end of today** the document is shorter, sharper, and honest about what it
> gave up.

---

## No new reading, and no new features

Today is revision. The rule, and it is the one people ignore:

> **Do not add a component.**

By today the document will feel thin. That feeling is normal and it is usually wrong — what
is missing is rarely a mechanism, it is a price, a consequence, or an admission.

---

## The order to work in

**1. Run your own linter.** Fix what it finds.

```bash
python3 -c "
import sys; sys.path.insert(0, 'week-11/day-2')
from design_lint import review
print('\n'.join(review(open('week-11/milestone/DESIGN.md').read())) or 'clean')
"
```

**2. Run `ai/editor.md`.** Paste the finished document. It is built to attack, and the
question it ends with — *the single question this document is least able to survive* — is
the one you should fix before Friday.

**3. Check the sources.** `python3 tools/check_sources.py`.

**4. Then cut.** In this order:

- background the reader does not need
- descriptions of mechanisms rather than decisions about them
- diagram boxes no request passes through
- rejected alternatives that were straw men — replace with one honest rejection

**5. Then add exactly two things, if they are missing:**

- a consequence to every assumption
- a price to every decision

---

## The one test

> **Delete every proper noun from your design. Is there anything left?**

Week 1's test, on the last document you will write in this course. If the decisions, the
numbers and the prices are all still there and only the labels are gone, the eleven weeks
worked.

---

## Then rehearse

`ai/defend.md` on your own document, then `ai/interviewer.md` on the same brief. Tomorrow is
forty minutes and phase 3 is twelve of them.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
