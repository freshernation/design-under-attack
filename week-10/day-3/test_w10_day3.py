"""Day 3 — the matching engine.

`test_a_replay_produces_exactly_the_same_fills` is the requirement. Everything
else is the machinery that makes it possible.
"""

import pytest

from orderbook import Fill, Order, OrderBook, replay, sequence


def buy(order_id, price, quantity, seq):
    return Order(order_id, "buy", price, quantity, seq)


def sell(order_id, price, quantity, seq):
    return Order(order_id, "sell", price, quantity, seq)


# -- resting ------------------------------------------------------------------


def test_an_uncrossed_order_rests():
    book = OrderBook()
    assert book.add(buy("a", 100.05, 500, 1)) == []
    assert book.best_bid == 100.05
    assert book.depth("buy") == 500


def test_bids_rest_highest_first():
    book = OrderBook()
    book.add(buy("a", 100.04, 100, 1))
    book.add(buy("b", 100.06, 100, 2))
    assert book.best_bid == 100.06


def test_asks_rest_lowest_first():
    book = OrderBook()
    book.add(sell("a", 100.08, 100, 1))
    book.add(sell("b", 100.06, 100, 2))
    assert book.best_ask == 100.06


def test_the_spread_needs_both_sides():
    book = OrderBook()
    assert book.spread is None
    book.add(buy("a", 100.05, 100, 1))
    assert book.spread is None
    book.add(sell("b", 100.06, 100, 2))
    assert book.spread == pytest.approx(0.01)


def test_an_unknown_side_is_an_error():
    with pytest.raises(ValueError):
        OrderBook().add(Order("a", "sideways", 100, 1, 1))


# -- matching -----------------------------------------------------------------


def test_a_crossing_order_fills():
    book = OrderBook()
    book.add(buy("a", 100.05, 500, 1))
    fills = book.add(sell("b", 100.05, 500, 2))

    assert fills == [Fill("a", "b", 100.05, 500)]
    assert book.depth("buy") == 0


def test_the_fill_happens_at_the_resting_price():
    """The order already in the book set the terms; the arriving order accepted
    them. A buyer willing to pay 100.10 against a resting ask of 100.06 pays
    100.06 — the price improvement belongs to whoever was there first."""
    book = OrderBook()
    book.add(sell("resting", 100.06, 100, 1))
    fills = book.add(buy("arriving", 100.10, 100, 2))
    assert fills[0].price == pytest.approx(100.06)


def test_price_beats_time():
    book = OrderBook()
    book.add(buy("early_but_low", 100.04, 100, 1))
    book.add(buy("late_but_high", 100.06, 100, 2))

    fills = book.add(sell("s", 100.00, 100, 3))
    assert fills[0].buy_order_id == "late_but_high"


def test_time_breaks_ties_on_price():
    """The rule the whole sequencer exists to make well-defined."""
    book = OrderBook()
    book.add(buy("first", 100.05, 100, 1))
    book.add(buy("second", 100.05, 100, 2))

    fills = book.add(sell("s", 100.05, 100, 3))
    assert fills[0].buy_order_id == "first"


def test_a_large_order_sweeps_several_levels():
    book = OrderBook()
    book.add(buy("a", 100.05, 500, 1))
    book.add(buy("b", 100.05, 200, 2))
    book.add(buy("c", 100.04, 900, 3))

    fills = book.add(sell("s", 100.05, 600, 4))
    assert [(f.buy_order_id, f.quantity) for f in fills] == [("a", 500), ("b", 100)]
    assert book.depth("buy") == 1_000, "b's remaining 100 and c's untouched 900"


def test_an_unfilled_remainder_rests():
    book = OrderBook()
    book.add(buy("a", 100.05, 100, 1))
    book.add(sell("s", 100.05, 400, 2))
    assert book.depth("sell") == 300


def test_a_non_crossing_order_does_not_fill():
    book = OrderBook()
    book.add(buy("a", 100.04, 100, 1))
    assert book.add(sell("s", 100.06, 100, 2)) == []


