# Course content

The reading for every day. One article per `Read first` item, each opening with the
**primary sources** for its topic — and, where none exists, saying so plainly.

Every day README links here; these articles link on to each other. They are written to
be publishable as standalone pages: the diagrams are self-contained SVG files in each
day's `img/` folder, and every relative link resolves within this tree
(`python3 tools/check_links.py`).

| | |
|---|---|
| **Articles** | 64 |
| **Diagrams** | 47 |
| **Weeks covered** | 1–12 |

---

## What "sources first" means here

The Python course anchors on docs.python.org, and that is easy: there is one authority
and it is obviously correct.

**System design has no specification.** Nobody owns it, and the loudest sources are all
interpretation. So each article opens with a source table that is *tiered and dated*,
and each one ends by saying which of its own claims are Tier 1 and which are this
course's opinion. See [`../SOURCES.md`](../SOURCES.md) for the doctrine, and
[`sources/`](sources/) for the claims ledgers.

Where an article is our own framing — the seven passes, the six dials, the reading
method — it says so. A course that will not apply its own rule to itself is not worth
much.

---

## Week 1 — A design is a set of decisions

**Day 1** · [What a design answer actually is](week-01/day-1/what-a-design-answer-is.md) · [The seven passes](week-01/day-1/the-seven-passes.md)

**Day 2** · [Interrogating the requirement](week-01/day-2/interrogating-the-requirement.md) · [The non-functional envelope](week-01/day-2/the-non-functional-envelope.md)

**Day 3** · [Back of the envelope](week-01/day-3/back-of-the-envelope.md) · [Latency numbers, and spending them](week-01/day-3/latency-numbers-and-budgets.md)

**Day 4** · [Source tiers and the claims ledger](week-01/day-4/source-tiers-and-the-claims-ledger.md) · [Reading an engineering blog post](week-01/day-4/reading-an-engineering-blog.md)

## Week 2 — Queues, utilisation and latency

