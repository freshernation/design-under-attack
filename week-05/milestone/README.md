# Milestone — Design a lease service

> Seven passes. A design document, and a working lease service with fencing.

| File | What |
|---|---|
| `DESIGN.md` | Your design document |
| `lease.py` | Leases, tokens, and a store that refuses stale writers |

Must pass `pytest week-05/milestone` and `python3 tools/check_sources.py`.

---

## The brief

A coordination service. Clients acquire a **lease** on a named resource, hold it while
they do something exclusive, and release it. It is the thing other systems use to decide
who is in charge of what.

**Scale**

| | |
|---|---|
| Clients | 40,000 processes |
| Resources | 200,000 named leases |
| Acquire rate | 5,000/second at peak, mostly renewals |
| Service nodes | 5 |

**Envelope**

| | |
|---|---|
| Acquire and renew | p99 under 30 ms |
| Availability | 99.99% for acquire |
| **Under partition** | **correctness beats availability.** A minority must refuse rather than guess |
| **Safety** | **two clients must never both act as the holder of one resource — including when one of them has been paused for a minute and does not know it** |
| Lease duration | tunable; the default should be justified |

**Not building**

Distributed transactions · a general-purpose key-value store · watches and notifications ·
access control · the storage system being protected

---

## The scenario this brief exists for

A client acquires a lease and starts work. Then its process stops — a garbage-collection
pause, a VM migration, a disk that stopped answering, an operator suspending it. For
ninety seconds it does nothing at all.

The lease expires. Another client acquires it, legitimately, and starts work.

Then the first process **resumes**. From inside, no time has passed. Its lease object says
it holds the resource. It carries on and writes.

Two things are worth being precise about:

**Checking the expiry does not help.** The first client can check "am I still valid?",
get yes, be paused for a minute, and then write. There is no gap you can close between
the check and the write, because the pause can happen inside it. This is a check-then-act
race and no amount of care in the client fixes it.

**Therefore the fix cannot live in the client.** It lives in whatever the client writes
to: every lease carries a **token** that only ever increases, every write carries its
token, and storage refuses a token lower than the highest it has seen. The paused client
may believe whatever it likes; nothing will accept its writes.

Notice what that does — it does not prevent the confusion, it makes the confusion
**harmless**. Your document should have a view on that distinction.

---

## `lease.py`

```python
Lease(resource, holder, token, expires_at_ms)

LeaseService(sim, lease_ms=10_000)
    .acquire(resource, holder)  -> Lease | None
    .renew(lease)               -> Lease | None       # same token, later expiry
    .release(lease)             -> bool
    .holder_of(resource)        -> str | None

FencedStore().write(key, value, token) -> bool        # rejects a token below the highest seen
UnfencedStore().write(key, value)                     # for the contrast test
```

Two details that carry the whole design:

**A renewal keeps the same token.** It is the same period of leadership continuing, not a
new one. A new token would mean the holder fenced *itself* out of storage it had already
written to.

**A fresh acquisition always takes a higher token.** Even for the same holder, and even
after a clean release. Tokens are the ordering; if they can repeat, they order nothing.

---

## `DESIGN.md`

The week-1 template. **The fence still forbids product names** — one more week.

This week your **Decide** section must contain:

- the **lease duration**, with the trade stated in both directions: shorter means more
  renewal traffic and more spurious expiries under load; longer means a crashed holder
  blocks the resource for that long. Give a number and defend it
- what happens on the **minority side of a partition**, and why the brief's envelope
  makes that decision for you
- whether fencing is enforced by the storage system or by convention, and what "by
  convention" costs

And your **Break** table needs a row for: *the lease service is unreachable and a client's
lease expires while it is still working.*

---

## The five questions to have answers to

1. Your lease is 10 seconds. A holder's host freezes for 40 seconds. Walk through every
   write it attempts on waking.
2. The lease service is partitioned 3–2. What does a client talking to the minority see,
   and what should it do?
3. Renewal traffic is 5,000/second against 5 nodes. What is the per-node rate, and what
   happens to it if you halve the lease duration?
4. Storage does not support fencing tokens — it is a system you do not control. What are
   your options, and what does each actually guarantee?
5. A holder releases cleanly and immediately re-acquires. Same token or a new one, and
   why does it matter?

Question 4 is the honest one. There are three defensible answers and none of them is as
good as fencing.

---

## Before you submit

```bash
pytest week-05/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md` on your own document.
