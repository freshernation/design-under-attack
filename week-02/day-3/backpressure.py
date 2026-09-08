"""A bounded queue, and what actually happens when it fills.

This is the first lab that runs on `simlib`. Time is simulated milliseconds, so a
ten-second workload runs instantly and identically every time.

Replace each `raise NotImplementedError` with your own code.
"""

from collections import deque

from simlib import Simulation

POLICIES = ("reject", "drop_oldest", "grow")


class BoundedQueue:
    """A queue with a bound and a stated policy for what happens at that bound.

    `grow` is the default in most languages and is included here so you can watch
    what it costs, not because it is a good idea.
    """

    def __init__(self, sim: Simulation, capacity: int, policy: str = "reject") -> None:
        """Raises ValueError for an unknown policy or a capacity below 1."""
        raise NotImplementedError

    def offer(self, item) -> bool:
        """Add an item. Returns whether it was accepted.

        Under `reject`, a full queue refuses and counts a rejection. Under
        `drop_oldest`, it evicts the front, counts a drop, and accepts. Under
        `grow`, capacity is ignored.

        Store the time each item was enqueued — `oldest_age_ms` needs it.
        """
        raise NotImplementedError

    def poll(self):
        """The front item as `(item, enqueued_at_ms)`, or None when empty."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def oldest_age_ms(self) -> int:
        """How long the front item has been waiting. 0 when empty.

        This, not depth, is the metric that tells you a queue is losing.
        """
        raise NotImplementedError


def run_workload(
    arrival_rate: float,
    service_rate: float,
    duration_s: float,
    capacity: int = 100,
    policy: str = "reject",
) -> dict:
    """Run a producer and a consumer against one queue, and report what happened.

    Arrivals are evenly spaced at `1000 / arrival_rate` ms, and the consumer takes
    `1000 / service_rate` ms per item. No randomness — the point here is the
    structure, not the statistics.

    Build it like this:

    * schedule every arrival up front with `sim.schedule`
    * a `consume` callback that polls, and reschedules itself after the service
      time; when the queue is empty, it reschedules 1 ms later and tries again
    * a `sample` callback every 10 ms that records the peak depth and peak age
    * `sim.run(until_ms=duration_s * 1000)` — the consumer never stops on its own,
      so the horizon is what ends the run

    Returns a dict with: served (the list of item ids), served_count, accepted,
    rejected, dropped, peak_depth, peak_age_ms, final_depth.
    """
    raise NotImplementedError
