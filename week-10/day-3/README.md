# Day 3 — Matching engines

> **By the end of today** you can explain why the fastest design here is
> single-threaded, and you have written something whose replay is byte-identical.

---

## Read first

- [ ] [**Matching engines: determinism as a requirement**](../../content/week-10/day-3/matching-engines.md) — 30 min · sources: [LMAX Disruptor](https://lmax-exchange.github.io/disruptor/disruptor.html), [Nasdaq ITCH](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHspecification.pdf)

Skim the ITCH message list. *Add order, order executed, order cancelled, trade, system
event* — that is the entire domain model, and reading a real protocol tells you more in ten
minutes than any explanation.

---

## The lab

`orderbook.py`.

```python
Order(id, side, price, quantity, sequence)      Fill(buy_order_id, sell_order_id, price, quantity)
sequence(orders, arrival_times, tie_break="id")
OrderBook()  .add(order) -> [Fill]  .cancel(id)  .best_bid  .best_ask  .spread  .depth(side)
replay(orders) -> [Fill]
```

The constraint that shapes everything: **nothing in the matching path may read a clock,
iterate a set, or draw a random number.** Time is an input, stamped by the sequencer and
carried in the order. Lists rather than dictionaries, so iteration order is a property of
the data rather than of the runtime.

Two behaviours the tests hold you to:

- **A fill happens at the resting order's price.** The order already in the book set the
  terms; the arriving order accepted them.
- **Simultaneous arrivals need a stated tie-break rule.** There is no sensible default, so
  the lab has no default — passing anything but `"id"` raises.

```bash
pytest week-10/day-3 -v
```

`test_a_replay_produces_exactly_the_same_fills` is the requirement, not a nicety: a
disputed trade is settled by replaying the log.

---

## The written exercise

`week-10/day-3/determinism-audit.md`, half a page.

Take **any** of your earlier designs and find every source of non-determinism in it:

- wall-clock reads inside processing
- iteration over a set or an unordered map
- randomness, including jitter and hashing
- concurrency without a defined interleaving
- floating-point accumulation order

For each: would a replay produce the same result? Then one sentence — **which of your
designs would benefit from being replayable, and what would it cost to make it so?**

Most would benefit, and most would find the cost surprisingly small if it were designed in
rather than retrofitted.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
