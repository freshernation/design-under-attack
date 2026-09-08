"""Day 3 — sizing.

These check that your definitions match the course's. They cannot check the far more
important thing, which is whether you noticed which number was the design problem.
"""

import pytest

from sizing import (
    budget_remaining,
    daily_bytes,
    first_hop_over_budget,
    human_bytes,
    is_geographically_possible,
    peak_qps,
    qps,
    storage_bytes,
    working_set_bytes,
)


# -- the chain ----------------------------------------------------------------


@pytest.mark.parametrize(
    "per_day, expected",
    [
        (86_400, 1.0),
        (30_000_000, 347.2),
        (500_000_000, 5787.0),
        (100_000, 1.2),
        (0, 0.0),
    ],
)
def test_qps(per_day, expected):
    assert qps(per_day) == pytest.approx(expected, abs=0.1)


def test_peak_defaults_to_five_times():
    assert peak_qps(347.2) == pytest.approx(1736.0, abs=0.1)


@pytest.mark.parametrize("factor, expected", [(1, 100.0), (3, 300.0), (10, 1000.0)])
def test_peak_factor(factor, expected):
    assert peak_qps(100.0, factor) == pytest.approx(expected, abs=0.1)


def test_daily_bytes():
    assert daily_bytes(3_333_333, 500) == 1_666_666_500


def test_storage_replicates_three_times_by_default():
    one_day_one_replica = daily_bytes(1_000, 100)
    assert storage_bytes(1_000, 100, retention_days=1) == one_day_one_replica * 3


def test_storage_over_five_years():
    """100M links a month, 500 bytes each, five years, three copies."""
    total = storage_bytes(3_333_333, 500, retention_days=1825, replicas=3)
    assert total == pytest.approx(9.125e12, rel=0.01)


def test_retention_is_the_bigger_lever_than_volume():
    ten_x_volume = storage_bytes(10_000, 100, 90)
    ten_x_retention = storage_bytes(1_000, 100, 900)
    assert ten_x_volume == ten_x_retention


def test_working_set():
    assert working_set_bytes(20_000, 2_000) == 40_000_000


def test_a_working_set_can_be_tiny_next_to_the_dataset():
    """Ten million products, but only twenty thousand are hot. This is the
    arithmetic that ends most caching arguments."""
    whole = working_set_bytes(10_000_000, 2_000)
    hot = working_set_bytes(20_000, 2_000)
    assert hot / whole < 0.01
    assert human_bytes(hot) == "40.0 MB"


# -- readable numbers ---------------------------------------------------------


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, "0 B"),
        (1, "1 B"),
        (999, "999 B"),
        (1_000, "1.0 KB"),
        (1_500, "1.5 KB"),
        (1_666_666_500, "1.7 GB"),
        (40_000_000, "40.0 MB"),
        (3_600_000_000_000, "3.6 TB"),
        (9_125_000_000_000, "9.1 TB"),
        (2_500_000_000_000_000, "2.5 PB"),
    ],
)
def test_human_bytes(n, expected):
    assert human_bytes(n) == expected


def test_human_bytes_uses_decimal_units_not_binary():
    """1 KB is 1,000 bytes here. Cloud bills are decimal; so is this course."""
    assert human_bytes(1_024) == "1.0 KB"


# -- latency budgets ----------------------------------------------------------

PAGE_HOPS = [
    ("client to edge", 40.0),
    ("edge to origin", 20.0),
    ("load balancer", 1.0),
    ("cache hit", 1.0),
    ("database", 10.0),
    ("render", 15.0),
    ("response to client", 60.0),
]


def test_budget_remaining():
    assert budget_remaining(200, PAGE_HOPS) == pytest.approx(53.0, abs=0.1)


def test_a_budget_can_go_negative():
    assert budget_remaining(100, PAGE_HOPS) == pytest.approx(-47.0, abs=0.1)


def test_no_hop_is_over_budget_when_it_fits():
    assert first_hop_over_budget(200, PAGE_HOPS) is None


def test_naming_the_hop_that_broke_it():
    assert first_hop_over_budget(100, PAGE_HOPS) == "response to client"


def test_the_first_hop_can_break_it_on_its_own():
    assert first_hop_over_budget(30, PAGE_HOPS) == "client to edge"


def test_an_empty_hop_list_spends_nothing():
    assert budget_remaining(200, []) == pytest.approx(200.0)
    assert first_hop_over_budget(200, []) is None


# -- physics ------------------------------------------------------------------


def test_london_to_new_york_round_trip_floor():
    """~5,600 km, so ~56 ms at the theoretical best. Real links are worse."""
    assert is_geographically_possible(56, 5_600) is True
    assert is_geographically_possible(50, 5_600) is False


def test_sub_100ms_to_sydney_is_impossible():
    """~17,000 km. No cache, no CDN, no cleverness. This is the answer to give
    when a brief asks for it, and giving it takes five seconds."""
    assert is_geographically_possible(100, 17_000) is False


def test_same_region_is_never_the_problem():
    assert is_geographically_possible(5, 50) is True