# -- cancelling ---------------------------------------------------------------


def test_cancelling_removes_a_resting_order():
    book = OrderBook()
    book.add(buy("a", 100.05, 100, 1))
    assert book.cancel("a") is True
    assert book.best_bid is None


def test_cancelling_something_already_filled_is_not_an_error():
    """A cancel racing a fill is the normal case, not an exception. The client
    sent it before it knew, and it is simply too late."""
    book = OrderBook()
    book.add(buy("a", 100.05, 100, 1))
    book.add(sell("s", 100.05, 100, 2))
    assert book.cancel("a") is False


# -- the sequencer ------------------------------------------------------------


def test_orders_are_numbered_by_arrival():
    orders = [buy("late", 100, 1, 0), buy("early", 100, 1, 0)]
    ordered = sequence(orders, arrival_times=[2.0, 1.0])
    assert [o.id for o in ordered] == ["early", "late"]
    assert [o.sequence for o in ordered] == [1, 2]


def test_simultaneous_arrivals_need_a_stated_rule():
    """Two orders at the same instant. Without a tie-break the result depends on
    list order, which depends on network arrival, which is not reproducible — and
    a replay that can produce a different answer settles no dispute."""
    orders = [buy("b", 100, 1, 0), buy("a", 100, 1, 0)]
    ordered = sequence(orders, arrival_times=[1.0, 1.0], tie_break="id")
    assert [o.id for o in ordered] == ["a", "b"]


def test_the_tie_break_must_be_named():
    """There is no sensible default, so there is no default."""
    with pytest.raises(ValueError):
        sequence([buy("a", 100, 1, 0)], [1.0], tie_break="whatever")


def test_every_order_needs_an_arrival_time():
    with pytest.raises(ValueError):
        sequence([buy("a", 100, 1, 0)], [])


# -- the requirement ----------------------------------------------------------

SCENARIO = [
    buy("a", 100.05, 500, 1),
    buy("b", 100.05, 200, 2),
    sell("c", 100.06, 300, 3),
    sell("d", 100.05, 600, 4),
    buy("e", 100.06, 400, 5),
    sell("f", 100.04, 1_000, 6),
]


def test_a_replay_produces_exactly_the_same_fills():
    """The requirement, and the reason for every constraint in this lab.

    Not approximately the same, not statistically the same — identical, including
    order. A disputed trade is settled by replaying the log, and if the replay can
    disagree with itself there is nothing to settle it with.

    Nothing in the matching path reads a clock, iterates a set, or draws a random
    number. That is what makes this pass.
    """
    assert replay(SCENARIO) == replay(SCENARIO)


def test_replay_is_stable_across_repetitions():
    results = [replay(SCENARIO) for _ in range(10)]
    assert all(r == results[0] for r in results)


def test_delivery_order_does_not_decide_who_fills_first():
    """The sequencer earning its keep.

    Orders a and b rest at the same price, so priority between them is decided by
    their **sequence numbers** rather than by which reached the matcher first. Swap
    their delivery order and the fills are identical.

    That is the property that makes the matcher's input a set rather than a stream:
    the ordering decision was made once, upstream, and written down.
    """
    reordered = [SCENARIO[1], SCENARIO[0]] + SCENARIO[2:]
    assert replay(reordered) == replay(SCENARIO)


def test_but_the_sequence_numbers_do():
    """Change what the sequencer decided, and it is a different market — with a
    different, equally correct, outcome. Which is why the tie-break rule is a
    stated policy rather than an implementation detail."""
    swapped = [
        buy("a", 100.05, 500, 2),      # a now sequenced second
        buy("b", 100.05, 200, 1),      # b first
    ] + SCENARIO[2:]

    first_fill_before = replay(SCENARIO)[0]
    first_fill_after = replay(swapped)[0]
    assert first_fill_before.buy_order_id != first_fill_after.buy_order_id


def test_replaying_nothing_produces_nothing():
    assert replay([]) == []
