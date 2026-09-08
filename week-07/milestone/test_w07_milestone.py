"""The milestone's mechanism.

The block under "the trap, and the way out" is the brief. Read those four tests in
order — they are the argument the design document has to make.
"""

import pytest

from aggregator import BucketAggregator, bucket_of, dedup_window_bytes, watermark
from simlib import Simulation

MINUTE = 60_000


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


@pytest.fixture
def agg(sim):
    return BucketAggregator(sim, late_window_ms=600_000, bucket_s=60)


# -- bucketing ----------------------------------------------------------------


@pytest.mark.parametrize(
    "timestamp, expected",
    [(0, 0), (59_999, 0), (60_000, 60_000), (185_000, 180_000)],
)
def test_bucket_of(timestamp, expected):
    assert bucket_of(timestamp, 60) == expected


def test_a_bucket_needs_a_width():
    with pytest.raises(ValueError):
        bucket_of(1_000, 0)


def test_the_watermark_trails_now_by_the_late_window():
    assert watermark(3_600_000, 600_000) == 3_000_000


# -- counting -----------------------------------------------------------------


def test_a_click_is_counted(agg):
    assert agg.add("evt-1", "campaign-7", 90_000) is True
    assert agg.count("campaign-7", 60_000) == 1


def test_a_duplicate_is_not(agg):
    """At-least-once delivery is the contract. This is what makes it survivable."""
    agg.add("evt-1", "campaign-7", 90_000)
    assert agg.add("evt-1", "campaign-7", 90_000) is False
    assert agg.count("campaign-7", 60_000) == 1
    assert agg.stats["duplicates"] == 1


def test_different_events_in_the_same_bucket_both_count(agg):
    agg.add("evt-1", "campaign-7", 90_000)
    agg.add("evt-2", "campaign-7", 95_000)
    assert agg.count("campaign-7", 60_000) == 2


def test_campaigns_are_counted_separately(agg):
    agg.add("evt-1", "campaign-7", 90_000)
    agg.add("evt-2", "campaign-9", 90_000)
    assert agg.count("campaign-7", 60_000) == 1
    assert agg.count("campaign-9", 60_000) == 1


# -- late arrivals ------------------------------------------------------------


def test_a_late_event_goes_in_the_bucket_it_belongs_to(sim, agg):
    """Not the bucket that is current when it arrives.

    An event timestamped 09:03 that turns up at 09:11 increments 09:03. Otherwise
    your minute counts are a record of when data arrived, which is not the thing
    anybody is buying.
    """
    advance(sim, 11 * MINUTE)
    agg.add("evt-late", "campaign-7", 3 * MINUTE + 20_000)

    assert agg.count("campaign-7", 3 * MINUTE) == 1
    assert agg.count("campaign-7", 11 * MINUTE) == 0


def test_an_event_for_a_closed_bucket_is_dropped_and_counted(sim, agg):
    """Dropped, and **counted as dropped**. A silent drop here is money."""
    agg.add("evt-1", "campaign-7", 60_000)
    advance(sim, 30 * MINUTE)
    agg.close_before(watermark(sim.now, agg.late_window_ms))

    assert agg.add("evt-2", "campaign-7", 60_000) is False
    assert agg.stats["too_late"] == 1
    assert agg.count("campaign-7", 60_000) == 1


def test_a_bucket_stays_open_inside_the_late_window(sim, agg):
    agg.add("evt-1", "campaign-7", 5 * MINUTE)
    advance(sim, 10 * MINUTE)
    agg.close_before(watermark(sim.now, agg.late_window_ms))
    assert agg.is_closed(5 * MINUTE) is False


# -- what closing is for ------------------------------------------------------


def test_closing_frees_the_deduplication_set(sim, agg):
    """The mechanism that bounds memory to the late-arrival window rather than the
    replay window."""
    for i in range(100):
        agg.add(f"evt-{i}", "campaign-7", 60_000)
    assert len(agg.seen[60_000]) == 100

    advance(sim, 30 * MINUTE)
    assert agg.close_before(watermark(sim.now, agg.late_window_ms)) >= 1
    assert 60_000 not in agg.seen


