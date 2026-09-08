# Milestone — Design a link shortener

> All seven passes, on one small system, in one document. Then defend it.

Due end of Friday. Two deliverables:

| File | What |
|---|---|
| `DESIGN.md` | Your design document. The template is there; fill every section |
| `estimate.py` | Your sizing, in code, using your own day-3 functions |

And it must pass `pytest week-01/milestone` and `python3 tools/check_sources.py`.

---

## About this problem

Yes: this is the most written-about design question in the industry, and you could find
a hundred answers in ten seconds.

Don't. Two reasons, and the second is the one that matters.

**The brief below carries constraints the published answers do not satisfy.** A storage
ceiling, one region, no guessable codes, and a read distribution that makes the obvious
answer wrong. An answer copied from elsewhere will contradict the brief in ways your
instructor can see from across the room.

**On Friday you will be asked to derive your numbers out loud.** Recited numbers come
apart in about fifteen seconds, and everyone in the room knows what happened. There is
no version of this where reading someone's answer helps you.

You may read every published answer you like **on Saturday**, once yours is defended.
Doing it in that order is genuinely valuable, and doing it in the other order wastes the
week.

---

## The brief

An internal link shortener for a company that sends a lot of marketing email.

**What it does**

- A service creates a short link for a long URL and gets back a short code
- Anyone following the short link is redirected to the long URL
- A caller may request a **custom alias** instead of a generated code
- A link can be deleted

**Scale**

| | |
|---|---|
| New links | 100 million per month |
| Redirects | 500 million per day |
| Read skew | **90% of redirects are for links created in the last 48 hours** |
| Stored record | about 500 bytes |

**Envelope**

| | |
|---|---|
| Redirect latency | p99 under 100 ms at the load balancer |
| Availability | 99.9% |
| Deletion freshness | a deleted link may still redirect for up to 60 seconds |
| Durability | a created link must survive one machine dying |
| **Storage ceiling** | **2 TB total, including replicas** |
| Codes | must not be guessable — you may not hand out sequential ids |
| Region | one, in Europe. Users are in Europe |

**Not building**

Click analytics beyond a count · a dashboard · authentication · custom domains ·
internationalisation · link previews · abuse and malware scanning

*(You may argue that last one should not be a non-goal. If you think so, say why in your
document — that is a legitimate and good answer.)*

---

## `estimate.py`

Implement `estimate()`, returning a dict with these keys. Import and use your own
functions from `week-01/day-3/sizing.py` — do not re-derive them.

| Key | |
|---|---|
| `write_qps`, `peak_write_qps` | link creation |
| `read_qps`, `peak_read_qps` | redirects |
| `read_write_ratio` | reads per write |
| `daily_storage_bytes` | per day, **including replicas** |
| `max_retention_days` | how long you can keep links before hitting the ceiling |
| `working_set_bytes`, `working_set_human` | the links covered by that 90% skew |

Then `pytest week-01/milestone -v`.

**Look at `max_retention_days` and `working_set_human` when they come out.** Both should
change your design, and one of them should change it a lot. If neither surprised you,
you have not understood what you computed — go back and say, in one sentence each, what
they mean for the system.

---

## `DESIGN.md`

The template has the seven passes as headings. Fill every one. Two to three pages.

**The fence applies**: no technology names anywhere in the document. Not one. Describe
what each component must do.

### The rubric

Your instructor marks each pass out of 5 on Friday. Pass is 3 everywhere.

| Pass | 5 looks like |
|---|---|
| **Interrogate** | Every requirement measurable; non-goals written; the assumptions labelled as assumptions |
| **Size** | Every number derived, consistent, and the two surprising ones acted on |
| **Contract** | An API a person could implement, and a data model that serves the one query that matters |
| **Path** | Ordered hops for a create and a redirect, with the slowest one named |
| **Decide** | 3–5 decisions, each with its rejected alternative and its price |
| **Break** | Every component considered dead, slow **and** lying |
| **Evolve** | What breaks first at 10x, and the metric that would show it |

### Sources

Your document will make at least one claim about how something behaves in the real
world. Put it in `content/sources/` with a tier and a date, or mark it in the document
as your own inference. `python3 tools/check_sources.py` must pass.

If you make no claims about the outside world at all, say so in one line under
**Sources**. That is a legitimate answer for a design this small, and stating it
deliberately is the point.

---

## The four questions to have answers to

Not a checklist to include — things Friday will find out whether you thought about.

1. Your cache is empty and every redirect is a miss. What is the load on the store, and
   is that a number you sized for?
2. Two callers request the same custom alias in the same millisecond.
3. Someone requests a million codes that do not exist.
4. `max_retention_days` runs out. What happens on that day, and who finds out first?

---

## Before you submit

```bash
pytest week-01/milestone -v
python3 tools/check_sources.py
```

Then run `ai/defend.md` on your own document. It takes twenty minutes and it will find
at least one thing. Fixing that thing before Friday is the difference between a 3 and a 5.
