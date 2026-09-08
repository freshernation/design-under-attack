# Week 8 — Realtime and fan-out

> **Destination**
> Deliver something to a million connected people, survive restarting the tier that
> holds them, and design so that a client which was never there loses nothing.

This is the keystone week of the second half. Friday's milestone is **Project 2**, and it
is the first brief where the hard part is choosing among eight mechanisms you already
have rather than learning a ninth.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Choose a transport with arithmetic, and size a connection tier |
| Tue | `day-2/` | Compute fan-out three ways and explain why real systems use two |
| Wed | `day-3/` | Size a presence system, and make delivery an optimisation |
| Thu | `day-4/` | Split the tiers, and survive a reconnect storm |
| Fri | `milestone/` | **Project 2** — ship the chat system, then defend it |

---

## The one idea

**When the distribution has two populations in it, the design needs two answers.**

The median channel has twelve members and the largest has eighty thousand. Most accounts
have fifty followers and a few have two hundred million. One strategy will be wrong for
one of them, and the answer is not to find a cleverer single strategy — it is to have two
and a rule for choosing.

You have now seen this four times: week 4's whale, week 6's long tail, week 7's hot
campaign, and this. It is the most transferable pattern in the course.

---

## The second idea

**Store the message; deliver it as an optimisation.**

Once delivery is a fast path over durable storage rather than the mechanism itself, an
offline client needs no queue, a duplicate push is harmless, a missed push is invisible,
and a deploy that drops a million connections risks nothing. A great deal of engineering
disappears from one inversion.

---

## Project 2

A team chat system: 1.2 million concurrent connections, an 80,000-member channel, clients
that are absent 60% of the time, and daily deploys. Spec in `milestone/README.md`.

Budget two days. And note the third deliverable — after you finish, you read Slack's own
account and write down what they did differently. **Reading it first would rob you of the
exercise; reading it afterwards is where most of the learning is.**

---

## What this week is not about

WebSocket libraries, or any particular realtime framework. The transport is the least
interesting decision in the week and it takes one paragraph.

What takes the rest of the week is: where the work happens, what a connection costs, what
happens when they all come back at once, and how a product survives its own users being
absent most of the time.
