"""Turning the words in an envelope into numbers a computer can check.

Every function here is one you will do by hand in an interview. The point of writing
them down is that you cannot fudge a definition you had to implement.

Replace each `raise NotImplementedError` with your own code.
"""

WINDOW_MINUTES = {
    "day": 1_440,
    "week": 10_080,
    "month": 43_200,   # 30 days
    "year": 525_600,   # 365 days
}


def downtime_minutes(target_percent: float, window: str = "month") -> float:
    """Minutes of downtime an availability target permits over `window`.

    >>> downtime_minutes(99.9)
    43.2
    >>> downtime_minutes(99, "year")
    5256.0

    Raises ValueError for an unknown window, or a target outside (0, 100].
    """
    raise NotImplementedError


def error_budget_remaining(target_percent: float, window: str, minutes_down: float) -> float:
    """Budget minus what has been spent, to one decimal place.

    Negative means the budget is blown, which is a normal thing to report and the
    reason error budgets are useful at all.
    """
    raise NotImplementedError


def parse_latency(text: str) -> tuple[float, float]:
    """A stated latency requirement into (percentile, milliseconds).

    >>> parse_latency("p99 < 200ms")
    (99.0, 200.0)
    >>> parse_latency("p99.9 < 1s")
    (99.9, 1000.0)

    Raises ValueError when there is no percentile or no number-with-unit.
    """
    raise NotImplementedError


def is_measurable(requirement: str) -> bool:
    """Whether a stated requirement contains a quantity — see the day's README for
    the exact rule. A heuristic, deliberately, and one of the tests says so."""
    raise NotImplementedError


def page_slow_probability(calls: int, tail_probability: float) -> float:
    """The chance that at least one of `calls` independent requests is slow,
    to four decimal places."""
    raise NotImplementedError
