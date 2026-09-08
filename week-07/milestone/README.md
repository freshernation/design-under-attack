# Milestone — Design an ad-click aggregator

> Seven passes. A design document, and a working bucketed aggregator.

| File | What |
|---|---|
| `DESIGN.md` | Your design document |
| `aggregator.py` | Bucketing, deduplication, watermarks, and replay by recomputation |

Must pass `pytest week-07/milestone` and `python3 tools/check_sources.py`.

---

## The brief

Count ad clicks. Advertisers are billed from these numbers.

**Scale**

| | |
|---|---|
| Clicks | 500,000/second at peak |
| Campaigns | 2,000,000 |
| **Skew** | the largest campaign is about 15% of all clicks |
| Late events | mobile clients buffer offline; **up to 10 minutes late** |
| Log retention | 24 hours |

**Queries**

| Share | Shape | Budget |
|---|---|---|
| 95% | one campaign, last hour | p99 under 200 ms |
| 5% | top 100 campaigns today | p99 under 2 s |

**Envelope**

| | |
|---|---|
| **Counting** | **exactly once. Advertisers are billed from this** — double-counting is fraud and undercounting is lost revenue |
| Replay | after an aggregation bug, the **last 24 hours** must be reprocessable to a correct result |
| Freshness | a click is reflected within 60 seconds at p99 |
| Retention | minute counts 30 days, hour counts 2 years |
| Availability | 99.9% for queries, 99.99% for ingest |

**Not building**

Fraud detection · attribution · the ad-serving path · invoice generation · budget
enforcement · a UI

---

## The trap this brief is built around

Read these three lines together:

- Delivery is at-least-once, so **duplicates are certain**
- Counting must be **exactly once**
- A **24-hour replay** must produce a correct result

The obvious answer is a deduplication window covering the replay depth. Compute it before
you design anything:

```
500,000 events/s × 86,400 s × 16 bytes = 690 GB of event ids
```

That is not a deduplication window, it is a database. And it has to be consulted on every
one of 500,000 events a second.

**So the deduplication window cannot be the replay window, and the way out is to stop
deduplicating the replay at all.** There is a second mechanism available, you met it on
Wednesday, and the lab makes you build it.

Work out what it is before reading `aggregator.py`'s docstrings — the answer is more
satisfying if you find it.

---

## `aggregator.py`

```python
bucket_of(timestamp_ms, bucket_s=60)
watermark(now_ms, late_window_ms)

BucketAggregator(sim, late_window_ms=600_000, bucket_s=60)
    .add(event_id, campaign, timestamp_ms)     -> bool     # False: duplicate, or too late
    .count(campaign, bucket)                                # what it has
    .close_before(watermark_ms)                 -> int      # seal buckets, free memory
    .recompute(campaign, bucket, events)        -> int      # replay: set, not add
    .stats                                                  # duplicates, too_late, closed

dedup_window_bytes(events_per_second, window_s, bytes_per_id=16, partitions=1)
```

Two design points the tests will hold you to:

**A late event goes into the bucket it belongs to**, not the one that is current. An event
timestamped 09:03 that arrives at 09:11 increments the 09:03 bucket. Otherwise your
minute counts are a record of when data arrived, which is not what anybody is buying.

**A bucket is closed once the watermark passes it**, and closing frees its deduplication
set. That bounds the memory to the *late-arrival* window rather than the replay window,
which is the difference between 7 GB and 690 GB.

---

## `DESIGN.md`

The week-1 template. Products may be named, with the property you need from them.

Your **Size** section must include:

- events per second per partition, at peak, and with the 15% campaign accounted for
- the deduplication memory for your chosen window, per partition — using
  `dedup_window_bytes`, and showing why the replay-sized window is not an option
- storage for minute counts over 30 days and hour counts over 2 years
- the read path for both query shapes, with a latency budget

Your **Decide** section must contain, each with its rejected alternative and price:

- how exactly-once counting is achieved given at-least-once delivery
- **how a 24-hour replay produces a correct result** — this is the one
- what happens to an event that is later than your late window

Your **Break** table needs rows for: the aggregator crashes mid-bucket · a consumer is
rebalanced mid-batch · an event arrives 3 hours late · the log's retention edge is
reached by a lagging consumer.

---

## The five questions to have answers to

1. An event arrives 3 hours late. What happens to it, and who finds out?
2. You replay 24 hours to fix an aggregation bug. Walk through what happens to a bucket
   that was already correct.
3. The largest campaign is 15% of clicks. Which partition holds it, and what is that
   partition's rate?
4. Your aggregator crashes with 40 seconds of un-flushed counts in memory. What is lost?
5. Billing runs at 02:00 for the previous day. When is a day's number final, and how do
   you know?

Question 5 is the one that separates a data pipeline from a billing system, and the answer
is a watermark rather than a time of day.

---

## Before you submit

```bash
pytest week-07/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md` on your own document.
