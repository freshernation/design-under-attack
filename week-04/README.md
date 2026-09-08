# Week 4 — Partitioning and routing

> **Destination**
> Split data across machines, measure what that does to the distribution, and say
> which query you just made expensive.

Week 3 chose how data sits on one machine. This week it does not fit on one machine, and
the same question — *what is the key?* — stops being reversible.

---

## The week

| Day | Folder | What you'll be able to do |
|---|---|---|
| Mon | `day-1/` | Say which limit you are hitting, and measure a key's skew before committing |
| Tue | `day-2/` | Build a hash ring, and choose between hashing and ranges |
| Wed | `day-3/` | Find a hot key and pick a remedy, with its price |
| Thu | `day-4/` | Generate ids, and see what sortability does to your distribution |
| Fri | `milestone/` | Ship the job-queue design, then defend it |

---

## The one idea

**Partitioning divides load only if load is divisible.**

Everything hard this week comes from that. Real key distributions are not uniform — one
tenant, one channel, one product, one row — and a system that assumes otherwise has
assumed away its actual problem. Adding machines does not help a hot key, and the
dashboard will say the cluster is fine while one machine burns.

---

## What is new

**Reversibility.** A bad index is an afternoon; a bad partition key is a migration, with
every row moving while you serve traffic. That is why this week has more measurement in
it than any other and less opinion.

**Two irreducible conflicts.** Sortable ids give you locality *or* evenness, never both.
Splitting a hot key gives you distribution *or* ordering, never both. Neither resolves;
you choose, and you say what you gave up. Friday's milestone is built on the second one.

---

## Milestone

A multi-tenant job queue. One tenant is a quarter of the platform, jobs in a queue must
run in order, and that tenant has exactly one queue. Spec in `milestone/README.md`.

There is no answer that costs nothing. Finding that out, and picking anyway, is the week.

---

## What this week is not about

Choosing a database that does this for you. Most systems you meet will already have a
partitioning scheme, and your job will be to say why the current key is hurting and what
the alternative costs.

That is a conversation with numbers in it — skew, moved keys, utilisation of the busiest
partition — and the numbers are the whole reason the conversation can be settled instead
of argued.
