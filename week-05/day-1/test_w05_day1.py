"""Day 1 — a leader, its followers, and the gap between them.

Every failure in this file is a correct asynchronous system behaving as designed.
"""

import pytest

from replica import (
    Follower,
    Leader,
    acknowledged_writes_lost,
    build,
    entries_behind,
    lag_ms,
    most_current,
)
from simlib import Simulation


@pytest.fixture
def cluster():
    sim = Simulation(seed=3)
    network, leader, followers = build(sim, followers=2, latency_ms=(10, 40))
    return sim, network, leader, followers


# -- the basics ---------------------------------------------------------------


def test_the_leader_has_it_immediately(cluster):
    sim, _net, leader, _followers = cluster
    leader.write("x", 2)
    assert leader.read("x") == 2


def test_a_write_is_acknowledged_before_anyone_else_has_it(cluster):
    """The definition of asynchronous, as an assertion."""
    sim, _net, leader, followers = cluster
    version = leader.write("x", 2)
    assert version == 1
    assert followers[0].read("x") is None
    assert entries_behind(leader, followers[0]) == 1


def test_it_arrives_shortly(cluster):
    sim, _net, leader, followers = cluster
    leader.write("x", 2)
    sim.run()
    assert all(f.read("x") == 2 for f in followers)
    assert all(entries_behind(leader, f) == 0 for f in followers)


def test_versions_increase(cluster):
    sim, _net, leader, _followers = cluster
    assert [leader.write("k", i) for i in range(3)] == [1, 2, 3]


# -- "I just saved it and it is not there" ------------------------------------


def test_a_follower_read_returns_the_old_value():
    """The most common user-visible consequence of replication. Nothing failed;
    every component did exactly what it was designed to do."""
    sim = Simulation(seed=3)
    _net, leader, followers = build(sim, followers=2, latency_ms=(10, 40))

    leader.write("profile", "old")
    sim.run()
    leader.write("profile", "new")

    assert leader.read("profile") == "new"
    assert followers[0].read("profile") == "old", "the user's own edit, gone"


def test_lag_is_measured_in_time_not_entries():
    """'Four entries behind' means nothing without the write rate. '1,900 ms
    behind' is directly comparable to the freshness line in an envelope."""
    sim = Simulation(seed=3)
    _net, leader, followers = build(sim, followers=1, latency_ms=(500, 600))

    leader.write("x", 1)
    sim.run(until_ms=200)
    assert lag_ms(sim, leader, followers[0]) == pytest.approx(200, abs=5)

    sim.run()
    assert lag_ms(sim, leader, followers[0]) == 0


def test_a_caught_up_follower_has_no_lag(cluster):
    sim, _net, leader, followers = cluster
    leader.write("x", 1)
    sim.run()
    assert lag_ms(sim, leader, followers[0]) == 0


# -- the network is not orderly -----------------------------------------------


def test_entries_arriving_out_of_order_are_applied_in_order():
    """Jitter reorders messages. A follower that applied entry 7 before entry 6
    would be in a state the leader was never in, so the stream is buffered."""
    sim = Simulation(seed=5)
    _net, leader, followers = build(sim, followers=1, latency_ms=(1, 300))

    for i in range(20):
        leader.write(f"k{i}", i)
    sim.run()

    follower = followers[0]
    assert follower.applied_version == 20
    assert follower.store == {f"k{i}": i for i in range(20)}


def test_one_lost_message_stalls_everything_behind_it():
    """The test to sit with.

    A single dropped replication message and the follower stops applying — not
    just that entry, but every entry after it, for ever. Thirteen writes are
    buffered in memory and the follower's data is at version zero.

    It is not corrupt and it is not complaining. It is silently, arbitrarily
    stale, and only a lag metric would ever tell you.
    """
    sim = Simulation(seed=1)
    _net, leader, followers = build(sim, followers=1, latency_ms=10, loss=0.3)

    for i in range(20):
        leader.write(f"k{i}", i)
    sim.run()

    follower = followers[0]
    assert follower.applied_version < leader.version
    assert follower.pending, "later entries arrived and are waiting on the gap"
    assert entries_behind(leader, follower) > 5


# -- failover -----------------------------------------------------------------


def test_promotion_picks_the_most_current_follower():
    sim = Simulation(seed=7)
    _net, leader, followers = build(sim, followers=3, latency_ms=(10, 200))

    for i in range(10):
        leader.write(f"k{i}", i)
    sim.run(until_ms=60)

    promoted = most_current(followers)
    assert all(promoted.applied_version >= f.applied_version for f in followers)


def test_promotion_is_deterministic():
    sim = Simulation(seed=7)
    _net, _leader, followers = build(sim, followers=3)
    assert most_current(followers).name == most_current(followers).name


def test_acknowledged_writes_disappear_on_failover():
    """A true statement about a correctly implemented asynchronous system.

    Ten writes were acknowledged. The leader died. The most up-to-date follower
    has never seen some of them, and there is no copy anywhere. Those clients
    were told 'saved'.

    This is not a bug to fix in the lab. It is the bill for not waiting, and the
    only question a design has to answer is whether it is willing to pay it.
    """
    sim = Simulation(seed=7)
    _net, leader, followers = build(sim, followers=3, latency_ms=(80, 200))

    for i in range(10):
        leader.write(f"k{i}", i)
    sim.run(until_ms=40)          # the leader dies before replication finishes
    leader.crash()

    promoted = most_current(followers)
    lost = acknowledged_writes_lost(leader, promoted)
    assert lost > 0
    assert promoted.read(f"k{10 - 1}") is None


def test_nothing_is_lost_when_replication_had_finished():
    sim = Simulation(seed=7)
    _net, leader, followers = build(sim, followers=3, latency_ms=(10, 40))

    for i in range(10):
        leader.write(f"k{i}", i)
    sim.run()
    leader.crash()

    assert acknowledged_writes_lost(leader, most_current(followers)) == 0
