"""Project 2's mechanism.

Two tests are the brief: `test_an_absent_client_loses_nothing` and
`test_the_largest_channel_is_not_pushed_to`.
"""

import pytest

from chat import (
    ChatSystem,
    delivery_fanout_per_second,
    feasible_globally,
    largest_channel_burst,
)
from simlib import Simulation


@pytest.fixture
def sim():
    return Simulation()


@pytest.fixture
def system(sim):
    return ChatSystem(sim, gateways=["gw-0", "gw-1"], capacity_each=100, broadcast_threshold=50)


# -- the arithmetic -----------------------------------------------------------


def test_delivery_fanout_at_peak():
    """30,000 messages a second into channels averaging 12 members, 40% of whom
    are connected: 144,000 pushes a second."""
    assert delivery_fanout_per_second(30_000, 12, 0.4) == pytest.approx(144_000)


def test_only_connected_members_cost_anything():
    """The connected fraction is most of your delivery budget. Sixty per cent of
    the work is not done because nobody is there to receive it."""
    everyone = delivery_fanout_per_second(30_000, 12, 1.0)
    realistic = delivery_fanout_per_second(30_000, 12, 0.4)
    assert realistic / everyone == pytest.approx(0.4)


def test_one_message_in_the_largest_channel():
    """Thirty-two thousand pushes, from one person typing. The median channel
    produces about five. Four orders of magnitude, in the same system, and systems
    fall over on maxima."""
    assert largest_channel_burst(80_000, 0.4) == 32_000
    assert largest_channel_burst(12, 0.4) < 10


def test_the_latency_target_survives_the_geography():
    """Week 1's check, in pass 1 where it belongs. 150 ms of round trip plus 50 ms
    of processing fits inside 500 ms — with 300 ms to spare, which is the margin
    that decides where messages are written."""
    assert feasible_globally(500, worst_rtt_ms=150, processing_ms=50) is True


def test_a_tighter_target_would_not():
    """And this is a requirement to renegotiate, not a design to attempt."""
    assert feasible_globally(150, worst_rtt_ms=150, processing_ms=50) is False


@pytest.mark.parametrize("fraction", [-0.1, 1.5])
def test_a_nonsense_connected_fraction_is_an_error(fraction):
    with pytest.raises(ValueError):
        delivery_fanout_per_second(100, 10, fraction)


# -- delivery -----------------------------------------------------------------


def test_a_message_reaches_connected_members(system):
    for user in ("ana", "bo", "carla"):
        system.join(user, "#general")
        system.connect(user)

    sequence, pushed = system.post("ana", "#general", "hello")
    assert sequence == 1
    assert pushed == ["bo", "carla"], "everyone but the sender"


def test_a_sequence_is_assigned_before_any_delivery(system):
    """The rule the design rests on. The message is durable and numbered; pushing
    is what happens afterwards, and it may fail entirely."""
    system.join("ana", "#general")
    sequence, pushed = system.post("ana", "#general", "into the void")
    assert sequence == 1
    assert pushed == []
    assert system.catch_up("ana", "#general") == [(1, "into the void")]


def test_sequences_are_per_channel(system):
    system.join("ana", "#general")
    system.join("ana", "#random")
    system.post("ana", "#general", "a")
    assert system.post("ana", "#random", "b")[0] == 1


def test_a_disconnected_member_is_skipped_and_counted(system):
    system.join("ana", "#general")
    system.join("bo", "#general")
    system.connect("ana")

    _seq, pushed = system.post("ana", "#general", "hello")
    assert pushed == []
    assert system.stats["skipped_offline"] == 1


# -- the brief ----------------------------------------------------------------


def test_an_absent_client_loses_nothing(system):
    """Sixty per cent of mobile clients are disconnected at any moment, and this is
    what makes that a non-event.

    Bo is offline for the entire conversation. Every push for bo does not happen —
    not degraded, not retried, *not attempted*. Bo reconnects and has all ten
    messages, in order.

    That is what "the message is durable and delivery is an optimisation" buys, and
    it is why this design needs no per-device queue and no delivery guarantee on the
    push path.
    """
    system.join("ana", "#general")
    system.join("bo", "#general")
    system.connect("ana")

    for i in range(10):
        system.post("ana", "#general", f"m{i}")

    assert system.stats["pushes"] == 0
    missed = system.catch_up("bo", "#general")
    assert [text for _seq, text in missed] == [f"m{i}" for i in range(10)]


