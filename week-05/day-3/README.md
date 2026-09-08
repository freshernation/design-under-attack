# Day 3 — Leader election

> **By the end of today** you have implemented Raft's election, and you can prove that
> no term ever has two leaders — under message loss, crashes and moving partitions.

---

## Read first

- [ ] [**Consensus, and enough Raft to argue about it**](../../content/week-05/day-3/consensus-and-raft.md) — 35 min · sources: [Raft §5.1–5.2](https://raft.github.io/raft.pdf), [raft.github.io](https://raft.github.io/), [etcd](https://etcd.io/docs/v3.5/learning/api/), [ZooKeeper](https://zookeeper.apache.org/doc/current/zookeeperOver.html)

**Read Raft §5.1 and §5.2 before you start.** Six pages, written to be read, and today's
lab is those two sections. Then spend ten minutes on the visualisation at raft.github.io —
watching an election happen is worth a lot.

---

## The biggest lab of the course so far

`election.py`. Budget three hours; it is worth every minute.

```python
RaftNode(name, sim, peers, tick_ms=10, heartbeat_ms=50, election_timeout_ms=(150, 300))
    .state       "follower" | "candidate" | "leader"
    .term  .voted_for  .leader  .leader_terms
    .start()

build_cluster(sim, n=5, latency_ms=(10, 30), loss=0.0)
current_leaders(nodes)   leader_terms(nodes)   split_brain_terms(nodes)
```

Build it in this order:

1. **The tick loop and heartbeats.** A leader that heartbeats and followers that stay
   quiet. No elections yet.
2. **Elections.** Candidates, `request_vote`, `vote`, and the majority count. Get
   `test_a_leader_is_elected` green.
3. **The one-vote-per-term rule.** This is where the safety property comes from.
4. **Check-quorum** — a leader that cannot reach a majority steps down. Without it, an
   old leader stranded in a minority keeps accepting writes, which is split brain.

Two things people get wrong, both worth knowing in advance:

- **Draw the election timeout from `sim.random`**, not the global `random`. The run has
  to be reproducible or a failing test is not a bug, it is a mood.
- **Re-randomise the timeout on every election.** Three candidates that time out together
  will keep doing so. There is no cleverer fix than randomness, and that is a real result
  rather than a shortcut.

```bash
pytest week-05/day-3 -v
```

The last test runs ten seeds of sustained abuse — loss, crashes, restarts, partitions
that move every 250 ms — and asserts `split_brain_terms(nodes) == {}`. Leaders come and
go and the cluster is often unavailable; none of that is a violation. Two leaders in one
term would be, and it cannot happen.

---

## The written exercise

`week-05/day-3/consensus-costs.md`, half a page.

1. Your cluster is 5 nodes across 3 datacentres, 15 ms apart. What does one write cost?
2. You are asked to move to 7 nodes for "more reliability". What actually changes?
3. Name one thing in your job-queue design that **should** go through consensus and one
   that should not, and say what distinguishes them.

Question 3 is the day's point. Consensus is for the small critical decisions — who is
leader, what the configuration is — and not for the bulk data, and being able to draw that
line quickly is worth a great deal in a design review.

---

## Log

`logs/stuck-log.md` and `logs/signal-log.md`.
