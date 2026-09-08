"""Can this index serve this query?

The rules are not quirks of any one database — they follow from what an ordering is,
so they hold for a B-tree index, a clustering key, and a sorted file you wrote.

Replace each `raise NotImplementedError` with your own code.
"""


def can_serve(
    index: list[str],
    equalities: set[str] | list[str],
    range_column: str | None = None,
    order_by: list[str] | None = None,
) -> bool:
    """Whether `index` answers this query without a scan.

    The rule, in order:

    1. The first `len(equalities)` index columns must be exactly the equality
       columns — as a set, since order among equality columns does not matter.
    2. After those, the range column must come next, if there is one.
    3. Then the order-by columns, in order, immediately after.

    A simplification worth knowing you made: real planners handle more cases than
    this (index-merge, skip scans, backwards scans). This is the leftmost-prefix
    rule, which is the part that transfers.
    """
    raise NotImplementedError


def is_covering(index: list[str], selected: list[str]) -> bool:
    """Whether every column the query returns is in the index, so the row itself
    is never read."""
    raise NotImplementedError


def selectivity(distinct_values: int, rows: int) -> float:
    """Distinct values over rows. 1.0 is unique; near zero narrows nothing.

    Raises ValueError for zero or fewer rows.
    """
    raise NotImplementedError


def write_amplification(index_count: int) -> int:
    """Structures touched by one insert: the table, plus every index."""
    raise NotImplementedError