def test_the_largest_channel_is_not_pushed_to(system):
    """The second population getting its second answer.

    A channel at or above the threshold produces no pushes at all — its members
    pull on their next interaction. One message to 80,000 people does not become
    32,000 simultaneous deliveries competing with every other channel in the
    product.
    """
    for i in range(60):
        user = f"user-{i}"
        system.join(user, "#announcements")
        system.connect(user)

    _seq, pushed = system.post("user-0", "#announcements", "all hands at 3pm")
    assert pushed == []
    assert system.stats["large_channel_messages"] == 1
    assert system.stats["pushes"] == 0


def test_and_its_members_still_get_the_message(system):
    """Not pushed is not lost. The pull path is the same one the offline clients
    use, which is why there is only one correctness path in this design."""
    for i in range(60):
        system.join(f"user-{i}", "#announcements")
    system.post("user-0", "#announcements", "all hands at 3pm")

    assert system.catch_up("user-7", "#announcements") == [(1, "all hands at 3pm")]


def test_a_small_channel_is_still_pushed(system):
    """Two strategies, chosen by size, in the same system."""
    for user in ("ana", "bo"):
        system.join(user, "#small")
        system.connect(user)
    _seq, pushed = system.post("ana", "#small", "hi")
    assert pushed == ["bo"]


# -- catch-up and read positions ----------------------------------------------


def test_marking_read_advances_the_position(system):
    system.join("ana", "#general")
    for i in range(5):
        system.post("bo", "#general", f"m{i}")

    assert system.unread("ana", "#general") == 5
    system.mark_read("ana", "#general", 3)
    assert system.unread("ana", "#general") == 2


def test_read_positions_never_go_backwards(system):
    """A late receipt from a second device must not un-read what the first read."""
    system.join("ana", "#general")
    for i in range(5):
        system.post("bo", "#general", f"m{i}")

    system.mark_read("ana", "#general", 5)
    system.mark_read("ana", "#general", 2)
    assert system.unread("ana", "#general") == 0


def test_ordering_is_preserved_for_every_member(system):
    system.join("ana", "#general")
    system.join("bo", "#general")
    for i in range(20):
        system.post("carla", "#general", f"m{i}")

    for user in ("ana", "bo"):
        assert [t for _s, t in system.catch_up(user, "#general")] == [f"m{i}" for i in range(20)]


# -- the deploy ---------------------------------------------------------------


def test_a_gateway_restart_returns_its_clients(system):
    for i in range(20):
        system.connect(f"user-{i}")

    dropped = system.restart_gateway("gw-0")
    assert len(dropped) == 10
    assert all(not system.is_connected(u) for u in dropped)


def test_reconnecting_after_a_restart_loses_nothing(system):
    """Daily deploys, hundreds of thousands of connections, and no message risk —
    because the connection was never where the messages lived."""
    system.join("ana", "#general")
    system.connect("ana")
    system.post("bo", "#general", "before the deploy")

    dropped = system.restart_gateway(system.gateway_of["ana"])
    system.post("bo", "#general", "during the deploy")
    for user in dropped:
        system.connect(user)

    assert [t for _s, t in system.catch_up("ana", "#general")] == [
        "before the deploy",
        "during the deploy",
    ]


def test_a_full_tier_rejects_rather_than_over_committing(sim):
    system = ChatSystem(sim, gateways=["gw-0"], capacity_each=2)
    system.connect("a")
    system.connect("b")
    assert system.connect("c") is None


def test_connecting_twice_is_idempotent(system):
    first = system.connect("ana")
    assert system.connect("ana") == first
    assert system.connections[first].count("ana") == 1


@pytest.mark.parametrize("gateways, capacity", [([], 10), (["gw-0"], 0)])
def test_a_nonsense_system_is_an_error(sim, gateways, capacity):
    with pytest.raises(ValueError):
        ChatSystem(sim, gateways=gateways, capacity_each=capacity)
