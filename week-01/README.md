# Week 1 — A design is a set of decisions

> **Destination**
> Take a one-sentence brief, produce a design document with derived numbers in it, and
> survive someone attacking it for twenty minutes.

By Friday you will have written four design documents, three of them badly and on
purpose. The gap between Monday's and Friday's is the only evidence that matters this
week.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Tell a diagram from a design, and name the seven passes |
| Tue | `day-2/` | Turn a vague brief into requirements with numbers on them |
| Wed | `day-3/` | Size a system in four minutes, out loud |
| Thu | `day-4/` | Read a real architecture post and say which parts are load-bearing |
| Fri | `milestone/` | Ship the URL shortener design, then defend it |

Each day folder has its own `README.md`. Start there, every time.

---

## How a day goes

1. **Read** the day's README. All of it, before writing anything.
2. **Read the primary sources it links.** Not a summary of them. This is the habit the
   whole course is built on and week 1 is where it is cheap to build.
3. **Estimate before you look.** Before running any lab, write down what you think the
   number will be. The gap between your guess and the answer is the lesson.
4. **Write** the exercises. In order — they build.
5. **Test** with `pytest week-01/day-N -v`. Green means the arithmetic is right, nothing
   more. Whether the *design* is any good is Friday's question.
6. **Log** anything that stuck you in `logs/stuck-log.md`, and your five numbers in
   `logs/signal-log.md`.
7. **Commit and push.** Every day.

Day 1 has no tests. That is deliberate and it is explained there.

---

## What is different about this course

In a programming course the tests tell you whether you are right. Here they mostly
cannot. `pytest` can check that you divided by 86,400 correctly; it cannot check whether
you should have put a queue there.

So the grading has three parts, and only one of them is automatic:

| | Checks | Automatic |
|---|---|---|
| `pytest week-01` | the arithmetic and the mechanisms | yes |
| The design document rubric | that all seven passes were run | partly |
| **Friday's defence** | whether you can hold it under attack | no |

The third one is the real one. A design document nobody has attacked is a draft.

---

## Milestone

A design for a URL shortener. Spec in `milestone/README.md`. It must pass its tests
**and** survive Friday's defence, which is a different and harder bar.

Yes, this is the most written-about design problem in the industry, and you can find a
hundred answers to it in ten seconds. Two things make that not matter: the brief carries
a constraint the published answers do not satisfy, and you will be asked to derive your
numbers live rather than recite them. Reading someone else's answer first will actively
hurt you on Friday, and it will be obvious.

---

## What this week is not about

Technology names. Cleverness. Anything in the "not yet" column of `FENCE.md`.

You will write designs this week that a senior engineer would find naive, and that is
correct. A naive design you can defend, whose numbers you derived and whose failure
modes you have thought about, beats a sophisticated one you assembled from blog posts —
and it is not close, because the second kind collapses the moment somebody asks why.
