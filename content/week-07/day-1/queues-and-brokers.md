# Queues, and the other model

*Week 7 · Day 1 · about 20 minutes*

> By the end of this you can describe a visibility timeout, say what a dead-letter queue
> is for, and choose between a queue and a log from the requirement rather than the habit.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**AWS SQS — visibility timeout**](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) | 1 | The mechanism that makes at-least-once work, documented precisely by an operator |
| [**Google Pub/Sub — subscriptions**](https://cloud.google.com/pubsub/docs/subscription-overview) | 1 | The same ideas with different names: ack deadlines, dead-letter topics, ordering keys |
| [**Kafka — Design**](https://kafka.apache.org/documentation/#design) | 1 | The contrast, in the project's own words |

---

## The visibility timeout

The mechanism at the heart of every queue, and it is worth being able to describe exactly.

1. A consumer **receives** a message. It is not deleted — it becomes **invisible** to
   other consumers for a period
2. The consumer does the work and **deletes** the message
3. If it does not delete in time, the message becomes visible again and somebody else
   gets it

That is the whole thing, and it produces at-least-once delivery for free: a consumer that
crashes mid-work never deletes, so the message reappears.

**The timeout is a guess**, in exactly the way week 5's failover timeout was a guess:

| Too short | Too long |
|---|---|
| a slow-but-working consumer's message is redelivered while it is still being processed — **two consumers doing the same work** | a crashed consumer's message is stuck for that long, and the queue silently stalls |

There is no correct value. Choose one, say why, and note that "the work usually takes 2
seconds so we set 30" is a reasonable sentence and "it was the default" is not.

Most queues also let a consumer **extend** the timeout while it works, which is the right
answer for jobs of unpredictable length — and it is a lease, renewed, exactly as in week 5.

---

## Dead-letter queues

A message that fails is redelivered. If it fails because of the message itself — malformed
input, a reference to something deleted, a bug triggered by one specific record — it will
fail again, for ever, at whatever rate your consumer retries.

That is a **poison message**, and untreated it can consume an entire consumer fleet
processing one bad record thousands of times a second.

A dead-letter queue is the answer: after N delivery attempts, move the message aside
instead of redelivering it. Two things follow that designs routinely miss:

- **Somebody has to look at it.** A dead-letter queue nobody reads is a data-loss
  mechanism with a reassuring name
- **A full DLQ is usually an incident, not a backlog.** If a hundred thousand messages
  dead-letter in an hour, the problem is not the messages

---

## Choosing

From the requirement, not the habit:

| If | Use |
|---|---|
| Several independent consumers need the same events | **a log** — a queue delivers to one |
| You may need to reprocess after a bug | **a log** |
| Order matters within a key | **a log**, keyed by that key |
| Work items are consumed once and then meaningless | **a queue** |
| Items need individual retry, delay or dead-lettering | **a queue** — logs are bad at per-message state |
| The backlog may be enormous and short-lived | **a queue** — it stores only what is outstanding |

The one that catches people: **logs are bad at per-message retry.** A log consumer is a
single moving offset, so "retry this one message in five minutes while continuing with the
rest" does not fit the model — you have to write the failed record somewhere else, which
is a queue you have now built by hand.

Systems that need both usually have both, and saying which does what is a good design
sentence.

---

## Backpressure, from week 2

A queue is a queue, so everything from week 2 applies without modification:

- It absorbs a burst. It cannot absorb a deficit
- The metric is the **age of the oldest message**, not depth
- It needs a bound and a policy for being full

And the week-2 question that matters most here: **what happens when the consumer has been
down for an hour and comes back?** The queue is at maximum depth, the consumer starts at
full speed, and everything downstream of it receives an hour of traffic compressed into
minutes. Designs survive the outage and fall over during the recovery.

---

## What goes in a design document

> Ingestion writes to a log; failed records are written to a retry queue with exponential
> backoff and dead-lettered after 5 attempts. **The log gives us replay after an
> aggregation bug; the queue gives us per-message retry, which a log cannot.**
> Visibility timeout is 60 seconds against a p99 processing time of 4 seconds. The DLQ is
> alerted on rate, not depth — a hundred messages an hour is a bug, not a backlog.

---

## Today's lab

`log.py`, from the previous article. The queue side appears tomorrow, where the delivery
guarantees make it necessary.

---

> **Sources for this article**
> [AWS SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html),
> [Google Pub/Sub](https://cloud.google.com/pubsub/docs/subscription-overview) and
> [Kafka](https://kafka.apache.org/documentation/#design) — all **Tier 1**, all operators
> or maintainers documenting their own systems. The choosing table is ours — **Tier 3**.
