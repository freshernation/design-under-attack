"""The milestone's mechanism and its economics.

The block under "the arithmetic that decides the design" is the brief. Work
through those five tests in order; they are an argument.
"""

import pytest

from catalogue import (
    SplitCache,
    cold_start_seconds,
    memory_bytes,
    origin_qps_for_class,
    required_hit_rate,
    total_origin_qps,
    ttl_that_starts_helping_ms,
)
from simlib import Simulation

HOT = (20_000, 380_000)          # 20k products taking 380k reads/s
TAIL = (1_980_000, 20_000)       # ~2M products taking 20k reads/s
ORIGIN_CAPACITY = 20_000


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


# -- the arithmetic that decides the design -----------------------------------


def test_the_origin_capacity_sets_the_hit_rate():
    """400,000 reads against an origin that serves 20,000. You need 95%, and that
    is not a target — it is a floor."""
    assert required_hit_rate(400_000, ORIGIN_CAPACITY) == pytest.approx(0.95)


def test_a_cache_cannot_fix_an_origin_that_is_simply_too_small():
    """If the origin could not cope even at a 100% hit rate, no cache helps —
    every miss is unrecoverable. Worth checking before designing a cache."""
    assert required_hit_rate(10_000, 20_000) == 0.0


def test_the_five_second_price_ttl_does_not_fit():
    """The milestone's first surprise.

    A 5-second TTL on both read classes puts 24,000 qps on an origin that serves
    20,000. The design fails, and the reason is not the hot products.
    """
    total = total_origin_qps([(*HOT, 5_000), (*TAIL, 5_000)])
    assert total == pytest.approx(24_000, rel=0.01)
    assert total > ORIGIN_CAPACITY


def test_and_the_hot_products_are_not_the_problem():
    """The 20,000 hot products cost 4,000 qps at a 5-second TTL. The other 20,000
    comes from the tail — from keys nobody would call hot."""
    assert origin_qps_for_class(*HOT, 5_000) == pytest.approx(4_000, rel=0.01)
    assert origin_qps_for_class(*TAIL, 5_000) == pytest.approx(20_000, rel=0.01)


def test_a_longer_ttl_does_nothing_for_the_tail():
    """The result that changes what you do.

    Going from a 5-second TTL to 60 seconds cuts the hot class by more than ten
    times and leaves the tail **completely unchanged**. A key read once every 99
    seconds gains nothing from a 60-second TTL: every read is a miss either way.
    """
    assert origin_qps_for_class(*TAIL, 5_000) == origin_qps_for_class(*TAIL, 60_000)
    assert origin_qps_for_class(*HOT, 60_000) < origin_qps_for_class(*HOT, 5_000) / 10


def test_the_tail_needs_a_ttl_of_at_least_ninety_nine_seconds():
    """And here is why. Below the inter-arrival time, a cache is just an
    additional lookup that always misses."""
    assert ttl_that_starts_helping_ms(*TAIL) == pytest.approx(99_000, rel=0.01)
    assert ttl_that_starts_helping_ms(*HOT) == pytest.approx(52.6, rel=0.01)


def test_a_long_ttl_finally_fits_but_breaks_the_requirement():
    """Five minutes brings the origin to 6,700 qps, comfortably inside capacity —
    and a price is now up to five minutes stale against a five-second envelope."""
    assert total_origin_qps([(*HOT, 300_000), (*TAIL, 300_000)]) < ORIGIN_CAPACITY


def test_invalidation_is_the_instrument_that_fits():
    """The payoff.

    2,000 writes a second against 400,000 reads. A TTL refreshes every key on a
    schedule whether or not anything changed; an invalidation refreshes only what
    did. With a one-hour TTL plus invalidation on write, the origin sees about
    2,600 qps — an eighth of its capacity — and freshness is now bounded by
    invalidation delivery rather than by a timer.

    Which means the 5-second requirement has become a property of your
    invalidation path, and that path can fail in ways a TTL cannot.
    """
    with_invalidation = total_origin_qps(
        [(*HOT, 3_600_000, 1_900), (*TAIL, 3_600_000, 100)]
    )
    assert with_invalidation < ORIGIN_CAPACITY / 5


def test_writes_only_cost_what_is_actually_read():
    """A write to a key nobody reads costs nothing — the entry is invalidated and
    never re-fetched. The `min` against the read rate is doing this."""
    read_rarely = origin_qps_for_class(1_000_000, 10, 3_600_000, class_write_qps=5_000)
    assert read_rarely <= 10


