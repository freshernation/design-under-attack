# The source doctrine

Every claim in this course carries a source, a date, and a tier. This page says how,
and why the rule is stricter here than in most technical writing.

---

## Why this exists

Ask ten interview-prep sites how WhatsApp handled two million connections per server
and you will get ten confident answers, most of them tracing back to one 2012
conference talk that none of them cite. The number may even be right. But a student who
repeats it has learned a fact, not a skill — and when they are asked about a system
nobody has blogged about, they have nothing.

**Source triage is the skill.** It is the difference between "Slack Engineering, 2017,
named author, describing a system they operate" and "an interview site asserting a
number with no citation". You cannot design honestly without it, and no amount of
architecture knowledge substitutes.

So sourcing is not a footnote in this course. It is graded from week 1, it has its own
AI role (`ai/librarian.md`), and it is machine-checked.

---

## The four tiers

| Tier | Meaning | Examples |
|---|---|---|
| **1 — Primary** | The people who build or run the system, on the record | [Slack Engineering](https://slack.engineering/real-time-messaging/), [Uber Blog](https://www.uber.com/blog/deepeta-how-uber-predicts-arrival-times/), [AT Protocol specs](https://atproto.com), a conference talk by a named engineer |
| **2 — Foundational** | The paper or official documentation the system is built on | Raft, Dynamo, Bigtable, Jupiter, [Kafka docs](https://kafka.apache.org/documentation/), [Redis docs](https://redis.io/docs/latest/) |
| **3 — Secondary** | Interpretation by people who did not build it | newsletters, InfoQ summaries, ByteByteGo, HighScalability, this course |
| **4 — Folklore** | Widely repeated, no traceable origin | most numbers in most interview prep |

Tier 3 is not forbidden — it is often the clearest explanation available, and a good
secondary source is more useful to a beginner than a dense paper. It is simply never
**load-bearing**.

---

## The four rules

**1. No claim rests on Tier 3 alone.**
If the only support for a number is a newsletter, the number does not go in as fact. It
goes in the "what we are inferring" box, or it goes out.

**2. Everything carries a date.**
A 2016 post describes 2016. Architectures move. Every source records `published` and
`retrieved`, and every case study ends with **Where this is now** — what has changed
since, or an honest "no public update since".

**3. Separate what is published from what is inferred.**
Every case study carries this box:

> **Known** — stated in the source, with the source id
> **Inferred** — our reasoning from what is stated, marked as ours
> **Derived** — follows from arithmetic, and cites nothing because there is nothing
> to cite
> **Unknown** — the questions the sources do not answer

Most write-ups quietly merge these. The last row is usually the most interesting one, and
it is always the one that gets cut elsewhere.

**Derived** was added while writing week 6, because the doctrine did not have a home for
"this is true because of multiplication". It is not inferred from a source and it is not
unknown — it is a consequence, and the honest thing is to say so and show the arithmetic
rather than hunt for a citation that does not exist. A course that will not amend its own
rules when they turn out to be incomplete is not applying them seriously.

**4. When there is no primary source, say so in the article.**

And when a whole topic has none — week 12's interview material is the case — the source
file says so in a `no_sources_reason` field and carries only `unknown` and `derived`
claims. You cannot infer from nothing, so those are the only two kinds available. An empty
`sources:` list with no reason is rejected, because it is indistinguishable from an
unfinished file.
Some systems have none. The URL shortener has no canonical write-up because nobody
famous has published one; "design a URL shortener" is an interview convention, not a
documented architecture. Articles about such systems open by saying that. A student who
knows *which* of their knowledge is unsourced is ahead of one who is confidently wrong.

---

## The machinery

Each case study has a source file next to its articles:

```yaml
# content/sources/slack-realtime.yml
system: Slack real-time messaging
sources:
  - id: slack-rtm-2018
    title: Real-time Messaging
    url: https://slack.engineering/real-time-messaging/
    publisher: Slack Engineering
    tier: 1
    published: 2018-01-11
    retrieved: 2026-09-02
    note: Channel Servers, Gateway Servers, consistent hashing of channels

claims:
  - id: cs-consistent-hashing
    text: Channel Servers are stateful and mapped to channels by consistent hashing
    kind: known
    sources: [slack-rtm-2018]
```

`tools/check_sources.py` fails the build when:

- a source has no `tier`, `published` or `retrieved` date
- a claim has no `sources`
- a `known` claim is supported only by Tier 3 or 4
- an `inferred` claim cites nothing (only `derived` and `unknown` may)
- a claim references a source id that does not exist
- `--check-urls` is passed and a URL does not resolve

`tools/check_links.py` fails when a relative link inside `content/` does not resolve.

Run both:

```bash
python3 tools/check_sources.py
python3 tools/check_links.py
```

---

## A note on retrieval

Some publishers block automated fetching — `redditinc.com` is one, so Reddit's
engineering posts are cited but retrieved by hand. That is fine. Record the
`retrieved` date you actually read it on, and mark it `manual: true`. The rule is
honesty about provenance, not automation for its own sake.
