# Week 8 — Concept fence

## Allowed

**Everything from weeks 1–7**, plus:

- **Transports** — polling, long polling, server-sent events, WebSocket, and the cost
  model that chooses between them
- **Connection tiers** — per-connection memory, sizing, why long-lived connections cannot
  be rebalanced, bounded outbound buffers
- **Fan-out** — on write, on read, and the hybrid; thresholds derived from a budget
- **Presence** — heartbeats, timeouts, hysteresis, debouncing, the broadcast
  multiplication
- **Delivery** — durable messages with per-conversation sequences, catch-up, coarse read
  positions
- **Gateway and channel tiers** — consistent hashing of channels, reconnect storms,
  rolling deploys

## Not yet

Circuit breakers, bulkheads and load shedding (week 9) · SLOs and error budgets as a
practice (week 9) · CRDTs and collaborative editing (week 10) · geospatial (week 10) ·
model serving (week 10)

---

## The rule

**Every design with two populations in it says where the boundary is and what happens on
each side.**

Not "we handle large channels differently" — this:

> Channels above 10,000 members are not pushed to; members pull on their next
> interaction. That threshold covers 99.98% of channels on the push path, and the 0.02%
> above it account for 40% of potential delivery volume.

Boundary, what fraction is on each side, and why the boundary is there. If you cannot
produce those three, you have noticed the problem without solving it.
