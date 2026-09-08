"""Per-field TTLs, and the arithmetic that decides whether the design fits.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation


def required_hit_rate(total_qps: float, origin_capacity_qps: float) -> float:
    """The hit rate you must sustain for the origin to survive, to four decimals.

    Raises ValueError when the origin could not cope even at a perfect hit rate —
    which is not a caching problem and no cache will fix it.
    """
    raise NotImplementedError


def origin_qps_for_class(
    products: int, class_read_qps: float, ttl_ms: int, class_write_qps: float = 0.0
) -> float:
    """Load reaching the origin from one class of keys.

        fetches per key per second = min(read rate, 1/ttl + write rate)

    A key is refetched when its entry expires **or** when a write invalidates it,
    whichever happens more often — but never more often than it is actually read.

    That last clause is the important one, and it is why a long tail behaves so
    unlike a hot set.
    """
    raise NotImplementedError


def total_origin_qps(classes: list[tuple]) -> float:
    """Sum over classes of `(products, read_qps, ttl_ms, write_qps)`.

    The write rate is optional in each tuple and defaults to zero.
    """
    raise NotImplementedError


def ttl_that_starts_helping_ms(products: int, class_read_qps: float) -> float:
    """The TTL below which caching does nothing for this class.

    A key read once every 99 seconds gains nothing from a 60-second TTL: every read
    is a miss either way. Only once the TTL exceeds the inter-arrival time does the
    cache begin to absorb anything.

    This is the number that explains why long tails are expensive, and almost
    nobody computes it.
    """
    raise NotImplementedError


def memory_bytes(entries: int, bytes_per_entry: int) -> int:
    """Splitting one object into three fields triples the entry count. That is a
    real cost and it belongs next to the freshness benefit."""
    raise NotImplementedError


def cold_start_seconds(entries: int, warm_rate_per_s: float) -> float:
    """How long a full warm takes at a rate the origin can actually serve.

    Compare it with how long a deploy takes. If warming is slower than deploying,
    the cache is never full and the hit rate you designed for is fictional.
    """
    raise NotImplementedError


class SplitCache:
    """One cache, a different TTL per field.

        cache = SplitCache(sim, capacity=1000,
                           field_ttls_ms={"price": 5_000, "description": 3_600_000})
        cache.read("p42", "price", loader)

    Fields expire independently, which is the point: a price may be five seconds
    old while the description beside it is an hour old, and neither drags the other
    down.
    """

    def __init__(self, sim: Simulation, capacity: int, field_ttls_ms: dict) -> None:
        """Raises ValueError for a capacity below 1 or an empty field map."""
        raise NotImplementedError

    def read(self, product_id: str, field: str, loader):
        """The cached value, or `loader()` on a miss — cached with **that field's**
        TTL. Raises ValueError for a field with no configured TTL, because a field
        cached with a TTL nobody chose is how freshness requirements get lost."""
        raise NotImplementedError

    def invalidate(self, product_id: str, field: str | None = None) -> int:
        """Drop one field, or every field of a product when `field` is None.
        Returns how many entries went."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
