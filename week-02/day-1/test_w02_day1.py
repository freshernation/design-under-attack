"""Day 1 — Little's Law."""

import pytest

from littles import (
    concurrency,
    max_throughput,
    pool_size,
    throughput_retained,
    wait_seconds,
)


@pytest.mark.parametrize(
    "throughput, latency, expected",
    [
        (500, 0.2, 100.0),
        (1000, 0.05, 50.0),
        (10, 3.0, 30.0),
        (28_935, 0.02, 578.7),
        (0, 0.2, 0.0),
    ],
)
def test_concurrency(throughput, latency, expected):
    assert concurrency(throughput, latency) == pytest.approx(expected, abs=0.1)


def test_the_number_is_smaller_than_people_expect():
    """500 requests a second does not mean 500 threads. It means 100."""
    assert concurrency(500, 0.2) < 500


def test_wait_behind_a_backlog():
    assert wait_seconds(10_000, 200) == pytest.approx(50.0, abs=0.1)


def test_a_deeper_queue_on_a_faster_consumer_can_be_fine():
    """Depth alone means nothing. This is why the metric is age, not depth."""
    assert wait_seconds(50_000, 5_000) < wait_seconds(1_000, 20)


@pytest.mark.parametrize("drain", [0, -1, -100])
def test_a_queue_that_is_not_draining_is_an_error(drain):
    with pytest.raises(ValueError):
        wait_seconds(1_000, drain)


def test_what_a_pool_supports():
    assert max_throughput(50, 0.01) == pytest.approx(5_000.0, abs=1)


def test_pool_sizing_rounds_up():
    assert pool_size(500, 0.2) == 150
    assert pool_size(1, 0.01) == 1


def test_pool_sizing_headroom_is_configurable():
    assert pool_size(500, 0.2, headroom=1.0) == 100
    assert pool_size(500, 0.2, headroom=2.0) == 200


def test_a_tripled_latency_costs_two_thirds_of_your_throughput():
    """10 ms to 30 ms. The pool is unchanged, the hardware is unchanged, and
    throughput is now a third of what it was."""
    assert throughput_retained(0.010, 0.030) == pytest.approx(0.333, abs=0.001)


@pytest.mark.parametrize(
    "old, new, expected",
    [
        (0.010, 0.010, 1.0),
        (0.010, 0.020, 0.5),
        (0.200, 0.100, 2.0),
        (0.010, 0.100, 0.1),
    ],
)
def test_throughput_retained(old, new, expected):
    assert throughput_retained(old, new) == pytest.approx(expected, abs=0.001)


def test_the_whole_law_is_consistent_with_itself():
    """L = λW, three ways round, must agree."""
    load, latency = 500, 0.2
    inside = concurrency(load, latency)
    assert max_throughput(inside, latency) == pytest.approx(load, abs=0.1)
    assert wait_seconds(inside, load) == pytest.approx(latency, abs=0.1)