def test_closing_keeps_the_counts(sim, agg):
    """The counts are the product. Only the deduplication state is transient."""
    agg.add("evt-1", "campaign-7", 60_000)
    advance(sim, 30 * MINUTE)
    agg.close_before(watermark(sim.now, agg.late_window_ms))
    assert agg.count("campaign-7", 60_000) == 1


def test_closing_twice_closes_nothing_new(sim, agg):
    agg.add("evt-1", "campaign-7", 60_000)
    advance(sim, 30 * MINUTE)
    mark = watermark(sim.now, agg.late_window_ms)
    assert agg.close_before(mark) >= 1
    assert agg.close_before(mark) == 0


def test_a_nonsense_aggregator_is_an_error(sim):
    with pytest.raises(ValueError):
        BucketAggregator(sim, late_window_ms=0)


# -- the trap, and the way out ------------------------------------------------


def test_a_replay_sized_dedup_window_is_not_a_window():
    """690 GB of event ids, consulted on every one of 500,000 events a second.
    That is not a deduplication window, it is a database."""
    assert dedup_window_bytes(500_000, 86_400) == pytest.approx(691e9, rel=0.01)


def test_and_sharding_it_does_not_rescue_it():
    """Ten gigabytes per partition, of nothing but ids, held for a day."""
    assert dedup_window_bytes(500_000, 86_400, partitions=64) > 10e9


def test_the_late_window_is_a_hundredth_of_that():
    """Fifteen minutes across 64 partitions is about 110 MB each — which is a
    deduplication window rather than an infrastructure project."""
    assert dedup_window_bytes(500_000, 900, partitions=64) < 200e6


def test_replay_recomputes_rather_than_adding(agg):
    """The answer the brief is built around.

    A replay that **adds** is not idempotent and needs a deduplication window as
    deep as the replay. A replay that **recomputes a bucket from its events** is
    idempotent by construction, at any depth, with no extra memory — because
    assignment is idempotent and addition is not.

    You proved that on Wednesday with two lines of dictionary manipulation.
    """
    agg.add("evt-1", "campaign-7", 60_000)
    agg.add("evt-2", "campaign-7", 60_000)
    assert agg.count("campaign-7", 60_000) == 2

    events = ["evt-1", "evt-2", "evt-3"]
    assert agg.recompute("campaign-7", 60_000, events) == 3
    assert agg.recompute("campaign-7", 60_000, events) == 3
    assert agg.recompute("campaign-7", 60_000, events) == 3


def test_replay_absorbs_duplicates_in_the_replayed_stream_too(agg):
    """The replayed log has the original duplicates in it. Recomputation handles
    them without any window at all."""
    assert agg.recompute("campaign-7", 60_000, ["a", "b", "a", "c", "b"]) == 3


def test_replay_works_on_a_bucket_that_was_already_closed(sim, agg):
    """Which is the point: closing frees deduplication memory, and replay does not
    need it."""
    agg.add("evt-1", "campaign-7", 60_000)
    advance(sim, 30 * MINUTE)
    agg.close_before(watermark(sim.now, agg.late_window_ms))

    assert agg.recompute("campaign-7", 60_000, ["evt-1", "evt-2"]) == 2
    assert agg.count("campaign-7", 60_000) == 2


def test_replay_of_a_correct_bucket_leaves_it_correct(agg):
    """Question 2 in the milestone README. Replaying 24 hours touches buckets that
    were already right, and they have to stay right."""
    agg.add("evt-1", "campaign-7", 60_000)
    before = agg.count("campaign-7", 60_000)
    agg.recompute("campaign-7", 60_000, ["evt-1"])
    assert agg.count("campaign-7", 60_000) == before
