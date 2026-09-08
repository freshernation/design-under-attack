# Day 3 — Size it

> **By the end of today** you can go from a user count to peak requests per second,
> storage after five years, and a latency budget — in about four minutes, out loud.

---

## Read first

- [ ] [**Back of the envelope**](../../content/week-01/day-3/back-of-the-envelope.md) — 30 min
- [ ] [**Latency numbers, and spending them**](../../content/week-01/day-3/latency-numbers-and-budgets.md) — 25 min · sources: [the latency table](https://gist.github.com/jboner/2841832) (Tier 3 — read the article on *why* it is Tier 3), [AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

---

## Before the lab: four numbers, from memory

Write these down without looking:

- seconds in a day
- how much slower an SSD read is than a memory read
- round-trip time inside one datacentre
- round-trip time London to Sydney

Then check them against the article. Whichever you got wrong is the one that will
embarrass you in an interview, and it is nearly always the third — people underestimate
the cost of a network hop by about an order of magnitude, which is exactly why designs
with eight sequential service calls keep getting drawn.

---

## The lab

`sizing.py`. Nine functions, each one line to three lines. The value is not the code, it
is that you now have exact definitions for things you have only ever done vaguely.

### The chain

```python
qps(events_per_day)                    # average per second, 1 dp
peak_qps(average_qps, factor=5)        # 1 dp
daily_bytes(events_per_day, bytes_per_event)
storage_bytes(events_per_day, bytes_per_event, retention_days, replicas=3)
working_set_bytes(hot_keys, bytes_per_key)
```

`storage_bytes` defaults to **three replicas**, because two is the number people assume
and three is the number that gets deployed. Defaults encode a belief; this one is worth
arguing about, and you should be ready to on Friday.

### Making it readable

```python
human_bytes(3_600_000_000_000)   # "3.6 TB"
human_bytes(999)                 # "999 B"
human_bytes(1000)                # "1.0 KB"
```

Decimal units — 1 KB is 1,000 bytes here, not 1,024. Disk vendors and cloud bills use
decimal, and this is the arithmetic you do in front of people. One decimal place; below
1,000 bytes, a plain integer and `B`.

### The budget

```python
budget_remaining(target_ms, hops)   # hops: [("edge to origin", 20.0), ...]
first_hop_over_budget(target_ms, hops)   # the hop that spent you past zero, or None
is_geographically_possible(target_ms, km)
```

`is_geographically_possible` uses light in fibre at **200,000 km/s** and a **round
trip**, so the floor in milliseconds is `km / 100`. London to Sydney is about 17,000 km,
which puts the floor at 170 ms — and no design, cache or budget changes that.

Use it before you design for a latency target, not after.

---

## Then

```bash
pytest week-01/day-3 -v
```

---

## The written exercise, and it is the important half

In `week-01/day-3/sizing-photos.md`, size yesterday's photo service. Out loud first,
then written. Ten minutes.

Given: 5 million daily actives, 2 photos uploaded each per day, each viewed 30 times,
average photo 3 MB, thumbnails 40 KB, kept for ever.

Produce:

- uploads per second, average and peak
- views per second, average and peak
- bytes stored per day, and after three years with three replicas
- egress bandwidth at peak
- the working set, if 5% of photos account for most views
- **one sentence** saying which of those numbers is the design problem

That last line is the whole exercise. Five of the six numbers will turn out to be
unremarkable. Finding the one that is not is what sizing is *for* — and once you have
found it, you know what the rest of the hour is about.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
