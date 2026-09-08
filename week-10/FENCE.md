# Week 10 — Concept fence

## Allowed

**Everything from weeks 1–9**, plus:

- **Geospatial** — cell systems, resolution choice, neighbour rings, the exact-distance
  filter, movement churn
- **Convergent data types** — operational transformation, G-counters, PN-counters,
  two-phase sets, LWW registers with causal clocks, sequence CRDTs
- **Deterministic processing** — sequencers, replayable input logs, single-threaded cores,
  price-time priority
- **Inference serving** — static and continuous batching, capacity in tokens, the two
  latency objectives, admission by token count
- **Media economics** — egress cost, edge placement, encode-once
- **Federated protocols** — self-verifying records, relays and app views, aggregation as a
  separate role

## Not yet — and not at all

Nothing is withheld for a later week; week 11 is a project and week 12 is the interview.

What remains out of scope is everything in `CUT_LIST.md`, and it is worth rereading now
that you can see what it would have displaced.

---

## The rule

**Every specialised mechanism states the volume at which a general one would have done.**

Not "we use a cell index" — this:

> A cell index, because a distance calculation over 400,000 positions per query exceeds
> the latency budget above about 40,000 rows. **Below that a table scan is sufficient and
> we would not build this.** We are at 400,000 and growing 8% a month.

The mechanism, the threshold, the honest admission that below it you would not bother, and
where you actually are. A design that cannot produce that threshold has adopted a
mechanism rather than chosen one.
