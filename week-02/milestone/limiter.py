"""A multi-tenant rate limiter: fairness and protection, which disagree.

Reuses `TokenBucket` from day 4. Replace each `raise NotImplementedError`.
"""

from dataclasses import dataclass

from simlib import Simulation
from token_bucket import TokenBucket

# tier -> (sustained rate per second, burst capacity)
TIERS = {
    "free": (1, 5),
    "pro": (50, 100),
    "enterprise": (500, 1_000),
}


@dataclass
class Decision:
    allowed: bool
    reason: str            # "ok" | "tenant" | "global"
    retry_after_ms: int


class MultiTenantLimiter:
    """Per-tenant quotas, plus one global limit that protects the platform.

    Buckets are created on first sight of a tenant, because 50,000 buckets
    allocated up front for the 500 tenants active this minute is not a good trade.
    """

    def __init__(
        self,
        sim: Simulation,
        tiers: dict | None = None,
        global_rate_per_second: float | None = None,
        global_burst: float | None = None,
        default_tier: str = "free",
    ) -> None:
        raise NotImplementedError

    def check(self, tenant: str, tier: str | None = None, n: float = 1) -> Decision:
        """Decide one request. See the milestone README for the exact order —
        in particular, a request refused by the global limit must not have spent
        the tenant's tokens.
        """
        raise NotImplementedError


def local_limit_worst_case(servers: int, per_server_limit: float) -> float:
    """What N independent limiters permit in total, when traffic finds them all."""
    raise NotImplementedError


def divided_limit_floor(servers: int, global_limit: float) -> float:
    """What one tenant actually gets when the global limit is divided evenly and
    that tenant's connections all land on one server."""
    raise NotImplementedError
