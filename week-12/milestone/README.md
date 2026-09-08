# Milestone — Ten scored mocks

> No new design. Ten interviews, scored, and the comparison against week 8.

| File | What |
|---|---|
| `MOCKS.md` | Ten mocks, each with a brief, per-pass scores, and one line of what went wrong |
| `READINESS.md` | The trend, the weakest pass, and what you would do with one more week |

Must pass `pytest week-12`.

---

## The ten

Ten forty-five-minute design interviews across the week, on briefs you have not seen. Use
`ai/interviewer.md`, which keeps time and introduces a twist at minute thirty.

Do them **out loud**, timed, and record at least three. Silent practice does not train the
thing being tested.

**Vary the briefs.** Suggested, and none of them is one you have designed:

1. A URL preview service — fetch, render and cache link previews
2. Ticketing for a stadium — 60,000 seats, all sold in ninety seconds
3. A feature-flag service read by 5,000 servers on every request
4. Warehouse pick-path optimisation
5. An e-signature workflow with an audit trail
6. A food-delivery dispatcher
7. A leaderboard for 40 million players
8. A notification service — email, push and SMS, with preferences
9. An API gateway with per-customer quotas
10. A "what changed" feed for a document product

Nine of these have no well-known published answer, which is deliberate: they measure design
rather than recall.

---

## Scoring

After each one, score it with `week-12/day-4/scoring.py`:

```python
score_mock({"interrogate": 4, "size": 3, "contract": 4,
            "path": 4, "decide": 3, "break": 2, "evolve": 1})
```

Record it in `MOCKS.md` with one line of what actually went wrong — not "I was nervous",
but "I spent eleven minutes on requirements and never reached failure modes".

**Score honestly.** The scores are for you; inflating them makes the trend useless and the
trend is the only thing in this milestone that matters.

---

## `READINESS.md`

Half a page, at the end of the week:

1. `progress(mocks)` — the trend per pass. Which improved, and which is flat?
2. Your weakest pass across all ten, and **why** it is weakest
3. `readiness(mocks)` — were the last three all a pass?
4. Your week-8 recording next to your tenth. Three specific differences
5. One more week: what would you practise, and what evidence says so?

Question 4 is the point of the milestone. "I improved" is a feeling; two recordings side by
side is evidence, and a career-changer's nerve is helped far more by evidence.

---

## The comparison

Watch your week-8 recording. All of it, without flinching.

Then your tenth. The difference is usually not knowledge — you knew most of it in week 8 —
it is **structure, arithmetic out loud, and reaching failure modes before the clock**. Those
are the three things that trained, and hearing them arrive is worth more than being told
they would.

---

## Before you finish

```bash
pytest week-12 -v
```

And then, genuinely: stop. The design work has been finished since week 11. Adding to it
now is avoidance wearing the clothes of diligence.
