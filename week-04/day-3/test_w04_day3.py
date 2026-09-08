"""Day 3 — hot keys."""

import pytest

from hotkeys import (
    TopK,
    is_hot,
    share,
    split_key,
    split_targets,
    utilisation_of_hot_partition,
)


# -- finding them -------------------------------------------------------------


def test_it_counts_what_it_tracks():
    top = TopK(k=3)
    for _ in range(5):
        top.observe("a")
    top.observe("b")
    assert top.heavy_hitters()[0] == ("a", 5)


def test_it_never_exceeds_its_memory():
    top = TopK(k=10)
    for i in range(10_000):
        top.observe(f"key-{i}")
    assert len(top.heavy_hitters()) == 10


def test_it_finds_a_genuinely_hot_key_in_a_sea_of_noise():
    """One channel takes 40% of a stream of otherwise-unique keys, and ten
    counters find it."""
    top = TopK(k=10)
    for i in range(6_000):
        top.observe(f"cold-{i}")
        if i % 3 == 0:
            top.observe("hot")
            top.observe("hot")

    assert top.heavy_hitters()[0][0] == "hot"


def test_counts_are_over_estimates_not_exact():
    """The price of fixed memory: an evicted key's count is inherited, so a
    tracked key's count is an upper bound. Good enough to rank; not a total."""
    top = TopK(k=2)
    top.observe("a", 10)
    top.observe("b", 10)
    top.observe("c")
    counts = dict(top.heavy_hitters())
    assert counts["c"] > 1


def test_results_are_ordered_and_deterministic():
    top = TopK(k=5)
    for key, n in [("a", 3), ("b", 7), ("c", 3)]:
        top.observe(key, n)
    assert top.heavy_hitters() == [("b", 7), ("a", 3), ("c", 3)]


def test_tracking_nothing_is_an_error():
    with pytest.raises(ValueError):
        TopK(k=0)


# -- deciding it is hot -------------------------------------------------------


def test_share_of_the_total():
    counts = {"a": 40, "b": 30, "c": 30}
    assert share(counts, "a") == pytest.approx(0.4)


def test_an_unseen_key_has_no_share():
    assert share({"a": 1}, "ghost") == 0.0


def test_no_traffic_at_all_is_not_a_division_by_zero():
    assert share({}, "a") == 0.0


def test_hot_is_a_threshold_you_choose():
    counts = {"whale": 40, **{f"t{i}": 1 for i in range(60)}}
    assert is_hot(counts, "whale") is True
    assert is_hot(counts, "t0") is False
    assert is_hot(counts, "whale", threshold=0.9) is False


# -- splitting ----------------------------------------------------------------


def test_a_split_key_has_a_suffix():
    assert split_key("hot", 16, 3) == "hot#3"


def test_a_reader_has_to_visit_all_of_them():
    """Sixteen targets, so a read of this key is a sixteen-way fan-out and its
    latency is the p99 of sixteen requests. You moved the cost, you did not
    remove it."""
    targets = split_targets("hot", 16)
    assert len(targets) == 16
    assert targets[0] == "hot#0"
    assert len(set(targets)) == 16


def test_a_split_beyond_its_ways_is_an_error():
    with pytest.raises(ValueError):
        split_key("hot", 4, 4)


def test_splitting_one_way_changes_nothing_useful():
    assert split_targets("hot", 1) == ["hot#0"]


# -- the number that ends the argument ----------------------------------------


def test_a_quiet_cluster_with_a_burning_partition():
    """Sixteen partitions, one key at 40% of traffic, cluster averaging 30%.

    The hot partition is at 192%. It is not slow, it is failing — and every
    average on the dashboard says the cluster is comfortable.
    """
    assert utilisation_of_hot_partition(0.40, 16, 0.30) == pytest.approx(1.92, abs=0.01)


def test_more_partitions_make_it_worse_not_better():
    """The reflex is to add machines. The hot key is still one key on one machine,
    and the average it is compared against just got smaller."""
    at_16 = utilisation_of_hot_partition(0.40, 16, 0.30)
    at_32 = utilisation_of_hot_partition(0.40, 32, 0.15)  # same total load, more machines
    assert at_32 == pytest.approx(at_16, abs=0.01), "identical, because nothing changed"


def test_an_even_workload_has_no_hot_partition():
    assert utilisation_of_hot_partition(1 / 16, 16, 0.30) == pytest.approx(0.30, abs=0.01)


def test_zero_partitions_is_an_error():
    with pytest.raises(ValueError):
        utilisation_of_hot_partition(0.4, 0, 0.3)
