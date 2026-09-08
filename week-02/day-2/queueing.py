"""Utilisation, waiting, and what variability does to both.

Replace each `raise NotImplementedError` with your own code.
"""


def utilisation(arrival_rate: float, service_rate: float) -> float:
    """Fraction of capacity in use, to three decimal places.

    Raises ValueError for a service rate of zero or less.
    """
    raise NotImplementedError


def wait_time(service_time_s: float, rho: float) -> float:
    """M/M/1 time spent waiting in the queue: rho/(1-rho) x service time.

    Raises ValueError for rho outside [0, 1). At rho = 1 the wait is not large,
    it is unbounded, and returning a number would be a lie.
    """
    raise NotImplementedError


def response_time(service_time_s: float, rho: float) -> float:
    """Waiting plus being served — what the client experiences."""
    raise NotImplementedError


def max_arrival_rate(service_rate: float, target_rho: float) -> float:
    """How much load fits under a utilisation target."""
    raise NotImplementedError


def servers_needed(arrival_rate: float, service_rate: float, target_rho: float) -> int:
    """How many servers keep utilisation at or under the target. Rounded up."""
    raise NotImplementedError


def utilisation_after_losing_one(instances: int, rho: float) -> float:
    """Utilisation on the survivors when one instance of `instances` dies,
    to three decimal places. May exceed 1, and when it does you have found
    something worth putting in your design document.

    Raises ValueError for fewer than two instances.
    """
    raise NotImplementedError


def variability_penalty(ca: float, cs: float) -> float:
    """The Kingman variability multiplier, (ca^2 + cs^2) / 2, to three decimals.

    ca and cs are coefficients of variation — standard deviation over mean — for
    arrivals and for service times. Both 1 is the textbook case, and gives 1.
    """
    raise NotImplementedError


def kingman_wait(service_time_s: float, rho: float, ca: float, cs: float) -> float:
    """Approximate wait for a general queue: the M/M/1 wait, times the
    variability penalty."""
    raise NotImplementedError


def bimodal_cv(fast_s: float, slow_s: float, slow_fraction: float) -> float:
    """Coefficient of variation of a two-valued service time, to three decimals.

    This is the shape a cache creates: mostly fast, occasionally slow. Run it on
    a 1 ms hit, a 40 ms miss and a 5% miss rate before you look at the test.
    """
    raise NotImplementedError
