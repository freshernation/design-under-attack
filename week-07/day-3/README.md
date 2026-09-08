# Day 3 — Idempotency, and the dual write

> **By the end of today** you can make an effect safe to repeat, size the window that
> makes deduplication possible, and remove a dual write with a table.

---

## Read first

- [ ] [**Idempotency**](../../content/week-07/day-3/idempotency.md) — 30 min · sources: [Stripe](https://docs.stripe.com/api/idempotent_requests), [Kafka](https://kafka.apache.org/documentation/#semantics)
- [ ] [**The dual write problem**](../../content/week-07/day-3/the-dual-write-problem.md) — 20 min · sources: [Debezium](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html), [Kleppmann](https://www.confluent.io/blog/using-logs-to-build-a-solid-data-infrastructure-or-why-dual-writes-are-a-bad-idea/)

Read Stripe's idempotency documentation closely. It is short and it specifies the details
most implementations get wrong — particularly what happens when a key is reused with a
different payload.

---

## The lab

`idempotency.py`.

```python
IdempotencyStore(sim, ttl_ms)   .execute(key, payload, fn)     # raises IdempotencyConflict
DedupWindow(sim, window_ms)     .seen(event_id)
window_bytes(events_per_second, window_s, bytes_per_id)
apply_absolute(state, key, value)      apply_increment(state, key, delta)

Database()  .insert_with_outbox(row, event)   .unsent_events()   .mark_sent(event)
dual_write(database, published, row, event, crash_between)
relay(database, published, crash_after_publish)
```

Start with `apply_absolute` and `apply_increment`. Two lines each, and the difference
between them is the entire subject: **absolute assignments are idempotent, relative
changes are not**, and restating an operation absolutely is very often the whole fix.

The last test is the week joining up. The outbox creates duplicates on purpose — because
converting "may be lost" into "may be duplicated" is a good trade once duplicates are
free — and then the deduplication window absorbs them.

```bash
pytest week-07/day-3 -v
```

---

## The written exercise

`week-07/day-3/dual-writes.md`, half a page.

Find every dual write in your six designs so far. Look for:

- write the database, then publish an event
- write the database, then invalidate the cache — **week 6's race is a dual write**
- write the database, then send an email
- call two services in sequence and call it a workflow

For each, say what a crash between the two leaves behind, and whether an outbox would fix
it or whether the second write is to somewhere an outbox cannot help.

Everyone finds at least two. The cache one usually comes as a surprise.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
