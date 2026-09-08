"""Choosing a transport with arithmetic instead of preference.

Replace each `raise NotImplementedError` with your own code.
"""

import math


def polling_qps(clients: int, interval_s: float) -> float:
    """Requests per second from clients polling on a fixed interval.

    Note what is missing from this formula: **how much is actually happening.**
    The load is identical on a quiet Sunday and during an incident, which is the
    whole problem with polling and the whole appeal of it.
    """
    raise NotImplementedError


def push_qps(events_per_second: float) -> float:
    """Deliveries per second under push. Scales with events, not with clients."""
    raise NotImplementedError


def wasted_fraction(clients: int, interval_s: float, events_per_second: float) -> float:
    """The share of polls that return nothing, to four decimals.

    Assume every event is one client's, so at most `events_per_second` polls per
    second can be useful. Clamped to [0, 1] — a poll rate below the event rate
    wastes nothing, it just delivers late.
    """
    raise NotImplementedError


def connection_memory_bytes(connections: int, bytes_each: int) -> int:
    """At a million connections, every kilobyte each is a gigabyte of RAM.

    Worth computing before deciding what per-connection state to keep, because the
    application's share is usually the largest and is the part you control.
    """
    raise NotImplementedError


def servers_needed(connections: int, per_server: int, target_utilisation: float = 1.0) -> int:
    """Hosts for a connection count, at a utilisation target. Rounded up.

    Week 2's target, arriving in a capacity plan. Sizing a connection tier at 100%
    means one host failing takes the rest past the knee.
    """
    raise NotImplementedError


def reconnect_rate(connections: int, window_s: float) -> float:
    """Reconnections per second when `connections` clients come back over a window.

    Run it for a window of 1 second and of 60. The two answers are three orders of
    magnitude apart, and the only difference is jitter on the client.
    """
    raise NotImplementedError
