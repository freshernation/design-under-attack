"""Presence, heartbeats, and delivering to a device that is usually not there.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation


class PresenceTracker:
    """Who is online, decided by heartbeats and a timeout.

        tracker = PresenceTracker(sim, timeout_ms=60_000, debounce_ms=5_000)
        tracker.heartbeat("ana")
        tracker.tick()      # -> [("ana", "offline")] when the timeout has passed

    **Asymmetric on purpose.** Going online is instant; going offline waits out the
    timeout and then the debounce. Flapping is the expensive failure, because every
    flicker is a presence broadcast to everyone who can see that user.
    """

    def __init__(self, sim: Simulation, timeout_ms: int, debounce_ms: int = 0) -> None:
        """Track the last heartbeat per user, who is currently believed online, and
        `broadcasts` — the number of state changes announced.

        Raises ValueError for a timeout of zero or less.
        """
        raise NotImplementedError

    def heartbeat(self, user: str) -> list[tuple[str, str]]:
        """Record a heartbeat. Returns any state changes to broadcast.

        A user who was offline comes back **immediately** — no debounce in this
        direction. A user who was silently pending an offline broadcast has that
        pending state cancelled, which is what makes debouncing work.
        """
        raise NotImplementedError

    def tick(self) -> list[tuple[str, str]]:
        """Called periodically. Returns `(user, "offline")` for anyone whose
        timeout has expired **and** whose debounce has since elapsed."""
        raise NotImplementedError

    def is_online(self, user: str) -> bool:
        raise NotImplementedError


def broadcast_cost(users_going_online: int, channels_each: int, members_each: int) -> int:
    """Notifications produced by presence changes.

    Run it on a morning rush before deciding presence is a small feature. A
    message goes to one conversation; a presence change goes to everyone who can
    see that person.
    """
    raise NotImplementedError


class MessageStore:
    """Durable messages with a per-conversation sequence.

    The inversion that makes everything else tractable: **the message is stored,
    and delivery is an optimisation.** A client that missed a push asks what it has
    missed since its last sequence number, and nothing is lost.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def append(self, conversation: str, message) -> int:
        """Store it and return its sequence number, starting at 1."""
        raise NotImplementedError

    def catch_up(self, conversation: str, since_sequence: int) -> list[tuple[int, object]]:
        """`(sequence, message)` pairs after `since_sequence`.

        This is the slow path, and it is also the correctness path. The fast path
        can fail entirely and nobody loses anything.
        """
        raise NotImplementedError

    def latest_sequence(self, conversation: str) -> int:
        raise NotImplementedError
