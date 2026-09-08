# Interrogating the requirement

*Week 1 · Day 2 · about 25 minutes*

> By the end of this you can take a one-sentence brief and produce a page of
> requirements with numbers on them — and a list of what you are not building.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Google SRE Book — Service Level Objectives**](https://sre.google/sre-book/service-level-objectives/) | 1 | The vocabulary: SLI, SLO, SLA, and why you must not set the target at 100% |
| [**Google SRE Workbook — Implementing SLOs**](https://sre.google/workbook/implementing-slos/) | 1 | The practical version: how to pick what to measure, with worked examples |

Read the first three sections of the SRE Book chapter before you continue. The single
idea to bring back: **the target is a decision, not a discovery.** Nobody found out that
Google's service should be 99.9% available; somebody chose it, and the choice had a
price.

---

## A brief is not a specification

Every design question you will ever be asked arrives underspecified, and this is not
laziness on the asker's part. It is the test.

> "Design a system where users can follow each other and see a feed of posts."

A junior engineer starts designing. A senior engineer starts asking, because that
sentence is compatible with a thousand different systems, and picking the wrong one
wastes the next six months rather than the next six minutes.

The skill has two halves, and the second is the hard one:

1. Ask the questions whose answers change the design
2. **Stop asking**, and commit to written assumptions

Interrogation that never ends is its own failure mode. Ten minutes of questions with no
design is indistinguishable from not knowing how to design. Get the numbers that move
the architecture, write down what you assumed for everything else, and move.

---

## The questions that change the design

Not a checklist to recite — a set of things whose answers you cannot design without.

### Who and how many

| Ask | Because |
|---|---|
| How many users, and how many are active daily? | this is the input to every number you compute next |
| How many actions each, per day? | DAU alone tells you nothing |
| Reads or writes — which dominates, and by how much? | a 100:1 read ratio and a 1:1 ratio are different systems |
| Is the load even, or spiky? | you size for peak, and the peak is often 5–10x |
| Is one entity far more popular than the rest? | hot keys break more designs than raw volume ever will |

That last one is the question people forget. A system where every user has roughly 200
followers is easy. The same system where one user has 200 million is a different
problem, and no amount of extra servers fixes it. Ask it every time.

### What must be true

| Ask | Because |
|---|---|
| How fast, at the 99th percentile? | tomorrow's article; the average is a lie |
| What happens if this is down for an hour? | separates "annoying" from "front page of the news" |
| Can we lose data? Which data? | a lost analytics event and a lost payment are not the same event |
| Must a user see their own write immediately? | this single question decides half your architecture |
| How stale can other people's view be? | one second and one minute are wildly different budgets |
| How long must we keep it? | retention drives storage more than volume does |

### What we are not building

The one that never gets asked and always should:

> "Am I designing the mobile client too? Search? Analytics? Moderation? Payments?
> Multi-region? I am going to assume **no** to all of those and say so."

Writing that down takes a minute and buys you the entire rest of the session. It is
also the clearest signal of experience you can give in an interview, because scope
control is the thing juniors do not do and seniors cannot stop doing.

---

## Requirements versus solutions in disguise

Half of what stakeholders call a requirement is an architecture they have already
chosen, wearing a requirement's clothes.

| What you are told | What is actually required | What was smuggled in |
|---|---|---|
| "We need a Redis cache" | reads must return in under 50 ms | the cache, and Redis specifically |
| "It should use a queue" | the client must not wait for the email to send | the queue |
| "We need it in three regions" | European users need sub-100 ms reads | the three regions |
| "It has to be real-time" | *ask what number they mean by real-time* | everything |

**Translate every one of these back into an observable property before designing.**
Sometimes the smuggled solution turns out to be right — but if you accept it unexamined
you have inherited someone else's decision and will be defending it on Friday as though
it were yours.

"Real-time" deserves special hostility. It means sub-second to one person and
sub-millisecond to another, and those two systems share no components. Never let the
word into a document without a number beside it.

---

## Functional and non-functional

**Functional** — what it does. A shopper can request a notification. An email is sent
on restock. These are usually easy, and they are what the brief already told you.

**Non-functional** — how well it must do it. Latency, availability, durability,
consistency, freshness, retention, cost.

Here is the thing that surprises people: **the non-functional requirements determine the
architecture almost entirely.** The functional ones tell you what to build; they rarely
tell you how. "Send an email when the item restocks" is satisfied by a cron job over a
CSV file — as long as the envelope permits an hour of delay, tolerates a lost email, and
covers ten thousand products. Tighten any one of those and the CSV dies.

So the interesting part of pass 1 is the envelope, which is [the next article](the-non-functional-envelope.md).

---

## Write it down like this

The output of pass 1 is a page, and it looks like this:

```
## What it does
- A shopper can register interest in an out-of-stock product
- When a product is restocked, every registered shopper is emailed once
- A shopper can cancel

## Envelope
- Signup: p99 < 200 ms, 99.9% available
- Notification: 95% delivered within 5 minutes of restock
- Durability: a registered watch must survive a server dying
- Duplicates: at most one email per shopper per restock (assumed; confirm)

## Scale (assumed where noted)
- 10M products, 5M monthly shoppers, ~100k signups/month (given)
- Worst-case fan-out: 50k watchers on one product (assumed)
- Restocks: ~5k/day (assumed)

## Not building
Mobile push · SMS · price-drop alerts · i18n · recommendations · analytics
```

Every assumption labelled. That labelling is not politeness — on Friday, someone will
attack one of your numbers, and there is a large difference between "I assumed 50k and
here is what changes if it is 500k" and a silence.

---

## Today's lab

`week-01/day-2/envelope.py` — turn the words in an envelope into numbers a computer can
check. Nines into minutes of downtime, percentile strings into milliseconds, and a
function that decides whether a stated requirement is measurable at all.

The last one is the point. "The system should be highly available" fails the test, and
it should.

---

> **Sources for this article**
> [Google SRE Book](https://sre.google/sre-book/service-level-objectives/) and
> [SRE Workbook](https://sre.google/workbook/implementing-slos/), both Tier 1, Google,
> 2016–2018. The question lists and the "solutions in disguise" table are this course's
> own framing — Tier 3.
