"""Day 4 — ids.

`test_sortable_ids_all_land_in_one_partition` is the day. Everything else is the
machinery that makes it possible to write.
"""

import pytest

from ids import (
    MAX_NODE,
    MAX_SEQUENCE,
    ClockWentBackwards,
    SequenceExhausted,
    SnowflakeGenerator,
    decode,
    hash_partitions,
    range_partitions,
)
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


def generate(sim, generator, milliseconds, per_ms):
    ids = []
    for _ in range(milliseconds):
        advance(sim, 1)
        ids.extend(generator.next_id() for _ in range(per_ms))
    return ids


# -- the id -------------------------------------------------------------------


def test_ids_are_unique(sim):
    generator = SnowflakeGenerator(sim, node_id=7)
    ids = generate(sim, generator, milliseconds=50, per_ms=20)
    assert len(set(ids)) == 1_000


def test_ids_sort_by_creation_time(sim):
    generator = SnowflakeGenerator(sim, node_id=7)
    ids = generate(sim, generator, milliseconds=50, per_ms=20)
    assert ids == sorted(ids)


def test_an_id_carries_its_time_node_and_sequence(sim):
    generator = SnowflakeGenerator(sim, node_id=7)
    advance(sim, 1_234)
    first = generator.next_id()
    second = generator.next_id()

    assert decode(first) == (1_234, 7, 0)
    assert decode(second) == (1_234, 7, 1)


def test_the_epoch_is_yours_to_choose(sim):
    generator = SnowflakeGenerator(sim, node_id=1, epoch_ms=1_000)
    advance(sim, 5_000)
    timestamp, node, _ = decode(generator.next_id(), epoch_ms=1_000)
    assert (timestamp, node) == (5_000, 1)


def test_two_nodes_never_collide(sim):
    """No lock, no round trip. The node field partitions the id space rather than
    sharing it — the same move as everything else this week, applied to a counter."""
    a = SnowflakeGenerator(sim, node_id=1)
    b = SnowflakeGenerator(sim, node_id=2)
    advance(sim, 10)
    ids = {a.next_id() for _ in range(100)} | {b.next_id() for _ in range(100)}
    assert len(ids) == 200


@pytest.mark.parametrize("node_id", [-1, MAX_NODE + 1, 5_000])
def test_an_impossible_node_id_is_an_error(sim, node_id):
    with pytest.raises(ValueError):
        SnowflakeGenerator(sim, node_id=node_id)


# -- the two ways it fails ----------------------------------------------------


def test_the_sequence_runs_out(sim):
    """4,096 ids in one millisecond, and then no more. A real generator spins
    until the next millisecond; this one tells you, because a lab that busy-waits
    on a simulated clock never returns."""
    generator = SnowflakeGenerator(sim, node_id=1)
    advance(sim, 1)
    for _ in range(MAX_SEQUENCE + 1):
        generator.next_id()
    with pytest.raises(SequenceExhausted):
        generator.next_id()


def test_the_sequence_resets_next_millisecond(sim):
    generator = SnowflakeGenerator(sim, node_id=1)
    advance(sim, 1)
    for _ in range(MAX_SEQUENCE + 1):
        generator.next_id()
    advance(sim, 1)
    assert decode(generator.next_id())[2] == 0


def test_a_backwards_clock_stops_the_generator(sim):
    """The right behaviour, and it is a choice: a generator that stops is an
    incident, and one that issues duplicates is a data-loss bug found weeks later."""
    generator = SnowflakeGenerator(sim, node_id=1)
    advance(sim, 1_000)
    generator.next_id()
    with pytest.raises(ClockWentBackwards):
        generator.next_id(now_ms=999)


def test_it_recovers_once_the_clock_catches_up(sim):
    generator = SnowflakeGenerator(sim, node_id=1)
    advance(sim, 1_000)
    generator.next_id()
    with pytest.raises(ClockWentBackwards):
        generator.next_id(now_ms=999)
    assert generator.next_id(now_ms=1_001) > 0


# -- the sting ----------------------------------------------------------------

DAY_MS = 86_400_000
DAY_ID_SPACE = DAY_MS << 22        # a whole day of ids, in id units


def test_sortable_ids_all_land_in_one_partition(sim):
    """The day, in one assertion.

    Ranges were split for a day of traffic. Every id generated in this run is
    adjacent to the last, so every one lands in the same partition. Fifteen
    machines hold history and are idle; one takes every write.

    Nothing is wrong with the id scheme. This is what "sortable" means.
    """
    generator = SnowflakeGenerator(sim, node_id=7)
    ids = generate(sim, generator, milliseconds=50, per_ms=20)

    counts = range_partitions(ids, 16, low=0, high=DAY_ID_SPACE)
    assert max(counts) == len(ids)
    assert sum(1 for c in counts if c > 0) == 1


def test_the_same_ids_hashed_spread_evenly(sim):
    """Same ids, different scheme, and the hotspot is gone — along with any hope
    of a range scan. That is Tuesday's trade, now with numbers."""
    generator = SnowflakeGenerator(sim, node_id=7)
    ids = generate(sim, generator, milliseconds=50, per_ms=20)

    counts = hash_partitions(ids, 16)
    assert min(counts) > 0
    assert max(counts) / (sum(counts) / 16) < 1.3


def test_range_partitioning_is_not_wrong_it_is_conditional():
    """Given ids spread across the whole space, ranges distribute perfectly well.
    The problem is never the scheme; it is the scheme applied to keys that grow."""
    spread = [i * (DAY_ID_SPACE // 1_000) for i in range(1_000)]
    counts = range_partitions(spread, 16, low=0, high=DAY_ID_SPACE)
    assert min(counts) > 0


def test_ids_outside_the_range_are_clamped():
    counts = range_partitions([-5, 10**30], 4, low=0, high=100)
    assert counts[0] == 1 and counts[-1] == 1


def test_an_empty_range_is_an_error():
    with pytest.raises(ValueError):
        range_partitions([1], 4, low=10, high=10)


def test_zero_partitions_is_an_error():
    with pytest.raises(ValueError):
        hash_partitions([1], 0)
