"""Day 4 — scoring the mocks."""

import pytest

from scoring import (
    PASSES,
    on_schedule,
    progress,
    readiness,
    score_mock,
    verdict,
    weakest_pass,
)


def mock(**overrides) -> dict:
    scores = {p: 4 for p in PASSES}
    scores.update(overrides)
    return scores


# -- one mock -----------------------------------------------------------------


def test_a_solid_mock_is_a_hire():
    assert verdict(mock()) == "hire"


def test_one_collapsed_pass_sinks_it():
    """How real interviews work. A design with no failure analysis is not rescued
    by excellent sizing, and the rubric should not pretend otherwise."""
    assert verdict(mock(**{"break": 2})) == "no hire"


def test_competent_everywhere_is_borderline():
    assert verdict({p: 3 for p in PASSES}) == "borderline"


def test_the_summary_names_the_weakest_pass():
    result = score_mock(mock(size=2, decide=3))
    assert result["weakest"] == "size"
    assert result["verdict"] == "no hire"


def test_ties_break_towards_the_earlier_pass():
    """An early collapse usually caused the later one — a design with no sizing
    tends to produce decisions that cannot be defended, and pointing at the
    decisions would be treating the symptom."""
    assert weakest_pass(mock(size=2, evolve=2)) == "size"


def test_an_unscored_pass_is_an_error():
    """Not a zero. A pass with no score is one the interviewer never reached, and
    recording it as zero would hide the fact that time ran out."""
    incomplete = {p: 4 for p in PASSES if p != "evolve"}
    with pytest.raises(ValueError):
        score_mock(incomplete)


@pytest.mark.parametrize("score", [0, 6, -1])
def test_a_score_outside_the_scale_is_an_error(score):
    with pytest.raises(ValueError):
        verdict(mock(decide=score))


# -- the clock ----------------------------------------------------------------


def test_reaching_decisions_by_minute_twenty_is_on_track():
    assert on_schedule("decide", 18) is True


def test_reaching_failure_modes_at_minute_forty_is_not():
    """Which is the failure the whole day is about: break and evolve are where the
    hiring decision is made, and they are at the end, so they are what gets cut."""
    assert on_schedule("break", 40) is False


def test_an_unknown_pass_is_an_error():
    with pytest.raises(ValueError):
        on_schedule("hand-waving", 10)


# -- across ten mocks ---------------------------------------------------------


def test_improvement_shows_up_per_pass():
    early = [mock(**{"break": 2}) for _ in range(3)]
    later = [mock(**{"break": 4}) for _ in range(3)]
    trend = progress(early + later)

    assert trend["break"] == pytest.approx(2.0)
    assert trend["decide"] == pytest.approx(0.0)


def test_a_pass_that_is_not_moving_is_visible():
    """And that is where the next evening goes. Averaged over ten mocks, "I feel
    better at this" is not evidence and a per-pass trend is."""
    flat = [mock(size=2) for _ in range(6)]
    assert progress(flat)["size"] == 0.0


def test_a_trend_needs_something_to_be_a_trend_across():
    with pytest.raises(ValueError):
        progress([mock(), mock(), mock()])


def test_readiness_needs_three_in_a_row():
    """One good mock is a good day. Three consecutive is a skill, and the
    difference matters when the real one is on a Tuesday morning."""
    good, bad = mock(), mock(**{"break": 2})
    assert readiness([bad, good, good, good]) is True
    assert readiness([good, good, good, bad]) is False


def test_too_few_mocks_is_not_readiness():
    assert readiness([mock(), mock()]) is False


def test_the_week_twelve_comparison():
    """What Friday actually looks like: the first mock next to the tenth.

    The point is not that the numbers went up. It is that the improvement is
    evidence rather than a feeling, and a career-changer's nerve is helped far more
    by evidence than by encouragement.
    """
    first = mock(interrogate=2, size=2, decide=3, **{"break": 1, "evolve": 1})
    tenth = mock(interrogate=4, size=5, decide=4, **{"break": 4, "evolve": 3})

    assert verdict(first) == "no hire"
    assert verdict(tenth) == "hire"
    assert score_mock(tenth)["total"] > score_mock(first)["total"]
