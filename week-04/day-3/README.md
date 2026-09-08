# Day 3 — Hot keys

> **By the end of today** you can find a hot key in fixed memory, choose a remedy, and
> produce the number that shows why adding machines will not help.

---

## Read first

- [ ] [**Hot keys**](../../content/week-04/day-3/hot-keys.md) — 30 min · sources: [Slicer](https://research.google/pubs/slicer-auto-sharding-for-datacenter-applications/), [The Tail at Scale](https://research.google/pubs/the-tail-at-scale/), [Discord Engineering](https://discord.com/blog/how-discord-stores-billions-of-messages)

---

## The lab

`hotkeys.py`.

```python
TopK(k)                    .observe(key, count=1)   .heavy_hitters()
share(counts, key)         is_hot(counts, key, threshold=0.05)
split_key(key, ways, which)     split_targets(key, ways)
utilisation_of_hot_partition(hot_share, partitions, fleet_utilisation)
```

`TopK` is the Space-Saving algorithm and the trick is one line: when you evict the
smallest entry, **the new key inherits its count**. That is what lets a genuinely hot key
climb quickly in fixed memory, and it is why the counts are over-estimates — good enough
to rank, not a total. The docstring has the exact rule.

`utilisation_of_hot_partition` is a crude model and it is the most useful function in the
week, because it turns "that key looks busy" into "that partition is at 192% while the
fleet dashboard says 30%".

```bash
pytest week-04/day-3 -v
```

---

## The written exercise

`week-04/day-3/hot-key-plan.md`, half a page.

Pick **one** of your designs and its most plausible hot key — the celebrity, the whale,
the front-page product, the shared config row.

1. What share of load do you expect it to reach?
2. Run `utilisation_of_hot_partition`. What is that partition running at?
3. Which of the four remedies, and **what does it cost you?**
4. How would you find out this key had gone hot, without a customer telling you?

Question 4 is the one to spend time on, and "we'd see it in the metrics" is not an
answer unless you say which metric and at what threshold. The cheapest real answer is
alerting on the spread between your busiest and median partition, and almost nobody
does it.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
