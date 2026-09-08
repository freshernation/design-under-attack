"""Read-your-writes and monotonic reads, without making anything linearizable.

Nine lines of token handling do what a majority round trip on every request would
also do, at roughly none of the cost.

Replace each `raise NotImplementedError` with your own code.
"""


class NoFreshReplica(Exception):
    """No replica in the pool has caught up to the version this client requires.

    Raising is a choice. The alternatives are to wait for one, or to fall back to
    the leader — both defensible, and your design document should say which.
    """


class Replica:
    """A copy, with a version counting how much of the leader's history it has."""

    def __init__(self, name: str) -> None:
        """`store`, and `version` starting at 0."""
        raise NotImplementedError

    def apply(self, version: int, key: str, value) -> None:
        """Take one entry from the leader's history."""
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError


class Cluster:
    """One leader and some followers, with replication you drive by hand.

    No network and no timers today: the point is which replica answers, and jitter
    would only make it harder to see.
    """

    def __init__(self, followers: int = 3) -> None:
        """A leader Replica plus `followers` of them. `history` records every write
        so a follower can be caught up later."""
        raise NotImplementedError

    def write(self, key: str, value) -> int:
        """Apply to the leader and return the new version."""
        raise NotImplementedError

    def replicate(self, follower: int, upto: int | None = None) -> None:
        """Advance one follower through the history, up to `upto` (default: all).

        Followers advance independently — that is the whole point of the day.
        """
        raise NotImplementedError

    def read_any(self, key, follower: int | None = None):
        """Read from a follower with no guarantees at all. What you get for free,
        and what the first test shows costs you."""
        raise NotImplementedError

    def read_fresh(self, key, min_version: int, follower: int | None = None):
        """Read only from a replica at `min_version` or later.

        With `follower` given, use that one and raise `NoFreshReplica` if it is
        behind. Without, use the first follower that is fresh enough, and raise if
        none is.
        """
        raise NotImplementedError


class Session:
    """One client's view. It carries the highest version it has ever seen.

    That single integer is what buys read-your-writes and monotonic reads. It is
    not a consistency model; it is a promise to one client, which is what products
    actually need.
    """

    def __init__(self, cluster: Cluster) -> None:
        """`version` starts at 0 — a new client has seen nothing and may read
        anything."""
        raise NotImplementedError

    def write(self, key: str, value) -> int:
        """Write, and remember the version so later reads cannot go behind it."""
        raise NotImplementedError

    def read(self, key, follower: int | None = None):
        """Read at or after the version this session has seen, and advance the
        session to whatever it read.

        Advancing on *read* is what gives monotonic reads: once you have seen
        version 9, no later read may be answered by a replica at version 4.
        """
        raise NotImplementedError


def stale_by(cluster: Cluster, follower: int) -> int:
    """How many entries behind the leader this follower is."""
    raise NotImplementedError


def read_pool(cluster: Cluster, max_stale: int) -> list[int]:
    """Which followers are fresh enough to serve reads.

    A follower that removes itself once it falls too far behind converts an
    invisible correctness problem into a visible capacity one, which is a much
    better problem to have.
    """
    raise NotImplementedError
