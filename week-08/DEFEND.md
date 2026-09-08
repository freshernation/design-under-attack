# Week 8 — Friday defence (Project 2)

**Thirty minutes, not twenty.** This is a project defence, and the document is longer.

Four phases: explain, mutate, break, and — new this week — the diff.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-08/milestone`, and check:

- Is the **largest-channel strategy** explicit, with a threshold and what fraction sits on
  each side? The new rule requires it.
- Is there a **reconnect arithmetic** and a rolling-deploy duration, as numbers?
- Does the document say a message is durable **before** it is delivered? Everything else
  depends on that ordering.
- Is `DIFF.md` written, and does it answer the third question rather than only the first
  two?

---

## Phase 1 — Explain (8 min)

1. *"One message in the 80,000-member channel. Walk me through what happens."*
2. *"A user's phone has been off for a week. They open the app. What happens, and what did
   the system store for them while they were gone?"* — the answer should be "nothing
   specific to them", and knowing why that is a *good* answer is the week.
3. *"Your gateway tier is 30 hosts. One restarts. Give me the numbers."*
4. *"p99 under 500 ms across three regions 150 ms apart. Where are messages durable, and
   how much margin does that leave?"*
5. *"Which claim here is sourced and which is you?"*

| 5 | 3 | 1 |
|---|---|---|
| Two strategies with a stated boundary; durability before delivery, unprompted | Describes the design accurately, needs prompting on the boundary | One uniform delivery strategy |

## Phase 2 — Mutate (8 min)

### A — *"Every channel now has read receipts, shown per message."*

The best mutation. Receipts are **more traffic than the messages** — N delivered and N
read per message — and in the 80,000-member channel it is catastrophic. Looking for: they
coarsen it to a read position rather than per-message, and they notice that a product
decision about a small grey tick is a capacity decision.

### B — *"A region goes offline. Users there cannot reach anything."*

Looking for: what happens to the other two regions, whether messages written in the lost
region are lost, and — the interesting bit — what happens when it comes back and its
clients all reconnect and catch up simultaneously.

### C — *"Message editing and deletion."*

Looking for: they recognise that a pushed message is a copy on a client, so an edit is an
invalidation problem — week 6, in a chat product. And that anything already fanned out to
80,000 clients cannot be recalled, only superseded.

| 5 | 3 | 1 |
|---|---|---|
| Connects the mutation to an earlier week unprompted | Gets there messily | Adds a component |

## Phase 3 — Break (8 min)

| Attack | Watching for |
|---|---|
| *"Your whole gateway tier restarts at once."* | The storm arithmetic, and whether the deploy strategy makes it impossible rather than survivable |
| *"A client is connected but not reading. Its outbound buffer fills."* | A bound and a policy. Unbounded here is a memory leak with a customer attached |
| *"Everyone arrives at 9am."* | Presence, not messages. The broadcast multiplication is the expensive thing |
| *"Two people post in the same channel in the same millisecond."* | A single sequence per channel, and what the sender's own client shows before the server has answered |
| *"The channel server owning #general dies."* | Consistent hashing, who takes over, and what happens to in-flight messages |

## Phase 4 — The diff (6 min)

Take their `DIFF.md`.

1. *"What did Slack do that you did not, and what do you think they knew that you did
   not?"*
2. *"What did you do that their write-up does not mention? Is that because it is wrong, or
   because a blog post is not a design document?"*
3. *"What does their post not tell you that you would need before building this?"*

The third question is the one that matters, and it is the whole source doctrine arriving
in a real situation. A student who can list four genuine unknowns from a good Tier 1
source has learned the thing this course is actually for.

| 5 | 3 | 1 |
|---|---|---|
| Names real unknowns and distinguishes them from disagreements | Lists differences | Treats the post as the right answer and their design as wrong |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"You have now seen two-population problems four times. Name them."* — week 4's whale,
   week 6's tail, week 7's hot campaign, this week's channels.
2. *"Which week's material did you reach for most in this design?"* — usually 2 and 7,
   which surprises people who expected it to be 8.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 9 is failure and operations: SLOs, retries, circuit breakers, bulkheads, load
shedding.

The sentence for Monday: **everything so far assumed the failure was somewhere else. Next
week your own service is the one that is failing, and the question is what it does about
it.** Week 9 revisits every design they have written and asks how it degrades.

The check: does their Project 2 `Break` table have a row for its own gateway tier being
overloaded, as opposed to a dependency failing? Most do not, and that gap is exactly what
week 9 fills.
