"""Day 2 — invalidation.

`test_the_cache_aside_race` is the day. It is driven step by step, so it fails
every run rather than one in ten thousand — which is the only difference between
this and production.
"""

import pytest

from invalidation import CacheAside, LeasedCache, Store, VersionedKeys
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


# -- cache-aside, working ------------------------------------------------------


def test_a_miss_populates_the_cache(sim):
    store = Store()
    store.write("k", 1)
    cache = CacheAside(sim, store)

    assert cache.read("k") == 1
    assert store.reads == 1
    assert cache.read("k") == 1
    assert store.reads == 1, "the second read came from the cache"


def test_a_write_invalidates(sim):
    store = Store()
    store.write("k", 1)
    cache = CacheAside(sim, store)
    cache.read("k")

    cache.write("k", 2)
    assert cache.read("k") == 2


def test_an_entry_expires(sim):
    store = Store()
    store.write("k", 1)
    cache = CacheAside(sim, store, ttl_ms=1_000)
    cache.read("k")

    store.write("k", 2)          # written behind the cache's back
    assert cache.read("k") == 1, "still cached, and now wrong"

    advance(sim, 1_001)
    assert cache.read("k") == 2


# -- the race -----------------------------------------------------------------


def test_the_cache_aside_race(sim):
    """A stale value, cached for the full TTL, by entirely correct code.

    1. a reader misses and loads x=1 from the store
    2. a writer writes x=2
    3. the writer deletes the cache entry, which is empty, so nothing happens
    4. the reader finally sets the cache to x=1

    The delete happened. The write happened. Nothing logs anything, and the wrong
    price is served until the TTL expires.
    """
    store = Store()
    store.write("price", 1)
    cache = CacheAside(sim, store, ttl_ms=600_000)

    loaded = cache.load("price")            # 1: the reader reads the store
    cache.write("price", 2)                 # 2 and 3: the writer writes and deletes
    cache.set_after_load("price", loaded)   # 4: the reader populates, too late

    assert store.read("price") == 2
    assert cache.read("price") == 1, "the cache is wrong and nothing will correct it"


def test_a_second_delete_shortens_the_exposure(sim):
    """The crude fix: delete again after the in-flight readers have finished. It
    does not close the window, it makes it milliseconds instead of a TTL."""
    store = Store()
    store.write("price", 1)
    cache = CacheAside(sim, store, ttl_ms=600_000)

    loaded = cache.load("price")
    cache.write("price", 2)
    cache.set_after_load("price", loaded)

    cache.write("price", 2)                 # the delayed second delete
    assert cache.read("price") == 2


# -- leases -------------------------------------------------------------------


def test_a_lease_lets_the_right_reader_populate(sim):
    store = Store()
    store.write("k", 1)
    cache = LeasedCache(sim, store)

    value, token = cache.read_or_lease("k")
    assert value is None
    assert cache.set_with_lease("k", store.read("k"), token) is True
    assert cache.read_or_lease("k")[0] == 1


def test_a_lease_refuses_the_stale_reader(sim):
    """The same race, and the fourth step is rejected.

    This is week 5's fencing token in a cache: the reader may be confused, and a
    monotonic token makes the confusion harmless.
    """
    store = Store()
    store.write("price", 1)
    cache = LeasedCache(sim, store, ttl_ms=600_000)

    _value, token = cache.read_or_lease("price")   # 1: reader takes a lease
    loaded = store.read("price")                    # still 1
    cache.write("price", 2)                         # 2 and 3: write bumps the token

    assert cache.set_with_lease("price", loaded, token) is False   # 4: refused
    assert cache.read_or_lease("price")[0] is None, "still a miss, and correctly so"


def test_a_hit_needs_no_lease(sim):
    store = Store()
    store.write("k", 1)
    cache = LeasedCache(sim, store)
    _v, token = cache.read_or_lease("k")
    cache.set_with_lease("k", 1, token)

    value, token = cache.read_or_lease("k")
    assert (value, token) == (1, None)


# -- versioned keys -----------------------------------------------------------


def test_versioning_makes_the_race_impossible(sim):
    """Nothing is ever overwritten in place, so there is no interleaving to lose.
    The stale reader populates the old version's key, which nobody reads."""
    store = Store()
    store.write("price", 1)
    cache = VersionedKeys(sim, store, ttl_ms=600_000)

    cache.read("price")                    # caches price:v1 = 1
    cache.write("price", 2)                # store updated, version bumped to 2
    assert cache.read("price") == 2


def test_the_old_version_is_still_in_memory(sim):
    """The price you paid. Superseded entries sit there until they expire, and
    that overhead belongs in your Size section."""
    store = Store()
    store.write("k", 1)
    cache = VersionedKeys(sim, store, ttl_ms=600_000)

    cache.read("k")
    cache.write("k", 2)
    cache.read("k")
    assert cache.entries_held() == 2


def test_superseded_entries_linger_past_their_ttl(sim):
    """Expiry is lazy, and that is not a shortcut in the lab — it is how caches
    work. Nothing reclaims a key that nobody asks for.

    The old version is expired and still occupying memory. A versioned scheme
    therefore needs a bound on memory as well as a TTL, and that belongs in the
    Size section rather than being assumed away.
    """
    store = Store()
    store.write("k", 1)
    cache = VersionedKeys(sim, store, ttl_ms=1_000)
    cache.read("k")
    cache.write("k", 2)
    cache.read("k")

    advance(sim, 1_001)
    cache.read("k")                      # re-populates v2; nobody asks for v1
    assert cache.entries_held() == 2


def test_a_sweep_reclaims_them(sim):
    store = Store()
    store.write("k", 1)
    cache = VersionedKeys(sim, store, ttl_ms=1_000)
    cache.read("k")
    cache.write("k", 2)
    cache.read("k")

    advance(sim, 1_001)
    assert cache.purge_expired() == 2
    assert cache.entries_held() == 0


def test_the_cache_key_carries_the_version(sim):
    cache = VersionedKeys(sim, Store())
    assert cache.cache_key("product:42", 7) == "product:42:v7"
