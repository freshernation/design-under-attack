"""Making an effect safe to repeat, and removing the dual write that makes it necessary.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Simulation


class IdempotencyConflict(Exception):
    """The same key arrived with a different payload.

    Silently returning the first result would hide a real bug: two different
    operations claiming to be the same one. This is an error, not a duplicate.
    """


class IdempotencyStore:
    """Key to stored result, with an expiry.

        store.execute("req-1", payload, do_the_work)   # runs it
        store.execute("req-1", payload, do_the_work)   # returns the stored result

    The stored **result** is returned, not merely "already done" — the retrying
    client wants the answer it missed.
    """

    def __init__(self, sim: Simulation, ttl_ms: int = 86_400_000) -> None:
        """The default is 24 hours, which is what Stripe keeps. The window must
        exceed the longest plausible retry, including a human retrying tomorrow.
        """
        raise NotImplementedError

    def execute(self, key: str, payload, fn):
        """Run `fn()` once per key and return its result on every call.

        Raises `IdempotencyConflict` when a live key is reused with a different
        payload.
        """
        raise NotImplementedError

    def __len__(self) -> int:
        """Live keys. This is the memory the window costs you."""
        raise NotImplementedError


class DedupWindow:
    """Ids seen inside a window. The whole question is how long you remember.

    Seconds for a visibility-timeout redelivery. Minutes for a consumer restart.
    **A week for a deliberate replay of a week** — and that is the number that
    decides whether an exact store fits in memory at all.
    """

    def __init__(self, sim: Simulation, window_ms: int) -> None:
        raise NotImplementedError

    def seen(self, event_id: str) -> bool:
        """Whether this id has been seen inside the window — and record it.

        Returns True for a duplicate, False for a first sighting.
        """
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


def window_bytes(events_per_second: float, window_s: float, bytes_per_id: int = 16) -> int:
    """The memory an exact deduplication window costs.

    Run it on 500,000 events a second over 24 hours before deciding that exact
    deduplication is available to you.
    """
    raise NotImplementedError


def apply_absolute(state: dict, key: str, value) -> None:
    """`state[key] = value`. Idempotent: doing it twice is doing it once."""
    raise NotImplementedError


def apply_increment(state: dict, key: str, delta: float) -> None:
    """`state[key] += delta`. **Not** idempotent, and the test says so.

    Restating a relative change as an absolute one is often the entire fix, and it
    costs nothing.
    """
    raise NotImplementedError


class Database:
    """A store with a transaction that either commits both rows or neither."""

    def __init__(self) -> None:
        """`rows` and `outbox`, both lists."""
        raise NotImplementedError

    def insert(self, row) -> None:
        raise NotImplementedError

    def insert_with_outbox(self, row, event) -> None:
        """Both, atomically. One database, one transaction, no protocol —
        which is the entire trick."""
        raise NotImplementedError

    def unsent_events(self) -> list:
        raise NotImplementedError

    def mark_sent(self, event) -> None:
        raise NotImplementedError


def dual_write(database: Database, published: list, row, event, crash_between: bool) -> None:
    """Insert the row, then publish — with a crash point between them.

    There is no transaction spanning the two systems, so a crash leaves exactly one
    of them done. Reordering does not help; retrying does not help.
    """
    raise NotImplementedError


def relay(database: Database, published: list, crash_after_publish: bool = False) -> int:
    """Publish unsent outbox events and mark them sent. Returns how many published.

    With `crash_after_publish`, die after publishing the first event and before
    marking it — so the next run publishes it again. **That duplicate is the
    point**: the outbox converts "an event may be lost" into "an event may be
    duplicated", and you have already built the thing that makes duplicates free.
    """
    raise NotImplementedError
