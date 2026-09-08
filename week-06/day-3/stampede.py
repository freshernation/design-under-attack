"""Coalescing, jitter, early refresh, and caching an absence.

On `simlib`, because concurrency is the whole subject — the requests have to
genuinely overlap in simulated time for any of this to mean anything.

Replace each `raise NotImplementedError` with your own code.
"""

import math

from simlib import Simulation


class SingleFlight:
    """One in-flight load per key. Everybody else waits for its result.

        flight = SingleFlight(sim)
        flight.do("k", loader, on_done, load_ms=40)

    `loader()` produces the value; `on_done(value)` is called for **every** caller,
    including the one that triggered the load. The origin sees one request.

    Twenty lines, no extra infrastructure, and it generalises far beyond caches —
    a config fetch, a token refresh, a schema lookup. Anywhere many callers want
    the same expensive thing at the same instant.
    """

    def __init__(self, sim: Simulation) -> None:
        """Track waiters per key, and count `loads` — the number of times the
        loader actually ran."""
        raise NotImplementedError

    def do(self, key, loader, on_done, load_ms: int) -> None:
        """If a load for `key` is already in flight, add `on_done` to its waiters.

        Otherwise start one: schedule the loader to complete in `load_ms`, and when
        it does, call every waiter with the result and clear the key.
        """
        raise NotImplementedError

    @property
    def in_flight(self) -> int:
        raise NotImplementedError


def jittered_ttl(base_ms: int, fraction: float, rng) -> int:
    """A TTL scattered by ±`fraction`, using the simulation's `rng`.

    Ten thousand entries written together with the same TTL expire together. Add
    jitter and the cliff becomes a slope.

    The rule, for the rest of the course: **anything scheduled to happen at the
    same moment for many things needs jitter.** Retries, renewals, TTLs, crons,
    health checks. Without it you have built a synchroniser.
    """
    raise NotImplementedError


def should_refresh_early(
    now_ms: int, expires_at_ms: int, recompute_ms: int, beta: float, rng
) -> bool:
    """Probabilistic early recomputation.

    Refresh when `now - recompute_ms * beta * log(random()) >= expires_at`.

    `log(random())` is negative, so the term grows the closer you get to expiry
    and the longer the recompute takes. Most callers keep using the cached value;
    one refreshes early; nobody ever sees a miss.

    You are not required to derive this — it is from the VLDB paper in the article.
    You are required to know that "refresh a bit early, randomly, so exactly one of
    us does it" is a real technique with a proof behind it.
    """
    raise NotImplementedError


class NegativeCache:
    """Remember that something does not exist, briefly.

    A request for a key with no value costs a full origin lookup and caches
    nothing, so the next identical request does it again. Point a scraper at
    random ids and every request reaches your database.

    The TTL must be **short**, because "does not exist" becomes wrong the moment
    somebody creates it.
    """

    def __init__(self, sim: Simulation, ttl_ms: int = 30_000) -> None:
        raise NotImplementedError

    def mark_absent(self, key) -> None:
        raise NotImplementedError

    def known_absent(self, key) -> bool:
        raise NotImplementedError

    def forget(self, key) -> None:
        """Called when the thing is created. Without this, a newly created object
        is invisible for the length of the negative TTL."""
        raise NotImplementedError
