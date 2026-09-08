# Milestone — A specialised design

> Pick one path. Seven passes, a design document, and an honest answer to the question
> this week keeps asking: **is the specialised mechanism worth it?**

| File | What |
|---|---|
| `DESIGN.md` | Your design document, for one of the five briefs below |
| `tradeoff.py` | The break-even arithmetic — when a specialised mechanism pays for itself |

Must pass `pytest week-10/milestone` and `python3 tools/check_sources.py`.

---

## Pick one

Each brief has a general answer that almost works, and a specialised mechanism that costs
something. Your document has to price both.

### 1 — Dispatch (geospatial)

Match riders to drivers in a city. 400,000 drivers reporting position every 4 seconds,
80,000 requests a minute at peak, p99 under 300 ms for a candidate list. Density varies by
a factor of a thousand between the centre and the edge of the service area.

**Twist:** drivers in dense areas must not be starved by drivers in sparse ones — the
matching must be fair across the region, not just fast.

### 2 — A collaborative editor

Documents up to 200,000 characters, up to 30 simultaneous editors, and **clients that may
be offline for a week** and must merge cleanly on return. Stored documents are read far
more often than they are edited.

**Twist:** the product also needs full-text search over document contents, which the
storage format has to support.

### 3 — A matching engine

A venue for a single asset class. 200,000 orders a second at peak, p99 under 100
microseconds from sequencer to fill, and **every trade must be reproducible from the log
for seven years.**

**Twist:** the venue operates in two datacentres for disaster recovery, and a failover
must not produce a different set of fills.

### 4 — An inference service

Serve one model behind an API. 2,000 requests a second at peak, generations from 20 to
4,000 tokens, p99 time-to-first-token under 800 ms and inter-token latency under 60 ms.

**Twist:** 5% of traffic is a batch workload with no latency requirement at all, and it
must not delay the interactive traffic — but it must also not leave hardware idle.

### 5 — A federated social service (reading-only path)

An app view over a federated protocol: consume the network's event stream, build a
searchable index and personalised feeds for 2 million users, and stay correct when servers
you do not operate go away, come back, or serve you invalid data.

**Twist:** you must be able to rebuild your entire index from the network after a
catastrophic loss, and say how long that takes.

There is no lab for path 5, which is a stated limitation rather than an oversight — the
interesting parts are protocol design and trust. The compensating requirement is that
**every claim about protocol behaviour must cite the specification**, which for once is
entirely possible.

---

## The question every path has to answer

> **What is the expensive thing here, and what is the design doing to avoid spending it?**

Answer that and most of the architecture explains itself. It is also the question to ask
when you meet a domain you have never seen, which is the real reason this week exists.

And then the harder one, which `tradeoff.py` is for:

> **Would a general mechanism have been good enough?**

A specialised mechanism has a fixed cost — to build, to operate, to hire for, to explain
to the next engineer. It pays for itself above some volume and not below it. **A design
that adopts one without computing that volume is guessing**, and week 10's biggest risk is
students over-building because the specialised answer is more interesting.

---

## `DESIGN.md`

The week-1 template. Four to six pages.

Your **Size** section must include:

- the expensive resource, named, with its capacity and current demand
- `binding_constraint` across at least three resources — the answer is often not the one
  the brief emphasises
- `headroom_months` at a stated growth rate. *When* you need the specialised mechanism is
  as much a design output as *whether*
- the specialised mechanism's fixed cost, and the break-even volume

Your **Decide** section must contain the specialisation decision itself, with the general
alternative you rejected, why it fails, and at what scale it would have been sufficient.

Your **Break** table needs a row for **the specialised mechanism itself failing** — a cell
index that is stale, a CRDT document that has grown past its memory budget, a sequencer
that is down, an accelerator that is unavailable, a relay that is feeding you rubbish.

---

## The five questions to have answers to

1. What is the binding constraint, and what is second? What changes when they swap?
2. At what volume would the general mechanism have been sufficient? How far are you from
   it?
3. How long is your headroom at current growth, in months?
4. Your specialised mechanism is unavailable for an hour. What does the product do?
5. What did you have to leave out because it did not fit the specialised model?

Question 5 is the one that separates a design from an enthusiasm. Every specialised
mechanism makes something else awkward — a cell index makes non-spatial queries hard, a
CRDT makes the document large, a single-threaded matcher caps throughput at one core, a
token-based capacity plan makes request-based SLOs meaningless.

---

## Before you submit

```bash
pytest week-10/milestone -v
python3 tools/check_sources.py
```

Then run `ai/librarian.md` on your chosen domain — this is the week where the source
tiering matters most, because four of the five paths have thin public records and the
fifth has an unusually good one.
