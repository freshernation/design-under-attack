"""Day 1 — the log."""

import pytest

from log import ConsumerGroup, Log, Partition


# -- the partition ------------------------------------------------------------


def test_offsets_start_at_zero_and_increase():
    partition = Partition(0)
    assert [partition.append(f"e{i}") for i in range(3)] == [0, 1, 2]
    assert partition.end_offset == 3


def test_reading_from_an_offset():
    partition = Partition(0)
    for i in range(5):
        partition.append(f"e{i}")
    assert partition.read(2) == [(2, "e2"), (3, "e3"), (4, "e4")]


def test_reading_respects_a_limit():
    partition = Partition(0)
    for i in range(10):
        partition.append(i)
    assert len(partition.read(0, max_records=3)) == 3


def test_reading_past_the_end_gives_nothing():
    partition = Partition(0)
    partition.append("only")
    assert partition.read(1) == []


def test_nothing_is_removed_by_reading():
    """The property that separates a log from a queue."""
    partition = Partition(0)
    partition.append("e0")
    assert partition.read(0) == [(0, "e0")]
    assert partition.read(0) == [(0, "e0")]


# -- retention ----------------------------------------------------------------


def test_truncation_removes_the_oldest():
    partition = Partition(0)
    for i in range(5):
        partition.append(i)
    assert partition.truncate_before(2) == 2
    assert partition.start_offset == 2
    assert partition.read(2) == [(2, 2), (3, 3), (4, 4)]


def test_offsets_do_not_shift_when_records_are_removed():
    """A consumer's stored offset has to keep meaning the same thing after a
    retention sweep, so offsets are never renumbered."""
    partition = Partition(0)
    for i in range(5):
        partition.append(i)
    partition.truncate_before(3)
    assert partition.read(3)[0] == (3, 3)
    assert partition.end_offset == 5


def test_a_consumer_that_falls_off_the_back_loses_data():
    """Silently. The records are simply not there when it arrives, and the only
    thing that would have warned you is lag compared against retention."""
    partition = Partition(0)
    for i in range(10):
        partition.append(i)
    partition.truncate_before(7)

    got = partition.read(2)
    assert got[0] == (7, 7), "it resumes at 7, and 2 through 6 are gone"
    assert len(got) == 3


# -- partitioning -------------------------------------------------------------


def test_the_same_key_always_lands_in_the_same_partition():
    log = Log(partitions=8)
    assert len({log.partition_for("campaign-42") for _ in range(50)}) == 1


def test_one_keys_records_are_ordered():
    log = Log(partitions=8)
    offsets = [log.append("user-1", f"e{i}") for i in range(5)]
    partitions = {p for p, _o in offsets}
    assert len(partitions) == 1
    assert [o for _p, o in offsets] == [0, 1, 2, 3, 4]


def test_different_keys_have_no_ordering_relationship():
    """The guarantee, stated as its limit. Two keys in different partitions carry
    no information about which happened first."""
    log = Log(partitions=8)
    keys = [f"user-{i}" for i in range(40)]
    assert len({log.partition_for(k) for k in keys}) > 1


def test_no_key_means_no_ordering_and_an_even_spread():
    log = Log(partitions=4)
    landed = [log.append(None, i)[0] for i in range(8)]
    assert sorted(landed) == [0, 0, 1, 1, 2, 2, 3, 3]


def test_a_log_needs_a_partition():
    with pytest.raises(ValueError):
        Log(partitions=0)


# -- consumer groups ----------------------------------------------------------


def test_a_consumer_starts_at_the_beginning():
    log = Log(partitions=1)
    for i in range(3):
        log.append("k", i)
    group = ConsumerGroup(log, "billing")
    assert [r for _o, r in group.poll(0)] == [0, 1, 2]


def test_polling_does_not_commit():
    """Where you commit relative to processing is the whole of tomorrow, so it had
    better not happen by accident."""
    log = Log(partitions=1)
    log.append("k", "e0")
    group = ConsumerGroup(log, "billing")
    group.poll(0)
    assert group.committed(0) == 0


def test_committing_advances_the_position():
    log = Log(partitions=1)
    for i in range(3):
        log.append("k", i)
    group = ConsumerGroup(log, "billing")
    group.commit(0, 2)
    assert [r for _o, r in group.poll(0)] == [2]


def test_two_groups_are_completely_independent():
    """What a queue cannot do: the same records consumed twice, by different
    systems, at different speeds, without either knowing about the other."""
    log = Log(partitions=1)
    for i in range(5):
        log.append("k", i)

    billing = ConsumerGroup(log, "billing")
    analytics = ConsumerGroup(log, "analytics")
    billing.commit(0, 5)

    assert billing.poll(0) == []
    assert len(analytics.poll(0)) == 5


def test_replay_is_setting_a_number():
    """The reason to choose a log. It is also a deliberate source of duplicates,
    which is why the effect has to be idempotent — Wednesday."""
    log = Log(partitions=1)
    for i in range(5):
        log.append("k", i)
    group = ConsumerGroup(log, "billing")
    group.commit(0, 5)

    group.seek(0, 0)
    assert len(group.poll(0)) == 5


# -- lag ----------------------------------------------------------------------


def test_lag_is_a_subtraction():
    log = Log(partitions=1)
    for i in range(10):
        log.append("k", i)
    group = ConsumerGroup(log, "billing")
    assert group.lag(0) == 10
    group.commit(0, 7)
    assert group.lag(0) == 3


def test_a_caught_up_consumer_has_none():
    log = Log(partitions=1)
    log.append("k", "e0")
    group = ConsumerGroup(log, "billing")
    group.commit(0, 1)
    assert group.lag(0) == 0


def test_the_total_hides_a_drowning_partition():
    """Four partitions, three idle, one badly behind. The total looks like a
    modest backlog; per-partition it is a hot key and an outage in waiting."""
    log = Log(partitions=4)
    for i in range(400):
        log.append("celebrity", i)
    for i in range(3):
        log.append(f"quiet-{i}", i)

    group = ConsumerGroup(log, "billing")
    per_partition = [group.lag(p) for p in range(4)]
    assert max(per_partition) > 300
    assert sum(1 for lag in per_partition if lag < 5) >= 2
