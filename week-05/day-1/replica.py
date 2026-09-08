"""A leader and its followers, on a network that delays and drops things.

Asynchronous replication: the leader acknowledges a write immediately and sends it
onward. Everything uncomfortable in this lab follows from that one decision.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Network, Node, Simulation


class Follower(Node):
    """Applies the leader's writes, in order.

    Messages arrive out of order — the network jitters — so a replication stream
    has to be buffered and applied in sequence. Applying entry 7 before entry 6
    would leave the follower in a state the leader was never in.
    """

    def __init__(self, name: str, sim: Simulation) -> None:
        """`store`, `applied_version` (0 before anything), and a `pending` buffer
        of entries that arrived early."""
        raise NotImplementedError

    def receive(self, src: str, message) -> None:
        """`("replicate", version, key, value)`.

        Buffer it, then apply everything that is now contiguous from
        `applied_version + 1`.
        """
        raise NotImplementedError

    def read(self, key):
        """Whatever this follower has. Possibly not what the leader has."""
        raise NotImplementedError


class Leader(Node):
    """Accepts writes, acknowledges immediately, replicates in the background."""

    def __init__(self, name: str, sim: Simulation, follower_names: list[str]) -> None:
        """`store`, `version` (0 before anything), and `written_at`, mapping each
        version to the millisecond it was written — `lag_ms` needs it."""
        raise NotImplementedError

    def write(self, key, value) -> int:
        """Apply locally, send to every follower, and return the new version.

        Returning is the acknowledgement. Nothing waits for a follower, which is
        what "asynchronous" means and why the failover test says what it says.
        """
        raise NotImplementedError

    def read(self, key):
        raise NotImplementedError

    def receive(self, src: str, message) -> None:
        """A leader in this lab has nothing to receive."""
        raise NotImplementedError


def build(
    sim: Simulation,
    followers: int = 2,
    latency_ms=(10, 40),
    loss: float = 0.0,
) -> tuple[Network, Leader, list[Follower]]:
    """A network, one leader, and `followers` followers, all wired up."""
    raise NotImplementedError


def entries_behind(leader: Leader, follower: Follower) -> int:
    """How many writes this follower has not applied yet."""
    raise NotImplementedError


def lag_ms(sim: Simulation, leader: Leader, follower: Follower) -> int:
    """How old the oldest missing write is, in milliseconds. 0 when caught up.

    Time, not entries. "Four entries behind" means nothing without knowing the
    write rate; "1,900 ms behind" is directly comparable to the freshness line in
    an envelope.
    """
    raise NotImplementedError


def most_current(followers: list[Follower]) -> Follower:
    """The follower with the highest applied version — the one to promote.

    Break ties by name, so the choice is deterministic.
    """
    raise NotImplementedError


def acknowledged_writes_lost(leader: Leader, promoted: Follower) -> int:
    """How many writes the leader acknowledged that the new leader has never seen.

    In an asynchronous system this is routinely above zero, and it is not a bug.
    It is the thing you bought when you chose not to wait.
    """
    raise NotImplementedError
