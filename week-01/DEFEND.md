# Week 1 — Friday defence

Twenty minutes on the milestone design, in three phases, then a retro. The student has
their document open; you have this page.

The bar this week is deliberately low on sophistication and high on honesty. You are
finding out whether they derived their numbers or borrowed them.

---

## Before they arrive

Read their `milestone/DESIGN.md` and their `estimate.py` output. Pick, in advance:

- the number you will ask them to derive live (choose the most load-bearing one)
- the mutation you will use in phase 2
- the two weakest points for phase 3

Also check: **does the document name any technology?** The fence forbids it this week.
If it does, that is the first question, and the answer is usually "I read someone's
answer" — which is worth knowing on day five rather than in week six.

---

## Phase 1 — Explain (6 min)

1. *"Walk me through what happens when someone clicks a short link. Every hop."* —
   looking for an ordered list, not a picture. A strong answer names four or five hops
   and knows which is slowest.
2. *"Where did the 29,000 reads per second come from?"* — make them derive it live, out
   loud, from the brief. **This is the question of the week.** A student who cannot
   rebuild their own number in sixty seconds did not compute it.
3. *"What are you not building, and why is that safe?"* — non-goals should be written
   down. If they improvise them now, say so and move on.
4. *"Which of your requirements is measurable, and which is a wish?"* — they should be
   able to point at one of their own and call it vague.
5. *"Which claim in here is sourced, and which is you guessing?"* — after Thursday, this
   should be answerable instantly.

| 5 | 3 | 1 |
|---|---|---|
| Derives any number on demand; separates sourced from inferred without prompting | Describes the flow accurately; needs a nudge to derive | Cannot rebuild their own arithmetic |

## Phase 2 — Mutate (7 min)

Pick **one**. Ask what parts of the document change *before* they say anything about how.

### A — *"One link goes viral. Ninety percent of all reads are for a single short code."*

The best mutation this week. Their per-second average is now irrelevant and the whole
system is one row. Looking for: they notice the average has stopped describing anything,
and they reach for keeping that one item close rather than adding machines. A student who
says "add more database replicas" has not understood that every replica has the same
problem.

### B — *"Links must now expire after 30 days."*

Looking for: storage stops growing without bound, which changes the five-year number
they computed — and something must now do the deleting, which is a new component and a
new failure mode they had not considered.

### C — *"It must work for users in Australia at p99 under 100 ms."*

Looking for: they check it against the speed of light before designing. Sydney to a US
region is ~150 ms round trip, so the requirement is impossible in one region, full stop.
The correct answer starts "that requirement can't be met from a single region, so
either the target moves or the data does."

| 5 | 3 | 1 |
|---|---|---|
| Names the affected sections before designing; checks the mutation against their numbers | Gets there messily | Starts adding components immediately |

## Phase 3 — Break (7 min)

Two attacks, pressed until they defend or concede. Do not accept *"I would monitor it"*
as an answer to anything.

| Attack | What you are watching for |
|---|---|
| *"Your cache is empty — every read is a miss. What happens?"* | Do they know their read path is sized for hits? The cold-cache number is usually 100x the warm one and nobody computes it |
| *"Two people create a short link at the same millisecond and your generator produces the same code. What happens?"* | Whether they thought about collisions at all. Many will not have |
| *"The store that holds the mapping is up but taking two seconds per read."* | Slow is not dead. Looking for: timeouts, and an answer about what the user sees |
| *"Someone points a scraper at you and requests a million codes that do not exist."* | Every miss goes to the database. This is the cheapest way to break their design and most will not have considered it |

| 5 | 3 | 1 |
|---|---|---|
| Reasons from their own numbers | Finds it with prompting | Answers every attack by adding a component |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"Which pass did you skip?"* — everyone skips one. It is nearly always **size**, and
   naming it now is what stops it happening in week 4.
2. *"What did you write down that you could not have defended?"* — honesty is the skill
   being graded here, not correctness.
3. *"Open Monday's first design next to Friday's. What is different?"* — they should be
   able to name three things. If they cannot, the week did not land and week 2 needs
   adjusting.
4. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 2 is Little's Law and queueing — utilisation, latency, and why a system at 90%
utilisation is not 90% fine. It only works if this week's arithmetic is genuinely
automatic.

The specific thing to check for: a student who computed their numbers **once, in a file,
and cannot rebuild them by hand** will struggle badly in week 2, where the numbers move
during the conversation. If phase 1 question 2 went poorly, spend Monday's live hour on
mental arithmetic and not on queueing.

The other signal to watch: a student who reached for the published URL-shortener answers
this week will do it again in week 8 with chat systems, where it does far more damage.
Address it now, plainly, as a matter of what they are here for rather than of rules.
