"""Day 2 — quorums and conflicts.

The pair to read: `test_overlapping_quorums_always_see_the_write` and
`test_non_overlapping_quorums_do_not`. Same code, one number different.
"""

import pytest

from quorum import (
    QuorumStore,
    Replica,
    Versioned,
    compare_and_set,
    last_write_wins,
    merge_sets,
    newest,
    read_repair,
    siblings,
)


def store_of(n=5, w=3, r=3):
    return QuorumStore([Replica(chr(ord("A") + i)) for i in range(n)], w=w, r=r)


# -- the pigeonhole -----------------------------------------------------------


def test_overlapping_quorums_always_see_the_write():
    """N=5, W=3, R=3. The write went to A B C, the read asks C D E, and C is in
    both sets. It cannot not be — three plus three does not fit in five."""
    store = store_of(5, w=3, r=3)
    assert store.overlaps is True

    store.write("x", Versioned(2, 1, "c1", 100), to=[0, 1, 2])
    assert [v.value for v in store.read("x", frm=[2, 3, 4])] == [2]


def test_non_overlapping_quorums_do_not():
    """N=5, W=2, R=2. The write went to A B, the read asks D E, and there is no
    node in both. The read returns the old value, confidently and correctly."""
    store = store_of(5, w=2, r=2)
    assert store.overlaps is False

    store.write("x", Versioned(2, 1, "c1", 100), to=[0, 1])
    assert store.read("x", frm=[3, 4]) == []


def test_the_common_default_overlaps():
    assert store_of(3, w=2, r=2).overlaps is True


def test_w_equals_n_stops_writes_when_one_node_is_down():
    """A strong guarantee on one side, bought by making the other side
    unavailable the moment a single node is unreachable. It is a common
    accidental configuration."""
    store = store_of(3, w=3, r=1)
    store.replicas[2].up = False
    assert store.write("x", Versioned(1, 1, "c1", 100), to=[0, 1, 2]) is False


def test_a_quorum_survives_one_node_down():
    store = store_of(3, w=2, r=2)
    store.replicas[2].up = False
    assert store.write("x", Versioned(1, 1, "c1", 100), to=[0, 1, 2]) is True
    assert newest(store.read("x", frm=[0, 1]))[0].value == 1


@pytest.mark.parametrize("w, r", [(0, 2), (4, 2), (2, 0), (2, 9)])
def test_impossible_quorum_settings_are_an_error(w, r):
    with pytest.raises(ValueError):
        QuorumStore([Replica("A"), Replica("B"), Replica("C")], w=w, r=r)


def test_a_failed_write_still_leaves_data_behind():
    """The case people are surprised by, and it is not a bug.

    W=3, one replica down, so the write is reported as failed. Two replicas took
    it anyway. A later read that happens to ask those two sees a value the client
    was told did not exist.
    """
    store = store_of(3, w=3, r=1)
    store.replicas[2].up = False

    assert store.write("x", Versioned(9, 1, "c1", 100), to=[0, 1, 2]) is False
    assert newest(store.read("x", frm=[0]))[0].value == 9


# -- concurrent writes --------------------------------------------------------


def concurrent_cart():
    store = store_of(3, w=2, r=2)
    store.write("cart", Versioned(frozenset({"apple"}), 2, "c1", 1_800), to=[0, 1])
    store.write("cart", Versioned(frozenset({"banana"}), 2, "c2", 1_200), to=[1, 2])
    return store


def test_two_writers_at_the_same_version_are_concurrent():
    versions = concurrent_cart().read("cart", frm=[0, 1, 2])
    assert len(siblings(versions)) == 2


def test_a_single_newest_version_is_not_a_conflict():
    store = store_of(3, w=2, r=2)
    store.write("x", Versioned(1, 1, "c1", 10), to=[0, 1])
    store.write("x", Versioned(2, 2, "c1", 20), to=[0, 1])
    assert siblings(store.read("x", frm=[0, 1])) == []
    assert newest(store.read("x", frm=[0, 1]))[0].value == 2


def test_a_skewed_clock_wins_a_race_it_should_have_lost():
    """The failure that has no error message.

    c2 wrote second in real time. c1's machine was 600 ms fast, so its timestamp
    is higher, so last-write-wins keeps c1's value and discards c2's — a write
    that was acknowledged, gone, with nothing logged anywhere.

    Last-write-wins is correct only when losing a write is acceptable.
    """
    versions = concurrent_cart().read("cart", frm=[0, 1, 2])
    winner = last_write_wins(versions)
    assert winner.writer == "c1"
    assert "banana" not in winner.value


def test_merging_keeps_both():
    """Dynamo's cart. The failure mode becomes 'a removed item came back' rather
    than 'your order vanished', which Amazon chose on purpose."""
    versions = concurrent_cart().read("cart", frm=[0, 1, 2])
    assert merge_sets(versions) == {"apple", "banana"}


def test_last_write_wins_of_nothing():
    assert last_write_wins([]) is None


# -- avoiding the question ----------------------------------------------------


def test_compare_and_set_accepts_a_current_writer():
    store = store_of(3, w=2, r=2)
    store.write("x", Versioned(1, 1, "c1", 10), to=[0, 1])
    assert compare_and_set(store, "x", 1, Versioned(2, 2, "c1", 20)) is True


def test_compare_and_set_rejects_a_stale_writer():
    """A visible rejection the client can retry, instead of a silently discarded
    write. Much the better failure."""
    store = store_of(3, w=2, r=2)
    store.write("x", Versioned(1, 1, "c1", 10), to=[0, 1])
    store.write("x", Versioned(2, 2, "c2", 20), to=[0, 1])
    assert compare_and_set(store, "x", 1, Versioned(3, 3, "c1", 30)) is False


def test_compare_and_set_on_a_new_key():
    assert compare_and_set(store_of(3, w=2, r=2), "fresh", 0, Versioned(1, 1, "c1", 1))


# -- repair -------------------------------------------------------------------


def test_read_repair_updates_the_replicas_that_are_behind():
    store = store_of(3, w=2, r=2)
    store.write("x", Versioned(1, 1, "c1", 10), to=[0, 1])
    assert store.replicas[2].get("x") == []

    assert read_repair(store, "x") == 1
    assert newest(store.replicas[2].get("x"))[0].value == 1


def test_read_repair_does_nothing_when_everyone_agrees():
    store = store_of(3, w=3, r=3)
    store.write("x", Versioned(1, 1, "c1", 10), to=[0, 1, 2])
    assert read_repair(store, "x") == 0


def test_read_repair_only_fixes_what_someone_reads():
    """Which is why a background sweep exists as well. A key nobody reads stays
    diverged for ever, and that is the cold tail of your dataset."""
    store = store_of(3, w=2, r=2)
    store.write("read-often", Versioned(1, 1, "c1", 10), to=[0, 1])
    store.write("read-never", Versioned(1, 1, "c1", 10), to=[0, 1])

    read_repair(store, "read-often")
    assert store.replicas[2].get("read-often") != []
    assert store.replicas[2].get("read-never") == []
