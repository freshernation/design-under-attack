"""A deterministic harness for systems that are allowed to fail.

    from simlib import Simulation, Network, Node

Time is simulated milliseconds. Randomness comes from one seeded generator. The
same seed produces the same trace every time, which is what turns "flaky
distributed test" back into "bug".
"""

from simlib.network import Network
from simlib.node import Node
from simlib.sim import Simulation

__all__ = ["Simulation", "Network", "Node"]
