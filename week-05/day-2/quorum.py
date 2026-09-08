"""Quorums, and what happens when copies disagree.

Deliberately not on the network. Days 1 and 3 are about timing; today is about
counting, and the pigeonhole argument is clearer without jitter in the way.

Replace each `raise NotImplementedError` with your own code.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Versioned:
    """One copy of a value, and enough metadata to argue about which is newer.

    `version` is a logical counter. Two writes with the *same* version from
    different writers are **concurrent** — neither happened before the other, and
    no amount of looking at timestamps changes that.
    """

    value: object
    version: int
    writer: str
    timestamp_ms: int


class Replica:
    """One node's copy. `up` is whether it can be reached."""

    def __init__(self, name: str) -> None:
        raise NotImplementedError

    def put(self, key: str, versioned: Versioned) -> None:
        """Store it, keeping every version at the highest version number seen.

        Keeping several is the point: a replica that silently picked a winner
        would hide the conflict from the layer that can actually resolve it.
        """
        raise NotImplementedError

    def get(self, key: str) -> list[Versioned]:
        """Every version this replica holds for the key. Empty if it has none."""
        raise NotImplementedError


class QuorumStore:
    """N replicas, W acknowledgements to write, R asked on read."""

    def __init__(self, replicas: list[Replica], w: int, r: int) -> None:
        """Raises ValueError if W or R is outside 1..N."""
        raise NotImplementedError

    @property
    def overlaps(self) -> bool:
        """Whether `W + R > N` — whether every read set must touch every write set."""
        raise NotImplementedError

    def write(self, key: str, versioned: Versioned, to: list[int] | None = None) -> bool:
        """Write to `to` (default: the first W replica indexes). Succeeds when at
        least W *reachable* replicas accepted.

        A replica that is down accepts nothing. Note that a failed write still
        leaves the value on whichever replicas did accept it — see the test.
        """
        raise NotImplementedError

    def read(self, key: str, frm: list[int] | None = None) -> list[Versioned]:
        """Ask `frm` (default: the first R reachable replicas) and return every
        version any of them held, deduplicated."""
        raise NotImplementedError


def newest(versions: list[Versioned]) -> list[Versioned]:
    """The versions at the highest version number. More than one means concurrent
    writes, which is a conflict rather than an ordering."""
    raise NotImplementedError


def last_write_wins(versions: list[Versioned]) -> Versioned | None:
    """Pick by wall-clock timestamp, breaking ties by writer name.

    Simple, cheap, and it discards a write that was acknowledged. Write it, then
    run the clock-skew test, and decide how you feel about it.
    """
    raise NotImplementedError


def siblings(versions: list[Versioned]) -> list[Versioned]:
    """The concurrent versions, if there is more than one. Empty when there is a
    single newest version — i.e. no conflict."""
    raise NotImplementedError


def merge_sets(versions: list[Versioned]) -> set:
    """Resolve set-shaped siblings by union — Dynamo's shopping cart.

    Every value must be a set. This is the *application's* job: storage can tell
    you there is a conflict, and only you know what the data means.
    """
    raise NotImplementedError


def compare_and_set(
    store: QuorumStore, key: str, expected_version: int, versioned: Versioned
) -> bool:
    """Write only if the newest version currently readable is `expected_version`.

    Turns a silent conflict into a visible rejection the client can retry, which
    is a much better failure than either picking a winner or returning siblings.
    """
    raise NotImplementedError


def read_repair(store: QuorumStore, key: str) -> int:
    """Push the newest version to every reachable replica that is behind.
    Returns how many were updated.

    Repairs only what somebody reads — so a key nobody reads stays diverged for
    ever, which is why real systems also run a background sweep.
    """
    raise NotImplementedError
