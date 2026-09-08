# Week 1 — Concept fence

## Allowed

- **The seven passes**: interrogate, size, contract, path, decide, break, evolve
- **Envelope vocabulary**: availability and nines, error budgets, latency percentiles
  (p50/p95/p99/p99.9), durability, read-your-writes, freshness/staleness, retention, cost
- **Estimation**: DAU → QPS, peak factors, record sizing, storage with retention and
  replication, bandwidth, working set, fan-out
- **Latency**: the ladder from cache to cross-ocean, latency budgets across hops, the
  speed of light as a constraint, timeouts as budget
- **Sources**: the four tiers, the two-click test, publication and retrieval dates, the
  known/inferred/unknown ledger
- **Components, named only in the plainest way**: a client, a server, a database, a
  cache, a queue. You may say "a cache". You may not yet say why it is Redis

## Not yet

Consistent hashing · replication protocols and quorums · Raft, Paxos, consensus of any
kind · CAP and PACELC · transaction isolation levels · LSM trees and B-trees ·
partitioning and resharding · CDNs · message brokers by name · WebSockets and long
polling · circuit breakers, bulkheads, load shedding · CRDTs and operational
transformation · geospatial indexing · anything with a vendor's name on it

---

## The rule that matters most this week

**You may not name a technology in a design document.**

Not Redis, not Kafka, not Postgres, not S3, not Cassandra. Write what the component must
*do* — "a store that can return one record by key in under a millisecond", "a durable
buffer that lets the writer finish before the work does".

This will feel like an artificial handicap for about two days. It is the single most
effective exercise in the course, for a reason worth understanding: naming a technology
ends thinking. The moment you write "Redis" you stop asking what you need, because the
noun has quietly answered a question you never asked. Every requirement it does not
satisfy becomes invisible.

From week 2 you may name things — and by then you will notice that you do it later, and
with reasons attached.

## The other rule

**No design document without numbers in it.** A document that could describe a system
with a thousand users and one with a billion has not engaged with the problem. If you
have not sized it, you are not designing, you are decorating.