@pytest.mark.parametrize("products, ttl", [(0, 1_000), (100, 0), (100, -5)])
def test_nonsense_class_arithmetic_is_an_error(products, ttl):
    with pytest.raises(ValueError):
        origin_qps_for_class(products, 100, ttl)


# -- memory and warming -------------------------------------------------------


def test_splitting_fields_multiplies_the_entry_count():
    """Three fields per product, so three entries. Real, and it is the cost you
    pay for independent freshness."""
    one_object = memory_bytes(2_000_000, 2_048)
    three_fields = memory_bytes(6_000_000, 2_048)
    assert three_fields == 3 * one_object
    assert three_fields < 200 * 10**9, "still comfortably inside the 200 GB budget"


def test_a_full_warm_takes_minutes():
    """Five minutes at the origin's full capacity — during which it is doing
    nothing else. Compare that with how long a deploy takes before assuming the
    cache is ever full."""
    assert cold_start_seconds(6_000_000, ORIGIN_CAPACITY) == pytest.approx(300, rel=0.01)


def test_warming_faster_than_the_origin_can_serve_is_not_a_plan():
    with pytest.raises(ValueError):
        cold_start_seconds(1_000_000, 0)


# -- the cache itself ---------------------------------------------------------


def loader_for(value):
    calls = []

    def load():
        calls.append(1)
        return value

    load.calls = calls
    return load


def test_fields_expire_independently(sim):
    """The point of splitting. A five-second price sitting next to an hour-old
    description, and neither drags the other down."""
    cache = SplitCache(sim, capacity=100, field_ttls_ms={"price": 5_000, "description": 3_600_000})
    cache.read("p42", "price", lambda: 100)
    cache.read("p42", "description", lambda: "a shoe")

    advance(sim, 6_000)
    price = loader_for(120)
    description = loader_for("a shoe")

    assert cache.read("p42", "price", price) == 120
    assert cache.read("p42", "description", description) == "a shoe"
    assert len(price.calls) == 1, "the price expired and was refetched"
    assert len(description.calls) == 0, "the description did not"


def test_one_object_would_have_forced_the_shortest_ttl(sim):
    """The alternative, as an assertion. Cached as a single entry with the price's
    TTL, the description is refetched every five seconds too — for nothing."""
    cache = SplitCache(sim, capacity=100, field_ttls_ms={"whole_product": 5_000})
    cache.read("p42", "whole_product", lambda: {"price": 100, "description": "a shoe"})

    advance(sim, 6_000)
    refetch = loader_for({"price": 100, "description": "a shoe"})
    cache.read("p42", "whole_product", refetch)
    assert len(refetch.calls) == 1


def test_a_field_with_no_configured_ttl_is_an_error(sim):
    """A field cached with a TTL nobody chose is how a freshness requirement gets
    lost, quietly, in a code review."""
    cache = SplitCache(sim, capacity=100, field_ttls_ms={"price": 5_000})
    with pytest.raises(ValueError):
        cache.read("p42", "stock_band", lambda: "in stock")


def test_invalidating_one_field_leaves_the_others(sim):
    cache = SplitCache(sim, capacity=100, field_ttls_ms={"price": 5_000, "description": 3_600_000})
    cache.read("p42", "price", lambda: 100)
    cache.read("p42", "description", lambda: "a shoe")

    assert cache.invalidate("p42", "price") == 1
    assert len(cache) == 1


def test_invalidating_a_product_drops_every_field(sim):
    cache = SplitCache(sim, capacity=100, field_ttls_ms={"price": 5_000, "description": 3_600_000})
    cache.read("p42", "price", lambda: 100)
    cache.read("p42", "description", lambda: "a shoe")
    cache.read("p99", "price", lambda: 50)

    assert cache.invalidate("p42") == 2
    assert len(cache) == 1


def test_invalidating_something_absent_is_harmless(sim):
    cache = SplitCache(sim, capacity=10, field_ttls_ms={"price": 5_000})
    assert cache.invalidate("nobody") == 0
    assert cache.invalidate("nobody", "price") == 0


def test_it_evicts_when_full(sim):
    cache = SplitCache(sim, capacity=2, field_ttls_ms={"price": 60_000})
    for i in range(3):
        cache.read(f"p{i}", "price", lambda: i)
    assert len(cache) == 2
    assert cache.stats["evictions"] == 1


@pytest.mark.parametrize("capacity, ttls", [(0, {"price": 1}), (10, {})])
def test_a_nonsense_cache_is_an_error(sim, capacity, ttls):
    with pytest.raises(ValueError):
        SplitCache(sim, capacity=capacity, field_ttls_ms=ttls)
