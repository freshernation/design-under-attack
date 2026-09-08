"""Day 4 — shedding and degradation.

The first two tests are the week in one picture.
"""

import pytest

from shedding import (
    DEFAULT_THRESHOLDS,
    PriorityShedder,
    admit,
    goodput,
    goodput_with_shedding,
    healthy_fleet_fraction,
)


# -- the curve ----------------------------------------------------------------


def test_below_capacity_everything_is_useful():
    assert goodput(8_000, capacity_qps=10_000) == pytest.approx(8_000)


def test_past_capacity_an_unprotected_service_does_less_useful_work():
    """The shape nobody expects, and the whole reason shedding exists.

    Double the offered load and useful work does not plateau — it *falls*, because
    every response arrives after its client has given up. At sufficient overload a
    service can be entirely busy and produce almost nothing.
    """
    at_capacity = goodput(10_000, 10_000)
    at_double = goodput(20_000, 10_000)
    at_quadruple = goodput(40_000, 10_000)

    assert at_double < at_capacity
    assert at_quadruple < at_double


def test_shedding_holds_it_flat():
    """Same load, excess refused quickly instead of queued. Everything accepted is
    served, and a service that serves 80% and rejects 20% has done its job far
    better than one that accepts everything and completes nothing in time."""
    for offered in (10_000, 20_000, 40_000, 100_000):
        assert goodput_with_shedding(offered, 10_000) == pytest.approx(10_000)


def test_shedding_never_helps_below_capacity():
    """It is not free throughput. Below capacity the two are identical."""
    assert goodput_with_shedding(5_000, 10_000) == goodput(5_000, 10_000)


def test_a_service_with_no_capacity_is_an_error():
    with pytest.raises(ValueError):
        goodput(100, 0)


# -- priority -----------------------------------------------------------------


def test_low_priority_work_goes_first():
    shedder = PriorityShedder()
    assert shedder.allow("sheddable", utilisation=0.8) is False
    assert shedder.allow("critical", utilisation=0.8) is True


def test_under_heavy_load_only_the_critical_survives():
    """At 96% utilisation the product is degraded and working: logins and payments
    go through, and prefetch, analytics and recommendations do not."""
    shedder = PriorityShedder()
    assert shedder.shed_levels(0.96) == ["sheddable", "best_effort", "important"]
    assert shedder.allow("critical", 0.96) is True


def test_a_healthy_service_sheds_nothing():
    assert PriorityShedder().shed_levels(0.5) == []


def test_critical_work_is_shed_only_when_it_cannot_be_served():
    """Above the critical threshold there is no choice left. That the threshold is
    above 1.0 is the statement that you would rather queue critical work than
    refuse it."""
    assert DEFAULT_THRESHOLDS["critical"] > 1.0
    assert PriorityShedder().allow("critical", utilisation=1.5) is False


def test_an_unlabelled_request_is_an_error():
    """Defaulting it silently is how critical traffic gets shed by accident."""
    with pytest.raises(ValueError):
        PriorityShedder().allow("unknown", 0.5)


def test_unknown_priorities_in_the_config_are_an_error():
    with pytest.raises(ValueError):
        PriorityShedder({"urgent": 0.9})


# -- admission control --------------------------------------------------------


def test_a_fresh_queue_accepts_work():
    assert admit(oldest_queue_age_ms=50, client_timeout_ms=1_000) is True


def test_a_stale_queue_refuses():
    """Everything already queued is dead, and so is anything added to it. This is
    a self-tuning rule: it has no threshold to pick and no capacity to estimate."""
    assert admit(oldest_queue_age_ms=1_500, client_timeout_ms=1_000) is False


def test_it_needs_no_knowledge_of_capacity():
    """The same rule works at any capacity, on any hardware, at any traffic level —
    which is exactly what a hand-tuned threshold does not."""
    assert admit(900, 1_000) is True
    assert admit(1_100, 1_000) is False


def test_a_client_that_waits_no_time_is_an_error():
    with pytest.raises(ValueError):
        admit(10, 0)


# -- health checks that lie ---------------------------------------------------


def test_removing_a_few_unhealthy_hosts_is_fine():
    assert healthy_fleet_fraction(hosts=100, failing=5, max_removable=0.3) == pytest.approx(0.95)


def test_a_shared_dependency_would_otherwise_remove_everything():
    """The trap in a deep health check. One database problem marks every host
    unhealthy at once, and without a cap you now have no service at all rather than
    a degraded one.

    The cap means the worst case is a degraded fleet, which is a much better
    outcome than an empty one.
    """
    with_cap = healthy_fleet_fraction(hosts=100, failing=100, max_removable=0.3)
    assert with_cap == pytest.approx(0.7)

    without_cap = healthy_fleet_fraction(hosts=100, failing=100, max_removable=1.0)
    assert without_cap == 0.0


def test_no_failures_leaves_the_fleet_whole():
    assert healthy_fleet_fraction(100, 0, 0.3) == 1.0


@pytest.mark.parametrize("hosts, removable", [(0, 0.3), (10, -0.1), (10, 1.5)])
def test_a_nonsense_fleet_is_an_error(hosts, removable):
    with pytest.raises(ValueError):
        healthy_fleet_fraction(hosts, 1, removable)
