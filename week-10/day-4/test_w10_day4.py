"""Day 4 — serving models and media."""

import pytest

from serving import (
    admission_by_tokens,
    capacity_in_requests,
    continuous_batch_utilisation,
    egress_cost,
    static_batch_utilisation,
    time_to_first_token_ms,
    tokens_per_second,
)

# One long generation and three short ones — the shape a real length distribution has.
SKEWED_BATCH = [2_000, 50, 50, 50]


# -- batching -----------------------------------------------------------------


def test_static_batching_wastes_most_of_the_accelerator():
    """Three of the four sequences finish in the first 3% of the batch and their
    slots then sit idle. Nothing is broken; the batch simply cannot end until its
    slowest member does."""
    assert static_batch_utilisation(SKEWED_BATCH) < 0.3


def test_a_uniform_batch_wastes_nothing():
    """Which is why this problem is invisible in a benchmark with fixed-length
    prompts, and unavoidable in production."""
    assert static_batch_utilisation([500, 500, 500, 500]) == pytest.approx(1.0)


def test_continuous_batching_fills_the_idle_slots():
    """The same batch, with a queue to refill from. This is the whole argument, and
    it is week 2 on expensive hardware: the batch is a queue, and its cost is set by
    its slowest member unless you keep refilling it."""
    assert continuous_batch_utilisation(SKEWED_BATCH, queue_depth=10) == 1.0


def test_a_shallow_queue_only_helps_partially():
    """There has to be work to refill with. At very low load, continuous batching
    and static batching converge — which is the case people benchmark."""
    partial = continuous_batch_utilisation(SKEWED_BATCH, queue_depth=1)
    assert static_batch_utilisation(SKEWED_BATCH) < partial < 1.0


def test_no_queue_is_static_batching():
    assert continuous_batch_utilisation(SKEWED_BATCH, 0) == static_batch_utilisation(SKEWED_BATCH)


@pytest.mark.parametrize("lengths", [[], [0, 10], [-5]])
def test_a_nonsense_batch_is_an_error(lengths):
    with pytest.raises(ValueError):
        static_batch_utilisation(lengths)


# -- capacity -----------------------------------------------------------------


def test_throughput_is_batch_times_step_rate():
    assert tokens_per_second(64, ms_per_step=25) == pytest.approx(2_560)


def test_capacity_in_requests_depends_entirely_on_length():
    """The number not to plan with.

    The same hardware, the same throughput, and a tenfold difference in capacity
    depending on how long the answers are. A capacity in requests is a capacity at
    one particular distribution, and the distribution moves whenever the product
    changes.
    """
    throughput = tokens_per_second(64, 25)
    short = capacity_in_requests(throughput, mean_tokens_per_request=300)
    long = capacity_in_requests(throughput, mean_tokens_per_request=3_000)
    assert short / long == pytest.approx(10, rel=0.01)


def test_planning_in_tokens_is_stable():
    """The same hardware always produces the same tokens per second, whatever
    anybody asks it. That is why the capacity plan is in tokens."""
    assert tokens_per_second(64, 25) == tokens_per_second(64, 25)


def test_a_request_producing_nothing_is_an_error():
    with pytest.raises(ValueError):
        capacity_in_requests(1_000, 0)


# -- the two latency objectives -----------------------------------------------


def test_a_deep_queue_delays_the_first_token():
    """Which users experience as "is it broken?" — a completely different feeling
    from slow tokens once it has started, and averaging the two describes neither."""
    throughput = tokens_per_second(64, 25)
    assert time_to_first_token_ms(5_000, throughput) > 1_500


def test_an_empty_queue_starts_immediately():
    assert time_to_first_token_ms(0, tokens_per_second(64, 25)) == 0.0


def test_admission_is_measured_in_tokens_not_requests():
    """One request can be a hundred times another, so counting requests in flight
    tells you almost nothing about what the queue actually costs."""
    assert admission_by_tokens(queued_tokens=3_000, budget_tokens=8_000) is True
    assert admission_by_tokens(queued_tokens=9_000, budget_tokens=8_000) is False


def test_a_budget_of_zero_admits_nothing():
    with pytest.raises(ValueError):
        admission_by_tokens(0, 0)


# -- the media half -----------------------------------------------------------


def test_bandwidth_is_the_bill():
    """Forty petabytes a month. For most systems bandwidth is a line item; here it
    is the largest number in the business, which is why the architecture is
    arranged around it rather than around latency."""
    assert egress_cost(40e15, cost_per_gb=0.02, edge_fraction=0.0) == pytest.approx(800_000)


def test_edge_coverage_is_the_lever():
    """Ninety per cent served from inside the viewer's network, and the bill falls
    by an order of magnitude. No amount of application optimisation does that."""
    central = egress_cost(40e15, 0.02, edge_fraction=0.0)
    at_edge = egress_cost(40e15, 0.02, edge_fraction=0.9)
    assert at_edge == pytest.approx(central / 10)


def test_a_percentage_point_is_a_large_number():
    """Which is why placement decisions get their own team."""
    difference = egress_cost(40e15, 0.02, 0.89) - egress_cost(40e15, 0.02, 0.90)
    assert difference == pytest.approx(8_000)


@pytest.mark.parametrize("fraction", [-0.1, 1.5])
def test_a_nonsense_edge_fraction_is_an_error(fraction):
    with pytest.raises(ValueError):
        egress_cost(1e12, 0.02, fraction)
