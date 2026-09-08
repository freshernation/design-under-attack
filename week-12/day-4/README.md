# Day 4 — Scoring

> **By the end of today** you can score a mock honestly, and see which pass is not
> improving.

---

## No new reading

Today is a short lab and then mocks. The week's material is done; what remains is
repetition and evidence.

---

## The lab

`scoring.py` — the rubric as code, so ten mocks can be compared rather than remembered.

```python
score_mock(scores)      verdict(scores)      weakest_pass(scores)
on_schedule(pass_name, minutes_elapsed)
progress(mocks)         readiness(mocks)
```

Three rules encoded in it, and each is a claim worth arguing with:

- **Any pass below 3 is a no-hire**, whatever the others are. A design with no failure
  analysis is not rescued by excellent sizing
- **An unscored pass is an error, not a zero.** A pass with no score is one the interviewer
  never reached, and recording it as zero would hide that the clock ran out
- **Readiness is three consecutive passes**, not a best-of. One good mock is a good day

```bash
pytest week-12/day-4 -v
```

---

## Then start the ten

Two mocks today, and the rest tomorrow. Score each one immediately — a mock scored the next
morning is scored from memory, and memory is generous.

Record in `week-12/milestone/MOCKS.md` with one line of what went wrong. Not "I was
nervous", but "I spent eleven minutes on requirements and never reached failure modes".

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
