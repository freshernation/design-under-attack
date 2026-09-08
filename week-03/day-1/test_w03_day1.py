"""Day 1 — what an index can and cannot serve.

The parametrised block walks every row of the composite-index table in the article.
"""

import pytest

from access import can_serve, is_covering, selectivity, write_amplification

TENANT_TIME = ["tenant", "created_at"]
TIME_TENANT = ["created_at", "tenant"]


# -- the leftmost prefix rule -------------------------------------------------


def test_equality_on_the_leading_column():
    assert can_serve(TENANT_TIME, {"tenant"}) is True


def test_equality_then_range():
    assert can_serve(TENANT_TIME, {"tenant"}, range_column="created_at") is True


def test_a_range_on_the_second_column_alone_is_a_scan():
    """The rows for a given time are scattered through every tenant's section."""
    assert can_serve(TENANT_TIME, set(), range_column="created_at") is False


def test_the_other_column_order_serves_the_other_query():
    assert can_serve(TIME_TENANT, set(), range_column="created_at") is True
    assert can_serve(TIME_TENANT, {"tenant"}) is False


def test_an_order_by_that_matches_the_index_is_free():
    assert can_serve(TENANT_TIME, {"tenant"}, order_by=["created_at"]) is True


def test_an_order_by_the_index_does_not_provide():
    assert can_serve(["tenant"], {"tenant"}, order_by=["created_at"]) is False


def test_you_cannot_start_in_the_middle_of_an_ordering():
    assert can_serve(["a", "b", "c"], {"b"}) is False
    assert can_serve(["a", "b", "c"], {"a"}) is True
    assert can_serve(["a", "b", "c"], {"a", "b"}) is True
    assert can_serve(["a", "b", "c"], {"a", "b", "c"}) is True


def test_order_among_equality_columns_does_not_matter():
    """Equality on a set of columns is order-independent — they are all pinned."""
    assert can_serve(["a", "b", "c"], ["b", "a"]) is True


def test_equalities_must_be_a_prefix_not_a_subset():
    """(tenant, created_at, status) cannot serve tenant = X AND status = Y as a
    lookup, because created_at sits between them in the ordering."""
    assert can_serve(["tenant", "created_at", "status"], {"tenant", "status"}) is False


def test_the_range_column_must_come_before_the_sort():
    assert can_serve(["a", "t", "s"], {"a"}, range_column="t", order_by=["t"]) is True
    assert can_serve(["a", "s", "t"], {"a"}, range_column="t") is False


def test_an_index_shorter_than_the_query_needs():
    assert can_serve(["a"], {"a", "b"}) is False


# -- covering -----------------------------------------------------------------


def test_a_covering_index_never_reads_the_row():
    assert is_covering(["tenant", "created_at", "status"], ["status"]) is True


def test_a_missing_column_costs_a_trip_to_the_row():
    assert is_covering(["tenant", "created_at"], ["email"]) is False


def test_selecting_nothing_is_trivially_covered():
    assert is_covering(["a"], []) is True


# -- selectivity --------------------------------------------------------------


def test_a_unique_column_is_perfectly_selective():
    assert selectivity(10_000_000, 10_000_000) == pytest.approx(1.0)


def test_a_status_column_narrows_almost_nothing():
    """Three values across a hundred million rows. An index here is worse than a
    scan, and a competent planner will ignore it."""
    assert selectivity(3, 100_000_000) < 0.0001


def test_selectivity_of_no_rows_is_an_error():
    with pytest.raises(ValueError):
        selectivity(3, 0)


# -- the write side -----------------------------------------------------------


def test_every_index_is_another_write():
    assert write_amplification(0) == 1
    assert write_amplification(4) == 5


def test_indexes_are_not_free_advice():
    """Four indexes means an insert writes five structures, at five different
    random positions. This is why write-heavy tables have few indexes."""
    assert write_amplification(4) == 5 * write_amplification(0)
