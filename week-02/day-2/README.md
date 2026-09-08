# Day 2 — Utilisation, and the knee

> **By the end of today** you can say what going from 80% to 90% utilised does to
> latency, and you will never again describe a system as "90% healthy".

---

## Read first

- [ ] [**Utilisation, and the knee**](../../content/week-02/day-2/utilisation-and-the-knee.md) — 30 min · sources: [Handling Overload](https://sre.google/sre-book/handling-overload/), [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/), [AWS load shedding](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [ ] [**Variability, and why the average lies twice**](../../content/week-02/day-2/variability.md) — 25 min · source: [Dean & Barroso, *The Tail at Scale*](https://research.google/pubs/the-tail-at-scale/)

Read *The Tail at Scale* properly. Ten pages, written for engineers, and you will cite
it for years.

---

## Predict first

1. A service is at 80% utilisation. You add load to bring it to 90%. Latency goes up
   by...?
2. You run three instances at 65% utilisation. One dies. What is the utilisation on the
   other two?
3. A cache turns a 40 ms operation into 1 ms, 95% of the time. Does the queue in front
   of it get better or worse?

Write all three down. The third one is the interesting one, and most engineers with
years of experience get it wrong.

---

## The lab

`queueing.py` — the curve, the outage arithmetic, and the variability multiplier.

```python
utilisation(arrival_rate, service_rate)
wait_time(service_time_s, rho)               # M/M/1, raises for rho >= 1
response_time(service_time_s, rho)
max_arrival_rate(service_rate, target_rho)
servers_needed(arrival_rate, service_rate, target_rho)
utilisation_after_losing_one(instances, rho)
variability_penalty(ca, cs)
kingman_wait(service_time_s, rho, ca, cs)
bimodal_cv(fast_s, slow_s, slow_fraction)
```

`wait_time` raises `ValueError` at `rho >= 1`. That is not defensive programming — at
full utilisation the wait is genuinely unbounded, and a function that returned a large
number would be teaching you something false.

Run `bimodal_cv(0.001, 0.040, 0.05)` before reading its test.

```bash
pytest week-02/day-2 -v
```

---

## The written exercise

In `week-02/day-2/utilisation-of-my-shortener.md`, half a page:

- Take your week-1 peak read number. Assume one instance serves 300 requests a second.
  How many instances at a 70% target?
- What is the utilisation if one dies? Two?
- Your redirect path has a cache. Estimate the hit and miss service times, pick a miss
  rate, and compute `bimodal_cv`. What does the variability penalty do to your queueing?
- One sentence: **did any of this change your week-1 design?**

If the answer to the last one is no, either your week-1 design was unusually good or you
have not believed the numbers yet. Both are worth saying out loud on Friday.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
