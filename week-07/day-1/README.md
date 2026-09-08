# Day 1 — The log

> **By the end of today** you can say what a log gives you that a queue cannot, and
> build one with offsets, consumer groups and replay.

---

## Read first

- [ ] [**The log**](../../content/week-07/day-1/the-log.md) — 25 min · sources: [Kafka — Design](https://kafka.apache.org/documentation/#design), [Kreps — The Log](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying)
- [ ] [**Queues, and the other model**](../../content/week-07/day-1/queues-and-brokers.md) — 20 min · sources: [AWS SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html), [Google Pub/Sub](https://cloud.google.com/pubsub/docs/subscription-overview)

Read the Kreps essay this week, in one sitting, ideally away from a desk. It is long and
it is the argument that made this the default way of thinking.

---

## You have built this before

Week 3, day 4: append-only, framed records, read forward. That was a write-ahead log
inside one machine; today it is the same structure with the readers outside. If today
feels familiar, that is the course working.

---

## The lab

`log.py`.

```python
Partition(index)      .append(record)   .read(offset, max_records)
                      .end_offset  .start_offset  .truncate_before(offset)
Log(partitions)       .partition_for(key)   .append(key, record)   .end_offsets
ConsumerGroup(log, name)
                      .poll(partition)  .commit(partition, offset)  .seek(...)
                      .lag(partition)   .total_lag()
```

Two details worth getting right rather than approximately right:

- **Offsets never shift**, including after a retention sweep. A consumer's stored offset
  has to keep meaning the same thing, so removing old records does not renumber the rest.
- **`poll` does not commit.** Where you commit relative to processing is tomorrow's whole
  subject, and it had better not happen by accident.

```bash
pytest week-07/day-1 -v
```

The test to read is `test_a_consumer_that_falls_off_the_back_loses_data`. No error, no
exception — the records are simply not there when it arrives.

---

## The written exercise

`week-07/day-1/log-or-queue.md`, half a page.

For each, choose and give one sentence of reason:

1. Order events, consumed by fulfilment, analytics and the customer email service
2. Thumbnail generation jobs, each of which may fail and need retrying
3. Database change events feeding a search index that occasionally needs rebuilding
4. Password reset emails

Then one paragraph: **which of your own earlier designs used a queue where a log would
have been better, and what would it have made possible?** The answer is usually
"reprocessing after a bug", and it is usually the metrics store or the job queue.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
