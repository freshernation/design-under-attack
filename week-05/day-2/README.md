# Day 2 — Quorums and conflicts

> **By the end of today** you can choose N, W and R, say precisely what the overlap
> guarantees, and watch a skewed clock silently delete a write.

---

## Read first

- [ ] [**Quorums**](../../content/week-05/day-2/quorums.md) — 25 min · sources: [Dynamo §4.5–4.6](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Jepsen](https://jepsen.io/consistency)
- [ ] [**When copies disagree**](../../content/week-05/day-2/conflicts.md) — 25 min · sources: [Dynamo §4.4](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Cassandra](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)

---

## Predict first

N=5, W=2, R=2. A client writes successfully. Another client reads.

Is the read guaranteed to see the write? Write down yes or no, and why, before the lab.

---

## No network today

Days 1 and 3 are about timing. Today is about counting, and jitter would only obscure the
pigeonhole argument. The replicas here are plain objects with an `up` flag, and the tests
choose exactly which nodes each read and write touches.

That is the point: `W + R > N` is not a probabilistic statement. It is arithmetic about
sets, and you can see the exact node that makes it work.

---

## The lab

`quorum.py`.

```python
Versioned(value, version, writer, timestamp_ms)
Replica(name)                 .put(key, versioned)   .get(key)   .up
QuorumStore(replicas, w, r)   .overlaps   .write(key, v, to=None)   .read(key, frm=None)

newest(versions)      siblings(versions)      last_write_wins(versions)
merge_sets(versions)  compare_and_set(...)    read_repair(store, key)
```

Write `last_write_wins` first, then run `test_a_skewed_clock_wins_a_race_it_should_have_lost`.
Watching a legitimate acknowledged write vanish because another machine's clock was 600 ms
fast is more persuasive than any amount of prose — and there is no error anywhere.

Also read `test_a_failed_write_still_leaves_data_behind`. The write was reported as failed
and two replicas kept the value. That is not a bug, and it surprises everyone.

```bash
pytest week-05/day-2 -v
```

---

## The written exercise

`week-05/day-2/quorum-choices.md`, half a page.

For each, choose N, W and R and say what breaks first:

1. A shopping cart — availability matters more than losing an item
2. A ledger of financial transactions
3. A cache of rendered pages
4. A user's list of API keys

Then one paragraph: **which of these can use last-write-wins, and which cannot, and how
would you tell the difference in general?** The general rule is one sentence and it is the
day's real output.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
