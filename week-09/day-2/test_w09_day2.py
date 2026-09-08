"""Day 2 — retries.

`test_jitter_flattens_the_wave` is the day. Same clients, same failure, same
backoff, one line different.
"""

import pytest

from retry import RetryBudget, arrival_spread, backoff_delays, storm_peak, total_attempts
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation(seed=4)


# -- backoff ------------------------------------------------------------------


def test_exponential_doubles(sim):
    assert backoff_delays(5, 100, "exponential", sim.random) == [100, 200, 400, 800, 1600]


def test_exponential_is_identical_for_every_client(sim):
    """Which is the problem. Ten thousand clients back off by exactly the same
    amount and return in exactly the same instant."""
    a = backoff_delays(5, 100, "exponential", sim.random)
    b = backoff_delays(5, 100, "exponential", sim.random)
    assert a == b
    assert arrival_spread([d[-1] for d in (a, b)]) == 0


def test_full_jitter_stays_within_the_window(sim):
    delays = backoff_delays(5, 100, "full_jitter", sim.random)
    assert all(0 <= d <= 100 * 2**n for n, d in enumerate(delays))


def test_jitter_spreads_clients_out(sim):
    """The same attempt, across many clients, lands all over the window instead of
    on one point."""
    third_attempts = [backoff_delays(3, 100, "full_jitter", sim.random)[-1] for _ in range(200)]
    assert arrival_spread(third_attempts) > 200


def test_a_cap_bounds_the_wait(sim):
    delays = backoff_delays(10, 100, "exponential", sim.random, cap_ms=1_000)
    assert max(delays) == 1_000


def test_decorrelated_grows_but_varies(sim):
    delays = backoff_delays(8, 100, "decorrelated", sim.random)
    assert all(d >= 100 for d in delays)
    assert len(set(delays)) > 1


@pytest.mark.parametrize("strategy, base", [("magic", 100), ("exponential", 0)])
def test_a_nonsense_backoff_is_an_error(sim, strategy, base):
    with pytest.raises(ValueError):
        backoff_delays(3, base, strategy, sim.random)


# -- the storm ----------------------------------------------------------------


def test_backoff_alone_does_not_spread_anything(sim):
    """Ten thousand clients fail together, all back off by 800 ms, and all return
    in the same 50 ms bucket. The wave is exactly as tall as the failure was."""
    assert storm_peak(10_000, 100, "exponential", sim.random, attempt=5) == 10_000


def test_jitter_flattens_the_wave(sim):
    """The day.

    Same ten thousand clients, same failure, same base and same attempt number.
    The only difference is one line in the client, and the peak the recovering
    service actually receives is nearly thirty times smaller.
    """
    plain = storm_peak(10_000, 100, "exponential", sim.random, attempt=5)
    jittered = storm_peak(10_000, 100, "full_jitter", sim.random, attempt=5)
    assert jittered < plain / 20


def test_the_later_the_attempt_the_more_jitter_helps(sim):
    """Because the window it spreads across doubles each time, while the
    unjittered wave stays exactly one instant wide."""
    early = storm_peak(10_000, 100, "full_jitter", sim.random, attempt=3)
    late = storm_peak(10_000, 100, "full_jitter", sim.random, attempt=6)
    assert late < early


# -- the retry budget ---------------------------------------------------------


def test_retries_are_allowed_when_failures_are_rare(sim):
    """Healthy conditions: the budget is nowhere near its limit and every request
    that needs a retry gets one."""
    budget = RetryBudget(sim, window_ms=60_000, ratio=0.1)
    for _ in range(1_000):
        budget.record_request()
    assert budget.allow() is True


def test_the_budget_runs_out_during_an_outage(sim):
    """And this is the point: it runs out immediately, which is exactly when you
    wanted the client to stop adding load."""
    budget = RetryBudget(sim, window_ms=60_000, ratio=0.1)
    for _ in range(100):
        budget.record_request()
    for _ in range(10):
        budget.record_retry()

    assert budget.allow() is False


def test_the_budget_recovers_as_the_window_moves(sim):
    budget = RetryBudget(sim, window_ms=60_000, ratio=0.1)
    for _ in range(100):
        budget.record_request()
    for _ in range(10):
        budget.record_retry()
    assert budget.allow() is False

    advance(sim, 60_001)
    for _ in range(100):
        budget.record_request()
    assert budget.allow() is True


def test_a_budget_with_no_traffic_allows_nothing(sim):
    """A client that has made no requests has no retry allowance, which is correct:
    there is nothing to be a fraction of."""
    assert RetryBudget(sim, 60_000, 0.1).allow() is False


@pytest.mark.parametrize("window, ratio", [(0, 0.1), (60_000, 0), (60_000, 1.5)])
def test_a_nonsense_budget_is_an_error(sim, window, ratio):
    with pytest.raises(ValueError):
        RetryBudget(sim, window, ratio)


# -- retrying at every layer --------------------------------------------------


def test_three_layers_of_three_is_twenty_seven():
    """One user action, twenty-seven requests at the bottom, and every layer
    believes it is being modest."""
    assert total_attempts(layers=3, retries_each=2) == 27


def test_retrying_at_one_layer_is_linear():
    assert total_attempts(layers=1, retries_each=2) == 3


def test_the_multiplication_gets_worse_quickly():
    assert total_attempts(4, 3) > 200


def test_no_retries_anywhere_is_one_request():
    assert total_attempts(layers=5, retries_each=0) == 1
