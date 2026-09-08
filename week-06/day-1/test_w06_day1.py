"""Day 1 — the cache, and the arithmetic around it."""

import pytest

from cache import (
    LRUCache,
    cold_start_multiplier,
    effective_latency_ms,
    fits_in,
    origin_qps,
    total_staleness_ms,
    working_set_bytes,
)
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


# -- the cache ----------------------------------------------------------------


def test_a_hit_returns_the_value(sim):
    cache = LRUCache(sim, capacity=10)
    cache.put("k", "v", ttl_ms=1_000)
    assert cache.get("k") == "v"
    assert cache.stats["hits"] == 1


def test_a_miss_returns_nothing(sim):
    cache = LRUCache(sim, capacity=10)
    assert cache.get("absent") is None
    assert cache.stats["misses"] == 1


def test_an_expired_entry_is_a_miss(sim):
    """Not a hit on old data. A cache that counted expiries as hits would report
    a hit rate with no relationship to the load reaching the origin."""
    cache = LRUCache(sim, capacity=10)
    cache.put("k", "v", ttl_ms=1_000)

    advance(sim, 1_001)
    assert cache.get("k") is None
    assert cache.stats["expirations"] == 1
    assert cache.stats["misses"] == 1


def test_the_least_recently_used_entry_goes_first(sim):
    cache = LRUCache(sim, capacity=2)
    cache.put("a", 1, 10_000)
    cache.put("b", 2, 10_000)
    cache.get("a")                 # a is now the most recent
    cache.put("c", 3, 10_000)      # so b is evicted

    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.stats["evictions"] == 1


def test_replacing_a_key_does_not_evict(sim):
    cache = LRUCache(sim, capacity=2)
    cache.put("a", 1, 10_000)
    cache.put("b", 2, 10_000)
    cache.put("a", 99, 10_000)

    assert len(cache) == 2
    assert cache.stats["evictions"] == 0
    assert cache.get("a") == 99


def test_inspecting_a_cache_does_not_change_its_statistics(sim):
    """A `__contains__` that counted would make every dashboard lie."""
    cache = LRUCache(sim, capacity=10)
    cache.put("k", "v", 1_000)
    assert "k" in cache
    assert "absent" not in cache
    assert cache.stats["hits"] == 0 and cache.stats["misses"] == 0


def test_hit_rate_starts_at_zero(sim):
    assert LRUCache(sim, capacity=10).hit_rate == 0.0


def test_hit_rate_counts_what_you_expect(sim):
    cache = LRUCache(sim, capacity=10)
    cache.put("k", "v", 10_000)
    for _ in range(9):
        cache.get("k")
    cache.get("absent")
    assert cache.hit_rate == pytest.approx(0.9)


def test_a_cache_with_no_capacity_is_an_error(sim):
    with pytest.raises(ValueError):
        LRUCache(sim, capacity=0)


# -- the arithmetic that matters ----------------------------------------------


def test_effective_latency():
    assert effective_latency_ms(0.95, 1, 40) == pytest.approx(2.95, abs=0.01)


def test_effective_latency_describes_almost_nobody():
    """2.95 ms is the mean of a distribution whose two values are 1 and 40. No
    request takes 2.95 ms. The p99 of a cached system is a miss."""
    mean = effective_latency_ms(0.95, 1, 40)
    assert mean != 1 and mean != 40


def test_the_last_few_percent_carry_the_load():
    """95% to 99% is not a 4% improvement. It is a five-fold reduction in what
    your database has to survive."""
    at_95 = origin_qps(400_000, 0.95)
    at_99 = origin_qps(400_000, 0.99)
    assert at_95 == pytest.approx(20_000)
    assert at_99 == pytest.approx(4_000)
    assert at_95 / at_99 == pytest.approx(5)


def test_and_it_works_the_other_way_too():
    """A cache degrading from 99% to 95% multiplies origin load by five, at an
    origin sized for one fifth of it."""
    assert origin_qps(400_000, 0.95) == 5 * origin_qps(400_000, 0.99)


def test_the_cold_start_multiplier_is_large():
    """At a 99% hit rate an empty cache sends a hundred times normal load at the
    origin, instantly, on every deploy and every failover."""
    assert cold_start_multiplier(0.99) == pytest.approx(100)
    assert cold_start_multiplier(0.999) == pytest.approx(1_000)


def test_a_perfect_hit_rate_has_no_usable_multiplier():
    with pytest.raises(ValueError):
        cold_start_multiplier(1.0)


def test_staleness_adds_across_layers():
    """Two minutes of browser, five of CDN, one of application. Seven minutes,
    and nobody chose seven minutes."""
    assert total_staleness_ms([120_000, 300_000, 60_000]) == 480_000


def test_the_working_set_makes_the_decision():
    """Twenty thousand hot keys at 2 KB is 40 MB, which fits on a laptop. Once you
    have this number the caching argument is arithmetic rather than opinion."""
    hot = working_set_bytes(20_000, 2_048)
    assert hot == pytest.approx(41e6, rel=0.05)
    assert fits_in(hot, 8 * 10**9) is True


def test_a_working_set_that_does_not_fit_is_a_different_design():
    assert fits_in(working_set_bytes(50_000_000, 2_048), 64 * 10**9) is False
