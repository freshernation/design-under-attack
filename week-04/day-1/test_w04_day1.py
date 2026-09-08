"""Day 1 — measuring a partition key."""

import pytest

from keys import (
    distribute,
    partition_for,
    partitions_needed,
    skew,
    utilisation_of_busiest,
)


# -- the hash -----------------------------------------------------------------


def test_a_key_always_lands_in_the_same_partition():
    assert partition_for("acme", 8) == partition_for("acme", 8)


def test_partitions_are_in_range():
    for i in range(200):
        assert 0 <= partition_for(f"key-{i}", 8) < 8


def test_it_does_not_move_between_runs():
    """Python randomises str hashing per process. A partition function built on
    the built-in `hash()` gives a different answer every time you restart, which
    is the kind of bug that only appears after a deploy."""
    assert partition_for("acme", 16) == 14


def test_zero_partitions_is_an_error():
    with pytest.raises(ValueError):
        partition_for("acme", 0)


# -- distribution -------------------------------------------------------------


def test_many_equal_keys_spread_evenly():
    keys = {f"key-{i}": 1.0 for i in range(10_000)}
    loads = distribute(keys, 8)
    assert sum(loads) == pytest.approx(10_000)
    assert skew(loads) < 1.1


def test_one_whale_ruins_it():
    """Ninety-nine ordinary tenants and one that is seventy per cent of the load."""
    keys = {f"tenant-{i}": 1.0 for i in range(99)}
    keys["whale"] = 231.0
    loads = distribute(keys, 8)
    assert skew(loads) > 4


def test_more_partitions_do_not_help_a_whale():
    """The reflex is to add machines. The whale is still one key on one machine,
    and the skew gets *worse* because the average drops."""
    keys = {f"tenant-{i}": 1.0 for i in range(99)}
    keys["whale"] = 231.0
    assert skew(distribute(keys, 32)) > skew(distribute(keys, 8))


# -- skew ---------------------------------------------------------------------


def test_a_perfect_split_is_one():
    assert skew([10, 10, 10, 10]) == pytest.approx(1.0)


def test_skew_is_busiest_over_average():
    assert skew([40, 20, 20, 20]) == pytest.approx(1.6)


def test_an_empty_fleet_is_an_error():
    with pytest.raises(ValueError):
        skew([])


def test_no_load_is_an_error():
    with pytest.raises(ValueError):
        skew([0, 0, 0])


# -- the translation that ends the argument -----------------------------------


def test_a_quiet_fleet_can_hide_a_burning_machine():
    """Fifteen per cent average utilisation, and one partition at eighty-seven.
    Every capacity number describes the average machine, and nobody is served by
    the average machine."""
    loads = [111.0] + [6.0] * 7
    assert skew(loads) == pytest.approx(5.8, abs=0.05)
    assert utilisation_of_busiest(loads, 0.15) == pytest.approx(0.87, abs=0.01)


def test_an_even_fleet_has_nothing_hidden():
    assert utilisation_of_busiest([10, 10, 10, 10], 0.6) == pytest.approx(0.6)


# -- sizing honestly ----------------------------------------------------------


def test_sizing_on_the_average_under_counts():
    even = partitions_needed(10_000, 1_000, skew_factor=1.0)
    lumpy = partitions_needed(10_000, 1_000, skew_factor=2.5)
    assert even == 10
    assert lumpy == 25


def test_sizing_rounds_up():
    assert partitions_needed(1_001, 1_000) == 2


def test_skew_below_one_is_impossible():
    """The busiest partition is at least the average, by definition. A skew of 0.8
    means the calculation upstream is wrong."""
    with pytest.raises(ValueError):
        partitions_needed(100, 10, skew_factor=0.8)


def test_no_capacity_is_an_error():
    with pytest.raises(ValueError):
        partitions_needed(100, 0)
