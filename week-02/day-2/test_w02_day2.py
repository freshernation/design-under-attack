"""Day 2 — utilisation, the knee, and variability."""

import pytest

from queueing import (
    bimodal_cv,
    kingman_wait,
    max_arrival_rate,
    response_time,
    servers_needed,
    utilisation,
    utilisation_after_losing_one,
    variability_penalty,
    wait_time,
)


# -- utilisation --------------------------------------------------------------


@pytest.mark.parametrize(
    "arrivals, capacity, expected",
    [(80, 100, 0.8), (50, 100, 0.5), (100, 100, 1.0), (0, 100, 0.0), (150, 100, 1.5)],
)
def test_utilisation(arrivals, capacity, expected):
    assert utilisation(arrivals, capacity) == pytest.approx(expected, abs=0.001)


def test_utilisation_over_one_is_reported_not_hidden():
    """A system receiving more than it can serve is a fact, not an exception."""
    assert utilisation(150, 100) > 1


@pytest.mark.parametrize("capacity", [0, -1])
def test_zero_capacity_is_an_error(capacity):
    with pytest.raises(ValueError):
        utilisation(10, capacity)


# -- the knee -----------------------------------------------------------------


@pytest.mark.parametrize(
    "rho, expected_multiples",
    [(0.0, 0.0), (0.5, 1.0), (0.7, 2.333), (0.8, 4.0), (0.9, 9.0), (0.95, 19.0), (0.99, 99.0)],
)
def test_the_wait_curve(rho, expected_multiples):
    """One second of service time, so the answer is in service times."""
    assert wait_time(1.0, rho) == pytest.approx(expected_multiples, abs=0.01)


def test_eighty_to_ninety_percent_roughly_doubles_the_wait():
    """The whole point of the article, as an assertion."""
    assert wait_time(1.0, 0.9) / wait_time(1.0, 0.8) == pytest.approx(2.25, abs=0.01)


def test_response_time_is_waiting_plus_being_served():
    assert response_time(0.010, 0.8) == pytest.approx(0.050, abs=0.0001)


@pytest.mark.parametrize("rho", [1.0, 1.2, -0.1])
def test_a_queue_that_does_not_drain_has_no_wait_time(rho):
    """At rho >= 1 the wait is unbounded. Returning a number would be a lie."""
    with pytest.raises(ValueError):
        wait_time(1.0, rho)


def test_load_that_fits_under_a_target():
    assert max_arrival_rate(100, 0.7) == pytest.approx(70.0)


def test_servers_needed_rounds_up():
    assert servers_needed(28_935, 300, 0.7) == 138
    assert servers_needed(1, 300, 0.7) == 1


def test_a_tighter_utilisation_target_costs_servers():
    at_ninety = servers_needed(10_000, 100, 0.9)
    at_seventy = servers_needed(10_000, 100, 0.7)
    assert at_seventy > at_ninety


# -- losing one ---------------------------------------------------------------


def test_three_at_sixty_five_percent_become_two_at_ninety_seven():
    """The most common outage shape there is, and the arithmetic takes ten seconds."""
    assert utilisation_after_losing_one(3, 0.65) == pytest.approx(0.975, abs=0.001)


def test_a_bigger_fleet_absorbs_a_loss_better():
    assert utilisation_after_losing_one(20, 0.65) < utilisation_after_losing_one(3, 0.65)


def test_losing_one_can_push_you_over_capacity():
    assert utilisation_after_losing_one(2, 0.8) > 1.0


@pytest.mark.parametrize("instances", [1, 0, -1])
def test_you_cannot_lose_one_of_one(instances):
    with pytest.raises(ValueError):
        utilisation_after_losing_one(instances, 0.5)


# -- variability --------------------------------------------------------------


def test_the_textbook_case_has_no_penalty():
    assert variability_penalty(1, 1) == pytest.approx(1.0, abs=0.001)


def test_doubling_service_variability_more_than_doubles_the_wait():
    assert variability_penalty(1, 2) == pytest.approx(2.5, abs=0.001)


def test_perfectly_regular_work_queues_far_less():
    """Batch jobs arriving on a fixed schedule, each taking the same time."""
    assert variability_penalty(0, 0) == pytest.approx(0.0, abs=0.001)


def test_kingman_is_the_mm1_wait_times_the_penalty():
    plain = wait_time(0.01, 0.8)
    assert kingman_wait(0.01, 0.8, 1, 1) == pytest.approx(plain, abs=1e-9)
    assert kingman_wait(0.01, 0.8, 1, 2) == pytest.approx(plain * 2.5, abs=1e-9)


# -- what a cache does to the distribution ------------------------------------


def test_a_cache_makes_service_times_wildly_variable():
    """1 ms hit, 40 ms miss, 5% miss rate.

    The mean service time is a healthy 3 ms. The coefficient of variation is
    nearly 3, which through Kingman means roughly five times the queueing of a
    steady 3 ms service. The average improved and the queue got worse.
    """
    cv = bimodal_cv(0.001, 0.040, 0.05)
    assert cv == pytest.approx(2.881, abs=0.01)
    assert variability_penalty(1, cv) > 4


def test_a_steady_service_time_has_no_variation():
    assert bimodal_cv(0.010, 0.010, 0.5) == pytest.approx(0.0, abs=0.001)


def test_a_rarer_miss_is_not_obviously_better():
    """Dropping the miss rate from 5% to 1% barely moves the variability, because
    the spread between the two values is what dominates, not their weighting."""
    assert bimodal_cv(0.001, 0.040, 0.01) == pytest.approx(2.792, abs=0.01)
