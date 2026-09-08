"""The milestone's arithmetic: is the specialised mechanism worth it?"""

import pytest

from tradeoff import (
    binding_constraint,
    break_even_volume,
    headroom,
    headroom_months,
    is_worth_it,
    total_cost,
)


# -- what is actually the constraint ------------------------------------------


def test_it_finds_the_tightest_resource():
    usage = {
        "cpu": (400, 1_000),
        "memory": (900, 1_000),
        "network": (200, 1_000),
    }
    assert binding_constraint(usage) == "memory"


def test_it_is_often_not_the_one_the_brief_emphasises():
    """A dispatch system talks about query latency and is bound by position-update
    writes. An inference service talks about compute and is bound by memory. The
    brief's emphasis is a description of what people worry about, not of what
    binds."""
    dispatch = {
        "query_cpu": (300, 4_000),
        "position_writes": (100_000, 110_000),
        "storage": (2_000, 50_000),
    }
    assert binding_constraint(dispatch) == "position_writes"


def test_headroom_is_reported_per_resource():
    assert headroom({"cpu": (400, 1_000), "memory": (900, 1_000)}) == {
        "cpu": 0.6,
        "memory": 0.1,
    }


def test_being_over_capacity_is_reported_rather_than_clamped():
    """A negative headroom is information. Clamping it at zero hides how far past
    the limit you already are."""
    assert headroom({"cpu": (1_200, 1_000)})["cpu"] < 0


def test_an_empty_or_impossible_resource_map_is_an_error():
    with pytest.raises(ValueError):
        binding_constraint({})
    with pytest.raises(ValueError):
        binding_constraint({"cpu": (10, 0)})


# -- when, not only whether ---------------------------------------------------


def test_headroom_in_months_at_a_growth_rate():
    """Half capacity and 10% monthly growth: about seven months. **When** you need
    the specialised mechanism is as much a design output as whether — seven months
    of headroom and a six-month build is a very different decision from eighteen."""
    assert headroom_months(used=500, capacity=1_000, monthly_growth=0.10) == pytest.approx(
        7.3, abs=0.1
    )


def test_faster_growth_shortens_it_sharply():
    slow = headroom_months(500, 1_000, 0.05)
    fast = headroom_months(500, 1_000, 0.30)
    assert fast < slow / 3


def test_no_growth_means_no_deadline():
    assert headroom_months(500, 1_000, 0) == float("inf")


def test_already_over_capacity_has_no_headroom():
    assert headroom_months(1_200, 1_000, 0.1) == 0.0


def test_nonsense_headroom_inputs_are_an_error():
    with pytest.raises(ValueError):
        headroom_months(0, 1_000, 0.1)


# -- the break-even -----------------------------------------------------------


def test_the_break_even_volume():
    """A specialised mechanism costing 200,000 to build and saving 0.4 per unit
    pays for itself at 500,000 units. Below that, the general answer is cheaper —
    and it is also simpler, easier to hire for, and easier to explain to the next
    engineer."""
    assert break_even_volume(
        general_unit_cost=1.0, specialised_unit_cost=0.6, specialised_fixed_cost=200_000
    ) == pytest.approx(500_000)


def test_below_the_break_even_the_general_answer_wins():
    args = dict(
        general_unit_cost=1.0, specialised_unit_cost=0.6, specialised_fixed_cost=200_000
    )
    assert is_worth_it(volume=100_000, **args) is False
    assert is_worth_it(volume=2_000_000, **args) is True


def test_a_specialisation_that_is_not_cheaper_per_unit_never_pays():
    """The most useful answer this function gives. No volume justifies it, and the
    decision is over before the design discussion starts.

    It happens more often than people expect: a mechanism that is faster but not
    cheaper, adopted for its performance, at a scale where performance was not the
    constraint.
    """
    assert break_even_volume(1.0, 1.4, 200_000) == float("inf")
    assert is_worth_it(10**12, 1.0, 1.4, 200_000) is False


def test_both_sides_are_compared_on_one_scale():
    """Rather than argued about. The general answer has no fixed cost and a higher
    unit cost; the specialised one is the reverse, and at some volume they cross."""
    volume = 500_000
    general = total_cost(volume, unit_cost=1.0)
    specialised = total_cost(volume, unit_cost=0.6, fixed_cost=200_000)
    assert general == pytest.approx(specialised)


def test_the_fixed_cost_is_the_thing_people_forget():
    """It is not only the build. It is the operating, the hiring, and explaining it
    to the next engineer — and none of those appear in a benchmark."""
    cheap_to_build = break_even_volume(1.0, 0.6, 20_000)
    expensive_to_build = break_even_volume(1.0, 0.6, 2_000_000)
    assert expensive_to_build == pytest.approx(100 * cheap_to_build)
