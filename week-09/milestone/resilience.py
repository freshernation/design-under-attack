"""Turning "we added a circuit breaker" into a number.

Composes the three days of this week into one incident model. Every formula here is
**stipulated** — it is a model for comparing designs, not a prediction. The tests
assert the direction of each effect and never its magnitude.

Replace each `raise NotImplementedError` with your own code.
"""

from dataclasses import dataclass


@dataclass
class Protections:
    """What the design has. All off by default, which is where most reviews start."""

    retry_budget: bool = False
    breaker: bool = False
    bulkhead: bool = False
    shedding: bool = False


def effective_offered(
    offered_qps: float, retries: int, has_retry_budget: bool, budget_ratio: float = 0.1
) -> float:
    """Load actually arriving once clients start retrying, to two decimals.

    Without a budget, `retries` extra attempts per request multiply the offered
    load — during an outage, when everything fails, by `1 + retries`.

    With a budget, retries are capped at `budget_ratio` of requests however many
    are failing, so the multiplier is `1 + budget_ratio` regardless.

    That is the whole value of a retry budget: it converts an unbounded multiplier
    into a bounded one, at the moment the multiplier matters.

    With `retries` of zero there is no amplification at all, budget or not — a
    system in which nothing is failing pays nothing for its retry policy.
    """
    raise NotImplementedError


def effective_capacity(
    base_capacity_qps: float,
    dependency_failing: bool,
    dependent_fraction: float,
    has_breaker: bool,
    has_bulkhead: bool,
) -> float:
    """Capacity while a dependency is degraded, to two decimals.

    The model:

    * healthy — full capacity
    * failing, **no protection** — the slow dependency's calls occupy the shared
      pool, so capacity collapses to 20% of base. Requests that never touch the
      dependency queue behind ones that do
    * failing, **breaker** — those calls fail instantly instead of waiting, so the
      only work lost is the dependent fraction: `base × (1 - dependent_fraction)`
    * failing, **bulkhead** — the dependency has its own pool, so the same result
      by a different mechanism
    * failing, **both** — the same again. They overlap, which is worth knowing
      before adding both

    Raises ValueError for a dependent fraction outside [0, 1].
    """
    raise NotImplementedError


def incident_goodput(offered_qps: float, capacity_qps: float, has_shedding: bool) -> float:
    """Useful work, to two decimals.

    Without shedding, overload wastes work: `capacity / overload²`, week 9 day 4's
    model. With shedding, everything accepted is served: `min(offered, capacity)`.
    """
    raise NotImplementedError


def run_incident(
    offered_qps: float,
    base_capacity_qps: float,
    dependency_failing: bool,
    dependent_fraction: float,
    protections: Protections,
    retries: int = 2,
) -> dict:
    """The three functions composed.

    Returns `{"offered": ..., "capacity": ..., "goodput": ...}`.

    **Clients only retry when requests fail**, so pass `retries` through only when
    `dependency_failing` is true. A healthy system pays nothing for having a retry
    policy, which is exactly why the policy is so easy to overlook until an
    incident.

    Run it with everything off, then turn the protections on one at a time. **The
    order in which they help is not the order people add them**, and that is the
    finding this lab exists to produce.
    """
    raise NotImplementedError
