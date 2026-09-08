# What this course does not teach

An advisor's most valuable output is the cut list. Every item below is a real thing
engineers know, and every one is out.

- **Memorised architectures.** No "how Netflix works" week. Real systems appear as
  evidence for decisions, never as things to recite
- Cloud vendor specifics — no AWS/GCP/Azure service catalogues, no certifications
- Kubernetes, Terraform, service meshes, and infrastructure-as-code
- Writing production code for any of this. You design; you implement mechanisms, not
  services
- Database administration: tuning, index internals beyond LSM-versus-B-tree, query planners
- Machine learning systems beyond week 10's optional serving path
- Security beyond the design level — no cryptography, no auth protocol internals
- Cost modelling in vendor pricing detail
- Frontend and mobile architecture
- Microservice organisational theory, team topologies, Conway's Law essays
- Whiteboard theatrics — the "always start by asking about scale" scripts
- Every framework, tool and pattern catalogue that will be renamed within two years

---

## Why

Every item above is learnable later in about a week, and **none of them is what fails
people in a design round.**

What fails people is: not sizing, choosing components before requirements, being unable
to name what they rejected, having no answer when a dependency is *slow* rather than
dead, and repeating a claim they cannot source. Those five things are the whole course.

Say this out loud in week 1. Students who know *why* something was cut stop worrying
that they are missing it, and that worry is a major cause of drift in month two.

---

## The one that will be argued about

**No memorised architectures.** Every competitor teaches exactly that, and it is what
students think they are buying.

The case against: an architecture you memorised is worth something only if you are asked
about that system, at the scale that post described, in the year it was written. It
transfers to nothing. Worse, it is actively misleading — the published version of a
system is a snapshot of a company with constraints you do not have, and copying it into
a design for a different problem is the most common way a good candidate produces a bad
answer.

The famous systems are all still here. You read them as **evidence** — the source of a
specific decision, with its date and its conditions attached — and never as a template.

---

## What to add afterwards, in order

If you finish and want more, roughly the order that pays back:

1. **One database, properly.** Postgres internals or Cassandra's data model. The most
   common real gap
2. **Run something in production.** Any size. Nothing teaches failure modes like being
   paged by one
3. **Read three papers end to end** — Dynamo, Raft, and one from your own domain
4. **A cost model** for something you designed here, in real prices
5. **The organisational half** — how these decisions actually get made, which this
   course deliberately ignores and which decides most real architectures
