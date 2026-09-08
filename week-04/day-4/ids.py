"""Snowflake-style ids, and what sortability costs you.

Runs on `simlib`'s clock, so a test can cross a millisecond boundary exactly.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation

NODE_BITS = 10
SEQUENCE_BITS = 12
MAX_NODE = (1 << NODE_BITS) - 1            # 1,023
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1    # 4,095


class ClockWentBackwards(Exception):
    """The clock moved backwards, so the next id might duplicate an old one.

    Refusing to issue is the right behaviour: a generator that stops is an
    incident, and a generator that issues duplicate ids is a data-loss bug you
    find out about weeks later.
    """


class SequenceExhausted(Exception):
    """4,096 ids already issued in this millisecond.

    A real implementation spins until the next millisecond. This one raises,
    because a lab that busy-waits on a simulated clock would never return.
    """


class SnowflakeGenerator:
    """
    gen = SnowflakeGenerator(sim, node_id=7)
    gen.next_id()   -> a 64-bit int: timestamp | node | sequence

    Layout, high bits first: 41 bits of milliseconds since `epoch_ms`, then
    `NODE_BITS` of node, then `SEQUENCE_BITS` of per-millisecond sequence.
    """

    def __init__(self, sim: Simulation, node_id: int, epoch_ms: int = 0) -> None:
        """Raises ValueError for a node id outside 0..MAX_NODE."""
        raise NotImplementedError

    def next_id(self, now_ms: int | None = None) -> int:
        """The next id. `now_ms` defaults to the simulation clock, and is a
        parameter only so a test can move the clock backwards on purpose.

        Raises ClockWentBackwards, and SequenceExhausted at 4,096 in one ms.
        """
        raise NotImplementedError


def decode(snowflake: int, epoch_ms: int = 0) -> tuple[int, int, int]:
    """`(timestamp_ms, node, sequence)` back out of an id."""
    raise NotImplementedError


def hash_partitions(ids, partitions: int) -> list[int]:
    """How many ids land in each partition under hash partitioning."""
    raise NotImplementedError


def range_partitions(ids, partitions: int, low: int, high: int) -> list[int]:
    """The same, under range partitioning over the span `low` to `high`.

    Ids below `low` go to partition 0 and ids at or above `high` to the last one.
    """
    raise NotImplementedError
