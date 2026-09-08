"""Retrying without making the outage worse.

Replace each `raise NotImplementedError` with your own code.
"""

from collections import deque

from simlib import Simulation

STRATEGIES = ("exponential", "full_jitter", "decorrelated")


def backoff_delays(
    attempts: int, base_ms: int, strategy: str, rng, cap_ms: int | None = None
) -> list[int]:
    """The wait before each attempt.

    * `"exponential"` — `base × 2^n`. Deterministic, and therefore a synchroniser
    * `"full_jitter"` — `random(0, base × 2^n)`. The usual recommendation
    * `"decorrelated"` — `random(base, previous × 3)`, starting from `base`.
      Spreads well and grows faster

    Cap each delay at `cap_ms` when given. Raises ValueError for an unknown
    strategy or a non-positive base.
    """
    raise NotImplementedError


def arrival_spread(delays: list[int]) -> int:
    """How wide a set of retry arrivals is: the largest minus the smallest.

    Zero means every client comes back in the same instant, which is what plain
    exponential backoff produces and what jitter exists to prevent.
    """
    raise NotImplementedError


def storm_peak(
    clients: int, base_ms: int, strategy: str, rng, attempt: int = 1, bucket_ms: int = 50
) -> int:
    """The tallest wave when `clients` all fail together and all retry.

    Compute each client's delay for `attempt`, drop them into buckets of
    `bucket_ms`, and return the fullest bucket. That number is the load the
    recovering service actually receives.
    """
    raise NotImplementedError


class RetryBudget:
    """Retries capped as a fraction of total requests, across the whole client.

        budget = RetryBudget(sim, window_ms=60_000, ratio=0.1)
        budget.record_request()
        if budget.allow():
            budget.record_retry()

    The mechanism that bounds the damage. In healthy conditions failures are rare,
    the budget is nowhere near its limit, and every request gets its retries. During
    an outage the budget is exhausted immediately and the client stops adding load —
    which is exactly when you wanted it to stop.
    """

    def __init__(self, sim: Simulation, window_ms: int, ratio: float) -> None:
        """Raises ValueError for a non-positive window or a ratio outside (0, 1]."""
        raise NotImplementedError

    def record_request(self) -> None:
        raise NotImplementedError

    def record_retry(self) -> None:
        raise NotImplementedError

    def allow(self) -> bool:
        """Whether another retry is within budget, counting only the window."""
        raise NotImplementedError


def total_attempts(layers: int, retries_each: int) -> int:
    """Requests reaching the bottom when every layer retries.

    Three layers of three retries is 27 requests for one user action, and each
    layer believes it is being modest. **Retry at one layer**, usually the one
    closest to the user, because it knows whether anybody is still waiting.
    """
    raise NotImplementedError
