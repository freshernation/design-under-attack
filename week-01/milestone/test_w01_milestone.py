"""The milestone's arithmetic.

Green here means your numbers are right. It says nothing at all about whether your
design is any good — that is what Friday is for, and no test can replace it.
"""

import pytest

from estimate import estimate


@pytest.fixture(scope="module")
def n():
    return estimate()


# -- traffic ------------------------------------------------------------------


def test_writes_are_not_the_problem(n):
    """39 link creations a second. One machine, and no cleverness required.
    Establishing this in ten seconds is what the whole pass is for."""
    assert n["write_qps"] == pytest.approx(38.6, abs=0.2)


def test_peak_writes(n):
    assert n["peak_write_qps"] == pytest.approx(193.0, abs=1.0)


def test_reads(n):
    assert n["read_qps"] == pytest.approx(5787.0, abs=1.0)


def test_peak_reads(n):
    """Nearly 29,000 redirects a second at peak. This is the design."""
    assert n["peak_read_qps"] == pytest.approx(28_935.0, abs=10.0)


def test_the_ratio_is_the_headline(n):
    """150 reads per write. Everything that follows should serve the read path."""
    assert n["read_write_ratio"] == pytest.approx(150.0, rel=0.01)


# -- storage ------------------------------------------------------------------


def test_daily_storage_includes_replicas(n):
    assert n["daily_storage_bytes"] == pytest.approx(5.0e9, rel=0.01)


def test_the_ceiling_binds(n):
    """About 400 days. The brief's storage ceiling is not decoration — it forces a
    retention decision, and that decision belongs in your document."""
    assert n["max_retention_days"] == pytest.approx(400, rel=0.02)


def test_the_ceiling_is_reached_inside_two_years(n):
    assert n["max_retention_days"] < 730


# -- the working set ----------------------------------------------------------


def test_the_working_set_is_small(n):
    """Two days of links: about 3.3 GB. It fits in memory on one machine, which
    means the read path's hard problem is not where most people put it."""
    assert n["working_set_bytes"] == pytest.approx(3.33e9, rel=0.02)


def test_the_working_set_is_human_readable(n):
    assert n["working_set_human"] == "3.3 GB"


def test_the_working_set_is_a_rounding_error_next_to_a_year_of_data(n):
    year_of_data = n["daily_storage_bytes"] * 365
    assert n["working_set_bytes"] / year_of_data < 0.01


# -- everything is there ------------------------------------------------------


def test_every_key_is_present(n):
    expected = {
        "write_qps",
        "peak_write_qps",
        "read_qps",
        "peak_read_qps",
        "read_write_ratio",
        "daily_storage_bytes",
        "max_retention_days",
        "working_set_bytes",
        "working_set_human",
    }
    assert expected <= set(n)
