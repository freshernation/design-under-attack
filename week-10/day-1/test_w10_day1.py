"""Day 1 — geospatial.

`test_searching_one_cell_misses_a_neighbour_eleven_metres_away` is the day.
"""

import pytest

from geo import (
    CellIndex,
    candidates_at_resolution,
    cell_of,
    cell_side_metres,
    churn_writes_per_second,
    haversine_m,
    neighbours,
)


# -- cells --------------------------------------------------------------------


def test_a_point_lands_in_a_cell():
    assert cell_of(51.5074, -0.1278, resolution=1_000) == (51_507, -128)


def test_nearby_points_usually_share_a_cell():
    assert cell_of(51.50741, -0.12781, 1_000) == cell_of(51.50749, -0.12779, 1_000)


def test_the_southern_hemisphere_is_not_an_afterthought():
    """`int(-0.5)` is 0 and `floor(-0.5)` is -1. Getting this wrong puts half the
    planet in the wrong cells, and every test written with London coordinates
    passes anyway."""
    assert cell_of(-0.5, -0.5, resolution=1) == (-1, -1)


def test_a_cell_has_eight_neighbours():
    ring = neighbours((10, 10))
    assert len(ring) == 8
    assert (10, 10) not in ring


def test_resolution_sets_the_cell_size():
    assert cell_side_metres(1_000) == pytest.approx(111, abs=1)
    assert cell_side_metres(100) == pytest.approx(1_110, abs=10)


def test_a_nonsense_resolution_is_an_error():
    with pytest.raises(ValueError):
        cell_of(0, 0, resolution=0)


# -- distance -----------------------------------------------------------------


def test_a_point_is_no_distance_from_itself():
    assert haversine_m((51.5, -0.1), (51.5, -0.1)) == 0.0


def test_london_to_new_york():
    assert haversine_m((51.5074, -0.1278), (40.7128, -74.0060)) == pytest.approx(5.57e6, rel=0.02)


# -- the index ----------------------------------------------------------------


def test_it_finds_what_is_in_the_cell():
    index = CellIndex(resolution=1_000)
    index.insert("driver-1", 51.5074, -0.1278)
    assert index.search(51.5074, -0.1278) == ["driver-1"]


def test_searching_one_cell_misses_a_neighbour_eleven_metres_away():
    """The bug this whole design has, and the reason the ring is not optional.

    Two points eleven metres apart, on opposite sides of a cell boundary. A search
    of the passenger's own cell returns nothing at all — no error, no warning, and
    the nearest driver is a few paces away.
    """
    index = CellIndex(resolution=1_000)
    index.insert("driver-1", 51.49995, -0.1278)
    passenger = (51.50005, -0.1278)

    assert haversine_m(passenger, (51.49995, -0.1278)) < 20
    assert index.search(*passenger, ring=0) == []
    assert index.search(*passenger, ring=1) == ["driver-1"]


def test_the_exact_filter_removes_the_rest():
    """Cells give candidates; they do not give an answer. The ring covers about
    330 metres across, so a 50-metre query needs the real distance check."""
    index = CellIndex(resolution=1_000)
    index.insert("close", 51.50005, -0.1278)
    index.insert("far", 51.5010, -0.1278)

    assert len(index.search(51.5000, -0.1278, ring=1)) == 2
    assert index.within(51.5000, -0.1278, radius_m=50, ring=1) == ["close"]


def test_moving_within_a_cell_is_not_a_write():
    index = CellIndex(resolution=1_000)
    index.insert("driver-1", 51.50741, -0.1278)
    assert index.move("driver-1", 51.50745, -0.1278) is False


def test_moving_across_a_boundary_is_a_delete_and_an_insert():
    index = CellIndex(resolution=1_000)
    index.insert("driver-1", 51.49995, -0.1278)
    assert index.move("driver-1", 51.50005, -0.1278) is True
    assert index.occupants((51_499, -128)) == 0
    assert index.occupants((51_500, -128)) == 1


def test_an_empty_cell_is_removed():
    """Otherwise a city's worth of empty cells accumulates over a day of movement."""
    index = CellIndex(resolution=1_000)
    index.insert("driver-1", 51.49995, -0.1278)
    index.move("driver-1", 51.50005, -0.1278)
    assert (51_499, -128) not in index.cells


# -- choosing the resolution --------------------------------------------------


def test_a_finer_resolution_returns_fewer_candidates():
    """Which is the whole trade: fewer to filter, more cells to read, and a hot
    cell in a dense area either way."""
    fine = candidates_at_resolution(500, resolution=1_000)
    coarse = candidates_at_resolution(500, resolution=300)
    assert fine < coarse / 5


def test_the_ring_dominates_the_candidate_count():
    """A ring-1 search reads nine cells, not one. Sizing on a single cell
    understates the work by an order of magnitude."""
    with_ring = candidates_at_resolution(500, 1_000, ring=1)
    without = candidates_at_resolution(500, 1_000, ring=0)
    assert with_ring == pytest.approx(9 * without, rel=0.02)


def test_density_is_not_uniform():
    """The same resolution that gives fifty candidates in a city gives a handful in
    the countryside — and ten thousand in a city centre on New Year's Eve. Week 4's
    hot key, in a new costume."""
    quiet = candidates_at_resolution(5, 1_000)
    busy = candidates_at_resolution(50_000, 1_000)
    assert quiet < 1
    assert busy > 5_000


# -- the write load nobody asked for ------------------------------------------


def test_a_moving_population_generates_enormous_write_load():
    """A hundred thousand writes a second before anybody has requested anything.
    That number is why live-position systems keep this in memory and treat
    durability as optional — a lost position is corrected four seconds later."""
    assert churn_writes_per_second(400_000, report_interval_s=4) == 100_000


def test_reporting_less_often_costs_less():
    assert churn_writes_per_second(400_000, 10) < churn_writes_per_second(400_000, 4)


def test_a_zero_interval_is_an_error():
    with pytest.raises(ValueError):
        churn_writes_per_second(100, 0)
