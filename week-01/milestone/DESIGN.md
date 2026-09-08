# Link shortener — design

*Your name · Week 1 milestone · date*

> Fill every section. Two to three pages. **No technology names anywhere** — see
> `week-01/FENCE.md`. Delete these instruction blocks as you go.

---

## 1. Interrogate

### What it does

> Three to five bullets. What a user or caller can do. No components.

### Envelope

| Dial | Target | Given or assumed? |
|---|---|---|
| Availability | | |
| Redirect latency | | |
| Create latency | | |
| Durability | | |
| Freshness | | |
| Retention | | |
| Storage ceiling | | |

> Every row a number. If you cannot write a number, write "not specified — assuming X"
> and carry on. An unlabelled assumption is the thing you will be caught on.

### Not building

> The list. One line. Thirty seconds of work, and it is the clearest signal of
> experience in the whole document.

### Open questions

> What you would ask if you could. Two or three. Say what each answer would change —
> a question whose answer changes nothing is not worth asking.

---

## 2. Size

> Paste the output of `estimate.py`, then say what each number **means**. The numbers
> alone are not the pass; noticing what they imply is.

```
(paste)
```

**What these say about the design:**

- Writes:
- Reads:
- The ratio:
- Retention against the ceiling:
- The working set:

**The one number that decides this design, and why:**

---

## 3. Contract

### API

```
POST   /links          {url, alias?}   -> {code}
GET    /{code}                          -> 302
DELETE /links/{code}                    -> 204
```

> Adjust to your design. Say what happens on each error case — a duplicate alias, an
> unknown code, a malformed URL.

### Entities

| Entity | Fields | Must answer |
|---|---|---|
| | | |

> The "must answer" column is the important one. Name the query, and check that the way
> you organised the data can serve it without scanning.

---

## 4. Path

### Creating a link

1.
2.
3.

### Following a link

1.
2.
3.

> Ordered hops, not a picture. Then: **which hop is the slowest, and what is your
> latency budget for the whole path?** Use `budget_remaining` from day 3.

---

## 5. Decide

> Three to five. This format, every time. A decision without a price is a preference.

### Decision 1 —

**Rejected:**
**Because:**
**Price:**

### Decision 2 —

**Rejected:**
**Because:**
**Price:**

### Decision 3 —

**Rejected:**
**Because:**
**Price:**

---

## 6. Break

| Component | Dead | Slow | Lying |
|---|---|---|---|
| | | | |

> Every row filled. The **slow** column is the one that matters and the one people
> leave blank.

Then, specifically:

- **Cold start.** Nothing cached, every redirect a miss. What is the load on the store,
  and did you size for it?
- **Alias collision.** Two callers ask for the same custom alias in the same
  millisecond.
- **Miss flood.** A million requests for codes that do not exist.

---

## 7. Evolve

**At 10x** — what breaks first, and why that thing before the others:

**The metric that would tell me** — one metric, and the number at which I would act:

**What I would do about it** — one paragraph, no more:

---

## Sources

> Any claim here about how something behaves in the real world: cite it with a tier and
> a date, in `content/sources/`. If you made no such claims, say so on one line — that
> is a fine answer for a design this small, and saying it deliberately is the point.
