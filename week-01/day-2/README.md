# Day 2 — Interrogate, and the envelope

> **By the end of today** you can turn a vague brief into requirements with numbers on
> them, and you can tell a measurable requirement from a wish in about a second.

---

## Read first

- [ ] [**Interrogating the requirement**](../../content/week-01/day-2/interrogating-the-requirement.md) — 25 min · source: [Google SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/)
- [ ] [**The non-functional envelope**](../../content/week-01/day-2/the-non-functional-envelope.md) — 30 min · sources: [SRE Workbook](https://sre.google/workbook/implementing-slos/), [AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

Read the first three sections of the SRE Book chapter properly. It is the primary source
for every reliability number you will write for the rest of the course.

---

## The lab

`envelope.py`. Five functions. Write them yourself; the file ships with the docstrings
and a `NotImplementedError`.

**Before you write each one, predict the answer to its first test.** 99.9% availability
over a month — how many minutes is that? Write your guess down. Being wrong here is
worth more than being right, because the number is smaller than almost everyone thinks.

### `downtime_minutes(target_percent, window="month")`

Minutes of downtime permitted by an availability target.

| Window | Minutes |
|---|---|
| `"day"` | 1,440 |
| `"week"` | 10,080 |
| `"month"` | 43,200 (30 days) |
| `"year"` | 525,600 (365 days) |

Returns a float rounded to one decimal place. Raises `ValueError` for an unknown window,
or for a target that is not greater than 0 and at most 100.

```python
downtime_minutes(99.9)            # 43.2
downtime_minutes(99.99)           # 4.3
downtime_minutes(99, "year")      # 5256.0
```

### `error_budget_remaining(target_percent, window, minutes_down)`

The budget, minus what has been spent. Rounded to one decimal. **May be negative** —
that is the interesting case, and the SRE Book's whole argument rests on it.

### `parse_latency(text)`

A stated latency requirement into `(percentile, milliseconds)`.

```python
parse_latency("p99 < 200ms")      # (99.0, 200.0)
parse_latency("p50 < 40 ms")      # (50.0, 40.0)
parse_latency("p99.9 < 1s")       # (99.9, 1000.0)
parse_latency("p95<250ms")        # (95.0, 250.0)
```

Understands `ms` and `s`. Raises `ValueError` when there is no percentile or no
number-with-unit — which means `parse_latency("under 200ms")` raises, and it should,
because a latency target without a percentile is not a target.

### `is_measurable(requirement)`

The test from the article, as a rule. A requirement is measurable when it contains at
least one **quantity**, which means any of:

- digits, optionally with a decimal point, followed by an optional space and one of:
  `% ms s sec secs seconds min mins minutes h hr hrs hours d day days B KB MB GB TB PB`
- a percentile token: `p` followed by digits, optionally with a decimal (`p99`, `p99.9`)
- the standalone word `zero`

```python
is_measurable("p99 read latency under 200ms")                    # True
is_measurable("99.9% of requests return non-5xx over 28 days")   # True
is_measurable("zero acknowledged writes lost")                   # True
is_measurable("The system should be fast")                       # False
is_measurable("It must be highly available")                     # False
```

**This is a heuristic and not a theory of measurability.** One of the tests asserts a
case it gets wrong, on purpose. Read that test — knowing what your checker cannot see is
part of using one.

### `page_slow_probability(calls, tail_probability)`

If one page makes `calls` requests and each has probability `tail_probability` of being
slow, how likely is it that the page is slow? Rounded to four decimals.

```python
page_slow_probability(20, 0.01)   # 0.1821
```

Twenty calls, a 1% tail, and **18%** of page loads are slow. This is the number that
justifies caring about p99, and computing it yourself is more convincing than being told.

---

## Then

```bash
pytest week-01/day-2 -v
```

---

## The written exercise

Take **brief 3 from yesterday** — the photo storage one — and write only its
`## Envelope` section. Six dials, every one a number, every assumption labelled as an
assumption. Half a page. Put it in `week-01/day-2/envelope-photos.md`.

Then read it back and ask: *could two engineers build measurably different systems and
both satisfy this?* If yes, it is not tight enough yet.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
