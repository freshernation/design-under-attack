# Day 3 — Queues, and what to do when they fill

> **By the end of today** you can bound a queue, choose what happens at that bound, and
> demonstrate that an unbounded queue serves no more work than a bounded one.

---

## Read first

- [ ] [**Queues, and what to do when they fill**](../../content/week-02/day-3/queues-and-backpressure.md) — 30 min · sources: [AWS load shedding](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/), [Handling Overload](https://sre.google/sre-book/handling-overload/)

The queue-management section of *Addressing Cascading Failures* is two pages and is the
best writing on this anywhere. Read it twice.

---

## New today: the simulator

From here the labs run on `simlib`, in the repo root. Time is **simulated
milliseconds**: a ten-second workload runs in microseconds and produces exactly the same
result every time.

Three things you need:

```python
from simlib import Simulation

sim = Simulation()
sim.now                              # milliseconds since the start
sim.schedule(delay_ms, callback)     # run callback later
sim.run(until_ms=10_000)             # fire everything up to that point
```

`sim.record("note")` appends to `sim.trace`, and `sim.print_trace()` prints it. When a
test fails for reasons you cannot see, that is the first thing to reach for.

You are using the harness, not building it. Its own tests are in `tests/test_simlib.py`
and are worth skimming — they are a specification of what it promises.

---

## The lab

`backpressure.py` — a `BoundedQueue` with three policies, and a workload runner.

```python
BoundedQueue(sim, capacity, policy)   # "reject" | "drop_oldest" | "grow"
    .offer(item) -> bool
    .poll()      -> (item, enqueued_at_ms) | None
    .oldest_age_ms()
    .accepted / .rejected / .dropped

run_workload(arrival_rate, service_rate, duration_s, capacity, policy) -> dict
```

The README docstring in the file tells you how to wire the runner. Two details that
matter:

- The consumer reschedules itself forever, so nothing ends the run except
  `sim.run(until_ms=...)`. That is deliberate — a real consumer does not stop either.
- Record the enqueue time with each item. `oldest_age_ms` is the whole point of the
  exercise and you cannot compute it afterwards.

**There is no `block` policy.** Backpressure needs a producer that can be suspended,
which this harness does not model; week 7 comes back to it. The three policies here are
the ones you can implement honestly today.

```bash
pytest week-02/day-3 -v
```

Read the last three tests even after they pass. They are the week's argument, and the
one about all three policies serving the same amount of work is the one to sit with.

---

## The written exercise

Two paragraphs in `week-02/day-3/queue-policy.md`:

Pick one queue from your week-1 design. State its bound, its policy, and **what a user
experiences** in each of the three cases. Not what the system does — what a person sees.

Then: what would you monitor, and at what value would you act? One metric. If you wrote
"queue depth", say what depth means without knowing the drain rate.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
