"""A chat core: durable messages, best-effort delivery, and two kinds of channel.

Replace each `raise NotImplementedError` with your own code.
"""

import math

from simlib import Simulation


def delivery_fanout_per_second(
    messages_per_second: float, avg_members: float, connected_fraction: float
) -> float:
    """Pushes per second across the whole system.

    Note the third term: you only push to members who are actually connected, and
    at a 40% connected fraction that is most of your delivery cost gone.
    """
    raise NotImplementedError


def largest_channel_burst(members: int, connected_fraction: float) -> int:
    """Pushes produced by **one** message in the largest channel.

    The average channel is twelve people. This number is four orders of magnitude
    larger, and systems fall over on maxima rather than averages.
    """
    raise NotImplementedError


def feasible_globally(p99_target_ms: float, worst_rtt_ms: float, processing_ms: float) -> bool:
    """Whether the latency target survives the geography.

    Week 1's check, and it belongs in pass 1 rather than pass 5 — a target that
    physics forbids is a requirement to renegotiate, not a design to attempt.
    """
    raise NotImplementedError


class ChatSystem:
    """
    system = ChatSystem(sim, gateways=["gw-0", "gw-1"], capacity_each=100_000)
    system.join("ana", "#general")
    system.connect("ana")
    sequence, pushed = system.post("bo", "#general", "hello")

    The rule the whole design rests on: **a message is durable before it is
    delivered.** `post` stores it and assigns a sequence, and only then attempts
    delivery. Delivery can fail completely without anything being lost.
    """

    def __init__(
        self,
        sim: Simulation,
        gateways: list[str],
        capacity_each: int,
        broadcast_threshold: int = 10_000,
    ) -> None:
        """Track: messages per channel, channel membership, who is connected and on
        which gateway, each user's read position per channel, and `stats` counting
        `pushes`, `skipped_offline` and `large_channel_messages`.

        Raises ValueError for no gateways or a capacity below 1.
        """
        raise NotImplementedError

    # -- connections ----------------------------------------------------------

    def connect(self, user: str) -> str | None:
        """Place a user on the least loaded gateway with room. None when full."""
        raise NotImplementedError

    def disconnect(self, user: str) -> None:
        raise NotImplementedError

    def is_connected(self, user: str) -> bool:
        raise NotImplementedError

    def restart_gateway(self, host: str) -> list[str]:
        """Drop a gateway's connections and return the users who must reconnect."""
        raise NotImplementedError

    # -- channels -------------------------------------------------------------

    def join(self, user: str, channel: str) -> None:
        raise NotImplementedError

    def members(self, channel: str) -> list[str]:
        """Sorted, so the tests are deterministic."""
        raise NotImplementedError

    # -- messages -------------------------------------------------------------

    def post(self, sender: str, channel: str, text: str) -> tuple[int, list[str]]:
        """Store the message, then attempt delivery.

        Returns `(sequence, pushed_to)`.

        * The sequence is assigned **first**, and it is per channel.
        * A channel at or above `broadcast_threshold` is **not pushed to at all** —
          its members pull on their next interaction. Count it in
          `large_channel_messages`.
        * Otherwise push to every connected member except the sender; count the
          disconnected ones in `skipped_offline`.
        """
        raise NotImplementedError

    def catch_up(self, user: str, channel: str) -> list[tuple[int, str]]:
        """Everything after this user's read position. The correctness path."""
        raise NotImplementedError

    def mark_read(self, user: str, channel: str, sequence: int) -> None:
        """Coarse by design: one position per user per channel, not one per
        message. Receipts are more traffic than the messages they describe."""
        raise NotImplementedError

    def unread(self, user: str, channel: str) -> int:
        raise NotImplementedError
