"""Buckets, aggregates, and the arithmetic that decides the retention policy.

Replace each `raise NotImplementedError` with your own code.
"""

from dataclasses import dataclass

# (resolution_seconds, retention_days), coarsest last
BRIEF_TIERS = [
    (1, 1),          # raw, 24 hours
    (60, 30),        # one minute, 30 days
    (3_600, 730),    # one hour, two years
]


def bucket(timestamp_ms: int, resolution_s: int) -> int:
    """The start of the bucket this timestamp falls in, in milliseconds.

    Raises ValueError for a resolution of zero or less.
    """
    raise NotImplementedError


@dataclass
class Agg:
    """What a bucket keeps.

    Four numbers rather than one, and the reason is `merge`: the mean of means is
    only the true mean when every bucket has the same count, and buckets never do.
    Keep count and total, and merging is exact.
    """

    count: int
    total: float
    minimum: float
    maximum: float

    @property
    def mean(self) -> float:
        """Raises ValueError for an empty aggregate — there is no mean of nothing,
        and returning 0.0 would quietly pull every average that touches it down."""
        raise NotImplementedError

    def merge(self, other: "Agg") -> "Agg":
        """Combine two aggregates exactly. Returns a new one; neither input changes."""
        raise NotImplementedError


def rollup(points, resolution_s: int) -> dict[int, Agg]:
    """Group `(timestamp_ms, value)` points into buckets."""
    raise NotImplementedError


def downsample(buckets: dict[int, Agg], to_resolution_s: int) -> dict[int, Agg]:
    """Regroup finer buckets into coarser ones, merging as you go.

    This is the operation that runs every night against a month of data, so it has
    to be exactly right and it has to be associative — downsampling twice must give
    the same answer as downsampling once.
    """
    raise NotImplementedError


def mean_of_means(aggs) -> float:
    """The average of each bucket's average.

    This is the wrong way to combine buckets and it is here so a test can show you
    how wrong. Do not use it for anything.
    """
    raise NotImplementedError


def retention_bytes(
    series: int,
    tiers=BRIEF_TIERS,
    bytes_per_bucket: int = 32,
    replicas: int = 3,
) -> int:
    """Total stored bytes for every series across every tier, including replicas.

    One bucket per series per resolution period, for the retention of that tier.
    """
    raise NotImplementedError


def tier_for(age_s: float, tiers=BRIEF_TIERS) -> int | None:
    """The resolution that still holds data of this age — the finest tier whose
    retention covers it. None when the data has aged out of every tier.
    """
    raise NotImplementedError
