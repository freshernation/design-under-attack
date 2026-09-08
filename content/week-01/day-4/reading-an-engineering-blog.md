# Reading an engineering blog post

*Week 1 · Day 4 · about 30 minutes, plus the reading*

> By the end of this you can read a real architecture post the way an engineer does:
> extracting claims, noticing which are precise, and finding what it declines to say.

---

## Today's primary source

| Source | Tier | Note |
|---|---|---|
| [**Slack Engineering — Real-time Messaging**](https://slack.engineering/real-time-messaging/) | 1 | Sameera Thanugdu, Senior Software Engineer, 11 April 2023. Named author, on Slack's own domain, describing a system her team operates |

**Read the whole thing before continuing.** Twenty minutes. Do not skim it, and do not
read anyone's summary of it — including the one below, which is deliberately incomplete.

That instruction matters more than it looks. The entire skill being taught today is
reading a primary source directly, and it is undermined by reading about the primary
source instead. This is the first Tier 1 document you take apart in this course; the
milestone in week 8 will have you do it to four at once.

---

## Why this post

It is unusually good, which makes it a fair teacher: a named engineer, a recent date,
concrete numbers, and a system large enough to be interesting. It is also honest about
what it leaves out, so you can practise noticing the gaps without the exercise feeling
like an attack on the author.

---

## Pass 1 — the metadata, before the content

Before reading a word of architecture, answer four questions. Ten seconds.

| Question | Here |
|---|---|
| Who wrote it? | A named senior engineer — not a marketing team, not an anonymous "Engineering" byline |
| When? | April 2023 |
| Where published? | slack.engineering — their own domain |
| What are they selling? | Nothing obvious. Engineering-brand and recruiting, which is the usual motive and a mild one |

All four are good, so this is about as reliable as public architecture writing gets.
Compare it with a post that has no author, no date, and a "download our whitepaper"
button at the bottom, and you can see how much the metadata alone tells you.

**The motive question is not cynical.** Vendor engineering blogs are often excellent and
often Tier 1 — but a post explaining why a company's own database solved their problem
is answering a different question than a post explaining what broke. Read both. Weight
them differently.

---

## Pass 2 — extract the claims

Read with a document open beside you and write down every specific statement. Do not
summarise; **quote or paraphrase precisely**, because the precision is the data.

Reading it that way, you should end up with something like this:

**Structural claims** — what exists

- The core services are written in Java: Channel Servers, Gateway Servers, Admin
  Servers, Presence Servers
- Channel Servers are stateful and in-memory, holding some channel history
- Each Channel Server maps to a subset of channels by consistent hashing
- Gateway Servers are deployed across multiple geographic regions; clients connect to
  the nearest edge

**Numeric claims** — with numbers attached

- Messages delivered worldwide in 500 ms
- 16 million channels served per host at peak
- A replacement Channel Server is ready in under 20 seconds
- Peaks around 11am and 2pm, with a dip at lunch
- Traffic spikes at the top of the hour from reminders and calendar events

Your list will differ from mine, and that is fine. What matters is that you produced one
rather than a feeling of having understood the post.

---

## Pass 3 — grade the precision

Now sort what you extracted. Not every claim in a Tier 1 source carries the same weight.

| Precise | Vague |
|---|---|
| "delivered in 500 ms" | "millions of messages every day" |
| "under 20 seconds" | "tens of millions of channels per host" |
| "16 million channels per host" | "hundreds of different types of events" |
| "11am and 2pm" | "different across regions" |

The vague ones are not dishonest — they are what a company is willing to say publicly,
and precision about scale is competitively sensitive. But **a vague claim cannot be
used as an input to arithmetic**, and if you build a capacity estimate on "tens of
millions" you have built it on a range spanning an order of magnitude.

### Look for tension between the numbers

There is a specific thing worth hunting for, and this post rewards it: does the article
give more than one figure for the same quantity?

Read the channel-per-host figures carefully. A precise number appears in one place and a
looser characterisation elsewhere. Both may be true — of different hosts, at different
times, of different things being counted — but **noticing that they need reconciling is
the skill.** Write down which reading you adopted and why.

This is what a claims ledger is for. A summary would have smoothed it into one number
and you would never have known there was a question.

---

## Pass 4 — what it does not say

The most valuable pass, and the one nobody does.

Go through the post asking what an engineer implementing this would still need to know.
Candidates:

- What happens to messages sent during the twenty seconds a Channel Server is being
  replaced?
- Where does channel history live durably? In-memory servers hold "some" history —
  what is behind them, and how does a client fetch what the server no longer has?
- How does a client learn which Channel Server owns its channel, and what happens when
  that mapping changes mid-session?
- Is the 500 ms figure a median, a p99, or a marketing round number? **This one matters
  enormously** and the post does not say — which, after yesterday, you know is the
  difference between two very different systems.

None of these are criticisms of the article. A blog post is not a design document and
was never trying to be. But the gap between "I read how Slack works" and "I know these
four things are unresolved in the public record" is the entire gap between a
memoriser and an engineer.

---

## Pass 5 — the ledger

Write it up in the format from [the previous article](source-tiers-and-the-claims-ledger.md):
known, inferred, unknown, with source ids. That file is today's deliverable and it goes
in `content/sources/slack-realtime.yml`.

Then run:

```bash
python3 tools/check_sources.py
```

It will tell you if you have cited something that does not exist, or stated as known
something you cannot support.

---

## The habit

Four minutes of metadata and claim extraction, on every architecture source you ever
read again. It is not much slower than reading normally, and the difference in what you
retain is dramatic — because you retain *structured* information with provenance
attached, rather than an impression.

An impression cannot be defended on a Friday.

---

> **Sources for this article**
> [Slack Engineering — Real-time Messaging](https://slack.engineering/real-time-messaging/),
> Sameera Thanugdu, 11 April 2023 — **Tier 1**, retrieved 2 September 2026.
> The claims listed above are our extraction and may be incomplete; the instruction to
> read the original first is there for exactly that reason. The five-pass reading method
> is ours — Tier 3.
