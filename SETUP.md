# Day zero

Twenty minutes. Do it before week 1, not during it.

---

## 1. Python

You need 3.10 or newer — the labs use `X | None` type syntax.

```bash
python3 --version
```

If that is missing or too old, install from [python.org](https://www.python.org/downloads/)
or your package manager.

## 2. The repository

```bash
git clone <your fork of this repo>
cd system-design
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Check it works

```bash
pytest tests/ -q
```

Twenty tests, all green. Those are the tests for `simlib/`, the simulation harness the
later weeks run on — it ships finished because you are not building it, you are using it.

```bash
pytest week-01 -q
```

**Almost everything red.** That is correct and it stays correct until you write the
code. Every lab in this repo ships as a stub that raises `NotImplementedError`.

```bash
python3 tools/check_sources.py
python3 tools/check_links.py
```

Both green.

## 4. A writing tool you will actually open

You will write a design document every week, in Markdown, in this repo. Any editor is
fine. What matters is that it is the same place as the code, because a design document
that lives in a different tool from the numbers stops agreeing with them by about week
three.

## 5. Your AI, set up properly

Read [`ai/README.md`](ai/README.md). Six roles, six files, and the rule is one fresh
chat per session with the whole role file pasted in first.

The one that matters most here is the **librarian** (`ai/librarian.md`), and it is the
one people skip. Any model will tell you how WhatsApp works. Very few will tell you who
said so, when, and which parts they are guessing — unless you make that the job.

---

## What you need to know already

- Enough Python to write a function and run `pytest`
- What a database is, roughly. Not how one works internally — that is week 3
- What an HTTP request is

That is the whole list. No distributed systems background is assumed.

**What you do not need:** a job in the industry, a computer science degree, or any
experience running production systems. Weeks are marked with a **deep track** for people
who have those; the core is written for people who do not.

---

## The one habit to start now

When you read anything about how a real system works, write down **who said it and
when** before you write down what they said.

It takes four seconds. It is the entire difference between knowing something and
having read something, and by week 4 you will not be able to read any other way.
