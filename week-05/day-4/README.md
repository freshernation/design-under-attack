# Day 4 — Consistency models, and the two you need

> **By the end of today** you can give a client read-your-writes and monotonic reads
> with one integer, and explain why most designs buy far more than they need.

---

## Read first

- [ ] [**Consistency models, and the two you actually need**](../../content/week-05/day-4/consistency-models.md) — 30 min · sources: [Jepsen — consistency models](https://jepsen.io/consistency), [Jepsen analyses](https://jepsen.io/analyses), [Spanner](https://research.google/pubs/spanner-googles-globally-distributed-database-2/)

Spend twenty minutes on the Jepsen consistency page properly. It is the best single
artefact in this field and it is free.

---

## The lab

`session.py` — no network, no timers. The point is *which replica answers*, and jitter
would obscure it.

```python
Cluster(followers=3)   .write(key, value)   .replicate(follower, upto=None)
                       .read_any(key, follower=None)
                       .read_fresh(key, min_version, follower=None)
Session(cluster)       .write(key, value)   .read(key, follower=None)   .version
stale_by(cluster, follower)     read_pool(cluster, max_stale)
```

The whole mechanism is one integer on the client. It is not a consistency model — it is a
promise to *one* client, which is what products actually need.

The detail worth noticing: **`Session.read` advances the session too**, not just
`Session.write`. That is what gives monotonic reads. Once you have seen version 9, no
later read may be answered by a replica sitting at version 4, even if you never wrote
anything.

Run `test_a_follower_read_can_return_the_old_value` and `test_read_your_writes` back to
back. Same scenario, nine lines of difference, and nothing became linearizable.

```bash
pytest week-05/day-4 -v
```

---

## The written exercise

`week-05/day-4/guarantees.md` — and this one is a rewrite rather than a new page.

Go back to **all four** of your design documents and write the guarantees paragraph each
one should have had:

> A user always sees their own writes. Others see them within N seconds at p99. There is
> no ordering guarantee between two different users' writes, and here is why the product
> does not need one. The one place that needs more is X, and it pays for it by Y.

Four paragraphs, one per design. At least two of them will turn out to have needed
read-your-writes and never said so — which is the exercise.

---

## Tomorrow

The milestone. Read `week-05/milestone/README.md` tonight. The scenario at the top of it
is the one the whole week has been building towards, and it is worth sleeping on before
you try to design around it.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
