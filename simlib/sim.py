"""The clock and the event queue.

Everything in this harness happens at an integer millisecond, decided by a priority
queue rather than by the wall clock. Two consequences, and they are the entire reason
the harness exists:

* A test that involves a three-second timeout runs in microseconds.
* The same seed always produces the same trace, so a failing distributed test is a
  bug you can reproduce rather than a mood the machine was in.
"""

from __future__ import annotations

import heapq
import random
from dataclasses import dataclass, field
from typing import Callable


@dataclass(order=True)
class _Event:
    at: int
    seq: int
    action: Callable[[], None] = field(compare=False)
    label: str = field(compare=False, default="")


class Simulation:
    """A virtual clock with a queue of things to do.

    Time is in **milliseconds since the simulation started**, always an integer.
    Ties are broken by insertion order, never by chance, which is what makes runs
    reproducible.
    """

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.random = random.Random(seed)
        self._time = 0
        self._seq = 0
        self._queue: list[_Event] = []
        self.trace: list[tuple[int, str]] = []

    @property
    def now(self) -> int:
        """Milliseconds since the simulation started."""
        return self._time

    def schedule(self, delay_ms: int, action: Callable[[], None], label: str = "") -> None:
        """Run `action` after `delay_ms` of simulated time."""
        if delay_ms < 0:
            raise ValueError("cannot schedule into the past")
        self._seq += 1
        heapq.heappush(self._queue, _Event(self._time + int(delay_ms), self._seq, action, label))

    def record(self, note: str) -> None:
        """Append a line to the trace. Cheap, and the first thing to reach for
        when a test fails for reasons you cannot see."""
        self.trace.append((self._time, note))

    def run(self, until_ms: int | None = None) -> int:
        """Fire every event in time order. Returns the time at the end.

        With `until_ms`, stops at that time and leaves later events queued — which
        is how you inspect a system mid-flight.
        """
        while self._queue:
            if until_ms is not None and self._queue[0].at > until_ms:
                break
            event = heapq.heappop(self._queue)
            self._time = event.at
            event.action()

        if until_ms is not None:
            self._time = max(self._time, until_ms)
        return self._time

    def print_trace(self) -> None:
        for at, note in self.trace:
            print(f"{at:>8} ms  {note}")
