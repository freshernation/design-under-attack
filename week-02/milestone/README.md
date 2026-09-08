# Milestone — Design a rate limiter

> Seven passes. A design document, and a working multi-tenant limiter.

| File | What |
|---|---|
| `DESIGN.md` | Your design document — the week-1 template, with this week's numbers |
| `limiter.py` | A multi-tenant limiter, tested |

Must pass `pytest week-02/milestone` and `python3 tools/check_sources.py`.

---

## The brief

A rate-limiting service for a public API platform. It sits at the edge and decides, for
every incoming request, whether to serve it.

**Scale**

| | |
|---|---|
| Peak traffic | 40,000 requests/second across all tenants |
| Tenants | 50,000, of which the top 1% send about 80% of the traffic |
| Edge servers | 12, in one region |
| Balance | **not even.** Connection reuse pins a tenant's traffic to whichever server it connected to, and large tenants hold long-lived connections |

**Tiers**

| Tier | Sustained | Burst |
|---|---|---|
| free | 1/s | 5 |
| pro | 50/s | 100 |
| enterprise | 500/s | 1,000 |

**Envelope**

| | |
|---|---|
| Decision latency | **p99 under 2 ms**, and this is inside every request's path |
| Availability | 99.99% — if the limiter is down, the platform is down |
| Direction of error | **over-limiting a paying tenant is worse than briefly under-limiting one.** Say what that implies and where you applied it |
| Protection | the platform must survive a tenant inside their paid quota still overwhelming a shared downstream dependency |
| Freshness | a tier change must take effect within 60 seconds |

**Not building**

Billing · the quota purchase flow · per-endpoint limits · authentication · anomaly
detection · a dashboard

---

## The three things this brief is actually about

Not a checklist — the questions your document has to have taken a position on.

**1. Two millisecond budget.** A shared counter is a network round trip, and inside one
datacentre that is around 0.5 ms — a quarter of your entire budget, on every request,
with a new dependency that can fail. Week 5 will give you the machinery to talk about
this properly; this week, price it and decide.

**2. Uneven balance.** Twelve servers each enforcing a twelfth of a tenant's limit is
wrong when that tenant's traffic lands on one server. Twelve servers each enforcing the
full limit permits twelve times the limit. Neither is acceptable and the brief tells you
which direction to err in.

**3. Fairness is not protection.** A single enterprise tenant at 500/s is within quota
and may still be the reason a downstream dependency falls over. A limiter that only
enforces what people paid for will let that happen. Your design needs both, and they
disagree — which makes it a decision with a price rather than a feature.

---

## `limiter.py`

Reuse `TokenBucket` from day 4 — it is importable.

### `MultiTenantLimiter`

```python
limiter = MultiTenantLimiter(sim, global_rate_per_second=40_000, global_burst=80_000)
decision = limiter.check("acme", tier="pro")
decision.allowed          # bool
decision.reason           # "ok" | "tenant" | "global"
decision.retry_after_ms   # 0 when allowed
```

Order matters, and this is the specified behaviour:

1. Resolve the tier. An unknown tenant gets `default_tier`
2. If the **tenant** bucket has not got the tokens — reject, `reason="tenant"`,
   `retry_after_ms` from the tenant bucket
3. Otherwise if the **global** bucket has not got them — reject, `reason="global"`,
   `retry_after_ms` from the global bucket, and **the tenant is not charged**
4. Otherwise spend both and allow

Step 3's last clause is the detail worth pausing on. If you spend the tenant's token and
then discover the global limit is exhausted, you have charged a customer for a request
you did not serve — and under sustained global pressure you would burn every tenant's
quota without serving anybody. Check both before spending either.

Counters: `allowed`, `rejected_tenant`, `rejected_global`.

### Two functions about doing this on twelve servers

```python
local_limit_worst_case(servers, per_server_limit)   # what N independent limiters permit
divided_limit_floor(servers, global_limit)          # what one tenant gets if pinned to one
```

Two lines each. Run them on the brief's numbers before writing your pass 5 — the two
answers are the two ways of being wrong, and your document has to choose between them
with a reason.

---

## `DESIGN.md`

Copy the template from `week-01/milestone/DESIGN.md`. Same seven headings, same rubric,
and the fence still applies — **no technology names**.

This week your **Size** section must include:

- requests per second per edge server, at peak and after losing one server
- **utilisation at peak, and utilisation after losing one server** — use
  `utilisation_after_losing_one` from day 2, and if the second number is above 0.8, say
  what you are doing about it
- the memory for limiter state across 50,000 tenants
- the decision latency budget, hop by hop, using `budget_remaining` from week 1

And your **Break** table must have an answer for: *what does the limiter do when the
thing it depends on for shared state is unreachable?* "Fail open" and "fail closed" are
both defensible, they are opposite, and the brief tells you which way to lean.

---

## The four questions to have answers to

1. A tenant upgrades from free to enterprise. How long until it takes effect, and what
   happens to requests in the meantime?
2. Your edge servers restart during a deploy. Every token bucket starts full. What has
   just happened to the platform?
3. A tenant sends 40,000 requests in one second from 4,000 connections spread across all
   twelve servers.
4. The global limit is hit. Which requests get rejected — and is that the set you would
   have chosen?

Question 2 is the one most people miss, and it is the same shape as a cold cache.

---

## Before you submit

```bash
pytest week-02/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md` on your own document.
