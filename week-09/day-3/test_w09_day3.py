"""Day 3 — breakers, bulkheads and shuffle sharding."""

import pytest

from breaker import Bulkhead, CircuitBreaker, overlap_probability, shuffle_shard
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


def drive(breaker, failures: int, successes: int = 0):
    for _ in range(failures):
        breaker.allow()
        breaker.record(False)
    for _ in range(successes):
        breaker.allow()
        breaker.record(True)


# -- the breaker --------------------------------------------------------------


def test_it_starts_closed(sim):
    breaker = CircuitBreaker(sim)
    assert breaker.state == "closed"
    assert breaker.allow() is True


def test_it_opens_on_sustained_failure(sim):
    breaker = CircuitBreaker(sim, failure_threshold=0.5, minimum_requests=20)
    drive(breaker, failures=20)
    assert breaker.state == "open"
    assert breaker.allow() is False


def test_a_low_traffic_path_does_not_trip_on_two_failures(sim):
    """Which is what `minimum_requests` is for. Two failures out of three is a
    100% failure rate and is not evidence of anything."""
    breaker = CircuitBreaker(sim, failure_threshold=0.5, minimum_requests=20)
    drive(breaker, failures=2, successes=1)
    assert breaker.state == "closed"


def test_an_open_breaker_fails_instantly(sim):
    """No thread waits, no timeout is consumed, and the dependency gets a rest.
    That is the point — not the failing, the *not waiting*."""
    breaker = CircuitBreaker(sim, minimum_requests=10)
    drive(breaker, failures=10)
    assert breaker.allow() is False


def test_it_half_opens_after_the_cool_off(sim):
    breaker = CircuitBreaker(sim, minimum_requests=10, cooloff_ms=10_000)
    drive(breaker, failures=10)

    advance(sim, 10_001)
    assert breaker.state == "half_open"


def test_only_one_probe_gets_through(sim):
    """The recovering dependency receives exactly one request, not the whole
    waiting population."""
    breaker = CircuitBreaker(sim, minimum_requests=10, cooloff_ms=10_000)
    drive(breaker, failures=10)
    advance(sim, 10_001)

    assert breaker.allow() is True
    assert breaker.allow() is False
    assert breaker.allow() is False


def test_a_successful_probe_closes_it(sim):
    breaker = CircuitBreaker(sim, minimum_requests=10, cooloff_ms=10_000)
    drive(breaker, failures=10)
    advance(sim, 10_001)

    breaker.allow()
    breaker.record(True)
    assert breaker.state == "closed"


def test_a_failed_probe_opens_it_again(sim):
    breaker = CircuitBreaker(sim, minimum_requests=10, cooloff_ms=10_000)
    drive(breaker, failures=10)
    advance(sim, 10_001)

    breaker.allow()
    breaker.record(False)
    assert breaker.state == "open"


def test_without_half_open_recovery_is_a_stampede(sim):
    """The state that does the work, shown by its absence.

    With half-open, one probe reaches the recovering dependency. Without it, the
    breaker simply closes and **every** waiting client resumes at once — which is
    how a recovering service is knocked straight back down, and why a breaker
    without half-open is a slower way to have the same outage twice.
    """
    careful = CircuitBreaker(sim, minimum_requests=10, cooloff_ms=10_000, half_open=True)
    naive = CircuitBreaker(sim, minimum_requests=10, cooloff_ms=10_000, half_open=False)
    for breaker in (careful, naive):
        drive(breaker, failures=10)

    advance(sim, 10_001)
    assert sum(careful.allow() for _ in range(100)) == 1
    assert sum(naive.allow() for _ in range(100)) == 100


@pytest.mark.parametrize("threshold, cooloff", [(0, 1_000), (1.5, 1_000), (0.5, 0)])
def test_a_nonsense_breaker_is_an_error(sim, threshold, cooloff):
    with pytest.raises(ValueError):
        CircuitBreaker(sim, failure_threshold=threshold, cooloff_ms=cooloff)


# -- bulkheads ----------------------------------------------------------------


def test_each_dependency_has_its_own_limit():
    pools = Bulkhead({"search": 2, "profile": 4})
    assert all(pools.acquire("search") for _ in range(2))
    assert pools.acquire("search") is False
    assert pools.acquire("profile") is True


def test_a_slow_dependency_cannot_starve_the_others():
    """The whole point. Search fills its own pool and stops there; profile is
    untouched, and requests that never needed search stay fast."""
    pools = Bulkhead({"search": 2, "profile": 4})
    while pools.acquire("search"):
        pass
    assert pools.available("search") == 0
    assert pools.available("profile") == 4


def test_releasing_frees_a_slot():
    pools = Bulkhead({"search": 1})
    pools.acquire("search")
    pools.release("search")
    assert pools.acquire("search") is True


def test_a_call_with_no_bulkhead_is_one_you_forgot():
    with pytest.raises(KeyError):
        Bulkhead({"search": 1}).acquire("recommendations")


def test_a_nonsense_bulkhead_is_an_error():
    with pytest.raises(ValueError):
        Bulkhead({"search": 0})


# -- shuffle sharding ---------------------------------------------------------


def test_a_customer_always_gets_the_same_shard():
    """Otherwise the isolation means nothing — a customer that moves around
    eventually touches everybody."""
    servers = [f"s{i}" for i in range(8)]
    assert shuffle_shard("acme", servers, 2) == shuffle_shard("acme", servers, 2)


def test_customers_get_different_shards():
    servers = [f"s{i}" for i in range(8)]
    shards = {tuple(shuffle_shard(f"cust-{i}", servers, 2)) for i in range(500)}
    assert len(shards) == 28, "every one of the 28 possible pairs gets used"


def test_a_shard_cannot_exceed_the_fleet():
    with pytest.raises(ValueError):
        shuffle_shard("acme", ["s0", "s1"], 3)


def test_plain_sharding_shares_a_lot():
    """One server each: two customers collide one time in eight."""
    assert overlap_probability(8, 1) == pytest.approx(0.125)


def test_pairs_are_already_much_better():
    """The same eight servers. Twenty-eight possible pairs instead of eight
    singletons, from nothing but a different assignment function."""
    assert overlap_probability(8, 2) == pytest.approx(0.0357, abs=0.001)


def test_a_hundred_servers_makes_collisions_vanish():
    """One in seventy-five million. A single abusive tenant degrades five servers
    and almost nobody else fully shares those five.

    No extra hardware, no new component, no code on the request path.
    """
    assert overlap_probability(100, 5) < 1e-7


def test_bigger_shards_isolate_better_but_spread_blast_radius():
    """The trade: a larger shard makes a full collision rarer and gives one bad
    customer more servers to degrade. It is not free in either direction."""
    assert overlap_probability(100, 5) < overlap_probability(100, 2)


def test_a_shard_of_everything_isolates_nothing():
    assert overlap_probability(8, 8) == pytest.approx(1.0)
