# Day 1 — Geospatial

> **By the end of today** you can answer "who is near me?" without scanning, and you
> know where the bugs are.

---

## Read first

- [ ] [**Geospatial: turning "near me" into a key lookup**](../../content/week-10/day-1/geospatial.md) — 30 min · sources: [H3](https://h3geo.org/docs/), [S2](https://s2geometry.io/), [Uber DeepETA](https://www.uber.com/blog/deepeta-how-uber-predicts-arrival-times/), [DeeprETA](https://arxiv.org/pdf/2206.02127)

Read H3's introduction and its resolution table. The table turns "what resolution?" from a
guess into arithmetic.

---

## The lab

`geo.py` — square cells, because the arithmetic is visible. Real systems use hexagons or a
space-filling curve; the mechanism and the edges are identical.

```python
cell_of(lat, lng, resolution)        neighbours(cell)      haversine_m(a, b)
CellIndex(resolution)  .insert  .move  .search(lat, lng, ring)  .within(...)
cell_side_metres(resolution)   candidates_at_resolution(density, resolution, ring)
churn_writes_per_second(objects, report_interval_s)
```

Two details worth getting right rather than approximately right:

- **Use `math.floor`, not `int`.** `int(-0.5)` is 0 and `floor(-0.5)` is -1. Getting this
  wrong puts half the planet in the wrong cells, and every test written with London
  coordinates passes anyway.
- **`move` reports whether the cell changed.** That boolean is the write load, and
  `churn_writes_per_second` turns it into the number that decides whether positions are
  durable at all.

```bash
pytest week-10/day-1 -v
```

`test_searching_one_cell_misses_a_neighbour_eleven_metres_away` is the day: no error, no
warning, and the nearest driver is a few paces away.

---

## The written exercise

`week-10/day-1/resolution-choice.md`, half a page.

For a dispatch service in a city:

1. Pick a resolution using `candidates_at_resolution` at 500 drivers/km², and say what a
   search costs
2. Run the same resolution at 5/km² and at 50,000/km². What happens at each end?
3. What would you do about the dense end? Name the mechanism from an earlier week

Question 3's answer is week 4 or week 8 — two populations, two answers — and noticing that
is worth more than the geospatial detail.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
