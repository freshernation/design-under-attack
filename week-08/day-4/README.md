# Day 4 — The gateway tier

> **By the end of today** you can split a realtime system into tiers that scale
> independently, and say how long a safe deploy takes.

---

## Read first

- [ ] [**The gateway tier, and the reconnect storm**](../../content/week-08/day-4/the-gateway-tier.md) — 25 min · sources: [Slack — RTM](https://slack.engineering/real-time-messaging/), [Slack — Flannel](https://slack.engineering/flannel-an-application-level-edge-cache-to-make-slack-scale/), [Discord](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users)

Read the Slack RTM post again, with week 4 in mind this time. The channel-to-server
mapping is the hash ring you built, in production.

---

## The lab

`gateway.py`.

```python
GatewayTier(hosts, capacity_each)   .connect(client)  .restart(host)  .connections(host)
channel_owner(channel, hosts, virtual_nodes=100)
reconnect_rate(clients, window_s)   storm_survivable(clients, window_s, accept_capacity)
rolling_restart_seconds(hosts, connections_each, accept_capacity, settle_s)
```

`channel_owner` is week 4's ring, reused unchanged. That is the point — you are not
learning a new mechanism, you are recognising one.

`test_find_out_which_term_actually_dominates` is worth reading carefully. With a
90-second settle, making reconnections ten times cheaper improves the deploy by about
16%; with a 10-second settle the same change nearly halves it. **The lever is whichever
term is larger, and you find that out by computing both** rather than by optimising the
expensive-sounding one.

```bash
pytest week-08/day-4 -v
```

---

## The written exercise

`week-08/day-4/deploy-plan.md`, half a page, for tomorrow's chat system.

1. 1.2M connections, 40,000 per host. How many hosts, at a 0.75 utilisation target?
2. One host restarts. What is the reconnect rate at 1 second, and at 60?
3. What is your accept capacity, and how would you measure it?
4. How long does a full rolling deploy take, and what would you tell a product manager who
   wants same-day rollbacks?

Question 3 is the one nobody has an answer to, and it is why "what happens if we restart
everything" is usually answered in production.

---

## Tomorrow

**Project 2.** Read `week-08/milestone/README.md` tonight — it is longer than the usual
brief and it has three deliverables.

Do **not** read the Slack posts before you design. `DIFF.md` is the third deliverable and
it only works if your design came first.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
