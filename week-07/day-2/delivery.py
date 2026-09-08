"""At most once, at least once, and the visibility timeout that produces one of them.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation


def consume_with_crash(
    records: list, commit_before_processing: bool, crash_after: int | None = None
) -> list:
    """Process a list of records, crash part-way, restart, and finish.

    Returns **every effect that happened**, in order — including anything done
    twice. That list is the delivery guarantee, made concrete.

    * `commit_before_processing=True` — commit the offset, then process. A crash
      between the two loses the record.
    * `commit_before_processing=False` — process, then commit. A crash between the
      two repeats it.
    * `crash_after` — how many records are handled before the process dies. None
      means no crash.

    Model the restart as resuming from the last committed offset, which is what a
    restarted consumer actually does.
    """
    raise NotImplementedError


def duplicate_rate(effects: list) -> float:
    """The fraction of effects that were repeats, to four decimals.

    "Duplicates are rare" is not a design statement until it is a number.
    """
    raise NotImplementedError


def lost(records: list, effects: list) -> list:
    """Records that never had an effect at all."""
    raise NotImplementedError


class VisibilityQueue:
    """Receive makes a message invisible; delete removes it; a timeout returns it.

        queue = VisibilityQueue(sim, visibility_ms=30_000)
        receipt, message = queue.receive()
        queue.delete(receipt)

    This is the whole of at-least-once: a consumer that crashes never deletes, so
    the message reappears. And a consumer that is merely *slow* also never deletes
    in time, which is the interesting case.
    """

    def __init__(self, sim: Simulation, visibility_ms: int = 30_000) -> None:
        """Raises ValueError for a visibility timeout of zero or less."""
        raise NotImplementedError

    def send(self, message) -> None:
        raise NotImplementedError

    def receive(self):
        """`(receipt, message)` for the first visible message, or None.

        A receipt identifies this particular delivery, not the message — so a
        receipt from a delivery that has already timed out is stale and must be
        refused by `delete`.
        """
        raise NotImplementedError

    def delete(self, receipt) -> bool:
        """Remove the message. False if this receipt is stale, which means somebody
        else has it now and deleting would remove their work."""
        raise NotImplementedError

    def extend(self, receipt, extra_ms: int) -> bool:
        """Keep it invisible for longer — the right answer for work of
        unpredictable length. It is a lease, renewed, exactly as in week 5."""
        raise NotImplementedError

    @property
    def visible_count(self) -> int:
        raise NotImplementedError
