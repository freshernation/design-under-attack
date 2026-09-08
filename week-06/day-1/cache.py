"""An LRU cache with TTLs, and the arithmetic that decides whether it saves you.

Replace each `raise NotImplementedError` with your own code.
"""

from collections import OrderedDict

from simlib import Simulation


class LRUCache:
    """Least-recently-used eviction, with a per-entry expiry.

        cache = LRUCache(sim, capacity=100)
        cache.put("k", "v", ttl_ms=5_000)
        cache.get("k")

    An expired entry is a **miss**, and it is removed when found — a cache that
    counted expiries as hits would report a hit rate that has nothing to do with
    the load reaching your origin.
    """

    def __init__(self, sim: Simulation, capacity: int) -> None:
        """Use an `OrderedDict`: recency is its order, and `move_to_end` and
        `popitem(last=False)` do the work. `stats` counts hits, misses, evictions
        and expirations separately, because they mean different things.
        """
        raise NotImplementedError

    def get(self, key):
        """The value, or None. Refresh recency on a hit; count and drop on expiry."""
        raise NotImplementedError

    def put(self, key, value, ttl_ms: int) -> None:
        """Insert or replace, evicting the least recently used entry when full."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, key) -> bool:
        """Whether a live entry exists. Must not count as a hit or a miss —
        inspecting a cache should not change its statistics."""
        raise NotImplementedError

    @property
    def hit_rate(self) -> float:
        """Hits over hits plus misses, to four decimals. 0.0 before anything."""
        raise NotImplementedError


def effective_latency_ms(hit_rate: float, hit_ms: float, miss_ms: float) -> float:
    """The average a client experiences.

    Note what this number hides: it is a mean over a bimodal distribution, so it
    describes almost nobody's actual request. The p99 of a cached system is a miss.
    """
    raise NotImplementedError


def origin_qps(total_qps: float, hit_rate: float) -> float:
    """How much load actually reaches the thing behind the cache.

    Run it for 0.95 and 0.99 on 400,000 qps. The difference is five-fold, and it
    is the number your database was sized against.
    """
    raise NotImplementedError


def cold_start_multiplier(hit_rate: float) -> float:
    """How many times its normal load the origin sees when the cache is empty.

    `1 / (1 - hit_rate)`. At a 99% hit rate it is 100, which arrives instantly on
    every deploy, restart or failover.

    Raises ValueError for a hit rate of 1.0 — an infinite multiplier is not a
    number your capacity plan can use, and a cache that never misses is not one
    you have measured.
    """
    raise NotImplementedError


def total_staleness_ms(layer_ttls_ms: list[int]) -> int:
    """Worst-case staleness across stacked caches: they add.

    Two minutes of browser, five of CDN and one of application is eight minutes,
    and nobody chose eight minutes.
    """
    raise NotImplementedError


def working_set_bytes(hot_keys: int, bytes_per_key: int) -> int:
    """The bytes you would have to hold to cover the traffic that matters."""
    raise NotImplementedError


def fits_in(working_set: int, memory_bytes: int) -> bool:
    """Whether the cache decision is already made."""
    raise NotImplementedError
