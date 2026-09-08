# Day 1 — Push, pull, and connections

> **By the end of today** you can choose a transport with arithmetic rather than
> preference, and size a tier that holds a million connections.

---

## Read first

- [ ] [**Push against pull**](../../content/week-08/day-1/push-versus-pull.md) — 25 min · sources: [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455), [MDN — SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events), [Slack Engineering](https://slack.engineering/real-time-messaging/)
- [ ] [**Connections at scale**](../../content/week-08/day-1/connections-at-scale.md) — 20 min · sources: [Discord](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users), [Rick Reed / WhatsApp](https://www.erlang-factory.com/upload/presentations/558/efsf2012-whatsapp-scaling.pdf)

The WhatsApp slides are from 2012 and the specific tuning is dated. Read them anyway — it
is one of very few first-hand accounts of this problem that exists.

---

## The lab

`transport.py` — six functions, all arithmetic, and the point is that you run them on
your own designs afterwards.

```python
polling_qps(clients, interval_s)          push_qps(events_per_second)
wasted_fraction(clients, interval_s, events_per_second)
connection_memory_bytes(connections, bytes_each)
servers_needed(connections, per_server, target_utilisation=1.0)
reconnect_rate(connections, window_s)
```

Note what `polling_qps` does not contain: any term for how much is actually happening.
The load is the same on a quiet Sunday and during an incident. That is the whole problem
with polling, and also the whole appeal.

```bash
pytest week-08/day-1 -v
```

---

## The written exercise

`week-08/day-1/transport-choices.md`, half a page.

For each, choose a transport and give the arithmetic:

1. A stock ticker, 50,000 viewers, prices changing several times a second
2. A build-status page, 200 engineers, builds finishing every few minutes
3. A collaborative document, 8 editors, keystroke-level updates
4. An order-tracking page, 2 million customers, a status change every few hours

Number 4 is the interesting one: two million connections held for a handful of events
each is an enormous cost for very little, and polling is almost certainly right. Say so
with a number.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
