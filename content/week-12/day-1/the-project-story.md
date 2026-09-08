# The story of a design

*Week 12 · Day 1 · about 20 minutes*

> By the end of this you can talk about a system you designed for ninety seconds, five
> minutes, or twenty, and each version is the right one.

---

## No sources, and that is the honest answer

This is the least sourced article in the course. There is no authority on interviewing,
the published advice is overwhelmingly Tier 3 or 4, and much of it is folklore repeated
until it sounded true.

What follows is **ours** — argued from what a design conversation is actually for, and you
should treat it exactly as sceptically as week 1 asked you to treat everything else.

---

## What is being assessed

Not whether you know an architecture. The interviewer knows you can look one up.

They are answering one question: **can this person be left alone with an ambiguous
problem?** Everything in the conversation is evidence for or against that, which is why a
confident wrong answer scores worse than an uncertain right one, and why "I don't know,
here is how I would find out" is a strong answer rather than a weak one.

Your three documents are evidence, and the way you talk about them is more evidence.

---

## Three lengths

You need each of them ready, and the mistake is having only the long one.

### Ninety seconds

The problem, the interesting constraint, and what you decided. No components.

> "A team chat system — a million concurrent connections, and clients that are offline
> about sixty per cent of the time. The interesting constraint was that the largest channel
> had eighty thousand members while the median had twelve, so one delivery strategy was
> going to be wrong for one of them. I pushed to small channels and made large ones pull,
> with the threshold set by a delivery budget rather than a round number."

That is the whole system, and it invites the next question. Compare it with a ninety-second
list of components, which invites nothing.

### Five minutes

The above, plus the two decisions you are proudest of and **one you got wrong**.

The last part is not modesty. A person who cannot name a mistake in their own design has
either not reviewed it or is not telling you the truth, and both are worse than the
mistake.

### Twenty minutes

The document, walked through, with the interviewer interrupting. Which is what Friday is.

---

## Talk about the decision, not the diagram

The most common failure in a project deep-dive is describing a system's *shape* rather than
its *choices*.

| Weak | Strong |
|---|---|
| "There's a gateway tier, then channel servers, then storage" | "Connections and message routing scale on different axes, so they are separate tiers — one sized by users, one by activity" |
| "We used a queue" | "The client shouldn't wait for the email, and the spike is twenty times the average, so a queue — bounded, dropping oldest, because the alert is worthless once it's stale" |
| "It's eventually consistent" | "The author sees their own writes; everyone else within two seconds. There is no ordering guarantee between different users' writes and the product doesn't need one" |

The pattern: **every sentence contains a reason.** That is the difference between having
built something and having been present while it was built, and interviewers hear it
immediately.

---

## The questions you will be asked about your own design

Have answers. These come up almost every time:

1. *"What would you do differently?"* — a specific thing, with why you did not do it then
2. *"What was the hardest part?"* — should be a decision, not a technology
3. *"What broke, or what would break?"* — if nothing has, say what would and at what scale
4. *"Why not [obvious alternative]?"* — this is your pass 5, and you have written it down
5. *"How did you know the numbers?"* — given, estimated, or invented. Say which

Question 5 is the one that separates the top answers. "I assumed 5x peak because I could
not measure it, and at 20x the queue tier triples" is a better answer than any real number,
because it shows the shape of your uncertainty.

---

## Today

Write the ninety-second version of all three projects. Out loud, timed, recorded.

They will be bad. Everyone's first one is a list of components. Do each three times and
watch the components fall out and the reasons arrive — that transition is the whole
exercise, and it does not happen by thinking about it.

---

> **Sources for this article**
> **None, and deliberately so.** Interview advice is almost entirely Tier 3 and 4, and the
> honest position is that this is our argument rather than a finding. The one thing it
> rests on is the course's own premise: that a design is a set of decisions, so a
> conversation about a design should be too.
