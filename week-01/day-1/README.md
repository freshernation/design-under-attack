# Day 1 — What a design answer is

> **By the end of today** you can tell a diagram from a design, name the seven passes in
> order, and you have three bad design documents with your name on them.

---

## Read first

- [ ] [**What a design answer actually is**](../../content/week-01/day-1/what-a-design-answer-is.md) — 25 min · sources: [Google SRE Book](https://sre.google/sre-book/service-level-objectives/), [AWS Builders' Library](https://aws.amazon.com/builders-library/)
- [ ] [**The seven passes**](../../content/week-01/day-1/the-seven-passes.md) — 30 min

Skim the two source links as well. You are not studying them today; you are noticing
that nobody in either one says "we chose X because it is scalable".

---

## There are no tests today

`pytest week-01/day-1` will find nothing, and that is on purpose.

Today's output is three documents that are wrong. There is nothing to assert about them,
and pretending otherwise would teach you that a green test means a good design — which
is the one belief this course cannot afford you to pick up. From tomorrow the tests
check arithmetic, and that is all they will ever check.

---

## The exercise: three timed designs

Three briefs. **Fifteen minutes each, on a timer.** No AI, no searching, no reading
ahead. Write in `week-01/day-1/attempt-1.md`, `attempt-2.md`, `attempt-3.md`.

When the timer goes, stop mid-sentence if you have to.

### Brief 1 — *A service that tells you when a website goes down*

People register a URL. You check it periodically. When it stops responding, you email
them.

### Brief 2 — *A leaderboard for a mobile game*

Players submit scores. Anyone can see the top 100 globally, and their own rank.

### Brief 3 — *A system that stores every photo a user uploads and shows them a grid*

That is the whole brief. It is meant to be underspecified.

---

## Then, and only then

Go back over what you wrote with a highlighter, and mark each of the seven passes where
you find it:

| Pass | Did you? |
|---|---|
| 1 Interrogate | Did you write down what you were **not** building? |
| 2 Size | Is there a single number in your document that you multiplied to get? |
| 3 Contract | Did you say what a client can ask for? |
| 4 Path | Is there an ordered list of hops anywhere? |
| 5 Decide | Did you name one alternative you rejected? |
| 6 Break | Did you say what happens when anything fails? |
| 7 Evolve | Did you say what breaks first when it grows? |

Write the tally at the bottom of each file. Most people score 2 or 3 out of 7 on their
first day, and the two they get are usually contract and path — because those feel like
"designing" and the rest feels like paperwork.

**Keep these three files.** You rewrite brief 2 on Friday, after the milestone, and put
the two versions side by side. That comparison is the point of today and it only works
if today's version is genuinely untutored. Do not go back and improve them.

---

## What to notice

Three things happen to almost everyone on day one. Recognising yours is the day's real
output — write it in `NOTES.md`.

**You drew boxes.** Within about two minutes, with no numbers anywhere. Ask yourself
what you would have had to know to place any of them deliberately.

**You ran out of time on brief 3 and were fine on brief 1.** Because brief 3 is vaguer.
The vagueness was not an obstacle to the design; it *was* the design work, and there was
no way to make progress without deciding what you were building.

**You named a technology.** Almost everyone does, in the first five minutes. Notice
where in the document it appeared — it is usually the moment thinking stopped, and the
rest of the document treats that noun as a settled fact.

---

## Log

`logs/stuck-log.md` for anything that stalled you, `logs/signal-log.md` for your five
numbers. Two minutes. Your instructor reads both before tomorrow's hour.
