"""The milestone's mechanism.

`test_you_cannot_average_averages` is the one the brief is built around. Read it
even after it passes.
"""

import pytest

from rollup import (
    Agg,
    BRIEF_TIERS,
    bucket,
    downsample,
    mean_of_means,
    retention_bytes,
    rollup,
    tier_for,
)

MINUTE_MS = 60_000
HOUR_MS = 3_600_000


# -- bucketing ----------------------------------------------------------------


@pytest.mark.parametrize(
    "timestamp, resolution, expected",
    [
        (0, 60, 0),
        (59_999, 60, 0),
        (60_000, 60, 60_000),
        (60_001, 60, 60_000),
        (3_661_000, 3_600, 3_600_000),
        (1_500, 1, 1_000),
    ],
)
def test_bucket(timestamp, resolution, expected):
    assert bucket(timestamp, resolution) == expected


def test_bucketing_is_idempotent():
    """Bucketing a bucket start gives the same bucket. Downsampling relies on it."""
    start = bucket(123_456_789, 60)
    assert bucket(start, 60) == start


@pytest.mark.parametrize("resolution", [0, -1])
def test_a_bucket_needs_a_width(resolution):
    with pytest.raises(ValueError):
        bucket(1_000, resolution)


# -- aggregates ---------------------------------------------------------------


def test_an_aggregate_knows_its_mean():
    assert Agg(4, 10.0, 1.0, 4.0).mean == pytest.approx(2.5)


def test_there_is_no_mean_of_nothing():
    """Returning 0.0 would quietly drag down every average that touched it."""
    with pytest.raises(ValueError):
        Agg(0, 0.0, 0.0, 0.0).mean


def test_merging_is_exact():
    left = Agg(2, 10.0, 3.0, 7.0)
    right = Agg(3, 30.0, 1.0, 20.0)
    merged = left.merge(right)
    assert merged == Agg(5, 40.0, 1.0, 20.0)
    assert merged.mean == pytest.approx(8.0)


def test_merging_does_not_change_its_inputs():
    left = Agg(1, 1.0, 1.0, 1.0)
    right = Agg(1, 2.0, 2.0, 2.0)
    left.merge(right)
    assert left == Agg(1, 1.0, 1.0, 1.0)
    assert right == Agg(1, 2.0, 2.0, 2.0)


# -- the reason for all of this -----------------------------------------------


def test_you_cannot_average_averages():
    """The line in the brief that says an average over any window must be right.

    One bucket holds a single reading of 100. The next holds ninety-nine readings
    of 1. The true mean of those hundred readings is 1.99. Averaging the two bucket
    averages gives 50.5 — off by a factor of twenty-five, and it would look
    entirely plausible on a dashboard.

    This is why every real time-series store keeps count and sum rather than a mean.
    """
    spike = Agg(1, 100.0, 100.0, 100.0)
    quiet = Agg(99, 99.0, 1.0, 1.0)

    assert spike.merge(quiet).mean == pytest.approx(1.99, abs=0.01)
    assert mean_of_means([spike, quiet]) == pytest.approx(50.5, abs=0.01)


def test_averaging_averages_is_only_right_when_the_counts_match():
    """Which is the case people test with, and why the bug ships."""
    left = Agg(10, 100.0, 1.0, 20.0)
    right = Agg(10, 200.0, 5.0, 40.0)
    assert mean_of_means([left, right]) == pytest.approx(left.merge(right).mean)


# -- rolling up ---------------------------------------------------------------


def test_points_land_in_their_buckets():
    points = [(0, 1.0), (30_000, 3.0), (60_000, 10.0)]
    buckets = rollup(points, 60)

    assert set(buckets) == {0, 60_000}
    assert buckets[0] == Agg(2, 4.0, 1.0, 3.0)
    assert buckets[60_000] == Agg(1, 10.0, 10.0, 10.0)


def test_no_points_is_no_buckets():
    assert rollup([], 60) == {}


def test_a_gap_leaves_no_bucket():
    """Missing data is missing, not zero. A store that invents empty buckets
    invents readings, and every average over that window is then wrong."""
    buckets = rollup([(0, 5.0), (600_000, 5.0)], 60)
    assert set(buckets) == {0, 600_000}
    assert 300_000 not in buckets


# -- downsampling -------------------------------------------------------------


def test_downsampling_merges_into_coarser_buckets():
    minute_buckets = rollup([(i * 1_000, float(i)) for i in range(180)], 60)
    assert len(minute_buckets) == 3

    hourly = downsample(minute_buckets, 3_600)
    assert set(hourly) == {0}
    assert hourly[0].count == 180
    assert hourly[0].total == pytest.approx(sum(range(180)))


def test_downsampling_preserves_the_mean():
    points = [(i * 1_000, float(i % 7)) for i in range(3_600)]
    fine = rollup(points, 60)
    coarse = downsample(fine, 3_600)

    true_mean = sum(v for _, v in points) / len(points)
    assert coarse[0].mean == pytest.approx(true_mean)


def test_downsampling_is_associative():
    """A month of one-minute buckets becomes hourly overnight, and those become
    daily later. Doing it in two steps must equal doing it in one."""
    points = [(i * 1_000, float(i % 13)) for i in range(7_200)]
    minutes = rollup(points, 60)

    in_one_step = downsample(minutes, 86_400)
    in_two_steps = downsample(downsample(minutes, 3_600), 86_400)
    assert in_one_step == in_two_steps


def test_downsampling_keeps_the_extremes():
    """The spike is the reason anyone opened the dashboard. Averaging it away is
    the one thing a rollup must not do."""
    points = [(i * 1_000, 1.0) for i in range(3_600)] + [(1_800_000, 999.0)]
    hourly = downsample(rollup(points, 60), 3_600)
    assert max(a.maximum for a in hourly.values()) == 999.0


# -- retention ----------------------------------------------------------------


def test_the_brief_fits_under_the_ceiling():
    """28.2 TB against a 40 TB ceiling. It fits, with room — and the room is
    smaller than it looks."""
    total = retention_bytes(2_000_000)
    assert total == pytest.approx(28.2e12, rel=0.02)
    assert total < 40e12


def test_doubling_raw_retention_blows_the_ceiling():
    """One line of the retention policy, and the design no longer fits its budget.
    Which change, and by how much, belongs in your document."""
    two_days = [(1, 2), (60, 30), (3_600, 730)]
    assert retention_bytes(2_000_000, two_days) > 40e12


def test_replication_is_not_free():
    single = retention_bytes(2_000_000, replicas=1)
    triple = retention_bytes(2_000_000, replicas=3)
    assert triple == pytest.approx(3 * single)


def test_the_coarse_tier_is_cheap_despite_its_length():
    """Two years at one hour costs less than one day at one second. Resolution
    drives storage far harder than retention does, which is the whole reason
    rollups exist."""
    raw_only = retention_bytes(2_000_000, [(1, 1)])
    two_years_hourly = retention_bytes(2_000_000, [(3_600, 730)])
    assert two_years_hourly < raw_only


# -- which tier answers a query -----------------------------------------------


def test_recent_data_is_served_at_full_resolution():
    assert tier_for(1_800) == 1


def test_a_week_old_query_gets_minutes():
    assert tier_for(7 * 86_400) == 60


def test_a_year_old_query_gets_hours():
    assert tier_for(365 * 86_400) == 3_600


def test_data_older_than_every_tier_is_gone():
    assert tier_for(3 * 365 * 86_400) is None


def test_the_boundary_belongs_to_the_finer_tier():
    assert tier_for(86_400, BRIEF_TIERS) == 1
    assert tier_for(86_401, BRIEF_TIERS) == 60
