"""Day 3 — bounded queues.

The last three tests are the week's argument. Read them even if they pass.
"""

import pytest

from backpressure import BoundedQueue, run_workload
from simlib import Simulation


# -- the queue itself ---------------------------------------------------------


def test_it_holds_things_in_order():
    sim = Simulation()
    q = BoundedQueue(sim, capacity=10)
    for i in range(3):
        assert q.offer(i) is True
    assert len(q) == 3
    assert [q.poll()[0] for _ in range(3)] == [0, 1, 2]
    assert q.poll() is None


def test_reject_refuses_when_full():
    sim = Simulation()
    q = BoundedQueue(sim, capacity=2, policy="reject")
    assert q.offer("a") is True
    assert q.offer("b") is True
    assert q.offer("c") is False
    assert q.rejected == 1
    assert q.accepted == 2
    assert [q.poll()[0], q.poll()[0]] == ["a", "b"], "the newcomer was refused, not swapped in"


def test_drop_oldest_evicts_the_front():
    sim = Simulation()
    q = BoundedQueue(sim, capacity=2, policy="drop_oldest")
    q.offer("a")
    q.offer("b")
    assert q.offer("c") is True
    assert q.dropped == 1
    assert q.rejected == 0
    assert [q.poll()[0], q.poll()[0]] == ["b", "c"], "the oldest went, not the newest"


def test_grow_ignores_capacity():
    sim = Simulation()
    q = BoundedQueue(sim, capacity=2, policy="grow")
    for i in range(100):
        assert q.offer(i) is True
    assert len(q) == 100
    assert q.rejected == 0 and q.dropped == 0


@pytest.mark.parametrize("policy", ["block", "", "REJECT", "drop"])
def test_an_unknown_policy_is_an_error(policy):
    with pytest.raises(ValueError):
        BoundedQueue(Simulation(), capacity=10, policy=policy)


@pytest.mark.parametrize("capacity", [0, -1])
def test_a_queue_with_no_capacity_is_an_error(capacity):
    with pytest.raises(ValueError):
        BoundedQueue(Simulation(), capacity=capacity)


def test_age_is_measured_in_simulated_time():
    sim = Simulation()
    q = BoundedQueue(sim, capacity=10)
    assert q.oldest_age_ms() == 0
    q.offer("a")
    sim.schedule(250, lambda: None)
    sim.run()
    assert q.oldest_age_ms() == 250


def test_an_empty_queue_has_no_age():
    sim = Simulation()
    q = BoundedQueue(sim, capacity=10)
    q.offer("a")
    q.poll()
    assert q.oldest_age_ms() == 0


# -- under capacity -----------------------------------------------------------


def test_a_system_that_is_keeping_up_barely_queues():
    result = run_workload(arrival_rate=100, service_rate=200, duration_s=10)
    assert result["served_count"] == 1000
    assert result["rejected"] == 0
    assert result["peak_depth"] <= 2
    assert result["peak_age_ms"] < 20
    assert result["final_depth"] == 0


# -- overloaded ---------------------------------------------------------------


@pytest.fixture(scope="module")
def overload():
    """Arrivals at twice the service rate, for ten seconds, three ways."""
    common = dict(arrival_rate=200, service_rate=100, duration_s=10, capacity=100)
    return {p: run_workload(policy=p, **common) for p in ("grow", "reject", "drop_oldest")}


def test_the_unbounded_queue_falls_five_seconds_behind(overload):
    grow = overload["grow"]
    assert grow["peak_depth"] == pytest.approx(1000, rel=0.05)
    assert grow["peak_age_ms"] == pytest.approx(5000, rel=0.05)
    assert grow["rejected"] == 0, "it never refused anything, which is the problem"


def test_a_bound_keeps_the_backlog_to_a_second(overload):
    reject = overload["reject"]
    assert reject["peak_depth"] == 100
    assert reject["peak_age_ms"] < 1_100
    assert reject["rejected"] > 800


def test_dropping_the_oldest_keeps_it_freshest(overload):
    dropped = overload["drop_oldest"]
    assert dropped["peak_age_ms"] < overload["reject"]["peak_age_ms"]
    assert dropped["dropped"] > 800
    assert dropped["rejected"] == 0


def test_and_it_serves_the_freshest_work(overload):
    """Under drop_oldest the consumer is working on recent items. Under reject it
    is working through a backlog of stale ones."""
    assert max(overload["drop_oldest"]["served"]) > max(overload["grow"]["served"])


# -- the argument -------------------------------------------------------------


def test_all_three_policies_serve_the_same_amount_of_work(overload):
    """The one to sit with.

    The unbounded queue did not serve one extra request. Capacity is set by the
    consumer, and no queue depth changes that. What the extra depth bought was
    five seconds of latency instead of one, and no signal that anything was wrong.

    A queue absorbs a burst. It cannot absorb a deficit.
    """
    counts = {p: r["served_count"] for p, r in overload.items()}
    assert max(counts.values()) - min(counts.values()) <= 1, counts


def test_the_unbounded_queue_hides_the_failure(overload):
    """`grow` accepted every request and rejected none, so every client-side
    metric says the service is healthy. It is five seconds behind."""
    assert overload["grow"]["accepted"] == 2000
    assert overload["grow"]["rejected"] == 0
    assert overload["grow"]["peak_age_ms"] > 4_000
