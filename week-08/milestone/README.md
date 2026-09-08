# Project 2 — Design a team chat system

> The keystone of the second half. Seven passes, a design document, a working
> mini-system, and a written comparison against a real one.

| File | What |
|---|---|
| `DESIGN.md` | Your design document |
| `chat.py` | A working chat core: delivery, presence, catch-up, large channels |
| `DIFF.md` | **After you finish**: read Slack's own write-up and say what they did differently |

Must pass `pytest week-08/milestone` and `python3 tools/check_sources.py`.

---

## Why this one is a project

Everything since week 1 lands here at once: sizing, queues, storage, partitioning,
replication, caching, idempotency, fan-out. It is the first brief where the hard part is
not any single mechanism but **which of the eight you reach for, and in what order**.

Budget two days rather than one. Friday's defence is longer, and this document is one you
should still be able to talk about in week 12.

---

## The brief

A team chat product. Channels, messages, presence, and clients that are frequently offline.

**Scale**

| | |
|---|---|
| Daily active users | 8,000,000 |
| **Concurrent connections at peak** | **1,200,000** |
| Channels | 400,000 |
| Channel membership | median 12; **the largest has 80,000 members** |
| Messages | 30,000/second at peak |
| Regions | 3, up to 150 ms apart |

**Envelope**

| | |
|---|---|
| Delivery | **p99 under 500 ms**, globally, for a connected recipient |
| **Message durability** | **no acknowledged message may be lost, ever** |
| Offline clients | mobile is disconnected ~60% of the time and must lose nothing |
| Ordering | messages in a channel appear in the same order for every member |
| Presence | online/away/offline, within 30 seconds |
| Deploys | daily, and a full gateway restart must not take the product down |
| Retention | messages kept indefinitely |

**Not building**

Search · voice and video · file storage · threads · integrations and bots · moderation ·
message editing

---

## The four things this brief is actually about

**1. The largest channel is 80,000 members.** One message there is 80,000 deliveries. At
the median channel size it is 12. **Two populations, so the design needs two answers** —
week 8's whole lesson, and the same shape as week 4's whale and week 6's long tail.

**2. Clients are absent most of the time.** If delivery is the mechanism, you need a queue
per device, cleanup for devices that never return, and a delivery guarantee on the push
path. If delivery is an *optimisation* over durable storage, you need none of those. The
lab makes you build the second one; your document has to say why.

**3. Three regions, 150 ms apart, and a 500 ms p99.** Check that against the speed of
light from week 1 **before** designing anything. It is feasible, and only just, and the
margin decides where messages are written.

**4. A gateway restart drops hundreds of thousands of connections.** Daily. Your document
needs the reconnect arithmetic and a deploy duration, both as numbers.

---

## `chat.py`

```python
ChatSystem(sim, gateways, capacity_each, broadcast_threshold=10_000)
    .connect(user) / .disconnect(user)
    .join(user, channel) / .members(channel)
    .post(sender, channel, text)     -> (sequence, pushed_to)
    .catch_up(user, channel)         -> [(sequence, message), ...]
    .mark_read(user, channel, sequence)
    .restart_gateway(host)           -> clients needing to reconnect
    .stats

delivery_fanout_per_second(messages_per_second, avg_members, connected_fraction)
largest_channel_burst(members, connected_fraction)
feasible_globally(p99_target_ms, worst_rtt_ms, processing_ms)
```

Three behaviours the tests hold you to:

- **A message is durable before it is delivered.** `post` assigns a sequence and stores it
  first; pushing is what happens afterwards, and it may fail entirely.
- **Above `broadcast_threshold`, a channel is not pushed to individually.** Members pull on
  their next interaction. This is the second population getting its second answer.
- **A member who was offline for the entire conversation loses nothing.** `catch_up`
  is the correctness path; push is the fast path.

---

## `DESIGN.md`

The week-1 template, and this one should be longer — four to six pages rather than two.

Your **Size** section must include:

- connections per gateway and the number of gateways, at a stated utilisation target
- delivery fan-out per second at peak, and the burst from one message in the largest
  channel
- the reconnect rate for one gateway restart, and the duration of a full rolling deploy
- presence broadcast cost during a morning rush
- storage for messages, indefinitely, with replication

Your **Decide** section needs at least five decisions, each with its rejected alternative
and price. At minimum: the transport, the large-channel strategy, where messages are
durable, how a client catches up, and what happens on the minority side of a region
partition.

Your **Break** table needs rows for: a gateway restarts · a whole region is unreachable ·
the largest channel gets a message during a deploy · a client is offline for a week · two
clients post at the same millisecond.

---

## `DIFF.md` — after you finish, not before

Read [Slack Engineering — Real-time Messaging](https://slack.engineering/real-time-messaging/)
and [Flannel](https://slack.engineering/flannel-an-application-level-edge-cache-to-make-slack-scale/),
then write one page:

1. **Three things they did differently from you**, and your best guess at why
2. **One thing you did that they do not describe** — and whether that is because it is a
   bad idea, or because a blog post is not a design document
3. **What their write-up does not tell you** that you would need before building this —
   the "unknown" column from week 1, applied to a real source

Reading it first would have robbed you of the exercise. Reading it afterwards is where
most of the learning in this milestone actually is, and the third question is the one that
separates a reader from an engineer.

---

## Before you submit

```bash
pytest week-08/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md`, and then `ai/interviewer.md` on the same design — this is the
first milestone worth taking into a mock interview, and week 12 will use it.
