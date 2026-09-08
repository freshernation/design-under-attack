# Decentralised protocols

*Week 10 · Day 4 · optional reading, about 20 minutes*

> A fifth specialisation, offered as reading rather than a lab. By the end of it you can
> say what changes when you cannot assume one operator.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**AT Protocol — overview**](https://atproto.com/guides/overview) | 1 | The specification, by the people building it |
| [**Bluesky — federation architecture**](https://docs.bsky.app/docs/advanced-guides/federation-architecture) | 1 | The pieces and what each does: personal data servers, relays, app views |
| [**Bluesky — the firehose**](https://docs.bsky.app/docs/advanced-guides/firehose) | 1 | The aggregation stream, and why it exists |
| [**Kleppmann — Bluesky and the AT Protocol**](https://bsky.social/about/bluesky-and-the-at-protocol-usable-decentralized-social-media-martin-kleppmann.pdf) | 1 | A paper co-authored with the protocol's designers |

This is one of the best-documented systems in the course. If you want to practise reading
a real architecture from primary sources, it is the place to do it — everything is
specified, in public, by the people who built it.

---

## What changes

Every design so far assumed one operator: you choose the partitioning, you deploy the
schema change, you decide the consistency model. Remove that and three things move.

**Identity stops being a row in your database.** A user must be able to move between
servers and remain the same person, which means identity is a resolvable name plus a key
rather than a primary key you issued. Everything that referenced them must keep working
after they move.

**Aggregation becomes a separate role.** If anybody can run a server, then producing a
global view — search, a feed, a follower count — requires reading from all of them.
Bluesky's answer is explicit: personal data servers hold user data, **relays** aggregate
their event streams into one, and **app views** build the products on top. That is a
deliberate split of "storing your data" from "computing over everybody's".

**Moderation becomes composable, and it is the hard part.** With one operator there is one
policy. With many, a labelling service publishes opinions and clients choose which to
apply. The interesting problem is social rather than technical, and the architecture's job
is to make several answers possible rather than to pick one.

---

## The systems shape

Underneath, it is machinery you already have:

| Piece | What you know it as |
|---|---|
| Signed, append-only per-user repositories | week 3's log, with cryptographic verification |
| The firehose | week 7's event stream, published rather than internal |
| Relays | consumers building a materialised view |
| App views | week 8's fan-out and read paths |

**The novelty is in the trust boundaries, not the mechanisms.** Because a server you do not
control produced the data, every record is signed and independently verifiable — you accept
data from strangers and can still prove it came from who it claims.

That is the transferable idea, and it applies far beyond social networks: **when you cannot
trust the source, make the data self-verifying and the aggregation stateless.**

---

## What it costs

- **Aggregation is expensive.** Somebody must consume the whole network's events to produce
  a global view. That is a large fixed cost with no obvious payer, and it is a real open
  question for these systems rather than a solved one.
- **Deletion is hard.** Data that has been published and independently aggregated cannot be
  reliably recalled — an issue with legal weight, not only an inconvenience.
- **Schema evolution needs agreement.** You cannot deploy a migration across servers you do
  not operate. The protocol's answer is versioned, extensible record types, and it is the
  same problem week 7 raised about change data capture, at a larger scale.

---

## If you take this path in the milestone

The brief is in `week-10/milestone/README.md`. There is no lab for it, and that is a
deliberate limitation rather than an oversight: the interesting parts are protocol design
and trust, and a small Python exercise would trivialise them. The compensating requirement
is that your design document must cite the specification for every claim about how the
protocol behaves — which, for once, is entirely possible.

---

> **Sources for this article**
> [atproto.com](https://atproto.com/guides/overview),
> [docs.bsky.app](https://docs.bsky.app/docs/advanced-guides/federation-architecture) and
> [the firehose guide](https://docs.bsky.app/docs/advanced-guides/firehose) — **Tier 1**,
> specification and operator documentation ·
> [Kleppmann et al.](https://bsky.social/about/bluesky-and-the-at-protocol-usable-decentralized-social-media-martin-kleppmann.pdf)
> — **Tier 1**, co-authored with the designers.
> The "what it costs" list is ours — **Tier 3** — and the aggregation-economics point is an
> open question rather than a criticism.
