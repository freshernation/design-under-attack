"""A participant. Something that receives messages, keeps state, and can die."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:  # pragma: no cover
    from simlib.network import Network
    from simlib.sim import Simulation


class Node:
    """Subclass this and override `receive`.

    A crashed node delivers nothing and fires no timers. What survives a restart is
    whatever you chose to treat as durable — the harness deliberately does not decide
    that for you, because deciding it is the exercise.
    """

    def __init__(self, name: str, sim: "Simulation") -> None:
        self.name = name
        self.sim = sim
        self.network: "Network" | None = None
        self.crashed = False

    # -- messaging ------------------------------------------------------------

    def send(self, dst: str, message: object) -> None:
        if self.crashed:
            return
        if self.network is None:
            raise RuntimeError(f"{self.name} is not on a network")
        self.network.send(self.name, dst, message)

    def receive(self, src: str, message: object) -> None:
        """Called when a message arrives. Override this."""
        raise NotImplementedError

    # -- time -----------------------------------------------------------------

    def set_timer(self, delay_ms: int, action: Callable[[], None]) -> None:
        """Run `action` later, unless this node is down when the moment comes."""

        def fire() -> None:
            if not self.crashed:
                action()

        self.sim.schedule(delay_ms, fire, label=f"timer:{self.name}")

    # -- faults ---------------------------------------------------------------

    def crash(self) -> None:
        self.crashed = True
        self.sim.record(f"CRASH {self.name}")

    def restart(self) -> None:
        self.crashed = False
        self.sim.record(f"START {self.name}")