**Day 1** · [Little's Law](week-02/day-1/littles-law.md) · [Concurrency, pools, and where the queue actually is](week-02/day-1/concurrency-and-pools.md)

**Day 2** · [Utilisation, and the knee](week-02/day-2/utilisation-and-the-knee.md) · [Variability, and why the average lies twice](week-02/day-2/variability.md)

**Day 3** · [Queues, and what to do when they fill](week-02/day-3/queues-and-backpressure.md)

**Day 4** · [Rate limiting](week-02/day-4/rate-limiting.md)

## Week 3 — Storage and the data model

**Day 1** · [Access patterns first](week-03/day-1/access-patterns-first.md) · [Indexes](week-03/day-1/indexes.md)

**Day 2** · [B-trees and LSM trees](week-03/day-2/b-trees-and-lsm-trees.md) · [Amplification, and the three-way trade](week-03/day-2/amplification.md)

**Day 3** · [Inside an LSM store](week-03/day-3/inside-an-lsm.md)

**Day 4** · [Write-ahead logs, and what durability costs](week-03/day-4/write-ahead-logs-and-durability.md)

## Week 4 — Partitioning and routing

**Day 1** · [Why partition, and when not to](week-04/day-1/why-partition.md) · [Choosing a partition key](week-04/day-1/choosing-a-partition-key.md)

**Day 2** · [Consistent hashing](week-04/day-2/consistent-hashing.md) · [Range partitioning against hash partitioning](week-04/day-2/range-versus-hash.md)

**Day 3** · [Hot keys](week-04/day-3/hot-keys.md)

**Day 4** · [Ids, and finding the right machine](week-04/day-4/ids-and-routing.md)

## Week 5 — Replication and consistency

**Day 1** · [Why copies, and what they cost](week-05/day-1/why-copies.md) · [Leaders, followers, and failover](week-05/day-1/leaders-and-followers.md)

**Day 2** · [Quorums](week-05/day-2/quorums.md) · [When copies disagree](week-05/day-2/conflicts.md)

**Day 3** · [Consensus, and enough Raft to argue about it](week-05/day-3/consensus-and-raft.md)

**Day 4** · [Consistency models, and the two you actually need](week-05/day-4/consistency-models.md)

## Week 6 — Caching and the read path

**Day 1** · [Why caches work, and what they hide](week-06/day-1/why-caches-work.md) · [Where to cache](week-06/day-1/where-to-cache.md)

**Day 2** · [Invalidation](week-06/day-2/invalidation.md)

**Day 3** · [Stampedes, and the misses you can avoid](week-06/day-3/stampedes.md)

**Day 4** · [Bloom filters](week-06/day-4/bloom-filters.md) · [The CDN, and the request you never receive](week-06/day-4/cdn-and-the-edge.md)

## Week 7 — Logs, queues and idempotency

**Day 1** · [The log](week-07/day-1/the-log.md) · [Queues, and the other model](week-07/day-1/queues-and-brokers.md)

**Day 2** · [Delivery guarantees](week-07/day-2/delivery-guarantees.md)

**Day 3** · [Idempotency](week-07/day-3/idempotency.md) · [The dual write problem](week-07/day-3/the-dual-write-problem.md)

**Day 4** · [Ordering, consumers, and rebalancing](week-07/day-4/ordering-and-consumers.md)

## Week 8 — Realtime and fan-out

**Day 1** · [Push against pull](week-08/day-1/push-versus-pull.md) · [Connections at scale](week-08/day-1/connections-at-scale.md)

**Day 2** · [Fan-out](week-08/day-2/fan-out.md)

**Day 3** · [Presence, heartbeats and delivery](week-08/day-3/presence-and-delivery.md)

**Day 4** · [The gateway tier, and the reconnect storm](week-08/day-4/the-gateway-tier.md)

## Week 9 — Failure and operations

**Day 1** · [SLOs, and spending an error budget](week-09/day-1/slos-and-error-budgets.md)

**Day 2** · [Retries, backoff, and jitter](week-09/day-2/retries-and-jitter.md)

**Day 3** · [Circuit breakers and bulkheads](week-09/day-3/circuit-breakers-and-bulkheads.md)

**Day 4** · [Load shedding, and degrading on purpose](week-09/day-4/load-shedding-and-degradation.md)

## Week 10 — The deep track

**Day 1** · [Geospatial: turning "near me" into a key lookup](week-10/day-1/geospatial.md)

**Day 2** · [Collaborative editing: converging without a lock](week-10/day-2/collaborative-editing.md)

**Day 3** · [Matching engines: determinism as a requirement](week-10/day-3/matching-engines.md)

**Day 4** · [Serving models, and serving media](week-10/day-4/serving-models-and-media.md) · [Decentralised protocols](week-10/day-4/decentralised-protocols.md)

## Week 11 — The full design

**Day 1** · [Designing from one line](week-11/day-1/from-a-one-line-brief.md)

**Day 2** · [Writing the document](week-11/day-2/writing-the-document.md)

**Day 3** · [The decision record](week-11/day-3/the-decision-record.md)

> Week 11's three articles are the most opinionated and least sourced in the course, and
> they say so. There is no authority on how to structure a design document.

## Week 12 — The interview is the deliverable

**Day 1** · [The story of a design](week-12/day-1/the-project-story.md)

**Day 2** · [The forty-five minutes](week-12/day-2/the-forty-five-minutes.md)

**Day 3** · [Explaining without drawing](week-12/day-3/explaining-without-drawing.md)

> Week 12 cites **nothing**, and says so. Interview advice is overwhelmingly Tier 3 and 4,
> and presenting ours as anything else would undo twelve weeks of insisting on provenance.

---

## Primary sources used so far

| Source | Tier | Used in |
|---|---|---|
| [Google SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/) | 1 | Days 1, 2 |
| [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/) | 1 | Day 2 |
| [AWS Builders' Library](https://aws.amazon.com/builders-library/) | 1 | Days 1, 2, 3 |
| [Slack Engineering — Real-time Messaging](https://slack.engineering/real-time-messaging/) | 1 | Days 3, 4 |
| [Norvig — approximate timings](https://norvig.com/21-days.html) | 2 | Day 3 |
| [The latency numbers gist](https://gist.github.com/jboner/2841832) | 3 | Week 1 day 3, as a worked example of a Tier 3 source everyone treats as Tier 1 |
| [Google SRE Book — Handling Overload](https://sre.google/sre-book/handling-overload/) | 1 | Week 2, days 2–4 |
| [Google SRE Book — Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) | 1 | Week 2, all week |
| [Dean & Barroso — The Tail at Scale](https://research.google/pubs/the-tail-at-scale/) | 1 | Week 2 day 2 |
| [RFC 6585](https://www.rfc-editor.org/rfc/rfc6585) | 2 | Week 2 day 4 |
| [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) | 1 | Week 3 day 1 |
| [Bigtable](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data/) | 1 | Week 3, days 1–3 |
| [LevelDB implementation notes](https://github.com/google/leveldb/blob/main/doc/impl.md) | 1 | Week 3, days 2–3 |
| [RocksDB wiki](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview) | 1 | Week 3 day 2 |
| [The RUM Conjecture](https://openproceedings.org/2016/conf/edbt/paper-12.pdf) | 2 | Week 3 day 2 |
| [SQLite — Atomic Commit](https://www.sqlite.org/atomiccommit.html) | 2 | Week 3 day 4 |
| [Slicer](https://research.google/pubs/slicer-auto-sharding-for-datacenter-applications/) | 1 | Week 4, days 1–3 |
| [Twitter Snowflake](https://github.com/twitter-archive/snowflake) | 1 | Week 4 day 4 |
| [Discord Engineering](https://discord.com/blog/how-discord-stores-billions-of-messages) | 1 | Week 4 day 3 |
| [Vitess — Sharding](https://vitess.io/docs/reference/features/sharding/) | 2 | Week 4, days 1–4 |
| [Jepsen — consistency models](https://jepsen.io/consistency) | 1 | Week 5, all week |
| [Spanner](https://research.google/pubs/spanner-googles-globally-distributed-database-2/) | 1 | Week 5, days 1 and 4 |
| [Raft](https://raft.github.io/raft.pdf) | 2 | Week 5 day 3 |
| [Kleppmann — distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) | 3 | Week 5 milestone — and a worked example of where our tiers come apart from quality |
| [Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf) | 1 | Week 6, all week |
| [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111) | 2 | Week 6, days 1–4 |
| [Cloudflare — Cache](https://developers.cloudflare.com/cache/) | 1 | Week 6 day 4 |
| [Apache Kafka documentation](https://kafka.apache.org/documentation/#design) | 1 | Week 7, all week |
| [Kreps — The Log](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) | 1 | Week 7 day 1 |
| [Stripe — idempotent requests](https://docs.stripe.com/api/idempotent_requests) | 1 | Week 7 day 3 |
| [Debezium — outbox](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html) | 1 | Week 7 day 3 |
| [Slack — Real-time Messaging](https://slack.engineering/real-time-messaging/) | 1 | Week 1 day 4, and all of week 8 |
| [Discord — scaling Elixir](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users) | 1 | Week 8, days 1, 3 and 4 |
| [Rick Reed — WhatsApp](https://www.erlang-factory.com/upload/presentations/558/efsf2012-whatsapp-scaling.pdf) | 1 | Week 8, days 1 and 3 |
| [AWS Builders' Library](https://aws.amazon.com/builders-library/) | 1 | Weeks 2 and 9, throughout |
| [Google SRE Book and Workbook](https://sre.google/sre-book/) | 1 | Weeks 1, 2 and 9 |
| [AWS — shuffle sharding](https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/) | 1 | Week 9 day 3 |
| [H3](https://h3geo.org/docs/) | 1 | Week 10 day 1 |
| [LMAX Disruptor](https://lmax-exchange.github.io/disruptor/disruptor.html) | 1 | Week 10 day 3 |
| [vLLM / PagedAttention](https://arxiv.org/abs/2309.06180) | 2 | Week 10 day 4 |
| [AT Protocol](https://atproto.com/guides/overview) | 1 | Week 10 day 4 |
