# Connections at scale

*Week 8 · Day 1 · about 20 minutes*

> By the end of this you can size a connection tier, and say what happens to it during a
> deploy.

---

## Read the primary sources first

| Source | Tier | What it gives you |
|---|---|---|
| [**Discord — scaling Elixir to 5,000,000 concurrent users**](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users) | 1 | Named engineers on holding millions of connections, and what broke |
| [**Rick Reed — Scaling to millions of simultaneous connections**](https://www.erlang-factory.com/upload/presentations/558/efsf2012-whatsapp-scaling.pdf) | 1 | WhatsApp, 2012. Slides rather than prose, and one of the few first-hand accounts of this that exists |
| [**Slack Engineering — Real-time Messaging**](https://slack.engineering/real-time-messaging/) | 1 | Gateway servers at the edge, channel servers behind them |

The WhatsApp slides are from 2012 and much of the specific tuning is dated. The *shape* of
the problem is not, and it is worth seeing somebody work through it first-hand.

---

## A connection is a small amount of state you cannot get rid of

Per connection you hold: socket buffers, TLS state, a file descriptor, and whatever your
application keeps — the user, their subscriptions, a sequence number.

The application part is usually the largest, and it is the part you control. It is also
the part that quietly grows: a subscription list per connection, a small outbound buffer,
a last-seen timestamp. At a million connections, **every kilobyte per connection is a
gigabyte of RAM**, and that arithmetic is worth doing before choosing what to keep.

```
1,000,000 connections × 20 KB = 20 GB, just to be connected
```

---

## The tiers this produces

Almost every system that holds many connections ends up with the same shape, and Slack's
description of theirs is a good example to have read:

**A gateway tier.** Holds the connections, terminates TLS, does nothing clever. Sized by
connection count. Stateless in the sense that matters: any gateway can serve any client,
so a client that reconnects lands anywhere.

**A routing or channel tier.** Knows which conversations exist and where a message should
go. Sized by message rate and by the number of things being subscribed to.

The split exists because the two scale on different axes. Connections scale with *users*;
message routing scales with *activity*. Combining them means adding capacity for one when
you needed the other, and it is a common source of a system that is expensive and still
falls over.

---

## The three failure modes

**Uneven distribution.** Connections are long-lived, so a load balancer cannot rebalance
them — there is no next request to route differently. A server that comes back after a
restart has zero connections and stays nearly empty until something forces clients to
reconnect. **Load balancing a connection tier is a slow-moving problem**, and the usual
answer is to expire connections deliberately, with jitter, so the population reshuffles.

**The reconnect storm.** Restart a server holding 100,000 connections and all 100,000
reconnect at once, at the exact moment you have less capacity than usual. Without jitter,
they arrive together, overwhelm the remaining servers, and cause the next set of
disconnections. This is a genuine cascading failure and it has taken down large systems.

**The slow client.** A client that does not read as fast as you write to it. The kernel
buffer fills, then your application buffer fills, and now one client is consuming
unbounded memory on your server. Every connection needs a bounded outbound buffer and a
policy for what happens when it is full — which is week 2, unchanged: **reject, drop
oldest, or grow**, and growing is how a process dies.

---

## What goes in a design document

> A gateway tier holds client connections, 50,000 per host, so 1M concurrent needs 20
> hosts plus headroom — 26 at a 0.75 utilisation target. **Each connection has a 64-message
> outbound buffer; a client that fills it is disconnected** and must reconnect and refetch,
> because one slow client must not consume unbounded memory. Deploys are rolling with a
> 60-second jittered reconnect, so the reconnect rate stays under 20,000/s against a
> measured accept capacity of 60,000/s.

Sizing, the buffer policy, and the deploy arithmetic. Three sentences, and most designs
have none of them.

---

## Today's lab

`transport.py`, from the previous article, includes the connection side. Run
`reconnect_rate` for a 100,000-connection server restarting instantly, and then over a
jittered 60-second window. The two numbers are three orders of magnitude apart.

---

> **Sources for this article**
> [Discord](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users),
> [Rick Reed / WhatsApp](https://www.erlang-factory.com/upload/presentations/558/efsf2012-whatsapp-scaling.pdf)
> and [Slack](https://slack.engineering/real-time-messaging/) — all **Tier 1**.
> The three-failure-modes framing is ours — **Tier 3**. Per-connection memory figures vary
> enormously by language and runtime, so we have not quoted one; measure yours.
