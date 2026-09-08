"""Two rate limiters, on a virtual clock.

Because time is simulated, a test can advance an hour instantly and get the same
answer every run. Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation


def advance(sim: Simulation, ms: int) -> None:
    """Move simulated time forward by `ms`, doing nothing else.

    One line: schedule a callback that does nothing, then run to that point.
    """
    raise NotImplementedError


class TokenBucket:
    """A sustained rate, plus a burst you can save up for.

    Starts full — a client that has never called you has its whole burst
    available, which is the behaviour people expect.

    Refill lazily, when someone asks. A background timer per key would be a
    background timer per key, and there are a lot of keys.
    """

    def __init__(self, sim: Simulation, rate_per_second: float, capacity: float) -> None:
        raise NotImplementedError

    @property
    def tokens(self) -> float:
        """Tokens available now, after refilling for elapsed time. Never above
        capacity — unused allowance expires rather than accumulating."""
        raise NotImplementedError

    def allow(self, n: float = 1) -> bool:
        """Spend `n` tokens if they are there. Returns whether the request passes.

        A refused request spends nothing.
        """
        raise NotImplementedError

    def retry_after_ms(self, n: float = 1) -> int:
        """How long until `n` tokens exist, rounded up. 0 if they exist now.

        This is the number that goes in the `Retry-After` header, and sending it
        is the difference between a limiter that reduces load and one that
        synchronises every client you have.
        """
        raise NotImplementedError


class FixedWindow:
    """Count per clock window, reset at the boundary.

    Cheap, obvious, and it lets through twice the intended rate at the boundary.
    You are implementing it so that a test can prove that to you.
    """

    def __init__(self, sim: Simulation, limit: int, window_ms: int) -> None:
        raise NotImplementedError

    def allow(self) -> bool:
        raise NotImplementedError
