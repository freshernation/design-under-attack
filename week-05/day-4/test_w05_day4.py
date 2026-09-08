"""Day 4 — session guarantees.

Two tests are the day: the user watching their own edit vanish, and the same
scenario with nine lines of token handling in the way.
"""

import pytest

from session import Cluster, NoFreshReplica, Replica, Session, read_pool, stale_by


# -- what you get for free ----------------------------------------------------


def test_a_follower_read_can_return_the_old_value():
    """The user saves, reloads, and their change is gone. Nothing failed."""
    cluster = Cluster(followers=3)
    cluster.write("profile", "old")
    for i in range(3):
        cluster.replicate(i)

    cluster.write("profile", "new")
    assert cluster.leader.read("profile") == "new"
    assert cluster.read_any("profile") == "old"


def test_followers_advance_independently():
    cluster = Cluster(followers=3)
    for i in range(5):
        cluster.write(f"k{i}", i)

    cluster.replicate(0)
    cluster.replicate(1, upto=2)

    assert stale_by(cluster, 0) == 0
    assert stale_by(cluster, 1) == 3
    assert stale_by(cluster, 2) == 5


# -- read your writes ---------------------------------------------------------


def test_read_your_writes():
    """The same scenario, with a session in the way.

    The client wrote at version 2, so it will not accept an answer from a replica
    that has not reached version 2. Follower 0 is behind and is skipped; follower
    1 has it. No consensus, no majority, no round trip — one integer.
    """
    cluster = Cluster(followers=3)
    cluster.write("profile", "old")
    for i in range(3):
        cluster.replicate(i)

    session = Session(cluster)
    session.write("profile", "new")
    cluster.replicate(1)                      # only this one has caught up

    assert session.read("profile") == "new"


def test_a_new_session_may_read_anything():
    """Read-your-writes is a promise to *you*. Someone who has written nothing is
    owed nothing, and may be served by the most convenient replica."""
    cluster = Cluster(followers=3)
    cluster.write("profile", "old")
    cluster.replicate(0)
    cluster.write("profile", "new")

    assert Session(cluster).read("profile") == "old"


def test_it_raises_when_no_replica_has_caught_up():
    cluster = Cluster(followers=2)
    session = Session(cluster)
    session.write("k", 1)
    with pytest.raises(NoFreshReplica):
        session.read("k")


def test_a_named_replica_that_is_behind_is_refused():
    cluster = Cluster(followers=2)
    session = Session(cluster)
    session.write("k", 1)
    cluster.replicate(1)

    assert session.read("k", follower=1) == 1
    with pytest.raises(NoFreshReplica):
        session.read("k", follower=0)


# -- monotonic reads ----------------------------------------------------------


def test_time_does_not_run_backwards():
    """A client bounces between replicas — a retry, a rerouted request, a load
    balancer changing its mind. Without the token it sees version 5, then version
    2, and the page it is looking at goes backwards.

    Advancing the session on *read* is what stops it.
    """
    cluster = Cluster(followers=2)
    for i in range(5):
        cluster.write("counter", i)

    cluster.replicate(0)                      # fully caught up
    cluster.replicate(1, upto=2)              # behind

    session = Session(cluster)
    assert session.read("counter", follower=0) == 4

    with pytest.raises(NoFreshReplica):
        session.read("counter", follower=1)


def test_without_a_session_it_does_run_backwards():
    """The same two reads, no token. This is the default behaviour of every
    replicated read path that nobody has thought about."""
    cluster = Cluster(followers=2)
    for i in range(5):
        cluster.write("counter", i)
    cluster.replicate(0)
    cluster.replicate(1, upto=2)

    assert cluster.read_any("counter", follower=0) == 4
    assert cluster.read_any("counter", follower=1) == 1


def test_a_session_advances_past_what_it_wrote():
    cluster = Cluster(followers=1)
    session = Session(cluster)
    session.write("a", 1)
    cluster.write("b", 2)                     # somebody else's write
    cluster.replicate(0)

    assert session.read("b") == 2
    assert session.version == 2, "reading advanced the session, not just writing"


# -- bounding the staleness ---------------------------------------------------


def test_a_replica_that_falls_behind_leaves_the_pool():
    """Converting an invisible correctness problem into a visible capacity one.
    Losing read capacity is a much better problem than serving stale data."""
    cluster = Cluster(followers=3)
    for i in range(10):
        cluster.write(f"k{i}", i)

    cluster.replicate(0)
    cluster.replicate(1, upto=8)
    cluster.replicate(2, upto=3)

    assert read_pool(cluster, max_stale=2) == [0, 1]
    assert read_pool(cluster, max_stale=0) == [0]


def test_everyone_is_in_the_pool_when_nothing_has_happened():
    assert read_pool(Cluster(followers=3), max_stale=0) == [0, 1, 2]


def test_a_replica_knows_its_own_version():
    replica = Replica("r")
    assert replica.version == 0
    replica.apply(4, "k", "v")
    assert (replica.version, replica.read("k")) == (4, "v")
