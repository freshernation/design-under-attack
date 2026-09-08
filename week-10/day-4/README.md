# Day 4 — Serving models and media

> **By the end of today** you can size an inference service in the right unit, and
> explain why a video platform's architecture is decided by its bandwidth bill.

---

## Read first

- [ ] [**Serving models, and serving media**](../../content/week-10/day-4/serving-models-and-media.md) — 30 min · sources: [vLLM / PagedAttention](https://arxiv.org/abs/2309.06180), [NVIDIA Triton](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html), [OpenAI](https://openai.com/index/scaling-postgresql/), [Netflix Open Connect](https://openconnect.netflix.com/)
- [ ] *Optional:* [**Decentralised protocols**](../../content/week-10/day-4/decentralised-protocols.md) — 20 min · sources: [atproto](https://atproto.com/guides/overview), [Bluesky](https://docs.bsky.app/docs/advanced-guides/federation-architecture)

The optional article has no lab. It is also the best-documented system in the course, so if
you want to practise reading a real architecture entirely from primary sources, it is the
place.

---

## The lab

`serving.py`.

```python
static_batch_utilisation(lengths)      continuous_batch_utilisation(lengths, queue_depth)
tokens_per_second(batch_size, ms_per_step)
capacity_in_requests(tokens_per_second, mean_tokens_per_request)
time_to_first_token_ms(queued_tokens, tokens_per_second)
admission_by_tokens(queued_tokens, budget_tokens)
egress_cost(bytes_served, cost_per_gb, edge_fraction)
```

The batching figures are a **stipulated model**, as in weeks 3 and 9, and the tests assert
the direction of each effect rather than its magnitude.

`capacity_in_requests` exists so that one test can show why not to use it: the same
hardware, the same throughput, and a tenfold difference in capacity depending on how long
the answers happen to be.

```bash
pytest week-10/day-4 -v
```

---

## The written exercise

`week-10/day-4/expensive-thing.md`, half a page.

For each of the five milestone paths — including the two you will not choose — write one
sentence answering: **what is the expensive thing, and what does the design do to avoid
spending it?**

Five sentences. It takes fifteen minutes and it is the most transferable exercise in the
week, because it is exactly what you will do when somebody asks you to design something in
a domain nobody taught you.

---

## Tomorrow

The milestone. Read `week-10/milestone/README.md` tonight and pick your path. Then run
`break_even_volume` on the specialised mechanism you are about to adopt, before you adopt
it.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
