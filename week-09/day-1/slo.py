"""Turning a reliability target into a budget, and a budget into an alert.

Replace each `raise NotImplementedError` with your own code.
"""

WINDOW_MINUTES_PER_DAY = 1_440


def error_budget_minutes(target_percent: float, window_days: int = 28) -> float:
    """Minutes of failure the objective permits, to one decimal.

    Permitted, not tolerated. It is a resource, and a team that never spends it has
    set its target too high.

    Raises ValueError for a target outside (0, 100] or a window below 1 day.
    """
    raise NotImplementedError


def budget_remaining(target_percent: float, window_days: int, minutes_down: float) -> float:
    """What is left, to one decimal. Negative is a normal thing to report."""
    raise NotImplementedError


def burn_rate(observed_error_rate: float, target_percent: float) -> float:
    """How fast the budget is being spent, relative to exactly on budget.

    `observed / allowed`. A burn rate of 1 finishes the window precisely on budget;
    10 empties a 28-day budget in under three days.

    Raises ValueError for a target of 100% — a budget of zero cannot be burned at
    a rate, and any failure at all is infinite.
    """
    raise NotImplementedError


def time_to_exhaustion_hours(rate: float, window_days: int = 28) -> float:
    """How long the budget lasts at this burn rate, to one decimal.

    A rate of zero returns `float("inf")`, which is the honest answer.
    """
    raise NotImplementedError


def dependency_ceiling(availabilities: list[float]) -> float:
    """The best availability achievable on top of these dependencies, to four
    decimals — their product, as percentages in and a percentage out.

    Four dependencies at 99.95% gives 99.8%. **You cannot promise 99.9% on top of
    that**, whatever you do to your own code, and this is the multiplication nobody
    does before agreeing a target.
    """
    raise NotImplementedError


def is_reachable(target_percent: float, availabilities: list[float]) -> bool:
    """Whether an objective is achievable given what it depends on.

    When this is False the answer is not better engineering. It is fewer
    dependencies on the critical path, or retries that mask them, or a different
    number in the contract.
    """
    raise NotImplementedError


def should_page(rate: float, window_hours: float) -> bool:
    """The SRE workbook's multi-window scheme, simplified to two rules:

    * a **fast** window — an hour or less — pages at a burn rate of 14.4 or above,
      which is about 2% of a 28-day budget in an hour
    * a **slow** window — six hours or less — pages at a burn rate of 6 or above,
      which catches a leak too gentle to trip the fast rule

    One window cannot do both: it is either too twitchy or too slow.
    """
    raise NotImplementedError
