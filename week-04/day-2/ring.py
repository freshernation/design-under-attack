"""A consistent hashing ring, and the modulo scheme it replaces.

The point of this lab is two measurements, not the data structure: how many keys
move when you add a node, and what virtual nodes do to the skew.

Replace each `raise NotImplementedError` with your own code.
"""

import bisect
import zlib


def ring_hash(value: str) -> int:
    """One hash function for keys and for node positions alike.

    `zlib.crc32` again, for the same reason as yesterday: it does not move between
    processes.
    """
    return zlib.crc32(value.encode())


class HashRing:
    """
    ring = HashRing(["a", "b", "c"], virtual_nodes=100)
    ring.node_for("some-key")   -> "b"
    ring.add("d")               # only the keys between d and its predecessor move
    ring.remove("a")            # a's load spreads across everyone, not onto one neighbour
    """

    def __init__(self, nodes=(), virtual_nodes: int = 100) -> None:
        """Keep a sorted list of `(position, node)` so lookups can bisect.

        Each node gets `virtual_nodes` positions, hashed from a name like
        `f"{node}#{i}"`. Raises ValueError for fewer than one virtual node.
        """
        raise NotImplementedError

    @property
    def nodes(self) -> list[str]:
        """The physical nodes, sorted."""
        raise NotImplementedError

    def add(self, node: str) -> None:
        raise NotImplementedError

    def remove(self, node: str) -> None:
        """Raises KeyError for a node that is not on the ring."""
        raise NotImplementedError

    def node_for(self, key: str) -> str:
        """The first node clockwise from the key's position — so `bisect`, and wrap
        round to position 0 when you fall off the end.

        Raises LookupError on an empty ring.
        """
        raise NotImplementedError


def distribution(ring: HashRing, keys) -> dict[str, int]:
    """How many of `keys` land on each node. Nodes with nothing get a zero."""
    raise NotImplementedError


def skew_of(counts: dict[str, int]) -> float:
    """Busiest over average, to two decimals."""
    raise NotImplementedError


def keys_moved(before: HashRing, after: HashRing, keys) -> float:
    """The fraction of `keys` that changed node, to three decimals."""
    raise NotImplementedError


def modulo_node_for(key: str, node_count: int) -> int:
    """The scheme a ring replaces: `hash(key) % node_count`."""
    raise NotImplementedError


def modulo_keys_moved(keys, before_count: int, after_count: int) -> float:
    """The fraction of keys that move when a modulo scheme changes size.

    Run it for 3 -> 4 before you look at the test. The answer is the reason
    consistent hashing exists.
    """
    raise NotImplementedError


def range_partition_for(key: str, boundaries: list[str]) -> int:
    """Range partitioning, for comparison: which contiguous span a key falls in.

    `boundaries` are the *upper* bounds, sorted, with the last partition taking
    everything above the final boundary.
    """
    raise NotImplementedError
