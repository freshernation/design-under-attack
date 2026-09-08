"""Day 2 — the ring.

Two of these are the day: `test_modulo_moves_three_quarters_of_the_keys` and
`test_virtual_nodes_fix_the_skew`. Both are measurements, not claims.
"""

import pytest

from ring import (
    HashRing,
    distribution,
    keys_moved,
    modulo_keys_moved,
    modulo_node_for,
    range_partition_for,
    skew_of,
)

KEYS = [f"key-{i}" for i in range(20_000)]


# -- the ring -----------------------------------------------------------------


def test_a_key_always_lands_on_the_same_node():
    ring = HashRing(["a", "b", "c"])
    assert ring.node_for("hello") == ring.node_for("hello")


def test_every_key_lands_somewhere_real():
    ring = HashRing(["a", "b", "c"])
    assert {ring.node_for(k) for k in KEYS[:500]} <= {"a", "b", "c"}


def test_an_empty_ring_has_nowhere_to_put_anything():
    with pytest.raises(LookupError):
        HashRing([]).node_for("hello")


def test_adding_a_node_twice_changes_nothing():
    ring = HashRing(["a", "b"])
    before = {k: ring.node_for(k) for k in KEYS[:200]}
    ring.add("a")
    assert ring.nodes == ["a", "b"]
    assert all(ring.node_for(k) == before[k] for k in before)


def test_removing_an_absent_node_is_an_error():
    with pytest.raises(KeyError):
        HashRing(["a"]).remove("b")


def test_a_node_needs_at_least_one_position():
    with pytest.raises(ValueError):
        HashRing(["a"], virtual_nodes=0)


# -- the reason it exists -----------------------------------------------------


def test_modulo_moves_three_quarters_of_the_keys():
    """Three nodes to four. Every one of those keys is a cache entry that just
    went cold, at the moment you were adding capacity because you were busy."""
    assert modulo_keys_moved(KEYS, 3, 4) > 0.7


def test_the_ring_moves_about_a_quarter():
    before = HashRing(["a", "b", "c"])
    after = HashRing(["a", "b", "c", "d"])
    assert keys_moved(before, after, KEYS) < 0.4


def test_the_ring_beats_modulo_by_a_lot():
    before = HashRing(["a", "b", "c"])
    after = HashRing(["a", "b", "c", "d"])
    assert keys_moved(before, after, KEYS) < modulo_keys_moved(KEYS, 3, 4) / 2


def test_keys_that_do_not_move_really_do_not_move():
    """Only the new node's arc changes hands. Everybody else's keys are untouched,
    which is the whole property."""
    before = HashRing(["a", "b", "c"])
    after = HashRing(["a", "b", "c", "d"])
    for key in KEYS[:2_000]:
        if before.node_for(key) != after.node_for(key):
            assert after.node_for(key) == "d", "a key moved somewhere other than the new node"


def test_nothing_moves_when_nothing_changes():
    ring = HashRing(["a", "b", "c"])
    assert keys_moved(ring, HashRing(["a", "b", "c"]), KEYS) == 0.0


# -- virtual nodes ------------------------------------------------------------


def test_one_position_per_node_distributes_badly():
    """Ten nodes, one ring position each. You asked for a ten-way split and luck
    gave you something else entirely."""
    ring = HashRing(list("abcdefghij"), virtual_nodes=1)
    assert skew_of(distribution(ring, KEYS)) > 3


def test_virtual_nodes_fix_the_skew():
    ring = HashRing(list("abcdefghij"), virtual_nodes=200)
    assert skew_of(distribution(ring, KEYS)) < 1.5


def test_a_departing_node_spreads_its_load():
    """The failure this prevents: with one position per node, a dead node's entire
    arc lands on its single clockwise neighbour, which then has double the load at
    the worst possible moment."""
    nodes = ["a", "b", "c", "d", "e"]
    before = HashRing(nodes, virtual_nodes=200)
    after = HashRing(nodes, virtual_nodes=200)
    after.remove("c")

    moved = [k for k in KEYS if before.node_for(k) != after.node_for(k)]
    landed = {n: sum(1 for k in moved if after.node_for(k) == n) for n in after.nodes}

    assert moved, "removing a node has to move something"
    assert len(landed) == 4, "its load reached every surviving node"
    assert max(landed.values()) / len(moved) < 0.6, "and no single node absorbed it all"


def test_only_the_departing_nodes_keys_move():
    nodes = ["a", "b", "c", "d", "e"]
    before = HashRing(nodes, virtual_nodes=200)
    after = HashRing(nodes, virtual_nodes=200)
    after.remove("c")
    for key in KEYS[:2_000]:
        if before.node_for(key) != after.node_for(key):
            assert before.node_for(key) == "c"


# -- the other scheme ---------------------------------------------------------


def test_range_partitioning_keeps_neighbours_together():
    boundaries = ["f", "m", "s"]
    assert range_partition_for("apple", boundaries) == 0
    assert range_partition_for("avocado", boundaries) == 0
    assert range_partition_for("grape", boundaries) == 1
    assert range_partition_for("tomato", boundaries) == 3


def test_a_hash_ring_scatters_the_same_neighbours():
    """Which is exactly why ranges are gone: 'everything from a to f' would have
    to ask every node."""
    ring = HashRing(list("abcdefgh"), virtual_nodes=200)
    neighbours = [f"user-000{i}" for i in range(8)]
    assert len({ring.node_for(k) for k in neighbours}) > 1


def test_modulo_still_has_its_uses():
    """It is not wrong, it is brittle. With a fixed node count it is fine, cheap
    and easy to reason about."""
    assert 0 <= modulo_node_for("acme", 8) < 8
    with pytest.raises(ValueError):
        modulo_node_for("acme", 0)
