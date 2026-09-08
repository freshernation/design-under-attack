"""A partitioned append-only log, offsets, and consumer groups.

You built this once already: week 3, day 4, a write-ahead log inside one machine.
This is the same structure with the readers moved outside.

Replace each `raise NotImplementedError` with your own code.
"""

import zlib


class Partition:
    """An ordered sequence with a number on each record.

    Offsets start at 0 and never repeat, **including after truncation** — a
    retention sweep removes old records without renumbering the rest, because a
    consumer's stored offset has to keep meaning the same thing.
    """

    def __init__(self, index: int) -> None:
        """Keep the records and the offset of the first one still present."""
        raise NotImplementedError

    def append(self, record) -> int:
        """Add a record. Returns its offset."""
        raise NotImplementedError

    @property
    def end_offset(self) -> int:
        """The offset the next append will get — so also the number ever written."""
        raise NotImplementedError

    @property
    def start_offset(self) -> int:
        """The oldest offset still present. Above 0 once retention has bitten."""
        raise NotImplementedError

    def read(self, offset: int, max_records: int = 100) -> list[tuple[int, object]]:
        """`(offset, record)` pairs from `offset` onward.

        An offset below `start_offset` means the consumer has fallen off the back
        of the retention window: return what is left, starting at `start_offset`.
        **That is data loss**, and the only thing that would tell you is a lag
        metric compared against retention.
        """
        raise NotImplementedError

    def truncate_before(self, offset: int) -> int:
        """Retention. Drop records below `offset` and return how many went."""
        raise NotImplementedError


class Log:
    """Partitions, and a key that decides which one a record lands in."""

    def __init__(self, partitions: int = 4) -> None:
        raise NotImplementedError

    def partition_for(self, key) -> int:
        """`zlib.crc32` of the key, modulo the partition count — the same stable
        hash as week 4. A key of None means round-robin: no ordering, even spread.
        """
        raise NotImplementedError

    def append(self, key, record) -> tuple[int, int]:
        """Returns `(partition, offset)`."""
        raise NotImplementedError

    @property
    def end_offsets(self) -> dict[int, int]:
        raise NotImplementedError


class ConsumerGroup:
    """A set of committed offsets, one per partition. That is all a consumer is.

    Two groups on the same log are completely independent — which is the property
    a queue cannot give you.
    """

    def __init__(self, log: Log, name: str) -> None:
        raise NotImplementedError

    def committed(self, partition: int) -> int:
        """Where this group has got to. 0 before anything is committed."""
        raise NotImplementedError

    def poll(self, partition: int, max_records: int = 100) -> list[tuple[int, object]]:
        """Read from the committed offset onward. **Does not commit** — where you
        commit relative to processing is tomorrow's whole subject."""
        raise NotImplementedError

    def commit(self, partition: int, offset: int) -> None:
        """Record that everything below `offset` is done."""
        raise NotImplementedError

    def seek(self, partition: int, offset: int) -> None:
        """Move the offset anywhere, including backwards.

        This is replay, and it is the reason to choose a log over a queue. It is
        also a deliberate source of duplicates, which your consumers must survive.
        """
        raise NotImplementedError

    def lag(self, partition: int) -> int:
        """How far behind this partition is. A subtraction, available for free."""
        raise NotImplementedError

    def total_lag(self) -> int:
        """Across every partition. Watch the per-partition numbers too — one
        partition drowning while five are fine is a hot key, and the total hides it.
        """
        raise NotImplementedError
