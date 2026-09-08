"""When is a specialised mechanism worth its cost?

The week's real question, and the one that stops a specialised design becoming an
enthusiasm.

Replace each `raise NotImplementedError` with your own code.
"""

import math


def binding_constraint(usage: dict[str, tuple[float, float]]) -> str:
    """The resource closest to its limit — `{name: (used, capacity)}`.

    It is frequently not the one the brief emphasises. A dispatch system talks
    about query latency and is bound by position-update write throughput; an
    inference service talks about compute and is bound by memory.

    Ties break by name, so the answer is deterministic. Raises ValueError for an
    empty map or a non-positive capacity.
    """
    raise NotImplementedError


def headroom(usage: dict[str, tuple[float, float]]) -> dict[str, float]:
    """The unused fraction of each resource, to four decimals. Negative when a
    resource is already over its limit, which is worth reporting rather than
    clamping."""
    raise NotImplementedError


def headroom_months(used: float, capacity: float, monthly_growth: float) -> float:
    """Months until this resource is exhausted, to one decimal.

    Compound growth, so `log(capacity/used) / log(1 + growth)`.

    **When** you need the specialised mechanism is as much a design output as
    whether. Eighteen months of headroom and a six-month build is a different
    decision from three months of headroom and the same build.

    Returns `float("inf")` for zero or negative growth. Raises ValueError for
    non-positive usage or capacity.
    """
    raise NotImplementedError


def break_even_volume(
    general_unit_cost: float, specialised_unit_cost: float, specialised_fixed_cost: float
) -> float:
    """The volume above which the specialised mechanism is cheaper, to one decimal.

    `fixed / (general_unit - specialised_unit)`.

    Returns `float("inf")` when the specialised mechanism is not cheaper per unit —
    which happens, and is the most useful answer this function gives: no volume
    justifies it, and the decision is over.
    """
    raise NotImplementedError


def is_worth_it(
    volume: float,
    general_unit_cost: float,
    specialised_unit_cost: float,
    specialised_fixed_cost: float,
) -> bool:
    """Whether you are past the break-even volume."""
    raise NotImplementedError


def total_cost(
    volume: float, unit_cost: float, fixed_cost: float = 0.0
) -> float:
    """Fixed plus variable, to two decimals — so both sides can be compared on one
    scale rather than argued about."""
    raise NotImplementedError
