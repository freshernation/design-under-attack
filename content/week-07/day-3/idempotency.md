# Idempotency

*Week 7 · Day 3 · about 30 minutes*

> By the end of this you can make an effect safe to repeat, size a deduplication window,
> and say which of your operations was already idempotent and did not need any of it.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Stripe — idempotent requests**](https://docs.stripe.com/api/idempotent_requests) | 1 | An operator documenting the contract precisely: keys, retention, and what happens on a conflicting retry |
| [**Kafka — Message Delivery Semantics**](https://kafka.apache.org/documentation/#semantics) | 1 | Idempotent producers and what they do and do not cover |
| [**AWS SQS**](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html) | 1 | The other side: at-least-once as a stated property you must design around |

---

## The move

Delivery cannot be exactly-once. So stop trying, and make the **effect** exactly-once
instead:

> An operation is idempotent when doing it twice has the same result as doing it once.

Then at-least-once delivery is not a problem to be tolerated, it is simply the contract.
The duplicate arrives, the effect does not change, nobody is charged twice.

---

## Four ways to get there

### 1. It already is

More operations than people expect, and this is always the cheapest answer:

| Operation | Idempotent? |
|---|---|
| `SET status = 'shipped'` | yes — an absolute value |
| `balance = balance + 10` | **no** — a relative change |
| `INSERT ... ON CONFLICT DO NOTHING` | yes |
| `add user to set` | yes — sets are idempotent by definition |
| `send email` | no |
| `DELETE WHERE id = 42` | yes |

The pattern: **absolute assignments and set operations are idempotent; increments and
side effects on the outside world are not.** Restating an operation absolutely rather than
relatively is often the entire fix, and it costs nothing.

This connects to week 5: commutative, idempotent operations have no conflicts either. It
is the same property earning its keep twice.

### 2. An idempotency key

The client generates a key per logical operation and sends it with every retry. The server
records the key and its result; a repeat returns the stored result without redoing the
work.

Stripe's documentation is the primary source here and it is worth reading for the details
most implementations get wrong:

- **The key must come from the client**, and must be the same across retries of the same
  logical operation. A server-generated key defeats the purpose entirely
- **The stored result is returned**, not just "already done". The retrying client wants
  the answer it missed
- **Keys expire.** Stripe keeps them 24 hours. A retry after that is a new operation, so
  the window must exceed the longest plausible retry — including a human retrying tomorrow
- **A key reused with a different payload is an error**, not a duplicate. Silently
  returning the first result would hide a real bug

### 3. Deduplicate on the way in

The consumer keeps the ids it has processed and drops repeats. Simple, and the whole
question is **how long you remember**:

```
window = how far apart two copies of the same message can be
```

For a redelivery after a visibility timeout, seconds. For a consumer crash and restart,
minutes. **For a deliberate replay of a week's data, a week** — and that is the number
that decides whether the store fits in memory.

At high volume the memory becomes the design: a million events a second against a
one-hour window is 3.6 billion ids. That is where week 6's membership filter comes back,
with the caveat that a filter's false positive means **dropping a real event**, which for
a click aggregator is acceptable at 1% and for a payment is not.

### 4. Make it commutative

If the effect is order-independent and repeat-independent, neither duplicates nor
reordering matter. `max(seen, value)`, "add to set", "set to absolute value" all qualify.

This is the strongest answer where it is available, because it survives duplicates,
reordering and replay all at once. Week 10 generalises it.

---

## What is not a solution

**"We'll check if it exists first."** Read, then write, with no atomicity between them —
two consumers both check, both find nothing, both proceed. This is week 5's check-then-act
race, and it is exactly as broken here.

**"Duplicates are rare."** They are rare until a network blip, a deploy, a rebalance, or
the day you replay a week deliberately. Rarity is not a property you can rely on, and the
day it stops being true is the day you least want to find out.

---

## What goes in a design document

> Every click carries a client-generated event id. The aggregator deduplicates against
> ids seen in the last 24 hours — **the window is 24 hours because that is our maximum
> replay depth**, not because duplicates arrive that late. At 500,000 events/s that is 43
> billion ids, so the store is a membership filter at 0.1% false positives, which drops
> about 500 real events an hour. **That is acceptable for ad statistics and would not be
> for billing**, which is why billing derives from a separate exact path.

Window, why that window, the memory it implies, the mechanism, and what the mechanism
costs in dropped data.

---

## Today's lab

`week-07/day-3/idempotency.py`:

- `IdempotencyStore` — key to stored result, with expiry, and a **conflict** when the same
  key arrives with a different payload
- `DedupWindow` — ids seen within a window, and the memory the window implies
- `apply_absolute` and `apply_increment`, with the test showing which survives a duplicate
- `window_bytes(events_per_second, window_s, bytes_per_id)` — the sizing that decides
  whether exact deduplication is possible at all

Read [the dual write problem](the-dual-write-problem.md) next; it is the other half of
today.

---

> **Sources for this article**
> [Stripe](https://docs.stripe.com/api/idempotent_requests) — **Tier 1**, and the primary
> source for the idempotency-key contract ·
> [Kafka](https://kafka.apache.org/documentation/#semantics) and
> [AWS SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
> — **Tier 1**. The four-ways framing and the idempotent-operations table are ours —
> **Tier 3**.
