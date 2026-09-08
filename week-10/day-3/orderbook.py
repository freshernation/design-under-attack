"""A matching engine, where reproducibility is the requirement.

Nothing here reads a clock, iterates a set, or calls a random number generator.
That is not fastidiousness — a disputed trade is settled by replaying the log, and
a replay that can produce a different answer settles nothing.

Replace each `raise NotImplementedError` with your own code.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: str
    side: str          # "buy" or "sell"
    price: float
    quantity: int
    sequence: int      # assigned by the sequencer, and the only notion of time


@dataclass(frozen=True)
class Fill:
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: int


def sequence(orders: list[Order], arrival_times: list[float], tie_break: str = "id") -> list[Order]:
    """Assign sequence numbers by arrival time, and return the ordered orders.

    Two orders can arrive at the same instant, and **a stated tie-break rule is the
    difference between deterministic and not.** `"id"` breaks ties by order id;
    anything else raises, because there is no sensible default.

    Raises ValueError when the lists differ in length.
    """
    raise NotImplementedError


class OrderBook:
    """Price, then time.

        book = OrderBook()
        fills = book.add(Order("o1", "buy", 100.05, 500, sequence=1))

    Bids rest highest-first, asks lowest-first, and among equal prices the lower
    sequence number fills first. A new order matches against the other side while
    the prices cross; whatever is left rests in the book.
    """

    def __init__(self) -> None:
        """Two lists — `bids` and `asks` — kept sorted. Lists rather than
        dictionaries so that iteration order is a property of the data rather than
        of the runtime."""
        raise NotImplementedError

    def add(self, order: Order) -> list[Fill]:
        """Match, then rest the remainder. Returns the fills in the order they
        happened.

        A fill happens **at the resting order's price**, not the incoming one —
        the order already in the book set the terms, and the arriving order
        accepted them.
        """
        raise NotImplementedError

    def cancel(self, order_id: str) -> bool:
        """Remove a resting order. False if it is not there — it may have filled
        already, and a cancel racing a fill is the normal case rather than an
        error."""
        raise NotImplementedError

    @property
    def best_bid(self) -> float | None:
        raise NotImplementedError

    @property
    def best_ask(self) -> float | None:
        raise NotImplementedError

    @property
    def spread(self) -> float | None:
        """None when either side is empty."""
        raise NotImplementedError

    def depth(self, side: str) -> int:
        """Total resting quantity on a side."""
        raise NotImplementedError


def replay(orders: list[Order]) -> list[Fill]:
    """Run a sequence of orders through a fresh book and return every fill.

    Called twice with the same input, this must return exactly the same list —
    which is the requirement the whole design exists to satisfy, and the test that
    proves it.
    """
    raise NotImplementedError
