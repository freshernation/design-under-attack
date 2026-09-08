# Day 4 — Reading a source

> **By the end of today** you can take a real architecture post apart into what is
> known, what you inferred, and what nobody has published — and you have done it to one.

---

## Read first

- [ ] [**Source tiers and the claims ledger**](../../content/week-01/day-4/source-tiers-and-the-claims-ledger.md) — 25 min
- [ ] [**Reading an engineering blog post**](../../content/week-01/day-4/reading-an-engineering-blog.md) — 30 min
- [ ] [**Slack Engineering — Real-time Messaging**](https://slack.engineering/real-time-messaging/) — **the whole post**, 20 min. Tier 1, Sameera Thanugdu, April 2023

Read the Slack post **before** the second article, not after. The second article
contains our extraction of its claims, and reading that first replaces the exercise with
a summary — which is precisely the habit today is trying to break.

---

## The lab

`triage.py` — the source doctrine, as code. You are implementing a small version of
`tools/check_sources.py`, which is the checker your milestone has to pass.

### `tier(source)`

Apply these rules **in order**, first match wins:

| | Rule | Tier |
|---|---|---|
| 1 | `source["runs_the_system"]` is `True` | **1** |
| 2 | `source["kind"]` is one of `"paper"`, `"official_docs"`, `"spec"` | **2** |
| 3 | it has a non-empty `author` **or** `publisher` | **3** |
| 4 | otherwise | **4** |

Missing keys are allowed and mean "no". The ordering is the interesting part: a paper
written by the team that runs the system is Tier 1, not Tier 2, because proximity beats
format.

### `is_load_bearing(tier_number)`

`True` for tiers 1 and 2. This is the whole doctrine in one line, and writing it down as
a function is the point.

### `check_claim(claim, sources_by_id)`

Returns a **sorted list of problem codes**, empty when the claim is fine. The codes are
defined at the top of the stub:

| Code | When |
|---|---|
| `"no-sources"` | the claim cites nothing, and its kind is not `"unknown"` |
| `"unknown-source"` | it cites an id that is not in `sources_by_id` |
| `"not-load-bearing"` | kind is `"known"` and none of the **resolvable** cited sources is tier 1 or 2 |

Note "resolvable": tiers are judged only among sources that exist. A claim citing
nothing but a bad id has one problem, not two — which is also how
`tools/check_sources.py` behaves, and matching it is deliberate.

An `unknown` claim citing nothing is legal — it is a question the sources do not answer,
and having somewhere legitimate to put those is why the third column exists.

### `ledger_problems(ledger)`

Runs `check_claim` over a whole ledger, returning `{claim_id: [codes]}` for the claims
that have problems, and nothing for the ones that do not.

### `is_stale(source, today, years=3)`

`True` when `published` is more than `years` before `today`. Dates are ISO strings or
`date` objects. A stale source is not a bad source — it is a source describing a
different year, and the difference matters.

---

## Then

```bash
pytest week-01/day-4 -v
```

---

## The deliverable: build the Slack ledger

Write `content/sources/slack-realtime.yml` yourself, in the format used by
[`content/sources/week-01-reading.yml`](../../content/sources/week-01-reading.yml) —
which is this week's own reading, done properly, as your worked example.

Yours must contain:

- the Slack post as a source, with `tier`, `published` and `retrieved`
- **at least six `known` claims**, each citing it — quote or paraphrase precisely
- **at least two `inferred` claims** — your reasoning, clearly yours
- **at least two `unknown` claims** — questions the post does not answer

Then:

```bash
python3 tools/check_sources.py
```

It must pass. If it does not, it will tell you which rule you broke.

### The one to hunt for

Somewhere in that post, two statements about how many channels a host serves do not
sit comfortably together. Find them. Then write, in a comment in your YAML, which
reading you adopted and why.

Nobody is going to grade that comment. It is the single most useful thing you will
write this week, because it is the exact move that separates reading a source from
absorbing one.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
