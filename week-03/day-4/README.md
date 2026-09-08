# Day 4 — The write-ahead log

> **By the end of today** you have a log that survives a power cut, and you can say
> exactly what "the write succeeded" means.

---

## Read first

- [ ] [**Write-ahead logs, and what durability costs**](../../content/week-03/day-4/write-ahead-logs-and-durability.md) — 30 min · sources: [PostgreSQL WAL](https://www.postgresql.org/docs/current/wal-intro.html), [SQLite WAL](https://www.sqlite.org/wal.html), [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html)

Read the SQLite atomic-commit page. It is the most concrete free account of what has to
happen for a commit to survive a power cut, and it will make you permanently suspicious
of the word "saved".

---

## The lab

`wal.py` — a real log, in a real file, damaged in the ways real crashes damage one.

```python
encode(payload)  -> bytes                # 4-byte length | 4-byte crc32 | payload
decode(data)     -> (records, clean)

WriteAheadLog(path)
    .append(payload)     # writes, flushes, and fsyncs before returning
    .recover()
    .checkpoint()
    .size_bytes()
```

Two things worth pausing on as you write them:

**`flush` then `fsync`.** The flush moves bytes from Python to the operating system. The
fsync moves them from the operating system to the device. Only the second one is
durability, and the gap between them is where "it said it saved" and "it did not save"
live.

**Stop at the first bad record.** Not "skip it and continue". One test asserts that an
intact record *after* a corrupt one is thrown away, and people argue with that test
before they think about it. The argument is in the article: a log is only useful if
replaying it produces a state the system could actually have been in, and a prefix is
such a state while a subset with a hole in it is not.

```bash
pytest week-03/day-4 -v
```

---

## The written exercise

`week-03/day-4/durability-of-my-designs.md`, half a page.

For each of your three designs so far — the link shortener, the rate limiter, the
metrics store — answer:

1. What does "accepted" mean? At which instant is a client's write safe?
2. What is lost if the process is killed one millisecond after you said yes?
3. Is that acceptable, and **which line of the envelope says so?**

Question 3 is the one to spend time on. If none of your envelopes say anything about
this, then you have been making a durability decision every week without writing it
down — and that is worth discovering today rather than in an incident.

---

## Tomorrow

The milestone. Read `week-03/milestone/README.md` tonight. Run `retention_bytes` on the
brief's numbers before Friday morning — the answer changes what you design.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
