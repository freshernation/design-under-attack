"""Day 3 — a log-structured store.

The tombstone tests are the ones that matter. Everything else is bookkeeping.
"""

import pytest

from memtable import LSMStore


# -- the basics ---------------------------------------------------------------


def test_read_your_writes():
    store = LSMStore()
    store.put("a", 1)
    assert store.get("a") == 1


def test_an_absent_key_is_none():
    assert LSMStore().get("nope") is None


def test_the_memtable_flushes_when_full():
    store = LSMStore(memtable_limit=3)
    for i in range(3):
        store.put(f"k{i}", i)
    assert store.stats["flushes"] == 1
    assert len(store.sstables) == 1
    assert store.memtable == {}


def test_values_survive_a_flush():
    store = LSMStore(memtable_limit=2)
    store.put("a", 1)
    store.put("b", 2)
    assert store.get("a") == 1
    assert store.get("b") == 2


def test_flushing_an_empty_memtable_does_nothing():
    store = LSMStore()
    store.flush()
    assert store.sstables == []
    assert store.stats["flushes"] == 0


# -- newest wins --------------------------------------------------------------


def test_the_memtable_shadows_the_files():
    store = LSMStore(memtable_limit=10)
    store.put("a", "old")
    store.flush()
    store.put("a", "new")
    assert store.get("a") == "new"


def test_a_newer_file_shadows_an_older_one():
    store = LSMStore(memtable_limit=10)
    store.put("a", "v1")
    store.flush()
    store.put("a", "v2")
    store.flush()
    assert store.get("a") == "v2"
    assert len(store.sstables) == 2, "both files still exist; the older is shadowed"


def test_the_search_stops_at_the_first_hit():
    """Not "collect everything and pick". The first hit is by construction the
    newest, and reading past it costs reads for no information."""
    store = LSMStore(memtable_limit=10)
    store.put("a", "v1")
    store.flush()
    store.put("a", "v2")
    store.flush()
    before = store.stats["sstables_read"]
    store.get("a")
    assert store.stats["sstables_read"] - before == 1


# -- tombstones ---------------------------------------------------------------


def test_a_delete_hides_a_value_in_an_older_file():
    """The test to read.

    "old" is still sitting in an sstable the whole time. A store that treats a
    tombstone as "keep looking" finds it and hands it back — a deleted record
    returning from the dead, which looks like a ghost rather than a bug.
    """
    store = LSMStore(memtable_limit=10)
    store.put("a", "old")
    store.flush()
    store.delete("a")
    store.flush()

    assert store.get("a") is None
    assert len(store.sstables) == 2


def test_a_delete_in_the_memtable_hides_a_flushed_value():
    store = LSMStore(memtable_limit=10)
    store.put("a", "old")
    store.flush()
    store.delete("a")
    assert store.get("a") is None


def test_a_key_can_come_back_after_being_deleted():
    store = LSMStore(memtable_limit=10)
    store.put("a", 1)
    store.flush()
    store.delete("a")
    store.flush()
    store.put("a", 2)
    assert store.get("a") == 2


def test_deleting_something_that_was_never_there_is_fine():
    store = LSMStore()
    store.delete("ghost")
    assert store.get("ghost") is None


# -- compaction ---------------------------------------------------------------


def test_compaction_merges_every_file_into_one():
    store = LSMStore(memtable_limit=2)
    for i in range(6):
        store.put(f"k{i}", i)
    assert len(store.sstables) == 3
    store.compact()
    assert len(store.sstables) == 1
    assert store.stats["compactions"] == 1


def test_compaction_keeps_the_newest_value():
    store = LSMStore(memtable_limit=10)
    for value in ("v1", "v2", "v3"):
        store.put("a", value)
        store.flush()
    store.compact()
    assert store.get("a") == "v3"


def test_compaction_drops_tombstones_and_the_data_under_them():
    store = LSMStore(memtable_limit=10)
    store.put("a", "old")
    store.put("b", "keep")
    store.flush()
    store.delete("a")
    store.flush()

    store.compact()
    assert store.get("a") is None
    assert store.get("b") == "keep"
    assert store.keys() == ["b"]
    assert len(store.sstables[0]) == 1, "the tombstone went too, not just the value"


def test_compaction_makes_reads_cheaper():
    """Not only a space saving. Read amplification is the other half, and it is
    the half people forget."""
    store = LSMStore(memtable_limit=1)
    for i in range(10):
        store.put(f"k{i}", i)

    before = store.stats["sstables_read"]
    store.get("missing")
    scattered = store.stats["sstables_read"] - before

    store.compact()
    before = store.stats["sstables_read"]
    store.get("missing")
    compacted = store.stats["sstables_read"] - before

    assert scattered == 10, "a miss checked every file"
    assert compacted == 1


def test_compacting_one_file_is_a_no_op():
    store = LSMStore(memtable_limit=2)
    store.put("a", 1)
    store.put("b", 2)
    store.compact()
    assert store.stats["compactions"] == 0


# -- keys ---------------------------------------------------------------------


def test_keys_are_sorted_and_live_only():
    store = LSMStore(memtable_limit=3)
    for key in ("c", "a", "b"):
        store.put(key, key.upper())
    store.delete("b")
    assert store.keys() == ["a", "c"]


def test_keys_spans_the_memtable_and_every_file():
    store = LSMStore(memtable_limit=2)
    store.put("a", 1)
    store.put("b", 2)      # flush
    store.put("c", 3)      # still in the memtable
    assert store.keys() == ["a", "b", "c"]
