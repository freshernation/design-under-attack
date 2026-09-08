# Day 2 — Collaborative editing

> **By the end of today** you have built a data type that converges without a server,
> and you know why convergence is not the same as correctness.

---

## Read first

- [ ] [**Collaborative editing: converging without a lock**](../../content/week-10/day-2/collaborative-editing.md) — 30 min · sources: [Apache Wave — OT](https://svn.apache.org/repos/asf/incubator/wave/whitepapers/operational-transform/operational-transform.html), [Shapiro et al.](https://inria.hal.science/inria-00555588), [Automerge](https://automerge.org/docs/), [Yjs](https://docs.yjs.dev/)

Note what is **not** in that list: Google Docs. The technique comes from a 1995 paper that
is not freely available, and Google has published almost nothing about its own
implementation. A week-1 lesson arriving in a week-10 topic — the most famous instance of a
technique is often the least documented.

---

## The lab

`crdt.py` — the simple types first, then a text sequence.

```python
GCounter(node)  PNCounter(node)  TwoPhaseSet()  LWWRegister(node)
RGA(node)  .insert_after(after_id, char)  .delete(id)  .text()  .merge(other)
```

Start with `GCounter`. Merging takes the **maximum** per node rather than adding, and
understanding why — merging the same state twice must not double anything — is most of the
family in one line.

`TwoPhaseSet` has a rule that looks like a bug: a removed element can never return. It is
what makes the type converge, and it is why the type is so often the wrong choice. Both
halves of that are worth carrying.

`RGA` is the meaty one. Build it in this order: elements with ids, then `text()` with the
descending-id ordering rule, then `delete` as a tombstone, then `merge` as a union.

```bash
pytest week-10/day-2 -v
```

Two tests are the day. `test_replicas_converge_whatever_the_order` is the property the
whole family exists to provide. `test_convergence_is_not_correctness` is its honest limit —
everyone agrees, and the result can still be nonsense.

---

## The written exercise

`week-10/day-2/crdt-or-ot.md`, half a page.

For each, choose OT or a CRDT and give one sentence:

1. A shared document in a product that already has a central server
2. A mobile note-taking app used on planes
3. A collaborative whiteboard where objects are moved rather than text edited
4. A shopping cart shared between a user's phone and laptop

Number 3 is the interesting one: it is not text, so most of the difficulty disappears and a
simple map-of-registers CRDT does the job. Number 4 you already met in week 5.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
