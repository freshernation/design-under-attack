"""Four ways to keep a cache from lying, and one race that catches everybody.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation


class Store:
    """The origin. Correct, and slow enough that you wanted a cache."""

    def __init__(self) -> None:
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError

    def write(self, key, value) -> None:
        raise NotImplementedError


class CacheAside:
    """Read: on a miss, load from the store and populate. Write: write the store,
    then delete the cache entry.

    What almost everyone uses, mostly by default. It has one specific race, and
    the tests drive it deterministically rather than hoping to catch it.
    """

    def __init__(self, sim: Simulation, store: Store, ttl_ms: int = 60_000) -> None:
        raise NotImplementedError

    def read(self, key):
        """Cache first; on a miss, load and populate."""
        raise NotImplementedError

    def load(self, key):
        """**Step one of a slow read**: fetch from the store and return the value
        without caching it.

        Split out so a test can interleave a write between the load and the set,
        which is exactly what a slow reader does in production.
        """
        raise NotImplementedError

    def set_after_load(self, key, value) -> None:
        """**Step two of a slow read**: populate the cache with what you loaded.

        By now the value may be stale. This method has no way to know, and that is
        the race.
        """
        raise NotImplementedError

    def write(self, key, value) -> None:
        """Write the store, then delete the cache entry."""
        raise NotImplementedError


class LeasedCache:
    """The Facebook mechanism: only the reader holding the current token may
    populate a key.

    On a miss the cache issues a token. An invalidation bumps the token. A reader
    holding a superseded token is refused — which is week 5's fencing token, in a
    cache. Same problem, same shape of answer.
    """

    def __init__(self, sim: Simulation, store: Store, ttl_ms: int = 60_000) -> None:
        raise NotImplementedError

    def read_or_lease(self, key):
        """Returns `(value, token)`. On a hit the token is None; on a miss the
        value is None and the token is yours to populate with."""
        raise NotImplementedError

    def set_with_lease(self, key, value, token: int) -> bool:
        """Populate only if `token` is still the current one for this key."""
        raise NotImplementedError

    def write(self, key, value) -> None:
        """Write the store, delete the entry, **and bump the token**."""
        raise NotImplementedError


class VersionedKeys:
    """Do not invalidate at all: put a version in the key.

    A write publishes a new version; nothing is ever overwritten in place, so
    there is no race to lose. The cost is that superseded entries occupy memory
    until they expire — the same trade as week 3's immutable files.
    """

    def __init__(self, sim: Simulation, store: Store, ttl_ms: int = 60_000) -> None:
        raise NotImplementedError

    def cache_key(self, key: str, version: int) -> str:
        """`"product:42:v7"`."""
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError

    def write(self, key, value) -> None:
        """Write the store and bump the version. No deletion, no race."""
        raise NotImplementedError

    def entries_held(self) -> int:
        """How many cache entries exist, including superseded and expired ones.

        Expiry here is **lazy** — an entry nobody reads is not reclaimed by the
        clock. So this is the memory actually occupied, which is the number your
        Size section needs, and it is larger than the number of live entries.
        """
        raise NotImplementedError

    def purge_expired(self) -> int:
        """Sweep out everything past its expiry. Returns how many went.

        Real caches do this with an eviction policy rather than a sweep, but the
        point is the same: a versioned scheme needs a bound on memory as well as a
        TTL, because nothing else reclaims a key nobody asks for.
        """
        raise NotImplementedError
