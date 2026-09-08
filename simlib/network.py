"""A network that is allowed to misbehave.

The default network in most people's heads delivers every message, instantly, in
order. Designs built on that assumption fail in production for reasons their author
finds mysterious. This one has latency, jitter, loss and partitions, and it does not
promise ordering — because none of the real ones do either.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:  # pragma: no cover
    from simlib.node import Node
    from simlib.sim import Simulation


class Network:
    """Carries messages between nodes, with configurable unpleasantness.

    latency_ms
        Either a fixed delay, or `(low, high)` for uniform jitter. Jitter is what
        makes messages arrive out of order, so `(low, high)` is the honest default
        for anything you intend to trust.
    loss
        Probability in [0, 1] that a message is silently dropped.
    """

    def __init__(
        self,
        sim: "Simulation",
        latency_ms: int | tuple[int, int] = (10, 40),
        loss: float = 0.0,
    ) -> None:
        self.sim = sim
        self.latency_ms = latency_ms
        self.loss = loss
        self.nodes: dict[str, "Node"] = {}
        self._partitions: list[set[str]] = []
        self.delivered = 0
        self.dropped = 0

    # -- wiring ---------------------------------------------------------------

    def add(self, node: "Node") -> "Node":
        if node.name in self.nodes:
            raise ValueError(f"duplicate node name {node.name!r}")
        self.nodes[node.name] = node
        node.network = self
        return node

    # -- faults ---------------------------------------------------------------

    def partition(self, *groups: Iterable[str]) -> None:
        """Split the network. Messages between groups are dropped; messages
        inside a group still flow, which is exactly what makes split brain
        possible."""
        self._partitions = [set(group) for group in groups]

    def heal(self) -> None:
        """Reconnect everything. Messages dropped during the partition stay
        dropped — healing is not delivery."""
        self._partitions = []

    def _reachable(self, src: str, dst: str) -> bool:
        if not self._partitions:
            return True
        for group in self._partitions:
            if src in group:
                return dst in group
        return True

    # -- delivery -------------------------------------------------------------

    def _delay(self) -> int:
        if isinstance(self.latency_ms, tuple):
            low, high = self.latency_ms
            return self.sim.random.randint(low, high)
        return int(self.latency_ms)

    def send(self, src: str, dst: str, message: object) -> None:
        """Hand a message to the network. It may arrive late, out of order, or
        never. There is no delivery receipt, because there isn't one in real life."""
        if dst not in self.nodes:
            raise KeyError(f"no node named {dst!r}")

        if not self._reachable(src, dst) or self.sim.random.random() < self.loss:
            self.dropped += 1
            self.sim.record(f"DROP  {src} -> {dst}  {message!r}")
            return

        delay = self._delay()
        self.sim.record(f"SEND  {src} -> {dst}  {message!r}  (+{delay}ms)")

        def deliver() -> None:
            node = self.nodes[dst]
            if node.crashed:
                self.dropped += 1
                self.sim.record(f"LOST  {src} -> {dst}  ({dst} is down)")
                return
            self.delivered += 1
            self.sim.record(f"RECV  {dst} <- {src}  {message!r}")
            node.receive(src, message)

        self.sim.schedule(delay, deliver, label=f"{src}->{dst}")
