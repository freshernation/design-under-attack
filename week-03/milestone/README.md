# Milestone — Design a metrics store

> Seven passes. A design document, and a working rollup engine.

| File | What |
|---|---|
| `DESIGN.md` | Your design document |
| `rollup.py` | Bucketing, aggregation, downsampling, and the retention arithmetic |

Must pass `pytest week-03/milestone` and `python3 tools/check_sources.py`.

---

## The brief

An internal metrics store. Services push numeric time series; engineers query them from
dashboards and during incidents.

**Scale**

| | |
|---|---|
| Ingest | 2,000,000 points/second at peak |
| Series | 2,000,000 distinct |
| A point | `(series_id, timestamp_ms, value)` — call it 32 bytes stored |
| Late arrivals | points up to **5 minutes** late must be accepted |

**Queries**

| Share | Shape | Budget |
|---|---|---|
| 95% | one series, last hour | p99 under 500 ms |
| 4% | one series, last 30 days | p99 under 2 s |
| 1% | 1,000 series, last 7 days — a dashboard loading | p99 under 5 s |

**Envelope**

| | |
|---|---|
| Retention | raw 24 hours · 1-minute rollups 30 days · 1-hour rollups 2 years |
| **Storage ceiling** | **40 TB total, including 3 replicas** |
| Durability | a point acknowledged must survive one host dying |
| Correctness | **an average over any window must be right** — not approximately right |
| Availability | 99.9% for queries, 99.99% for ingest |

**Not building**

Alerting · dashboards and UI · tracing and logs · cardinality management · anomaly
detection · multi-tenancy

---

## What this brief is about

**1. The correctness line is the whole milestone.** An average over any window must be
right. That single sentence rules out the obvious implementation of rollups, and if you
do not notice why, the lab will show you in about four seconds.

**2. The ceiling binds — just.** Run `retention_bytes` on the brief's numbers before
you design anything. The answer fits inside 40 TB with room, and one plausible change to
the retention policy takes it over. Which change, and by how much, belongs in your
document.

**3. Late points and immutable files disagree.** You spent Wednesday learning that
log-structured stores like data that arrives in order and never changes. Now points may
arrive five minutes late, which means a bucket you already wrote out may need updating.
Say what you do about that. There are several honest answers and no free one.

**4. The read path has three shapes.** 95% of queries touch one series and one hour;
1% touch a thousand series and a week. Designing for the 95% is right, and saying what
the 1% costs is the part people skip.

---

## `rollup.py`

```python
bucket(timestamp_ms, resolution_s) -> int          # the bucket's start, in ms

Agg(count, total, minimum, maximum)
    .mean                                          # total / count
    .merge(other) -> Agg

rollup(points, resolution_s) -> dict[int, Agg]     # points: (timestamp_ms, value)
downsample(buckets, to_resolution_s) -> dict[int, Agg]

mean_of_means(aggs) -> float                       # the wrong way. It is here to fail
retention_bytes(series, tiers, bytes_per_bucket=32, replicas=3) -> int
tier_for(age_s, tiers) -> int | None               # which resolution serves this age
```

### Why `Agg` holds four numbers instead of one

Store the mean of each bucket and you cannot merge buckets correctly, because **the mean
of means is only the true mean when every bucket has the same count** — and buckets never
do, because series arrive at different rates and gaps exist.

Store `count` and `total` and merging is exact: add the counts, add the totals, divide at
the end. Minimum and maximum merge trivially. This is why every real time-series store
keeps count-and-sum rather than an average, and it is a five-second demonstration in the
tests.

Which aggregates do *not* work this way is a good thing to know: percentiles and distinct
counts cannot be merged from summaries without either keeping much more state or
accepting an approximation. Mention it in your document if your queries need them.

---

## `DESIGN.md`

The week-1 template. Seven headings, same rubric. **The fence still forbids product
names** — you may name mechanisms freely now, and you have a lot of them.

This week your **Size** section must include:

- ingest in points/second and bytes/second, at peak
- **device write rate** — apply a write amplification and say which model you used
- `retention_bytes` for the brief's tiers, against the ceiling, with the headroom stated
- the working set for the 95% query: how much data is "the last hour" across all series?
- the read path for each of the three query shapes, with a latency budget

And your **Decide** section must contain a decision about **late points**, with its
rejected alternative and its price.

---

## The five questions to have answers to

1. A point arrives 4 minutes late for a bucket you have already written out. What
   happens?
2. Someone queries a 7-day window for 1,000 series. Which tier serves it, how many
   buckets is that, and does it fit the budget?
3. The raw retention changes from 24 hours to 48. What happens to the ceiling?
4. A deploy makes one service emit 10x its normal number of series. What breaks first?
5. Your store is log-structured, and dashboards read the last hour constantly while
   compaction runs. What does that do to your p99, and what would you measure?

Question 5 is the week-2 connection and it is the one that separates a good document
from a complete one.

---

## Before you submit

```bash
pytest week-03/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md` on your own document.
