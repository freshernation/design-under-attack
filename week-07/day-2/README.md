# Day 2 — Delivery guarantees

> **By the end of today** you can say which guarantee a consumer provides by looking at
> where it commits, and you will have watched a healthy consumer do the same work twice.

---

## Read first

- [ ] [**Delivery guarantees**](../../content/week-07/day-2/delivery-guarantees.md) — 30 min · sources: [Kafka — Message Delivery Semantics](https://kafka.apache.org/documentation/#semantics), [AWS SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html), [Google Pub/Sub](https://cloud.google.com/pubsub/docs/subscription-overview)

---

## Predict first

A consumer crashes half way through a batch. Write down what happens if it commits before
processing, and if it commits after.

Then: a consumer that is **not** crashing, just slow — slower than the queue's visibility
timeout. What happens to its message?

The third one is the interesting one and most people have not thought about it.

---

## The lab

`delivery.py`.

```python
consume_with_crash(records, commit_before_processing, crash_after)  -> effects
duplicate_rate(effects)      lost(records, effects)

VisibilityQueue(sim, visibility_ms)
    .send(message)   .receive() -> (receipt, message)
    .delete(receipt) .extend(receipt, extra_ms)   .visible_count
```

`consume_with_crash` returns **every effect that happened**, including repeats. That list
is the delivery guarantee made concrete, and comparing the two lists is the day.

In `VisibilityQueue`, a receipt identifies **one delivery**, not the message. That is why
a receipt from a delivery that has already timed out must be refused: deleting on a stale
receipt would remove work somebody else is now doing.

```bash
pytest week-07/day-2 -v
```

`test_a_slow_consumer_has_its_work_done_twice` is the test to sit with. Nothing crashed.
Nothing failed. The work was done twice because a number was too small.

---

## The written exercise

`week-07/day-2/guarantees-audit.md`, half a page.

Go through your designs and find every place a message crosses a boundary. For each:

1. At-most-once or at-least-once? Where is the commit relative to the work?
2. Which of the five duplicate sources apply?
3. What happens to the *user* when a duplicate occurs?

The third question is the one that turns this from bookkeeping into design. "The counter
is wrong" and "the customer is charged twice" are the same bug with very different
consequences.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
