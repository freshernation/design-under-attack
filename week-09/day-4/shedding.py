"""Refusing work on purpose, in priority order, and degrading instead of failing.

Replace each `raise NotImplementedError` with your own code.
"""

import math

# Lowest first. Shedding starts at the bottom.
PRIORITIES = ("sheddable", "best_effort", "important", "critical")

# Utilisation above which each level is refused. Stipulated defaults — the numbers
# are a product decision, and yours should come from your own envelope.
DEFAULT_THRESHOLDS = {
    "sheddable": 0.70,
    "best_effort": 0.85,
    "important": 0.95,
    "critical": 1.20,
}


def goodput(offered_qps: float, capacity_qps: float, overload_penalty: float = 2.0) -> float:
    """Useful work — responses that reached a client still waiting — to two decimals.

    **A stipulated model, not a measurement.** Below capacity, goodput tracks
    offered load. Above it, requests queue for longer than their client will wait,
    so work is completed and thrown away:

        goodput = capacity / overload ** overload_penalty

    The shape is the point: past capacity an unprotected service does *less* useful
    work as load rises. The exponent is a knob for how sharply, and the tests assert
    the shape rather than the values.
    """
    raise NotImplementedError


def goodput_with_shedding(offered_qps: float, capacity_qps: float) -> float:
    """The same load, with excess refused quickly instead of queued.

    Everything accepted is served, so goodput holds flat at capacity rather than
    collapsing. This is the whole argument for shedding, in one function.
    """
    raise NotImplementedError


class PriorityShedder:
    """Refuse from the bottom of the priority list upwards.

        shedder = PriorityShedder()
        shedder.allow("best_effort", utilisation=0.9)   -> False
        shedder.allow("critical", utilisation=0.9)      -> True

    The priority must be **on the request**, set by the client or the edge. By the
    time it reaches the busy service you do not want to be computing it.
    """

    def __init__(self, thresholds: dict[str, float] | None = None) -> None:
        """Raises ValueError for an unknown priority in the thresholds."""
        raise NotImplementedError

    def allow(self, priority: str, utilisation: float) -> bool:
        """Raises ValueError for an unknown priority — an unlabelled request is one
        nobody decided about, and defaulting it silently is how critical traffic
        gets shed."""
        raise NotImplementedError

    def shed_levels(self, utilisation: float) -> list[str]:
        """Which levels are being refused right now, lowest first."""
        raise NotImplementedError


def admit(oldest_queue_age_ms: float, client_timeout_ms: float) -> bool:
    """Whether to accept new work, based on how stale the queue already is.

    If the oldest queued request is older than the client's timeout, everything in
    the queue is already dead and so is anything you add to it.

    A self-tuning rule with no magic number: it refuses exactly when the queue has
    become useless, whatever the current capacity happens to be.
    """
    raise NotImplementedError


def healthy_fleet_fraction(hosts: int, failing: int, max_removable: float) -> float:
    """The fraction of the fleet still taking traffic, to four decimals.

    A load balancer refuses to remove more than `max_removable` of the fleet,
    however many hosts report unhealthy. Without that guard, one shared dependency
    failing marks every host unhealthy at once and you have no service at all
    rather than a degraded one.
    """
    raise NotImplementedError
