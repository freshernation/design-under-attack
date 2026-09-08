"""Data types that converge, whatever order the updates arrive in.

Replace each `raise NotImplementedError` with your own code.
"""


class GCounter:
    """A counter that only goes up. One count per node; the value is their sum.

    Merging takes the **maximum** per node rather than adding, which is what makes
    merging idempotent — merging the same state twice must not double anything.
    """

    def __init__(self, node: str) -> None:
        raise NotImplementedError

    def increment(self, amount: int = 1) -> None:
        """Raises ValueError for a negative amount — that is what PNCounter is for."""
        raise NotImplementedError

    @property
    def value(self) -> int:
        raise NotImplementedError

    def merge(self, other: "GCounter") -> None:
        raise NotImplementedError


class PNCounter:
    """Up and down, as two G-counters. The value is increments minus decrements."""

    def __init__(self, node: str) -> None:
        raise NotImplementedError

    def increment(self, amount: int = 1) -> None:
        raise NotImplementedError

    def decrement(self, amount: int = 1) -> None:
        raise NotImplementedError

    @property
    def value(self) -> int:
        raise NotImplementedError

    def merge(self, other: "PNCounter") -> None:
        raise NotImplementedError


class TwoPhaseSet:
    """Add and remove, with one hard rule: **a removed element can never return.**

    Removal is recorded as a tombstone, and a later add of the same element is
    ignored. That is not a bug to work around — without it, an add and a remove
    arriving in different orders on two replicas would leave them disagreeing, and
    there would be no way to decide which is right.

    It is also why this type is so often the wrong choice, and knowing that is the
    point of implementing it.
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def add(self, element) -> None:
        raise NotImplementedError

    def remove(self, element) -> None:
        raise NotImplementedError

    def __contains__(self, element) -> bool:
        raise NotImplementedError

    def elements(self) -> set:
        raise NotImplementedError

    def merge(self, other: "TwoPhaseSet") -> None:
        raise NotImplementedError


class LWWRegister:
    """One value, last writer wins — with a **causal** clock rather than wall time.

    The clock is `(counter, node)`. A writer sets its counter above every counter
    it has seen, so "later" means "knew about the earlier one" rather than "had a
    faster clock". Week 5's clock-skew problem, avoided rather than tolerated.

    Ties on the counter are broken by node name, so the result is deterministic.
    """

    def __init__(self, node: str) -> None:
        raise NotImplementedError

    def set(self, value) -> None:
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError

    def merge(self, other: "LWWRegister") -> None:
        raise NotImplementedError


class RGA:
    """A sequence CRDT: text that converges without a central server.

    Every character has a unique id and is inserted **after** another id, rather
    than at a position. An insert stays meaningful however many other operations
    arrive first, which is why there is nothing to transform.

    Materialising the text:

    * group elements by the id they were inserted after
    * sort each group by id, **descending**, so a later insert at the same point
      comes first
    * walk depth-first from the root (`None`)

    Deletes are tombstones — the element stays and stops being rendered.
    """

    def __init__(self, node: str) -> None:
        raise NotImplementedError

    def _next_id(self) -> tuple[int, str]:
        """`(counter, node)`, with the counter above anything seen. Comparable, so
        the ordering rule above is total."""
        raise NotImplementedError

    def insert_after(self, after_id, char: str):
        """Insert `char` after `after_id` — `None` means at the start. Returns the
        new element's id."""
        raise NotImplementedError

    def delete(self, element_id) -> None:
        raise NotImplementedError

    def text(self) -> str:
        raise NotImplementedError

    def merge(self, other: "RGA") -> None:
        """Union the elements and the tombstones, and take the higher counter.

        No transformation, no ordering requirement, no server. **That is the whole
        claim of the family**, and the convergence test is what proves it.
        """
        raise NotImplementedError
