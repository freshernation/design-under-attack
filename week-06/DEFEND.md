# Week 6 — Friday defence

Twenty minutes on the catalogue read path, three phases, then a retro.

This week's theme: whether the arithmetic changed the design, or was computed and then
ignored.

---

## Before they arrive

Read their `DESIGN.md`, run `pytest week-06/milestone`, and check:

- Did they run `total_origin_qps` at a 5-second TTL and **notice it does not fit**? A
  document that proposes a 5-second TTL without that number has not engaged with the brief.
- Is `ttl_that_starts_helping_ms` for the tail anywhere in the document? 99 seconds is the
  week's most surprising number.
- Do the caches have hit rate, TTL, and a cold-start answer? The new rule requires it.
- Products may now be named — do the named ones come with the property needed from them?

---

## Phase 1 — Explain (6 min)

1. *"What origin load does a 5-second price TTL produce, and does it fit?"* — 24,000
   against 20,000. The question of the week.
2. *"Where does that 24,000 come from?"* — 4,000 from the hot products and 20,000 from the
   tail. If they say "the popular products", they have not looked.
3. *"Your cache tier restarts at peak. Walk me through the next sixty seconds."* — the
   cold-start multiplier is 20; the origin sees 400,000. Looking for a real answer:
   coalescing, staged restart, warming, or admitted degradation.
4. *"How long does a full warm take, and does that fit inside a deploy?"* — five minutes
   at full origin capacity, during which it does nothing else.
5. *"Which claim here is sourced and which is you?"*

| 5 | 3 | 1 |
|---|---|---|
| Knows the tail is the cost and why; has a real cold-start answer | Has the numbers, needs prompting on what they mean | Proposed a TTL without computing its load |

## Phase 2 — Mutate (7 min)

### A — *"A flash sale makes one product 60% of all reads."*

Week 4 arriving in a week 6 design. Looking for: they realise the cache handles this
*well* — one hot key is the easiest thing in the world to cache — and that the risk is
elsewhere: the moment it is invalidated, 240,000 requests a second miss the same key
simultaneously. Single-flight and early recomputation are the answers, and they built both
on Wednesday.

A student who says "we'd add cache nodes" has missed that a hot key is one key.

### B — *"Invalidation delivery is delayed by two minutes. Reads still work."*

Looking for: they notice the 5-second requirement is now a property of the invalidation
path, so a slow path means silently wrong prices with every dashboard green. Then: how
would anyone find out? The good answer instruments invalidation lag as a metric, the way
week 5 instrumented replication lag.

### C — *"The 5-second price requirement now applies to all 50 million products."*

Looking for: they go straight to `origin_qps_for_class` for the whole catalogue rather
than reasoning qualitatively, and then to the conclusion that TTL-based freshness cannot
do this at all — the answer has to be invalidation, or the requirement moves.

| 5 | 3 | 1 |
|---|---|---|
| Reaches for their own numbers; connects to weeks 4 and 5 unprompted | Gets there messily | Adds hardware |

## Phase 3 — Break (7 min)

| Attack | Watching for |
|---|---|
| *"Every entry you wrote during the warm has the same TTL."* | Jitter. Without it, the whole cache expires together five minutes after every deploy |
| *"Someone requests a million product ids that do not exist."* | Negative caching, or the filter. Otherwise every one is a full origin lookup |
| *"A price is updated and one cache node misses the invalidation."* | How long is it wrong for, and is the TTL a backstop? A design with an infinite TTL and no backstop is one lost message from being permanently wrong |
| *"You have 200 GB. What is not in the cache?"* | Did they decide, or did they let eviction decide? |
| *"Your CDN config gains `Vary: Cookie`."* | The hit rate goes to approximately zero and every CDN dashboard still looks healthy |

| 5 | 3 | 1 |
|---|---|---|
| Reasons from their own numbers | Finds it with prompting | Adds a component to every attack |

**Pass is 3 in every phase.**

---

## Retro (15 min)

1. *"What surprised you most this week?"* — usually the 99-second tail number, sometimes
   the cold-start multiplier.
2. *"You have used product names for the first time in six weeks. Did it feel different?"*
   — the useful answer is that they reached for them later than they would have in week 1.
3. *"What did I explain badly?"*

---

## Instructor: what next week rests on

Week 7 is logs, queues, delivery guarantees and idempotency.

The link for Monday: **invalidation is a message, and this week you assumed it arrives.**
Next week is about what happens when messages arrive twice, out of order, or an hour late
— which is exactly the failure mode that makes a two-minute invalidation delay possible.

The check: can they say why a TTL is a backstop for a lost invalidation? If yes, week 7's
at-least-once material lands on something they already believe. If not, ten minutes on the
day-2 lab, because week 7's whole subject is messages that do not behave.
