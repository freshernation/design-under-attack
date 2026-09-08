# Week 3 — Friday defence

Twenty minutes on the metrics store, three phases, then a retro.

The theme this week: whether the numbers in their document actually constrained the
design, or were computed and then ignored.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-03/milestone`, and check:

- Did they run `retention_bytes` and put the result against the ceiling? A document
  without that number has not engaged with the brief at all.
- Is there a **late points** decision in pass 5, with a rejected alternative?
- Did they state the access pattern before the storage shape? The fence requires it.
- Any product names? Still forbidden.

---

## Phase 1 — Explain (6 min)

1. *"Why does a bucket keep four numbers instead of one?"* — the week's question. A
   strong answer says "because the mean of means is wrong when the counts differ" and
   can give an example. A weak one says "for min and max".
2. *"Walk me through a query for one series over the last hour. Every hop, and which
   tier answers it."*
3. *"You are at 28 TB of a 40 TB ceiling. What is your headroom, in days of growth?"* —
   most will not have converted it into time. Make them do it live.
4. *"A point arrives four minutes late. What happens?"* — they should have a decision,
   not a hope.
5. *"Which claim here is sourced and which is you?"*

| 5 | 3 | 1 |
|---|---|---|
| Explains count-and-sum from first principles; knows the ceiling headroom in days | Describes the design accurately | Cannot say why an average of averages is wrong |

## Phase 2 — Mutate (7 min)

### A — *"Raw retention goes from 24 hours to 48."*

The mutation this brief was built for. It is one line of policy and it takes them from
28 TB to 45 TB — over a hard ceiling. Looking for: they go to the arithmetic before
saying anything, then propose a trade (shorter minute tier, coarser raw, fewer replicas,
compression) rather than "we'd need more disk".

The best answers price two options against each other.

### B — *"Points may now arrive up to 24 hours late, not 5 minutes."*

Looking for: they see this attacks the immutability of already-written buckets. Five
minutes can be held in memory; a day cannot. The honest answers are rewriting buckets,
keeping a late-arrival side path, or refusing — and each has a price they should name.

### C — *"Dashboards now query 50,000 series at once, not 1,000."*

Looking for: fan-out, from week 2. Fifty thousand parallel reads means the query's
latency is the p99.99 of a single read, and the tail is now the median. A student who
connects this to *The Tail at Scale* unprompted has had a good three weeks.

| 5 | 3 | 1 |
|---|---|---|
| Reaches for their own numbers first, then prices two options | Gets there messily | Proposes more hardware |

## Phase 3 — Break (7 min)

| Attack | Watching for |
|---|---|
| *"Compaction is running while a dashboard loads. What does the user see?"* | The week-2 connection. Service-time spike, variability, queueing. "It's a background process" is not an answer |
| *"A service starts emitting ten times its usual number of series after a deploy."* | Cardinality. Series count drives storage and memory far harder than point rate; their ceiling arithmetic just broke |
| *"Your process is killed between accepting a point and writing it out."* | The WAL, and whether they said what "accepted" means |
| *"Someone deletes a month of one series to save space."* | Tombstones. Space is not reclaimed until compaction, and the scan over that range is now slower, not faster |
| *"The 1% dashboard query and the 95% incident query hit the same machines."* | Isolation. A dashboard refresh should not slow down an incident investigation, and nothing in most designs stops it |

| 5 | 3 | 1 |
|---|---|---|
| Reasons from their own numbers and last week's curve | Finds it with prompting | Adds a component to every attack |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"Which is bigger: dropping raw retention by a day, or halving the resolution of the
   minute tier?"* — make them compute it. Resolution beats retention, and having the
   instinct for which lever is bigger is what this week buys.
2. *"You built an LSM store and a WAL this week. Which surprised you?"* — it is usually
   the tombstone behaviour, and that surprise is worth naming.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 4 is partitioning: hash rings, hot keys, resharding, and id generation.

The link to say out loud on Monday: **this week you chose how data is organised on one
machine; next week the data does not fit on one machine, and the same question — what is
the key? — becomes irreversible.** A badly chosen index can be dropped and rebuilt in an
afternoon. A badly chosen partition key is a migration.

The check: can they state, unprompted, the access pattern for their metrics store in one
sentence? If they still describe the storage shape first, week 4 will produce partition
keys chosen from the entity rather than from the query, and that mistake is much more
expensive.
