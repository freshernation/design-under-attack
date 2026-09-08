"""Day 3 — stampedes.

`test_a_thousand_misses_become_one_load` is the day, and the mechanism behind it
is twenty lines.
"""

import pytest

from simlib import Simulation
from stampede import NegativeCache, SingleFlight, jittered_ttl, should_refresh_early


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation(seed=7)


# -- single flight ------------------------------------------------------------


def test_a_thousand_misses_become_one_load(sim):
    """One popular key expires and a thousand requests notice at the same instant.
    Nine hundred and ninety-nine of those queries are pure waste, and they arrive
    together.

    With coalescing the origin is asked once, and everybody gets the answer.
    """
    flight = SingleFlight(sim)
    origin_calls = []
    results = []

    def loader():
        origin_calls.append(sim.now)
        return "value"

    for _ in range(1_000):
        flight.do("hot", loader, results.append, load_ms=40)

    sim.run()

    assert len(origin_calls) == 1
    assert flight.loads == 1
    assert len(results) == 1_000
    assert set(results) == {"value"}


def test_everyone_waits_for_the_same_answer(sim):
    flight = SingleFlight(sim)
    results = []
    for _ in range(5):
        flight.do("k", lambda: sim.now, results.append, load_ms=40)
    sim.run()
    assert results == [40] * 5, "all resolved at the same moment, by the same load"


def test_different_keys_do_not_coalesce(sim):
    flight = SingleFlight(sim)
    for key in ("a", "b", "c"):
        flight.do(key, lambda: 1, lambda _v: None, load_ms=10)
    assert flight.in_flight == 3
    sim.run()
    assert flight.loads == 3


def test_a_later_request_starts_a_new_load(sim):
    """Coalescing covers the requests that overlap. Once the load completes the
    key is clear, and the next miss starts a fresh one."""
    flight = SingleFlight(sim)
    flight.do("k", lambda: 1, lambda _v: None, load_ms=10)
    sim.run()

    flight.do("k", lambda: 1, lambda _v: None, load_ms=10)
    sim.run()
    assert flight.loads == 2


def test_nothing_is_in_flight_afterwards(sim):
    flight = SingleFlight(sim)
    for _ in range(10):
        flight.do("k", lambda: 1, lambda _v: None, load_ms=10)
    sim.run()
    assert flight.in_flight == 0


# -- jitter -------------------------------------------------------------------


def test_jitter_spreads_a_synchronised_expiry(sim):
    """Ten thousand entries written together. Without jitter they expire in the
    same millisecond; with it, over a minute."""
    plain = [300_000 for _ in range(10_000)]
    spread = [jittered_ttl(300_000, 0.1, sim.random) for _ in range(10_000)]

    assert len(set(plain)) == 1
    assert max(spread) - min(spread) > 50_000


def test_jitter_stays_inside_its_bounds(sim):
    values = [jittered_ttl(1_000, 0.1, sim.random) for _ in range(500)]
    assert all(900 <= v <= 1_100 for v in values)


def test_no_jitter_changes_nothing(sim):
    assert jittered_ttl(1_000, 0.0, sim.random) == 1_000


@pytest.mark.parametrize("base, fraction", [(-1, 0.1), (1_000, -0.1), (1_000, 1.5)])
def test_nonsense_jitter_is_an_error(sim, base, fraction):
    with pytest.raises(ValueError):
        jittered_ttl(base, fraction, sim.random)


# -- early recomputation ------------------------------------------------------


def test_nobody_refreshes_long_before_expiry(sim):
    """A hundred readers, well inside the TTL. Almost none of them should decide
    to do the expensive thing."""
    refreshers = sum(
        should_refresh_early(
            now_ms=0, expires_at_ms=60_000, recompute_ms=50, beta=1.0, rng=sim.random
        )
        for _ in range(100)
    )
    assert refreshers == 0


def test_somebody_refreshes_just_before_expiry(sim):
    """Close to expiry, the probability rises until one of the readers goes and
    does it — and the others carry on using a value that is still valid."""
    refreshers = sum(
        should_refresh_early(
            now_ms=59_950, expires_at_ms=60_000, recompute_ms=50, beta=1.0, rng=sim.random
        )
        for _ in range(100)
    )
    assert 0 < refreshers < 100


def test_everyone_refreshes_after_expiry(sim):
    assert should_refresh_early(
        now_ms=61_000, expires_at_ms=60_000, recompute_ms=50, beta=1.0, rng=sim.random
    ) is True


def test_a_slower_recompute_starts_earlier(sim):
    """The term scales with how long the refresh takes, which is the point: an
    expensive value should start being refreshed sooner."""
    quick = sum(
        should_refresh_early(59_000, 60_000, recompute_ms=10, beta=1.0, rng=sim.random)
        for _ in range(300)
    )
    slow = sum(
        should_refresh_early(59_000, 60_000, recompute_ms=2_000, beta=1.0, rng=sim.random)
        for _ in range(300)
    )
    assert slow > quick


# -- negative caching ---------------------------------------------------------


def test_an_absence_is_remembered(sim):
    negative = NegativeCache(sim, ttl_ms=30_000)
    assert negative.known_absent("ghost") is False

    negative.mark_absent("ghost")
    assert negative.known_absent("ghost") is True


def test_it_forgets_quickly(sim):
    """The TTL must be short: 'does not exist' becomes wrong the instant somebody
    creates it, and nothing tells the cache."""
    negative = NegativeCache(sim, ttl_ms=30_000)
    negative.mark_absent("ghost")

    advance(sim, 30_001)
    assert negative.known_absent("ghost") is False


def test_creating_the_thing_clears_it(sim):
    """Without this, a newly created object is invisible for the whole negative
    TTL — which users experience as 'I just made it and it is not there'."""
    negative = NegativeCache(sim, ttl_ms=30_000)
    negative.mark_absent("new-product")
    negative.forget("new-product")
    assert negative.known_absent("new-product") is False


def test_a_negative_cache_needs_a_ttl(sim):
    with pytest.raises(ValueError):
        NegativeCache(sim, ttl_ms=0)
