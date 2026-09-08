# Day 2 — Fan-out

> **By the end of today** you can compute the work a post creates under three
> strategies, and explain why a hybrid beats both rather than compromising between them.

---

## Read first

- [ ] [**Fan-out**](../../content/week-08/day-2/fan-out.md) — 30 min · sources: [Slack](https://slack.engineering/real-time-messaging/), [Discord](https://discord.com/blog/how-discord-stores-billions-of-messages), [The Tail at Scale](https://research.google/pubs/the-tail-at-scale/)

---

## Predict first

An account with 200 million followers posts once. Your fan-out writes 50,000 timeline
entries a second.

How long does that one post take? Write a number down.

---

## The lab

`fanout.py`, over a deliberately skewed follower distribution.

```python
write_fanout_work(distribution, posts_per_account_per_day)
read_fanout_work(reads_per_day, avg_following)
celebrity_write_cost_seconds(followers, writes_per_second)
hybrid_work(distribution, posts_each, reads, big_followed_each, threshold)
covered_by_write_fanout(distribution, threshold)
threshold_for(writes_per_second, max_seconds)
```

`test_the_hybrid_beats_both` is the day, and the reason it wins matters more than the
number: **the distribution has two populations in it, so the design has two answers.** It
is not a compromise; it is better than either pure strategy on both axes, because each
strategy is applied only where it is cheap.

`threshold_for` is the habit to take away — a threshold derived from a latency budget
rather than picked because it is round.

```bash
pytest week-08/day-2 -v
```

---

## The written exercise

`week-08/day-2/two-populations.md`, half a page.

You have now met this shape four times: week 4's whale tenant, week 6's long tail, week
7's hot campaign, and this week's channels.

1. Write down what the two populations were in each
2. What was the boundary, and what decided it?
3. Find a **fifth** one, in any design you have written, that you have not yet treated as
   two populations

The third question is the exercise. There is one in almost every design, and it is usually
being handled by a single strategy that is wrong for one side.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
