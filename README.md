# Designing Systems

Twelve weeks learning to design a system you have never seen, size it, and defend it
against someone attacking it.

This is not a tour of famous architectures. A student who memorises fifteen answers
freezes on the sixteenth question, and the sixteenth question is the one you get asked.
What transfers is the method — and real systems, read from primary sources, are the
evidence rather than the syllabus.

---

## The three rules

**1. No claim without a source, no source without a date.**
Ask anything how a famous system works and you get a fluent, confident answer with no
citations, a portion of which is wrong or a decade old. You will not be able to tell
which portion. So every architectural claim you write down carries a tier and a date,
and `python3 tools/check_sources.py` enforces it. See [`SOURCES.md`](SOURCES.md).

**2. Arithmetic before architecture.**
You may not choose a component before you have counted the load. A design that would be
identical with a thousand users and a billion has not engaged with the problem, because
the scale *is* the problem.

**3. A design nobody has attacked is a draft.**
Every week ends with twenty minutes of somebody trying to break your document. That is
the grade. The tests are not.

---

## The seven passes

The spine of the course. Every milestone runs all seven; every week deepens one or two.

| Pass | Produces | The failure it prevents |
|---|---|---|
| **1 Interrogate** | requirements, the envelope, explicit non-goals | designing for a problem nobody stated |
| **2 Size** | QPS, storage, bandwidth, fan-out, working set | boxes drawn before numbers |
| **3 Contract** | the API, the entities, the access patterns | a data model that cannot serve the query |
| **4 Path** | the ordered hops of one read and one write | a diagram that hides the work |
| **5 Decide** | 3–5 trade-offs, each with its rejected alternative | "I'd use Kafka", with no reason attached |
| **6 Break** | per component: dead, slow, or lying | a design that only works on a good day |
| **7 Evolve** | what breaks first at 10x, and the metric for it | a snapshot instead of a system |

---

## The twelve weeks

| Week | | Milestone |
|---|---|---|
| 1 | A design is a set of decisions | A link shortener, under a storage ceiling |
| 2 | Queues, utilisation and latency | A rate limiter, on twelve edge servers |
| 3 | Storage and the data model | A metrics store, under a storage ceiling |
| 4 | Partitioning and routing | A job queue whose whale cannot be split |
| 5 | Replication and consistency | A coordination service |
| 6 | Caching and the read path | A catalogue read path, against a fixed origin |
| 7 | Logs, queues and idempotency | An ad-click aggregator |
| 8 | **Realtime and fan-out** | **Project 2** — chat, and the four-source read |
| 9 | Failure and operations | A resilience review of Project 2 |
| 10 | Deep track — geospatial, CRDTs, matching, serving | A specialised design, priced |
| 11 | **The full design** | **Project 3** — from one line of brief |
| 12 | The interview is the deliverable | Ten recorded mocks, scored |

Week 2 is where most people's intuition breaks. Week 8 is the keystone.

---

## How to work

```bash
source .venv/bin/activate          # every session

pytest week-01/day-2 -v            # one day
pytest week-01 -v                  # one week
python3 tools/check_sources.py     # your claims
python3 tools/check_links.py       # your links
```

Tests are the *smallest* part of the grade here, and it is worth being clear about that
on day one. `pytest` can check that you divided by 86,400 correctly. It cannot check
whether you should have put a queue there. Three graders:

| | Checks | Can it be faked |
|---|---|---|
| `pytest` | the arithmetic and the mechanisms | no |
| The milestone rubric | that all seven passes were run | partly |
| **The Friday defence** | whether you can hold it under attack | no |

**1,086 lab tests** across all twelve weeks, and every one of them fails before you
write anything. The 24 tests in `tests/` are the harness's own plus four repo guards, and they ship
green — you use `simlib`, you do not build it. One of the four skips for you: it checks
that every lab has a reference solution, and the solutions are in your instructor's
private repository rather than yours.

---

## Map

| Path | What it is |
|---|---|
| [`SETUP.md`](SETUP.md) | Day zero. Do this before anything else |
| [`SOURCES.md`](SOURCES.md) | The source doctrine. The rule that makes this course different |
| `week-01/` … `week-12/` | Four days, a milestone, a fence, a defence |
| [`content/`](content/README.md) | The reading for every day, each opening with its primary sources |
| `content/sources/` | The claims ledgers — what is known, inferred, and unknown |
| [`ai/`](ai/README.md) | Your six AI roles — librarian, tutor, editor, interviewer, defend, roommate |
| `simlib/` | The deterministic harness the later labs run on |
| `tools/` | The two checkers |
| `logs/` | Your stuck log and your daily five numbers |
| [`CUT_LIST.md`](CUT_LIST.md) | What this course deliberately does not teach, and why |

Each week has a `FENCE.md` listing what you have met and what you have not. Paste both
lists into any AI role before you use it — it is what stops the model teaching you
something six weeks early and making your toolkit feel inadequate.

Both logs are **read by your instructor before every live hour.** They are not marked.
An honest amber gets you help; a blank log gets you asked why it is blank.

---

## The decision library

The thing you actually carry out of this course. Roughly thirty one-page trade-off cards
— the decision, the alternatives, the conditions that flip the answer, and a primary
source where one exists — accumulated one milestone at a time.

It is what lets you design a system nobody has written a blog post about, which is the
only thing that generalises.

---

## What this is not about

Memorising architectures. Naming technologies. Being able to say what Netflix does.

You will produce designs a senior engineer would call naive, and that is correct in week
1. A naive design whose numbers you derived and whose failure modes you have thought
about beats a sophisticated one assembled from blog posts, and it is not close — the
second kind collapses the moment somebody asks why.
