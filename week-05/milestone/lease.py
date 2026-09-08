"""Leases, and the token that makes a confused holder harmless.

Replace each `raise NotImplementedError` with your own code.
"""

from dataclasses import dataclass

from simlib import Simulation


@dataclass(frozen=True)
class Lease:
    resource: str
    holder: str
    token: int
    expires_at_ms: int

    def is_valid(self, now_ms: int) -> bool:
        """Whether this lease has expired yet.

        Useful for a client deciding whether to renew. **Useless as a safety
        check before a write** — the process can be paused between the check and
        the write, and no amount of care closes that gap. That is why tokens
        exist.
        """
        raise NotImplementedError


class LeaseService:
    """Exclusive, expiring leases with ever-increasing tokens."""

    def __init__(self, sim: Simulation, lease_ms: int = 10_000) -> None:
        """Track the current lease per resource and the next token to issue.

        Tokens are global rather than per-resource here, which is simplest and
        gives a total order across the whole service. Per-resource would also work;
        say which you chose in your document.
        """
        raise NotImplementedError

    def acquire(self, resource: str, holder: str) -> Lease | None:
        """Take the lease if nobody holds a live one. None if somebody does.

        A fresh acquisition always takes a **new, higher** token — even for the
        same holder, and even straight after a clean release. If tokens can repeat
        they order nothing.
        """
        raise NotImplementedError

    def renew(self, lease: Lease) -> Lease | None:
        """Extend an existing lease, **keeping the same token**.

        None if this lease is not the current one, or has already expired and been
        taken by someone else. A new token here would fence the holder out of
        storage it had already written to.
        """
        raise NotImplementedError

    def release(self, lease: Lease) -> bool:
        """Give it up early. False if this lease is not the current holder's."""
        raise NotImplementedError

    def holder_of(self, resource: str) -> str | None:
        """Who holds a live lease on this resource, if anyone."""
        raise NotImplementedError


class FencedStore:
    """Storage that refuses a writer whose token is behind.

    The rule: accept a write whose token is greater than or equal to the highest
    token seen for that key. A holder writing repeatedly with its own token is
    fine; a holder writing with a token that has been superseded is not.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def write(self, key: str, value, token: int) -> bool:
        """Returns whether the write was accepted."""
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError


class UnfencedStore:
    """Ordinary storage, which believes whoever is talking to it.

    Here so one test can show what the same sequence of events does without
    fencing. It is not a strawman — it is most storage systems.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def write(self, key: str, value) -> bool:
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError


def renewals_per_second(leases_held: int, lease_ms: int, renew_at: float = 0.5) -> float:
    """Renewal load: each holder renews after `renew_at` of its lease has elapsed.

    Run it on the brief's numbers, then halve the lease duration and run it again.
    The result belongs in your Size section.
    """
    raise NotImplementedError
