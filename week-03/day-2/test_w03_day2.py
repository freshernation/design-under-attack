"""Day 2 — amplification.

Note what these tests do and do not assert. The compaction tests check the
*direction* of the trade, never the numbers, because the numbers are a stipulated
model and asserting them would teach you to trust them.
"""

import pytest

from amplification import (
    btree_write_amplification,
    compare_compaction,
    device_write_rate,
    lsm_read_amplification,
    lsm_write_amplification,
    space_amplification,
)


# -- B-tree -------------------------------------------------------------------


def test_a_small_row_in_a_big_page():
    """The number that explains why write-heavy workloads leave B-trees."""
    assert btree_write_amplification(8_192, 100) == pytest.approx(81.9, abs=0.1)


def test_a_row_that_fills_its_page_costs_nothing_extra():
    assert btree_write_amplification(8_192, 8_192) == pytest.approx(1.0)


def test_a_row_of_no_bytes_is_an_error():
    with pytest.raises(ValueError):
        btree_write_amplification(8_192, 0)


# -- LSM ----------------------------------------------------------------------


def test_lsm_write_amplification_grows_with_levels():
    assert lsm_write_amplification(7, 10) == pytest.approx(70.0)
    assert lsm_write_amplification(4, 10) < lsm_write_amplification(7, 10)


def test_filters_take_read_amplification_to_about_one():
    """Twenty files, and a filter that is wrong one time in a hundred."""
    assert lsm_read_amplification(20, 0.01) == pytest.approx(1.2, abs=0.01)


def test_without_a_filter_you_read_every_file():
    assert lsm_read_amplification(20, 1.0) == pytest.approx(21.0)


def test_a_filter_is_worth_more_than_compaction_for_reads():
    """Twenty files with a filter beats two files without one. Filters are week 6,
    and this is why they matter."""
    assert lsm_read_amplification(20, 0.01) < lsm_read_amplification(2, 1.0)


def test_a_nonsense_false_positive_rate_is_an_error():
    with pytest.raises(ValueError):
        lsm_read_amplification(20, 1.5)


# -- space --------------------------------------------------------------------


def test_nothing_wasted_is_one():
    assert space_amplification(1_000, 0) == pytest.approx(1.0)


def test_deleted_data_still_costs_until_compaction():
    """Half the bytes on disk are values nobody can read any more."""
    assert space_amplification(1_000, 1_000) == pytest.approx(2.0)


# -- the multiplication that matters ------------------------------------------


def test_the_device_sees_far_more_than_the_application_writes():
    """40,000 writes a second of 200 bytes is 8 MB/s — comfortable. At 30x it is
    240 MB/s, which is a different conversation about hardware."""
    app = device_write_rate(40_000, 200, 1)
    device = device_write_rate(40_000, 200, 30)
    assert app == pytest.approx(8e6)
    assert device == pytest.approx(240e6)


def test_a_write_ahead_log_alone_doubles_it():
    """Everything is written twice before any page or compaction overhead."""
    assert device_write_rate(1_000, 100, 2) == 2 * device_write_rate(1_000, 100, 1)


# -- the trade ----------------------------------------------------------------


def test_leveled_pays_on_writes_and_saves_on_reads():
    leveled = compare_compaction("leveled")
    tiered = compare_compaction("tiered")
    assert leveled["write"] > tiered["write"]
    assert leveled["read"] < tiered["read"]
    assert leveled["space"] < tiered["space"]


def test_neither_strategy_wins_on_everything():
    """The RUM conjecture, as an assertion. If one row beat the other on all three,
    the config option would not exist."""
    leveled = compare_compaction("leveled")
    tiered = compare_compaction("tiered")
    better = [leveled[k] < tiered[k] for k in ("write", "read", "space")]
    assert any(better) and not all(better)


def test_an_unknown_strategy_is_an_error():
    with pytest.raises(ValueError):
        compare_compaction("magic")


def test_the_model_is_a_copy_you_cannot_corrupt():
    """compare_compaction hands back its own dict if you are careless, and then
    the next caller gets your edits. A small thing, and a real bug."""
    first = compare_compaction("leveled")
    first["write"] = 0
    assert compare_compaction("leveled")["write"] != 0
