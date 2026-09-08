"""Counting clicks exactly once, on a stream that delivers them more than once.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation


def bucket_of(timestamp_ms: int, bucket_s: int = 60) -> int:
    """The start of the bucket a timestamp belongs to, in milliseconds.

    The same function as week 3's rollup, and for the same reason: a count is
    only meaningful against a window.
    """
    raise NotImplementedError


def watermark(now_ms: int, late_window_ms: int) -> int:
    """The point before which no more events are expected.

    Everything older than this is considered complete, so its buckets can be
    sealed and their deduplication sets discarded. **This number is the answer to
    "when is a day's total final?"** — not a time of day.
    """
    raise NotImplementedError


def dedup_window_bytes(
    events_per_second: float, window_s: float, bytes_per_id: int = 16, partitions: int = 1
) -> int:
    """Memory for an exact deduplication window, per partition.

    Run it twice: once with the replay depth as the window, and once with the
    late-arrival window. The first answer is why this milestone is interesting.
    """
    raise NotImplementedError


class BucketAggregator:
    """Per-campaign, per-minute counts, deduplicated inside a bounded window.

        agg = BucketAggregator(sim, late_window_ms=600_000)
        agg.add("evt-1", "campaign-7", timestamp_ms)
    """

    def __init__(
        self, sim: Simulation, late_window_ms: int = 600_000, bucket_s: int = 60
    ) -> None:
        """Track counts per `(campaign, bucket)`, the ids seen per bucket, and
        `stats` counting duplicates, too_late and closed.

        Raises ValueError for a non-positive late window or bucket size.
        """
        raise NotImplementedError

    def add(self, event_id: str, campaign: str, timestamp_ms: int) -> bool:
        """Count an event. Returns whether it was counted.

        Three rules:

        * **A late event goes in the bucket it belongs to**, not the current one.
          An event timestamped 09:03 arriving at 09:11 increments 09:03 — otherwise
          your minute counts record when data arrived, which nobody is buying.
        * A duplicate id **within a bucket that is still open** is ignored.
        * An event for a **closed** bucket is too late to count. It is dropped, and
          the drop is counted — a silent drop here is money.
        """
        raise NotImplementedError

    def count(self, campaign: str, bucket: int) -> int:
        raise NotImplementedError

    def close_before(self, watermark_ms: int) -> int:
        """Seal every bucket that ends before the watermark, **and free its
        deduplication set**. Returns how many buckets closed.

        This is what bounds the memory to the late-arrival window rather than the
        replay window, and it is the difference between 7 GB and 690 GB.
        """
        raise NotImplementedError

    def is_closed(self, bucket: int) -> bool:
        raise NotImplementedError

    def recompute(self, campaign: str, bucket: int, event_ids: list[str]) -> int:
        """Replay: **set** the bucket's count from the given events, rather than
        adding to it. Returns the new count.

        This is the answer the brief is built around. A replay that adds is not
        idempotent and needs a deduplication window as deep as the replay. A replay
        that recomputes a bucket from its events is idempotent by construction, at
        any depth, with no extra memory at all — because assignment is idempotent
        and addition is not, which you proved on Wednesday.

        Deduplicate within `event_ids` as you go: the replayed stream has duplicates
        in it too.
        """
        raise NotImplementedError
