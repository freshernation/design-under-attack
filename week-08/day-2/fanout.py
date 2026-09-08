"""When to do the work: at write time, at read time, or both.

Replace each `raise NotImplementedError` with your own code.
"""

import math

# (followers, number of accounts with roughly that many) — a heavily skewed
# distribution, because real ones are. Most accounts have very few followers and
# a handful have enormous numbers, which is what breaks a single strategy.
SKEWED = [
    (50, 900_000),
    (500, 90_000),
    (5_000, 9_000),
    (100_000, 900),
    (5_000_000, 90),
    (200_000_000, 10),
]


def total_accounts(distribution) -> int:
    raise NotImplementedError


def write_fanout_work(distribution, posts_per_account_per_day: float) -> float:
    """Timeline writes per day if every post is fanned out on write.

    Sum over the distribution of `followers x accounts x posts`.
    """
    raise NotImplementedError


def read_fanout_work(reads_per_day: float, avg_following: float) -> float:
    """Source fetches per day if every timeline is merged at read time."""
    raise NotImplementedError


def celebrity_write_cost_seconds(followers: int, writes_per_second: float) -> float:
    """How long one post takes to fan out, to one decimal.

    Run it for 200 million followers. The answer is why no large system fans out
    everything on write, and it is not a subtle margin.
    """
    raise NotImplementedError


def hybrid_work(
    distribution,
    posts_per_account_per_day: float,
    reads_per_day: float,
    big_accounts_followed_each: float,
    threshold: int,
) -> dict:
    """Write-fanout below the threshold, read-merge above it.

    Returns `{"timeline_writes_per_day": ..., "read_merges_per_day": ...}`.

    Accounts at or above `threshold` are not fanned out at all; instead every read
    merges in the `big_accounts_followed_each` large accounts that reader follows.
    """
    raise NotImplementedError


def covered_by_write_fanout(distribution, threshold: int) -> float:
    """The fraction of *accounts* below the threshold, to four decimals.

    Usually above 0.999, which is the argument for the hybrid: the exception is
    tiny in count and enormous in cost.
    """
    raise NotImplementedError


def threshold_for(writes_per_second: float, max_seconds: float) -> int:
    """The largest follower count you can fan out inside a latency budget.

    A threshold picked from a constraint rather than from a round number, which is
    the difference between a design decision and a guess.
    """
    raise NotImplementedError
