"""A small log-structured store: memtable, sstables, tombstones, compaction.

About eighty lines. A production engine is a hundred thousand, and the extra is
levels, filters, block indexes, compression and a write-ahead log — not a different
shape.

Replace each `raise NotImplementedError` with your own code.
"""

TOMBSTONE = object()   # a value meaning "deleted". It is a write, not a removal.


class LSMStore:
    """
    store = LSMStore(memtable_limit=4)
    store.put("k", "v")     # flushes automatically when the memtable is full
    store.delete("k")       # writes a tombstone
    store.get("k")          # None when absent or tombstoned
    store.flush()           # memtable -> a new sstable at the front of the list
    store.compact()         # merge every sstable into one, dropping tombstones
    """

    def __init__(self, memtable_limit: int = 4) -> None:
        """`sstables` is newest-first. `stats` counts flushes, compactions and
        sstables_read — the last one is read amplification, counted."""
        raise NotImplementedError

    def put(self, key: str, value) -> None:
        """Write to the memtable. Flush when it reaches `memtable_limit` keys."""
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """Write a tombstone. You cannot modify an immutable file, so a delete is
        a write like any other."""
        raise NotImplementedError

    def get(self, key: str):
        """Memtable first, then sstables newest to oldest. The first hit wins, and
        a tombstone is a hit meaning "not found".

        Count every sstable you look in, in `stats["sstables_read"]`.
        """
        raise NotImplementedError

    def flush(self) -> None:
        """Turn the memtable into an immutable sstable at the front of the list.
        Flushing an empty memtable does nothing."""
        raise NotImplementedError

    def compact(self) -> None:
        """Merge every sstable into one, keeping the newest value per key.

        This may drop tombstones — but only because it merges *all* the files.
        A compaction that left an older file untouched would resurrect deleted
        keys, which is why a real engine only drops tombstones at the bottom level.
        """
        raise NotImplementedError

    def keys(self) -> list[str]:
        """Every live key, sorted. Tombstoned keys are not live."""
        raise NotImplementedError
