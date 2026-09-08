# Writing the document

*Week 11 · Day 2 · about 25 minutes*

> By the end of this you can structure a design document that survives being read
> without you in the room — which is the only way it is ever read.

---

## Why the document is the deliverable

From week 1, and now with ten of them behind you.

A design is not a diagram and not a conversation. It is a document, because a document can
be read by somebody who was not there, attacked in your absence, and disagreed with
precisely. A confident presenter with a nice diagram survives scrutiny that a written
sentence does not.

This week's document is the one you will still be talking about in week 12 and in
interviews after that. It is worth more care than the previous ten.

---

## The shape

The seven passes are the spine, and the document follows them because a reader follows
them:

| Section | What a reader is checking |
|---|---|
| **Problem and non-goals** | do you know what you were asked, and what you refused? |
| **Envelope** | are the requirements numbers, and are they measurable? |
| **Sizing** | were these derived, and do they agree with each other? |
| **API and data model** | can the model serve the queries the API promises? |
| **Request paths** | is there an ordered hop list for the critical read and write? |
| **Decisions** | does each name what it rejected, and what it cost? |
| **Failure modes** | dead, slow and lying, per component |
| **Growth** | what breaks first at 10x, and which metric shows it? |
| **What we do not know** | the sourced/inferred/unknown split, applied to your own design |

That last section is unusual and it is the one that most improves a document. Every design
rests on assumptions and estimates; listing them is not weakness, it is the difference
between a document a colleague can build on and one they have to reverse-engineer.

---

## Length, and what to cut

Four to six pages for Project 3. If you are past eight, you are explaining rather than
deciding.

What to cut, in order:

1. **Background nobody needs.** The reader knows what a cache is
2. **Descriptions of mechanisms.** "A circuit breaker prevents cascading failure" is a
   textbook sentence. "A breaker on the search dependency at 50% over 20 requests, because
   search failing must not delay message sends" is a decision
3. **Diagrams that no request passes through.** If you cannot trace a path through a box,
   it should not be in the picture
4. **Alternatives you never seriously considered.** Three rejected options where two were
   straw men is worse than one honest rejection

What never to cut: the numbers, the non-goals, and the prices attached to decisions.

---

## The tells a reader looks for

You have been accumulating these since week 1. Collected, because your own document should
be checked against them before anybody else sees it:

| Tell | What it usually means |
|---|---|
| A technology named with no property attached | a decision inherited rather than made |
| No number that was derived by multiplication | pass 2 was skipped |
| "Scalable", "highly available", "real-time" without a figure | a requirement nobody can check |
| A decision with no rejected alternative | a preference wearing a decision's clothes |
| A cache with no invalidation story | week 6 was skipped |
| A queue with no bound and no full-policy | week 2 was skipped |
| A component that appears in the diagram and in no request path | decoration |
| Availability promised above the dependency ceiling | pass 1 arithmetic was skipped |

Today's lab turns this table into a program.

---

## Writing for the reader you actually have

Two of them, and they want the same document for different reasons.

**A colleague who has to build it.** They want to know what to type on Monday. Precision
about the write path matters more than elegance; ambiguity costs them a meeting with you.

**A reviewer deciding whether to trust the design.** They are looking for the places you
have thought hardest and the places you have not, and they will find both. The fastest way
to signal the first is to be specific about costs — a document that says what each decision
made worse is far harder to attack than one that only lists benefits.

Both are helped by the same habit: **write the sentence that a critic would write, before
they do.** "This makes cross-user queries a scatter-gather, which is acceptable because
they are 0.1% of traffic" removes an entire line of attack and takes eleven words.

---

## Today's lab

`week-11/day-2/design_lint.py` — the tells table, as a program.

You have written ten design documents. Now write the thing that reviews them:

- `has_derived_numbers(text)` — is there arithmetic anywhere?
- `unmeasurable_claims(text)` — "scalable", "highly available", "real-time" with no figure
- `bare_technology_names(text)` — a product named with no property in the same sentence
- `sections_present(text)` — the seven passes, by heading
- `decisions_without_alternatives(text)` — a decision heading with no rejection near it
- `review(text)` — all of it, as a list of findings

Then run it on **your own week-8 Project 2**. It will find things. That is the point, and it
is a better argument for the checklist than this article.

---

> **Sources for this article**
> **Tier 3 — ours.** There is no authority on design-document structure, and anybody who
> claims otherwise is selling a template. The tells are accumulated from the previous ten
> weeks and every one of them has a source in the week it came from.
