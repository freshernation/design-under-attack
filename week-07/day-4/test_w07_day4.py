"""Day 4 — consumer groups, rebalancing, and lag."""

import pytest

from consumers import (
    Group,
    assign,
    at_risk_of_data_loss,
    lag,
    rebalances_during_deploy,
    reprocessed_on_rebalance,
    total_lag,
)


# -- assignment ---------------------------------------------------------------


def test_partitions_are_spread_evenly():
    result = assign(6, ["a", "b", "c"])
    assert sorted(len(v) for v in result.values()) == [2, 2, 2]
    assert sorted(p for ps in result.values() for p in ps) == list(range(6))


def test_an_uneven_split_is_as_even_as_possible():
    result = assign(7, ["a", "b", "c"])
    assert sorted(len(v) for v in result.values()) == [2, 2, 3]


def test_assignment_is_deterministic():
    """A rebalance that gave a different answer for the same inputs would make
    every failure irreproducible."""
    assert assign(6, ["c", "a", "b"]) == assign(6, ["a", "b", "c"])


def test_you_cannot_have_more_consumers_than_partitions():
    """The ceiling on parallelism, set when the topic was created. Two consumers
    are permanently idle, and no amount of scaling changes it."""
    result = assign(6, [f"c{i}" for i in range(8)])
    idle = [c for c, ps in result.items() if not ps]
    assert len(idle) == 2


def test_no_consumers_means_nothing_is_assigned():
    assert assign(4, []) == {}


def test_a_topic_needs_a_partition():
    with pytest.raises(ValueError):
        assign(0, ["a"])


# -- membership ---------------------------------------------------------------


def test_joining_redistributes():
    group = Group(partitions=4)
    group.join("a")
    assert group.assignment["a"] == [0, 1, 2, 3]

    group.join("b")
    assert len(group.assignment["a"]) == 2
    assert len(group.assignment["b"]) == 2


def test_leaving_redistributes():
    group = Group(partitions=4)
    group.join("a")
    group.join("b")
    group.leave("b")
    assert group.assignment["a"] == [0, 1, 2, 3]


def test_a_group_with_nobody_in_it():
    assert Group(partitions=4).assignment == {}


def test_idle_consumers_are_named():
    group = Group(partitions=2)
    for name in ("a", "b", "c", "d"):
        group.join(name)
    assert group.idle == ["c", "d"]


def test_leaving_twice_is_harmless():
    group = Group(partitions=2)
    group.join("a")
    group.leave("a")
    assert group.leave("a") == {}


# -- what a rebalance costs ---------------------------------------------------


def test_work_between_the_last_commit_and_the_reassignment_happens_twice():
    """The consumer processed to offset 940 and last committed at 900. It loses
    the partition; the new owner starts at 900. Forty records are done again —
    a duplicate source with a name, and one your idempotency has to cover."""
    assert reprocessed_on_rebalance(committed_offset=900, processed_offset=940) == 40


def test_a_consumer_that_commits_often_loses_little():
    assert reprocessed_on_rebalance(940, 940) == 0


def test_a_rolling_deploy_rebalances_twice_per_instance():
    """A leave and a join each. Twenty instances is forty rebalances, which is why
    throughput dips for a minute after every release."""
    assert rebalances_during_deploy(20) == 40
    assert rebalances_during_deploy(20, rolling=False) == 2


# -- lag ----------------------------------------------------------------------


def test_lag_is_per_partition():
    ends = {0: 100, 1: 100, 2: 100}
    committed = {0: 100, 1: 90, 2: 50}
    assert lag(ends, committed) == {0: 0, 1: 10, 2: 50}


def test_a_partition_never_polled_is_fully_behind():
    assert lag({0: 100}, {}) == {0: 100}


def test_the_total_hides_the_hot_partition():
    """Sixty-four partitions. The total says 12,000 records behind across the whole
    topic, which sounds like a modest backlog. One partition holds all of it and is
    an outage in waiting."""
    ends = {p: 10_000 for p in range(64)}
    committed = {p: 10_000 for p in range(64)}
    committed[17] = 0

    per_partition = lag(ends, committed)
    assert total_lag(ends, committed) == 10_000
    assert max(per_partition.values()) == 10_000
    assert sum(1 for v in per_partition.values() if v == 0) == 63


# -- the alert nobody has -----------------------------------------------------


def test_a_consumer_near_the_retention_edge_is_about_to_lose_data():
    """It will not get an error. The records are simply gone when it arrives."""
    assert at_risk_of_data_loss(lag_records=850_000, retention_records=1_000_000) is True


def test_a_healthy_consumer_is_not():
    assert at_risk_of_data_loss(lag_records=5_000, retention_records=1_000_000) is False


def test_a_fixed_threshold_would_have_missed_it():
    """The reason this alert is phrased against retention rather than a number:
    the same lag is fine on a long retention and fatal on a short one."""
    assert at_risk_of_data_loss(90_000, retention_records=100_000) is True
    assert at_risk_of_data_loss(90_000, retention_records=10_000_000) is False


def test_no_retention_is_an_error():
    with pytest.raises(ValueError):
        at_risk_of_data_loss(100, 0)
