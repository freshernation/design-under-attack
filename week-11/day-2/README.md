# Day 2 — Sizing, contract, paths — and the linter

> **By the end of today** passes 2 to 4 are written, and you have built the thing that
> reviews design documents.

---

## Read first

- [ ] [**Writing the document**](../../content/week-11/day-2/writing-the-document.md) — 25 min, if you did not read it yesterday

---

## The design work

Passes 2, 3 and 4, in `DESIGN.md`:

- **Sizing.** Every number derived. The chain from week 1, and the storage arithmetic from
  week 3, and the dependency ceiling from week 9
- **API and data model.** Backwards from the queries, week 3
- **Request paths.** An ordered hop list for the critical read and the critical write. Not
  a picture

---

## The lab

`design_lint.py` — the tells you have been collecting since week 1, as a program.

```python
has_derived_numbers(text)          unmeasurable_claims(text)
bare_technology_names(text)        sections_present(text)
decisions_without_alternatives(text)
review(text)
```

Two implementation notes that are also design notes:

- **Split sentences on enders and blank lines, not on every newline.** Markdown wraps
  lines, and splitting mid-sentence would flag a product whose justification is on the line
  above. A linter with false positives gets switched off
- **`bare_technology_names` is the week-1 fence, surviving as a rule.** Not a ban — a
  requirement that the sentence naming a product also says what property it is needed for

```bash
pytest week-11/day-2 -v
```

Then run it on your **week-8 Project 2**:

```bash
python3 -c "
import sys; sys.path.insert(0, 'week-11/day-2')
from design_lint import review
print('\n'.join(review(open('week-08/milestone/DESIGN.md').read())) or 'clean')
"
```

It will find things. That is more persuasive than any checklist, and it is the point of
building it rather than being given it.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
