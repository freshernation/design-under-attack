"""A bloom filter, and the cache key that decides your hit rate.

Replace each `raise NotImplementedError` with your own code.
"""

import hashlib
import math


class BloomFilter:
    """A bit array and `k` hashes. One guarantee, in one direction.

        filter = BloomFilter(expected_keys=1_000_000, false_positive_rate=0.01)
        filter.add("apple")
        "plum" in filter        # False means definitely not. Certain.
        "grape" in filter       # True means probably — or a collision

    **No false negatives, ever.** That asymmetry is the whole value: a "no" is
    trustworthy, so you can skip the expensive lookup on a no, and a "maybe" costs
    only the lookup you were going to do anyway.
    """

    def __init__(self, expected_keys: int, false_positive_rate: float = 0.01) -> None:
        """Size yourself from those two numbers:

            bits = -n * ln(p) / (ln 2)^2
            k    = (bits / n) * ln 2, at least 1

        Ten bits per key is about 1%; fifteen is about 0.1%. A million keys at 1%
        is 1.2 MB, which is small enough to change a design.

        Raises ValueError for a non-positive key count or a rate outside (0, 1).
        """
        raise NotImplementedError

    def _positions(self, key) -> list[int]:
        """The `k` bit positions for a key.

        Derive them from one hash rather than computing k independent ones:
        `hashlib.sha256` of the key, split into two 8-byte halves `h1` and `h2`,
        then position `i` is `(h1 + i * h2) % bits`. Standard, cheap, and good
        enough — a bloom filter is not a security boundary.
        """
        raise NotImplementedError

    def add(self, key) -> None:
        raise NotImplementedError

    def __contains__(self, key) -> bool:
        raise NotImplementedError

    @property
    def bits_per_key(self) -> float:
        raise NotImplementedError

    @property
    def bytes_used(self) -> int:
        raise NotImplementedError

    def estimated_false_positive_rate(self) -> float:
        """From how full the array actually is: `(set_bits / bits) ** k`.

        This is the number that tells you a filter has been overfilled. Once every
        bit is 1 it answers "maybe" to everything, consumes memory and does nothing
        — which is why a filter needs a rebuild policy.
        """
        raise NotImplementedError


def cache_key(url: str, vary_on: list[str], request_headers: dict) -> str:
    """What an edge cache actually stores a response against.

    The URL, plus the value of each header named in `vary_on`, in that order.
    Everything about your hit rate follows from what goes in here.
    """
    raise NotImplementedError


def distinct_entries(urls: int, vary_cardinality: list[int]) -> int:
    """How many entries a cache ends up holding: the URLs multiplied by the
    cardinality of everything you vary on.

    Run it for `Vary: Accept-Encoding` (3) and then for `Vary: Cookie` (one per
    user). The second is how a shared cache becomes a per-user cache with a hit
    rate near zero, while every dashboard still says the CDN is working.
    """
    raise NotImplementedError


def is_fresh(
    cached_at_ms: int, now_ms: int, max_age_s: int, s_maxage_s: int | None, shared: bool
) -> bool:
    """Whether a cached response may still be served without asking the origin.

    A shared cache prefers `s-maxage` when it is present; a private one always
    uses `max_age`. That asymmetry is the whole reason the second directive
    exists: a long TTL where you can purge, a short one where you cannot.
    """
    raise NotImplementedError
