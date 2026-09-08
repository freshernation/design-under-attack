"""Day 2 — fan-out.

`test_the_hybrid_beats_both` is the day, and the reason it wins is worth more than
the number: the distribution has two populations in it, so the design has two
answers.
"""

import pytest

from fanout import (
    SKEWED,
    celebrity_write_cost_seconds,
    covered_by_write_fanout,
    hybrid_work,
    read_fanout_work,
    threshold_for,
    total_accounts,
    write_fanout_work,
)

POSTS_EACH = 0.5           # posts per account per day
READS = 500_000_000        # timeline reads per day
FOLLOWING = 200            # accounts a reader follows
BIG_FOLLOWED = 3           # of which are above the threshold


def test_the_distribution_is_a_million_accounts():
    assert total_accounts(SKEWED) == 1_000_000


# -- the two pure strategies --------------------------------------------------


def test_write_fanout_makes_reads_trivial_and_writes_enormous():
    """1.3 billion timeline writes a day, from half a post per account."""
    assert write_fanout_work(SKEWED, POSTS_EACH) == pytest.approx(1.34e9, rel=0.02)


def test_read_fanout_makes_writes_trivial_and_reads_enormous():
    """A hundred billion source fetches a day. Seventy-five times the write-fanout
    number, in the other place."""
    assert read_fanout_work(READS, FOLLOWING) == pytest.approx(1e11)
    assert read_fanout_work(READS, FOLLOWING) > 70 * write_fanout_work(SKEWED, POSTS_EACH)


def test_neither_number_is_small():
    """Both strategies are expensive. The choice is about *where*, and it follows
    from the read/write ratio you have been computing since week 1."""
    assert write_fanout_work(SKEWED, POSTS_EACH) > 1e9
    assert read_fanout_work(READS, FOLLOWING) > 1e9


# -- why neither survives a real distribution ---------------------------------


def test_one_post_can_take_an_hour():
    """Two hundred million followers at fifty thousand writes a second. Sixty-seven
    minutes for one post — during which every ordinary user's post is queued behind
    it, if you built one queue.

    This is not a margin to tune. It is why no large system fans out everything.
    """
    seconds = celebrity_write_cost_seconds(200_000_000, 50_000)
    assert seconds == pytest.approx(4_000)
    assert seconds / 60 > 60


def test_an_ordinary_account_costs_nothing():
    """The same mechanism, on the other population: fifty followers is a
    millisecond. One strategy, two completely different outcomes."""
    assert celebrity_write_cost_seconds(50, 50_000) < 0.01


def test_a_fanout_that_writes_nothing_is_an_error():
    with pytest.raises(ValueError):
        celebrity_write_cost_seconds(1_000, 0)


# -- the hybrid ---------------------------------------------------------------


def test_the_threshold_covers_almost_every_account():
    """The exception is ten accounts in a million. Tiny in count, enormous in cost
    — which is exactly the shape that makes a second strategy worth having."""
    assert covered_by_write_fanout(SKEWED, threshold=100_000) == pytest.approx(0.999)


def test_the_hybrid_beats_both():
    """Not a compromise between two strategies. Better than either, on both axes.

    Write fanout without a threshold is dominated by ten accounts. Read fanout
    merges all two hundred sources for every reader. The hybrid removes the ten
    from the write side and merges only three on the read side, and both numbers
    fall by more than an order of magnitude.
    """
    hybrid = hybrid_work(SKEWED, POSTS_EACH, READS, BIG_FOLLOWED, threshold=100_000)

    assert hybrid["timeline_writes_per_day"] < write_fanout_work(SKEWED, POSTS_EACH) / 10
    assert hybrid["read_merges_per_day"] < read_fanout_work(READS, FOLLOWING) / 50


def test_a_higher_threshold_moves_work_to_the_write_side():
    low = hybrid_work(SKEWED, POSTS_EACH, READS, BIG_FOLLOWED, threshold=1_000)
    high = hybrid_work(SKEWED, POSTS_EACH, READS, BIG_FOLLOWED, threshold=10_000_000)
    assert high["timeline_writes_per_day"] > low["timeline_writes_per_day"]


def test_an_infinite_threshold_is_just_write_fanout():
    hybrid = hybrid_work(SKEWED, POSTS_EACH, READS, 0, threshold=10**12)
    assert hybrid["timeline_writes_per_day"] == pytest.approx(
        write_fanout_work(SKEWED, POSTS_EACH)
    )


def test_a_zero_threshold_is_just_read_fanout():
    hybrid = hybrid_work(SKEWED, POSTS_EACH, READS, FOLLOWING, threshold=0)
    assert hybrid["timeline_writes_per_day"] == 0
    assert hybrid["read_merges_per_day"] == pytest.approx(read_fanout_work(READS, FOLLOWING))


# -- choosing the threshold ---------------------------------------------------


def test_the_threshold_comes_from_a_budget():
    """Fifty thousand writes a second and a ten-second budget for a post to reach
    everybody: half a million followers. A number derived from a constraint rather
    than picked because it is round."""
    assert threshold_for(50_000, 10) == 500_000


def test_a_tighter_budget_lowers_the_threshold():
    assert threshold_for(50_000, 2) < threshold_for(50_000, 10)


@pytest.mark.parametrize("rate, seconds", [(0, 10), (50_000, 0)])
def test_a_budget_needs_both_halves(rate, seconds):
    with pytest.raises(ValueError):
        threshold_for(rate, seconds)


def test_an_empty_distribution_is_an_error():
    with pytest.raises(ValueError):
        covered_by_write_fanout([], threshold=100)
