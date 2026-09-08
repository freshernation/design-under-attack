"""Raft leader election, on a network that drops messages and can be cut in two.

This is Raft §5.2, plus the practical extension that a leader which cannot reach
a majority steps down. Log replication is not here — election is the part that
carries the safety argument, and it is the part you will be asked about.

Replace each `raise NotImplementedError` with your own code.
"""

from simlib import Network, Node, Simulation


class RaftNode(Node):
    """A follower, candidate, or leader.

    Messages, all tuples:

        ("request_vote", term, candidate)
        ("vote", term, granted)
        ("heartbeat", term, leader)
        ("heartbeat_ack", term)

    Keep `leader_terms`, the set of terms in which *this* node became leader. The
    safety test collects them across the cluster and asserts no term has two names
    in it. That set is the guarantee, written down.
    """

    def __init__(
        self,
        name: str,
        sim: Simulation,
        peers: list[str],
        tick_ms: int = 10,
        heartbeat_ms: int = 50,
        election_timeout_ms: tuple[int, int] = (150, 300),
    ) -> None:
        """State starts as `"follower"`, term 0, nobody voted for.

        Draw the election timeout from `sim.random`, not the global `random` —
        the run has to be reproducible.
        """
        raise NotImplementedError

    @property
    def cluster_size(self) -> int:
        raise NotImplementedError

    @property
    def majority(self) -> int:
        """More than half. Five nodes need three; six also need four, which is why
        an even cluster size buys nothing."""
        raise NotImplementedError

    def start(self) -> None:
        """Begin ticking."""
        raise NotImplementedError

    def _tick(self) -> None:
        """Every `tick_ms`:

        * a **leader** sends heartbeats every `heartbeat_ms`, and steps down if
          fewer than a majority have acknowledged one within an election timeout
          (give it one timeout's grace after being elected)
        * anyone **else** starts an election if nothing has been heard from a
          leader within its election timeout

        Then reschedule. A crashed node's timers do not fire — `simlib` handles
        that — so a crash needs no special case here.
        """
        raise NotImplementedError

    def _start_election(self) -> None:
        """Increment the term, become a candidate, vote for yourself, **draw a new
        random timeout**, and ask everyone for a vote.

        The new random timeout is what breaks a split vote. Three candidates that
        all time out together will keep doing so unless something separates them,
        and there is no cleverer fix than randomness.
        """
        raise NotImplementedError

    def _become_leader(self) -> None:
        """Record the term in `leader_terms` and heartbeat immediately — a new
        leader that waits for its first heartbeat interval invites a rival."""
        raise NotImplementedError

    def receive(self, src: str, message) -> None:
        """The four message kinds.

        The rule that carries the whole safety argument: **a node votes at most
        once per term.** A higher term always wins and resets the vote; an equal
        term is granted only if this node has not already voted for somebody else.
        """
        raise NotImplementedError


def build_cluster(
    sim: Simulation,
    n: int = 5,
    latency_ms=(10, 30),
    loss: float = 0.0,
    **node_kwargs,
) -> tuple[Network, list[RaftNode]]:
    """`n` nodes on one network, named `n0`..., all started."""
    raise NotImplementedError


def current_leaders(nodes: list[RaftNode]) -> list[RaftNode]:
    """Nodes that believe they are leader right now and are not crashed.

    More than one is not necessarily a violation — they may be in different terms,
    which is exactly what happens for a moment after a partition heals.
    """
    raise NotImplementedError


def leader_terms(nodes: list[RaftNode]) -> dict[int, set[str]]:
    """Every term any node was ever leader in, and who."""
    raise NotImplementedError


def split_brain_terms(nodes: list[RaftNode]) -> dict[int, set[str]]:
    """Terms with more than one leader. **This must always be empty.**"""
    raise NotImplementedError
