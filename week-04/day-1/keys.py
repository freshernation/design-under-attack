"""Measuring how badly a partition key distributes, before you commit to it.

A bad index is an afternoon. A bad partition key is a migration. Ten minutes of
arithmetic here is the cheapest ten minutes in the week.

Replace each `raise NotImplementedError` with your own code.
"""

import zlib


def partition_for(key: str, partitions: int) -> int:
    """Which partition a key lands in.

    Use `zlib.crc32(key.encode())`, not the built-in `hash()` — Python randomises
    string hashing per process, so `hash()` would give you a different answer on
    every run, and a partition function that moves between runs is not a partition
    function.

    Raises ValueError for fewer than one partition.
    """
    raise NotImplementedError


def distribute(weighted_keys: dict[str, float], partitions: int) -> list[float]:
    """Total load landing on each partition. Index i is partition i."""
    raise NotImplementedError


def skew(loads: list[float]) -> float:
    """The busiest partition's load over the average, to two decimals.

    1.0 is perfect. Under about 1.5 is comfortable. Above 3 you are running one hot
    machine and a lot of idle ones. Raises ValueError for no partitions or no load.
    """
    raise NotImplementedError


def utilisation_of_busiest(loads: list[float], fleet_utilisation: float) -> float:
    """What the busiest partition is actually running at, to three decimals.

    The number that ends the argument: a fleet at 15% with a skew of 5.8 has one
    machine at 87%, which is past the knee, and no average on any dashboard shows it.
    """
    raise NotImplementedError


def partitions_needed(
    total_load: float, per_partition_capacity: float, skew_factor: float = 1.0
) -> int:
    """How many partitions the load actually needs, allowing for imbalance.

    Sizing on the average is the common mistake. The busiest partition carries
    `skew_factor` times the average, and it is the one that falls over.
    """
    raise NotImplementedError
