"""Day 1 — SLOs and error budgets."""

import pytest

from slo import (
    budget_remaining,
    burn_rate,
    dependency_ceiling,
    error_budget_minutes,
    is_reachable,
    should_page,
    time_to_exhaustion_hours,
)


# -- the budget ---------------------------------------------------------------


def test_three_nines_over_four_weeks():
    assert error_budget_minutes(99.9, 28) == pytest.approx(40.3, abs=0.1)


def test_four_nines_is_four_minutes():
    """Less time than a human takes to read a page and decide what to do — which is
    why the next nine is a different system rather than a better one."""
    assert error_budget_minutes(99.99, 28) < 5


def test_a_perfect_target_permits_nothing():
    assert error_budget_minutes(100, 28) == 0.0


def test_budget_can_go_negative():
    assert budget_remaining(99.9, 28, minutes_down=60) < 0


@pytest.mark.parametrize("target, window", [(0, 28), (101, 28), (99.9, 0)])
def test_nonsense_budgets_are_an_error(target, window):
    with pytest.raises(ValueError):
        error_budget_minutes(target, window)


# -- burn rate ----------------------------------------------------------------


def test_exactly_on_budget_is_a_rate_of_one():
    assert burn_rate(0.001, 99.9) == pytest.approx(1.0)


def test_a_five_percent_error_rate_against_three_nines():
    """Fifty times the permitted rate. Not "slightly degraded"."""
    assert burn_rate(0.05, 99.9) == pytest.approx(50.0)


def test_a_month_of_budget_can_go_in_days():
    """The number that turns an error rate into an incident. At a burn rate of 10,
    four weeks of budget is gone in under three days."""
    assert time_to_exhaustion_hours(10, 28) / 24 < 3


def test_on_budget_lasts_exactly_the_window():
    assert time_to_exhaustion_hours(1, 28) == pytest.approx(28 * 24)


def test_no_errors_never_exhausts_it():
    assert time_to_exhaustion_hours(0) == float("inf")


def test_a_hundred_percent_target_has_no_burn_rate():
    with pytest.raises(ValueError):
        burn_rate(0.01, 100)


# -- the ceiling nobody computes ----------------------------------------------


def test_dependencies_multiply():
    """Four things at 99.95% gives 99.8%. Your own code is not in this calculation
    at all."""
    assert dependency_ceiling([99.95] * 4) == pytest.approx(99.8, abs=0.01)


def test_a_target_can_be_unreachable_before_you_write_any_code():
    """The single most useful thing to compute before agreeing to a number, and the
    one people never do. When this is False the answer is fewer dependencies on the
    critical path, not better engineering."""
    assert is_reachable(99.9, [99.95] * 4) is False
    assert is_reachable(99.5, [99.95] * 4) is True


def test_one_weak_dependency_sets_the_ceiling():
    assert dependency_ceiling([99.99, 99.99, 99.0]) < 99.1


def test_fewer_dependencies_raise_the_ceiling():
    assert dependency_ceiling([99.95] * 2) > dependency_ceiling([99.95] * 8)


@pytest.mark.parametrize("availabilities", [[], [0], [101]])
def test_nonsense_dependencies_are_an_error(availabilities):
    with pytest.raises(ValueError):
        dependency_ceiling(availabilities)


# -- alerting -----------------------------------------------------------------


def test_a_severe_burn_pages_quickly():
    """Two per cent of a four-week budget in an hour."""
    assert should_page(rate=20, window_hours=1) is True


def test_a_brief_blip_does_not():
    """A thirty-second wobble costs a fraction of a per cent of the budget. Paging
    for it is how on-call rotations become unbearable."""
    assert should_page(rate=3, window_hours=1) is False


def test_a_slow_leak_is_caught_on_a_longer_window():
    """Too gentle to trip the fast rule and it will still empty the month. One
    window cannot do both — it is either too twitchy or too slow."""
    assert should_page(rate=8, window_hours=1) is False
    assert should_page(rate=8, window_hours=6) is True


def test_a_gentle_burn_is_a_ticket_not_a_page():
    assert should_page(rate=2, window_hours=6) is False
    assert should_page(rate=2, window_hours=24) is False
