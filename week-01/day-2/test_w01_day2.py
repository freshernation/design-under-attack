"""Day 2 — the envelope, in numbers.

Green means your arithmetic matches the definitions. It says nothing about whether
the envelope you wrote for the photo service is any good; that is Friday's problem.
"""

import pytest

from envelope import (
    downtime_minutes,
    error_budget_remaining,
    is_measurable,
    page_slow_probability,
    parse_latency,
)


# -- downtime -----------------------------------------------------------------


@pytest.mark.parametrize(
    "target, window, expected",
    [
        (99.0, "month", 432.0),
        (99.9, "month", 43.2),
        (99.95, "month", 21.6),
        (99.99, "month", 4.3),
        (99.999, "month", 0.4),
        (99.9, "year", 525.6),
        (99.0, "year", 5256.0),
        (99.9, "week", 10.1),
        (99.9, "day", 1.4),
        (100.0, "month", 0.0),
    ],
)
def test_downtime_minutes(target, window, expected):
    assert downtime_minutes(target, window) == pytest.approx(expected, abs=0.05)


def test_month_is_the_default_window():
    assert downtime_minutes(99.9) == downtime_minutes(99.9, "month")


def test_four_nines_is_under_five_minutes_a_month():
    """The number worth internalising: less time than it takes a human to notice."""
    assert downtime_minutes(99.99, "month") < 5


@pytest.mark.parametrize("window", ["fortnight", "MONTH", "", "quarter"])
def test_unknown_window_is_an_error(window):
    with pytest.raises(ValueError):
        downtime_minutes(99.9, window)


@pytest.mark.parametrize("target", [0, -1, 100.1, 150])
def test_impossible_target_is_an_error(target):
    with pytest.raises(ValueError):
        downtime_minutes(target)


# -- error budget -------------------------------------------------------------


def test_budget_remaining_after_an_outage():
    assert error_budget_remaining(99.9, "month", 20) == pytest.approx(23.2, abs=0.05)


def test_budget_can_go_negative():
    """A blown budget is a number, not an exception. You report it."""
    assert error_budget_remaining(99.9, "month", 60) == pytest.approx(-16.8, abs=0.05)


def test_an_untouched_budget_is_the_whole_budget():
    assert error_budget_remaining(99.99, "month", 0) == downtime_minutes(99.99, "month")


# -- latency ------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("p99 < 200ms", (99.0, 200.0)),
        ("p50 < 40 ms", (50.0, 40.0)),
        ("p95<250ms", (95.0, 250.0)),
        ("p99.9 < 1s", (99.9, 1000.0)),
        ("p99.99 < 2.5s", (99.99, 2500.0)),
        ("P90 < 300 MS", (90.0, 300.0)),
    ],
)
def test_parse_latency(text, expected):
    percentile, ms = parse_latency(text)
    assert (percentile, ms) == pytest.approx(expected)


@pytest.mark.parametrize(
    "text",
    [
        "under 200ms",       # no percentile — not a target
        "p99",               # no number
        "fast",
        "",
        "p99 < quick",
    ],
)
def test_unparseable_latency_is_an_error(text):
    with pytest.raises(ValueError):
        parse_latency(text)


# -- measurability ------------------------------------------------------------


@pytest.mark.parametrize(
    "requirement",
    [
        "p99 read latency under 200ms at the load balancer",
        "99.9% of requests return a non-5xx over a 28 day window",
        "zero acknowledged writes lost given one AZ failure",
        "retain data for 90 days",
        "responses under 20 KB",
        "p99.9 < 1s",
    ],
)
def test_measurable_requirements(requirement):
    assert is_measurable(requirement) is True


@pytest.mark.parametrize(
    "requirement",
    [
        "The system should be fast",
        "It must be highly available",
        "The design should be scalable",
        "Data must be safe",
        "Users should have a good experience",
        "Near real-time",
    ],
)
def test_wishes_are_not_requirements(requirement):
    assert is_measurable(requirement) is False


def test_the_heuristic_has_a_known_blind_spot():
    """Read this one.

    "three replicas" is perfectly measurable and the rule says otherwise, because
    the rule looks for digits and this has a word. The rule is not wrong so much as
    narrow — it exists to catch "fast", "scalable" and "highly available", which are
    the failures that actually occur.

    A checker encodes a rule. It does not encode the truth, and the moment you forget
    that you start designing for the checker.
    """
    assert is_measurable("we need three replicas") is False


# -- the tail -----------------------------------------------------------------


def test_twenty_calls_and_a_one_percent_tail():
    """The number that justifies caring about p99 at all."""
    assert page_slow_probability(20, 0.01) == pytest.approx(0.1821, abs=0.0001)


@pytest.mark.parametrize(
    "calls, tail, expected",
    [
        (1, 0.01, 0.01),
        (100, 0.01, 0.6340),
        (10, 0.001, 0.0100),
        (5, 0.0, 0.0),
        (0, 0.5, 0.0),
    ],
)
def test_page_slow_probability(calls, tail, expected):
    assert page_slow_probability(calls, tail) == pytest.approx(expected, abs=0.0001)


def test_fan_out_makes_the_tail_the_typical_case():
    """100 parallel calls against a 1% tail: two thirds of requests hit it."""
    assert page_slow_probability(100, 0.01) > 0.6
