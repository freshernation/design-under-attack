"""Day 4 — rate limiting."""

import pytest

from simlib import Simulation
from token_bucket import FixedWindow, TokenBucket, advance


@pytest.fixture
def sim():
    return Simulation()


# -- the clock helper ---------------------------------------------------------


def test_advance_moves_time(sim):
    assert sim.now == 0
    advance(sim, 1_500)
    assert sim.now == 1_500
    advance(sim, 500)
    assert sim.now == 2_000


# -- token bucket -------------------------------------------------------------


def test_a_new_bucket_is_full(sim):
    bucket = TokenBucket(sim, rate_per_second=10, capacity=50)
    assert bucket.tokens == pytest.approx(50)


def test_the_burst_is_the_capacity(sim):
    bucket = TokenBucket(sim, rate_per_second=10, capacity=50)
    assert sum(bucket.allow() for _ in range(50)) == 50
    assert bucket.allow() is False


def test_a_refused_request_spends_nothing(sim):
    bucket = TokenBucket(sim, rate_per_second=10, capacity=1)
    assert bucket.allow() is True
    before = bucket.tokens
    assert bucket.allow() is False
    assert bucket.tokens == pytest.approx(before)


def test_it_refills_at_the_stated_rate(sim):
    bucket = TokenBucket(sim, rate_per_second=10, capacity=50)
    for _ in range(50):
        bucket.allow()
    advance(sim, 1_000)
    assert bucket.tokens == pytest.approx(10, abs=0.01)
    advance(sim, 2_000)
    assert bucket.tokens == pytest.approx(30, abs=0.01)


def test_unused_allowance_expires(sim):
    """An idle hour does not buy you an hour's worth of burst."""
    bucket = TokenBucket(sim, rate_per_second=10, capacity=50)
    for _ in range(50):
        bucket.allow()
    advance(sim, 3_600_000)
    assert bucket.tokens == pytest.approx(50)


def test_the_sustained_rate_is_the_refill_rate(sim):
    """Drain the burst, then take everything offered over the next minute.
    Sixty seconds at ten a second is six hundred, and not one more."""
    bucket = TokenBucket(sim, rate_per_second=10, capacity=50)
    for _ in range(50):
        bucket.allow()

    served = 0
    for _ in range(600):          # try ten times a second for a minute
        advance(sim, 100)
        served += sum(bucket.allow() for _ in range(10))

    assert served == pytest.approx(600, abs=2)


def test_a_larger_bucket_allows_a_bigger_burst_at_the_same_rate(sim):
    small = TokenBucket(sim, rate_per_second=10, capacity=10)
    large = TokenBucket(sim, rate_per_second=10, capacity=100)
    assert sum(small.allow() for _ in range(200)) == 10
    assert sum(large.allow() for _ in range(200)) == 100


def test_a_full_bucket_says_retry_now(sim):
    bucket = TokenBucket(sim, rate_per_second=10, capacity=50)
    assert bucket.retry_after_ms() == 0


def test_an_empty_bucket_says_how_long(sim):
    """Ten a second means one token every hundred milliseconds."""
    bucket = TokenBucket(sim, rate_per_second=10, capacity=5)
    for _ in range(5):
        bucket.allow()
    assert bucket.retry_after_ms() == 100
    assert bucket.retry_after_ms(3) == 300


def test_retry_after_shrinks_as_time_passes(sim):
    bucket = TokenBucket(sim, rate_per_second=10, capacity=5)
    for _ in range(5):
        bucket.allow()
    assert bucket.retry_after_ms(2) == 200
    advance(sim, 150)
    assert bucket.retry_after_ms(2) == 50


def test_you_can_spend_more_than_one(sim):
    bucket = TokenBucket(sim, rate_per_second=10, capacity=50)
    assert bucket.allow(30) is True
    assert bucket.allow(30) is False
    assert bucket.allow(20) is True


@pytest.mark.parametrize("rate, capacity", [(0, 10), (-1, 10), (10, 0), (10, -5)])
def test_a_nonsense_bucket_is_an_error(sim, rate, capacity):
    with pytest.raises(ValueError):
        TokenBucket(sim, rate_per_second=rate, capacity=capacity)


# -- fixed window, and its flaw -----------------------------------------------


def test_a_fixed_window_holds_its_limit(sim):
    window = FixedWindow(sim, limit=100, window_ms=60_000)
    assert sum(window.allow() for _ in range(150)) == 100


def test_it_resets_at_the_boundary(sim):
    window = FixedWindow(sim, limit=100, window_ms=60_000)
    for _ in range(100):
        window.allow()
    assert window.allow() is False
    advance(sim, 60_000)
    assert window.allow() is True


def test_the_boundary_lets_through_twice_the_limit():
    """The reason nobody protects capacity with a fixed window.

    A limit of 100 a minute, and 200 requests land inside one second — because
    the counter reset happened between them. Not a rounding error. A factor of two,
    arriving at the worst possible moment.
    """
    sim = Simulation()
    window = FixedWindow(sim, limit=100, window_ms=60_000)

    advance(sim, 59_500)
    first = sum(window.allow() for _ in range(100))

    advance(sim, 500)             # 500 ms later, and a new window
    second = sum(window.allow() for _ in range(100))

    assert first == 100
    assert second == 100
    assert first + second == 200, "200 requests in 500 ms, under a 100-a-minute limit"


def test_a_token_bucket_does_not_do_that():
    """Same limit, same instant. The bucket has no boundary to exploit."""
    sim = Simulation()
    bucket = TokenBucket(sim, rate_per_second=100 / 60, capacity=100)

    advance(sim, 59_500)
    first = sum(bucket.allow() for _ in range(100))
    advance(sim, 500)
    second = sum(bucket.allow() for _ in range(100))

    assert first + second < 110
