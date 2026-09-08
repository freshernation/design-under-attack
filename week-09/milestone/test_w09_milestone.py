"""The review's arithmetic.

`test_the_order_they_help_is_not_the_order_people_add_them` is the milestone.
"""

import pytest

from resilience import (
    Protections,
    effective_capacity,
    effective_offered,
    incident_goodput,
    run_incident,
)

# One incident, used throughout: a dependency that 30% of traffic needs has failed.
INCIDENT = dict(
    offered_qps=10_000,
    base_capacity_qps=10_000,
    dependency_failing=True,
    dependent_fraction=0.3,
)


def goodput_with(**protections) -> float:
    return run_incident(protections=Protections(**protections), **INCIDENT)["goodput"]


# -- retries ------------------------------------------------------------------


def test_retries_multiply_the_load_during_an_outage():
    """Two retries each, everything failing: three times the traffic, arriving at
    a service that is already unable to cope."""
    assert effective_offered(10_000, retries=2, has_retry_budget=False) == 30_000


def test_a_budget_caps_the_multiplier():
    """From 3x to 1.1x, whatever the failure rate. An unbounded multiplier becomes
    a bounded one, at exactly the moment the multiplier matters."""
    assert effective_offered(10_000, retries=2, has_retry_budget=True) == 11_000


def test_a_healthy_system_pays_nothing_for_its_retry_policy():
    """Which is why the policy is so easy to overlook until an incident, and why
    it never shows up in a load test that does not break anything."""
    assert effective_offered(10_000, retries=0, has_retry_budget=False) == 10_000
    assert effective_offered(10_000, retries=0, has_retry_budget=True) == 10_000


def test_negative_retries_are_an_error():
    with pytest.raises(ValueError):
        effective_offered(100, retries=-1, has_retry_budget=False)


# -- capacity -----------------------------------------------------------------


def test_a_slow_dependency_collapses_a_shared_pool():
    """Thirty per cent of requests need the broken thing, and **all** of the
    capacity is gone — because the slow calls hold the shared pool and everything
    else queues behind them. Little's Law, in an incident."""
    collapsed = effective_capacity(10_000, True, 0.3, has_breaker=False, has_bulkhead=False)
    assert collapsed < 0.25 * 10_000


def test_a_breaker_limits_the_loss_to_the_dependent_fraction():
    """The calls fail instantly instead of waiting, so the 70% that never needed
    the dependency keep working. That is the whole trade."""
    protected = effective_capacity(10_000, True, 0.3, has_breaker=True, has_bulkhead=False)
    assert protected == pytest.approx(7_000)


def test_a_bulkhead_reaches_the_same_place_differently():
    breaker = effective_capacity(10_000, True, 0.3, has_breaker=True, has_bulkhead=False)
    bulkhead = effective_capacity(10_000, True, 0.3, has_breaker=False, has_bulkhead=True)
    assert breaker == bulkhead


def test_having_both_does_not_help_twice():
    """Worth knowing before adding the second one. They overlap: one stops you
    waiting, the other stops the waiting from spreading, and against this failure
    either is sufficient."""
    one = effective_capacity(10_000, True, 0.3, has_breaker=True, has_bulkhead=False)
    both = effective_capacity(10_000, True, 0.3, has_breaker=True, has_bulkhead=True)
    assert one == both


def test_nothing_is_lost_when_nothing_is_failing():
    assert effective_capacity(10_000, False, 0.3, False, False) == 10_000


def test_a_nonsense_dependent_fraction_is_an_error():
    with pytest.raises(ValueError):
        effective_capacity(10_000, True, 1.5, False, False)


# -- goodput ------------------------------------------------------------------


def test_overload_without_shedding_wastes_the_work():
    assert incident_goodput(40_000, 10_000, has_shedding=False) < 10_000


def test_shedding_holds_it_at_capacity():
    assert incident_goodput(40_000, 10_000, has_shedding=True) == 10_000


def test_no_capacity_produces_nothing():
    assert incident_goodput(10_000, 0, has_shedding=True) == 0.0


# -- the milestone ------------------------------------------------------------


def test_an_unprotected_system_produces_almost_nothing():
    """Ten thousand requests a second offered, and single-figure goodput. The
    service is entirely busy and the product is down."""
    assert goodput_with() < 100


def test_every_protection_helps_on_its_own():
    baseline = goodput_with()
    assert goodput_with(retry_budget=True) > baseline
    assert goodput_with(breaker=True) > baseline
    assert goodput_with(shedding=True) > baseline


def test_the_order_they_help_is_not_the_order_people_add_them():
    """The milestone, and the finding worth taking into a review.

    Circuit breakers get added first because they are the famous one. On this
    incident, **shedding alone beats a breaker and a retry budget together** — by
    a wide margin — because it stops the service doing work nobody is waiting for.

    That is not an argument against breakers. It is an argument for computing the
    numbers before deciding what to build, which is the whole of a resilience
    review.
    """
    breaker_and_budget = goodput_with(breaker=True, retry_budget=True)
    shedding_alone = goodput_with(shedding=True)

    assert goodput_with(breaker=True) < shedding_alone
    assert shedding_alone < breaker_and_budget, "and together they still win"


def test_all_four_degrade_by_exactly_the_broken_part():
    """The outcome to aim for. Thirty per cent of traffic needed the failed
    dependency and thirty per cent of the goodput is gone — no more.

    A design that loses only what actually depends on the broken thing has
    degraded rather than failed, and that distinction is the week.
    """
    protected = goodput_with(retry_budget=True, breaker=True, bulkhead=True, shedding=True)
    healthy = run_incident(
        offered_qps=10_000,
        base_capacity_qps=10_000,
        dependency_failing=False,
        dependent_fraction=0.3,
        protections=Protections(),
    )["goodput"]

    assert protected == pytest.approx(0.7 * healthy)


def test_protections_cost_nothing_when_nothing_is_wrong():
    """Which is why they are hard to justify and easy to remove. The only evidence
    they were worth having is an incident that did not happen."""
    for protections in (Protections(), Protections(True, True, True, True)):
        result = run_incident(
            offered_qps=10_000,
            base_capacity_qps=10_000,
            dependency_failing=False,
            dependent_fraction=0.3,
            protections=protections,
        )
        assert result["goodput"] == 10_000
