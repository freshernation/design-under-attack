"""Day 3 — presence and delivery.

`test_every_push_is_dropped_and_nothing_is_lost` is the day: delivery failed
completely and the product was unaffected, because delivery was never the
mechanism.
"""

import pytest

from presence import MessageStore, PresenceTracker, broadcast_cost
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


# -- presence -----------------------------------------------------------------


def test_a_heartbeat_brings_a_user_online(sim):
    tracker = PresenceTracker(sim, timeout_ms=60_000)
    assert tracker.heartbeat("ana") == [("ana", "online")]
    assert tracker.is_online("ana") is True


def test_a_second_heartbeat_announces_nothing(sim):
    """A presence broadcast for a user who was already present is pure cost."""
    tracker = PresenceTracker(sim, timeout_ms=60_000)
    tracker.heartbeat("ana")
    assert tracker.heartbeat("ana") == []
    assert tracker.broadcasts == 1


def test_silence_eventually_means_offline(sim):
    tracker = PresenceTracker(sim, timeout_ms=60_000)
    tracker.heartbeat("ana")

    advance(sim, 59_000)
    assert tracker.tick() == []

    advance(sim, 2_000)
    assert tracker.tick() == [("ana", "offline")]
    assert tracker.is_online("ana") is False


def test_coming_back_is_immediate(sim):
    """Asymmetric on purpose. Going offline waits out a timeout; coming back does
    not wait for anything."""
    tracker = PresenceTracker(sim, timeout_ms=60_000)
    tracker.heartbeat("ana")
    advance(sim, 61_000)
    tracker.tick()

    assert tracker.heartbeat("ana") == [("ana", "online")]


def test_a_presence_tracker_needs_a_timeout(sim):
    with pytest.raises(ValueError):
        PresenceTracker(sim, timeout_ms=0)


# -- flapping -----------------------------------------------------------------


def flap(sim, tracker, cycles=5):
    """A client on a marginal network: heartbeats, a gap past the timeout, back."""
    for _ in range(cycles):
        tracker.heartbeat("ana")
        advance(sim, 61_000)
        tracker.tick()
        advance(sim, 1_000)


def test_flapping_generates_broadcasts(sim):
    """And a broadcast is the expensive thing. A system that gets *more* expensive
    when the network is bad has a feedback loop in it."""
    tracker = PresenceTracker(sim, timeout_ms=60_000)
    flap(sim, tracker, cycles=5)
    assert tracker.broadcasts >= 10


def test_debouncing_absorbs_a_brief_gap(sim):
    """The user disappears for 65 seconds against a 60-second timeout, but the
    debounce has not elapsed when they return — so nobody is told anything."""
    tracker = PresenceTracker(sim, timeout_ms=60_000, debounce_ms=30_000)
    tracker.heartbeat("ana")

    advance(sim, 65_000)
    assert tracker.tick() == []

    tracker.heartbeat("ana")
    assert tracker.is_online("ana") is True
    assert tracker.broadcasts == 1, "one broadcast in total: the original arrival"


def test_debouncing_still_declares_a_real_departure(sim):
    tracker = PresenceTracker(sim, timeout_ms=60_000, debounce_ms=30_000)
    tracker.heartbeat("ana")

    advance(sim, 65_000)
    tracker.tick()
    advance(sim, 31_000)
    assert tracker.tick() == [("ana", "offline")]


# -- the multiplication -------------------------------------------------------


def test_presence_costs_more_than_messages():
    """One user arriving, forty channels, thirty members each: 1,200 notifications
    from one event. Multiply by a morning rush and presence dwarfs the messages."""
    assert broadcast_cost(1, 40, 30) == 1_200
    assert broadcast_cost(100_000, 40, 30) == 120_000_000


def test_subscribing_narrowly_is_the_lever():
    """A client watching the one channel it has open rather than all forty."""
    all_channels = broadcast_cost(100_000, 40, 30)
    open_channel_only = broadcast_cost(100_000, 1, 30)
    assert all_channels / open_channel_only == pytest.approx(40)


# -- delivery -----------------------------------------------------------------


def test_messages_get_sequence_numbers():
    store = MessageStore()
    assert [store.append("general", f"m{i}") for i in range(3)] == [1, 2, 3]


def test_sequences_are_per_conversation():
    """Week 7's per-partition ordering, arriving as a product feature. Two messages
    in different conversations have no order, and nobody has ever cared."""
    store = MessageStore()
    store.append("general", "a")
    assert store.append("random", "b") == 1


def test_catching_up_returns_what_was_missed():
    store = MessageStore()
    for i in range(5):
        store.append("general", f"m{i}")
    assert store.catch_up("general", since_sequence=3) == [(4, "m3"), (5, "m4")]


def test_a_caught_up_client_gets_nothing():
    store = MessageStore()
    store.append("general", "m0")
    assert store.catch_up("general", since_sequence=1) == []


def test_a_new_client_gets_everything():
    store = MessageStore()
    for i in range(3):
        store.append("general", f"m{i}")
    assert len(store.catch_up("general", since_sequence=0)) == 3


def test_catching_up_on_an_unknown_conversation():
    assert MessageStore().catch_up("nowhere", 0) == []


def test_every_push_is_dropped_and_nothing_is_lost():
    """The day.

    A client is offline for the whole conversation. Every real-time delivery fails
    — not degraded, *failed* — and the client sees every message the moment it
    reconnects.

    That is what "the message is stored and delivery is an optimisation" buys, and
    it is why this design needs no per-device queue, no delivery guarantee on the
    push path, and no cleanup for devices that never come back.
    """
    store = MessageStore()
    client_sequence = 0

    for i in range(10):
        store.append("general", f"m{i}")      # every push into the void

    missed = store.catch_up("general", client_sequence)
    assert [m for _seq, m in missed] == [f"m{i}" for i in range(10)]


def test_a_duplicate_push_is_harmless():
    """The client deduplicates by sequence number, so at-least-once push needs no
    machinery at all."""
    store = MessageStore()
    store.append("general", "hello")

    seen = set()
    for _ in range(3):
        for sequence, _message in store.catch_up("general", 0):
            seen.add(sequence)
    assert seen == {1}
