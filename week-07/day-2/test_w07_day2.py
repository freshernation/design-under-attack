"""Day 2 — delivery guarantees.

The first two tests are the same crash, at the same instant, with one line of the
consumer moved.
"""

import pytest

from delivery import VisibilityQueue, consume_with_crash, duplicate_rate, lost
from simlib import Simulation

RECORDS = [f"e{i}" for i in range(6)]


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


# -- the two guarantees that exist --------------------------------------------


def test_committing_first_loses_a_record():
    """At most once. The offset was recorded, the work was not done, and the
    restart resumes past it. Nothing is ever done twice; something is never done."""
    effects = consume_with_crash(RECORDS, commit_before_processing=True, crash_after=3)
    assert lost(RECORDS, effects) == ["e2"]
    assert duplicate_rate(effects) == 0.0


def test_committing_last_repeats_a_record():
    """At least once. Same crash, same instant, one line moved. The work was done
    and the offset was not recorded, so the restart does it again."""
    effects = consume_with_crash(RECORDS, commit_before_processing=False, crash_after=3)
    assert lost(RECORDS, effects) == []
    assert effects.count("e2") == 2


def test_without_a_crash_they_are_indistinguishable():
    """Which is why this is invisible in testing and appears in production."""
    a = consume_with_crash(RECORDS, commit_before_processing=True)
    b = consume_with_crash(RECORDS, commit_before_processing=False)
    assert a == b == RECORDS


def test_duplicates_are_a_number_not_an_adjective():
    effects = consume_with_crash(RECORDS, commit_before_processing=False, crash_after=3)
    assert duplicate_rate(effects) == pytest.approx(0.1429, abs=0.001)


def test_nothing_processed_has_no_duplicates():
    assert duplicate_rate([]) == 0.0


def test_at_least_once_is_the_right_default():
    """Not because duplicates are pleasant, but because they are fixable and
    losses are not. A duplicate can be absorbed by Wednesday's mechanism; a lost
    record cannot be recovered by anything."""
    at_most = consume_with_crash(RECORDS, commit_before_processing=True, crash_after=3)
    at_least = consume_with_crash(RECORDS, commit_before_processing=False, crash_after=3)
    assert lost(RECORDS, at_most)
    assert not lost(RECORDS, at_least)


# -- the visibility timeout ---------------------------------------------------


def test_a_received_message_is_invisible_to_others(sim):
    queue = VisibilityQueue(sim, visibility_ms=30_000)
    queue.send("job-1")

    receipt, message = queue.receive()
    assert message == "job-1"
    assert queue.receive() is None
    assert queue.visible_count == 0


def test_deleting_removes_it(sim):
    queue = VisibilityQueue(sim, visibility_ms=30_000)
    queue.send("job-1")
    receipt, _ = queue.receive()
    assert queue.delete(receipt) is True

    advance(sim, 60_000)
    assert queue.receive() is None


def test_a_crashed_consumer_gets_the_message_redelivered(sim):
    """At-least-once, from the mechanism. The consumer never deleted, so the
    message comes back."""
    queue = VisibilityQueue(sim, visibility_ms=30_000)
    queue.send("job-1")
    queue.receive()                       # and then the consumer dies

    advance(sim, 30_001)
    assert queue.receive()[1] == "job-1"


def test_a_slow_consumer_has_its_work_done_twice(sim):
    """The test to sit with.

    Nothing crashed. Nothing failed. The consumer is working, correctly, and takes
    45 seconds against a 30-second timeout — so somebody else picks up the same
    message and does the same work.

    Then the first consumer finishes and its delete is refused, because the
    receipt is stale and deleting would remove the other consumer's work.
    """
    queue = VisibilityQueue(sim, visibility_ms=30_000)
    queue.send("slow-job")
    first_receipt, _ = queue.receive()

    advance(sim, 30_001)
    second_receipt, message = queue.receive()
    assert message == "slow-job", "a second consumer now has it too"

    advance(sim, 15_000)
    assert queue.delete(first_receipt) is False, "the first consumer's receipt is stale"
    assert queue.delete(second_receipt) is True


def test_extending_keeps_it(sim):
    """The right answer for work of unpredictable length: a lease, renewed. Exactly
    week 5, in a queue."""
    queue = VisibilityQueue(sim, visibility_ms=30_000)
    queue.send("slow-job")
    receipt, _ = queue.receive()

    advance(sim, 25_000)
    assert queue.extend(receipt, 30_000) is True

    advance(sim, 20_000)
    assert queue.receive() is None, "still invisible, because the lease was renewed"
    assert queue.delete(receipt) is True


def test_a_stale_receipt_cannot_extend(sim):
    queue = VisibilityQueue(sim, visibility_ms=10_000)
    queue.send("job")
    stale, _ = queue.receive()

    advance(sim, 10_001)
    queue.receive()
    assert queue.extend(stale, 10_000) is False


def test_messages_are_delivered_in_order_when_nothing_times_out(sim):
    queue = VisibilityQueue(sim, visibility_ms=30_000)
    for i in range(3):
        queue.send(f"job-{i}")
    assert [queue.receive()[1] for _ in range(3)] == ["job-0", "job-1", "job-2"]


def test_a_queue_needs_a_timeout(sim):
    with pytest.raises(ValueError):
        VisibilityQueue(sim, visibility_ms=0)
