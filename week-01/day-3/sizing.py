"""Back-of-the-envelope arithmetic, with the definitions pinned down.

You will do all of this by hand in an interview. Writing it once means you have
committed to what each term means — which multiplier, which rounding, which default.

Replace each `raise NotImplementedError` with your own code.
"""

SECONDS_PER_DAY = 86_400
FIBRE_KM_PER_SECOND = 200_000


def qps(events_per_day: float) -> float:
    """Average events per second, to one decimal place."""
    raise NotImplementedError


def peak_qps(average_qps: float, factor: float = 5) -> float:
    """The number you actually design for, to one decimal place."""
    raise NotImplementedError


def daily_bytes(events_per_day: float, bytes_per_event: float) -> int:
    """Bytes written per day, as a whole number of bytes."""
    raise NotImplementedError


def storage_bytes(
    events_per_day: float,
    bytes_per_event: float,
    retention_days: float,
    replicas: int = 3,
) -> int:
    """Total stored bytes, including replication. Three replicas by default."""
    raise NotImplementedError


def working_set_bytes(hot_keys: float, bytes_per_key: float) -> int:
    """How much of the data is actually being touched. Usually the number that
    settles the caching argument before it starts."""
    raise NotImplementedError


def human_bytes(n: float) -> str:
    """Decimal units, one decimal place, plain integer below 1,000.

    >>> human_bytes(3_600_000_000_000)
    '3.6 TB'
    >>> human_bytes(999)
    '999 B'
    """
    raise NotImplementedError


def budget_remaining(target_ms: float, hops: list[tuple[str, float]]) -> float:
    """What is left of a latency budget after spending it on `hops`, to one
    decimal place. Negative means the design does not fit its target."""
    raise NotImplementedError


def first_hop_over_budget(target_ms: float, hops: list[tuple[str, float]]) -> str | None:
    """The name of the hop at which the running total passes the target, or None
    if the budget survives. Knowing *which* hop broke it is the point."""
    raise NotImplementedError


def is_geographically_possible(target_ms: float, km: float) -> bool:
    """Whether a latency target survives the speed of light over `km`, round trip,
    at 200,000 km/s. Nothing you build changes this answer."""
    raise NotImplementedError
