"""Little's Law, in the three directions you actually use it.

Replace each `raise NotImplementedError` with your own code.
"""


def concurrency(throughput: float, latency_s: float) -> float:
    """How many requests are inside the system right now, to one decimal place.

    >>> concurrency(500, 0.2)
    100.0
    """
    raise NotImplementedError


def wait_seconds(queue_depth: float, drain_rate: float) -> float:
    """How far behind the back of a queue is, to one decimal place.

    Raises ValueError for a drain rate of zero or less — a queue that is not
    draining has no wait time, it has an unbounded one.
    """
    raise NotImplementedError


def max_throughput(concurrency_limit: float, latency_s: float) -> float:
    """The most a pool of this size can support at this latency, to one decimal."""
    raise NotImplementedError


def pool_size(throughput: float, latency_s: float, headroom: float = 1.5) -> int:
    """A pool sized for this load, with headroom, rounded up to a whole number.

    Headroom is not padding — it absorbs the variance the average hides.
    """
    raise NotImplementedError


def throughput_retained(old_latency_s: float, new_latency_s: float) -> float:
    """The fraction of throughput a fixed-size pool keeps when latency changes,
    to three decimal places.

    This is the arithmetic behind most incidents: nothing about your service
    changed, a dependency got slower, and your throughput fell.
    """
    raise NotImplementedError
