# Day 3 — Presence and delivery

> **By the end of today** you can size a presence system, and build delivery that
> survives every push failing.

---

## Read first

- [ ] [**Presence, heartbeats and delivery**](../../content/week-08/day-3/presence-and-delivery.md) — 30 min · sources: [Slack](https://slack.engineering/real-time-messaging/), [Discord](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users), [WhatsApp](https://www.erlang-factory.com/upload/presentations/558/efsf2012-whatsapp-scaling.pdf)

---

## The lab

`presence.py`, on `simlib`.

```python
PresenceTracker(sim, timeout_ms, debounce_ms=0)
    .heartbeat(user)  .tick()  .is_online(user)  .broadcasts
broadcast_cost(users_going_online, channels_each, members_each)
MessageStore()  .append(conversation, message)  .catch_up(conversation, since)
```

`PresenceTracker` is deliberately **asymmetric**: coming online is instant, going offline
waits out a timeout and then a debounce. Flapping is the expensive failure, because every
flicker is a broadcast to everyone who can see that user — and a system that costs more
when the network is bad has a feedback loop in it.

The last test is the day. Every push is dropped — not degraded, *dropped* — and the client
sees every message. That is what "the message is stored and delivery is an optimisation"
buys you, and it removes a per-device queue, a delivery guarantee, and a cleanup problem
from the design.

```bash
pytest week-08/day-3 -v
```

---

## The written exercise

`week-08/day-3/presence-budget.md`, half a page, for tomorrow's chat system.

1. 100,000 people arrive between 08:55 and 09:05. How many presence notifications is
   that, at 40 channels each and 30 members each?
2. Compare it with the message volume over the same ten minutes.
3. Which three of the mitigations — batching, narrow subscription, coarsening, debouncing
   — would you use, and what does each cost the product?

Question 2 is the one that surprises people: presence usually wins by an order of
magnitude, and it is the feature nobody budgets for.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
