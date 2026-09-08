"""Stopping a failing dependency from consuming you, and one tenant from consuming
everyone.

Replace each `raise NotImplementedError` with your own code.
"""

import math
from collections import deque

from simlib import Simulation


class CircuitBreaker:
    """Closed, open, half-open.

        breaker = CircuitBreaker(sim, failure_threshold=0.5, minimum_requests=20)
        if breaker.allow():
            ok = call_the_dependency()
            breaker.record(ok)

    **Half-open is the state that does the work.** Without it, the breaker closes
    after its cool-off, every waiting client resumes at once, and the recovering
    service is knocked straight back down — a slower way to have the same outage
    twice.

    `minimum_requests` exists so a low-traffic path does not trip on two failures
    out of three.
    """

    def __init__(
        self,
        sim: Simulation,
        failure_threshold: float = 0.5,
        minimum_requests: int = 20,
        cooloff_ms: int = 10_000,
        half_open: bool = True,
    ) -> None:
        """`half_open=False` exists so a test can show what its absence costs.

        Raises ValueError for a threshold outside (0, 1] or a non-positive cool-off.
        """
        raise NotImplementedError

    @property
    def state(self) -> str:
        """`"closed"`, `"open"` or `"half_open"`."""
        raise NotImplementedError

    def allow(self) -> bool:
        """Whether to attempt the call.

        Open means fail instantly: no thread waits, no timeout is consumed, and the
        dependency gets a rest. In half-open, allow exactly **one** probe at a time.
        """
        raise NotImplementedError

    def record(self, success: bool) -> None:
        """Report the outcome. A success in half-open closes the breaker; a failure
        opens it again and restarts the cool-off."""
        raise NotImplementedError


class Bulkhead:
    """A separate limit per dependency, so one cannot exhaust the others.

        pools = Bulkhead({"search": 20, "profile": 40})
        if pools.acquire("search"):
            ...
            pools.release("search")

    The cost is week 2's pooling result: partitioned pools cannot share capacity,
    so you are buying isolation with efficiency, deliberately.
    """

    def __init__(self, limits: dict[str, int]) -> None:
        raise NotImplementedError

    def acquire(self, name: str) -> bool:
        """False when that dependency's pool is full. Raises KeyError for an
        unknown dependency — a call with no bulkhead is one you forgot."""
        raise NotImplementedError

    def release(self, name: str) -> None:
        raise NotImplementedError

    def in_use(self, name: str) -> int:
        raise NotImplementedError

    def available(self, name: str) -> int:
        raise NotImplementedError


def shuffle_shard(customer: str, servers: list[str], shard_size: int) -> list[str]:
    """The subset of servers this customer uses.

    Deterministic: seed a generator from the customer name and sample. The same
    customer must always get the same shard, or the isolation means nothing.

    Raises ValueError when `shard_size` exceeds the number of servers.
    """
    raise NotImplementedError


def overlap_probability(servers: int, shard_size: int) -> float:
    """The chance two customers get **exactly** the same shard: `1 / C(n, k)`.

    Run it for 8 servers with shards of 1 and 2, then for 100 with shards of 5.
    The last number is why this idea is worth knowing: no extra hardware, no new
    component, just a different assignment function.
    """
    raise NotImplementedError
