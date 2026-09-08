"""Day 3 — idempotency and the outbox."""

import pytest

from idempotency import (
    Database,
    DedupWindow,
    IdempotencyConflict,
    IdempotencyStore,
    apply_absolute,
    apply_increment,
    dual_write,
    relay,
    window_bytes,
)
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


# -- operations that are already idempotent -----------------------------------


def test_an_absolute_assignment_survives_a_duplicate():
    state = {}
    apply_absolute(state, "status", "shipped")
    apply_absolute(state, "status", "shipped")
    assert state["status"] == "shipped"


def test_an_increment_does_not():
    """The whole difference between a safe operation and an unsafe one, and often
    restating it absolutely is the entire fix."""
    state = {}
    apply_increment(state, "balance", 10)
    apply_increment(state, "balance", 10)
    assert state["balance"] == 20


# -- idempotency keys ---------------------------------------------------------


def test_the_work_happens_once(sim):
    store = IdempotencyStore(sim)
    calls = []

    def charge():
        calls.append(1)
        return {"charge_id": "ch_1"}

    first = store.execute("req-1", {"amount": 500}, charge)
    second = store.execute("req-1", {"amount": 500}, charge)

    assert len(calls) == 1
    assert first == second == {"charge_id": "ch_1"}


def test_the_stored_result_comes_back_not_just_a_flag(sim):
    """The retrying client wants the answer it missed, not the news that somebody
    else already has it."""
    store = IdempotencyStore(sim)
    store.execute("req-1", {"amount": 500}, lambda: {"charge_id": "ch_1"})
    assert store.execute("req-1", {"amount": 500}, lambda: {"never": "runs"}) == {
        "charge_id": "ch_1"
    }


def test_a_different_payload_on_the_same_key_is_an_error(sim):
    """Two different operations claiming to be the same one. Returning the first
    result silently would hide a real bug."""
    store = IdempotencyStore(sim)
    store.execute("req-1", {"amount": 500}, lambda: "ok")
    with pytest.raises(IdempotencyConflict):
        store.execute("req-1", {"amount": 50_000}, lambda: "ok")


def test_different_keys_do_different_work(sim):
    store = IdempotencyStore(sim)
    calls = []
    for key in ("a", "b", "c"):
        store.execute(key, {}, lambda: calls.append(1))
    assert len(calls) == 3


def test_keys_expire(sim):
    """A retry after the window is a new operation, which is why the window must
    exceed the longest plausible retry — including a human retrying tomorrow."""
    store = IdempotencyStore(sim, ttl_ms=1_000)
    calls = []
    store.execute("req-1", {}, lambda: calls.append(1))

    advance(sim, 1_001)
    store.execute("req-1", {}, lambda: calls.append(1))
    assert len(calls) == 2


def test_a_store_needs_a_window(sim):
    with pytest.raises(ValueError):
        IdempotencyStore(sim, ttl_ms=0)


# -- deduplication ------------------------------------------------------------


def test_a_repeat_inside_the_window_is_caught(sim):
    window = DedupWindow(sim, window_ms=60_000)
    assert window.seen("evt-1") is False
    assert window.seen("evt-1") is True


def test_a_repeat_outside_the_window_is_not(sim):
    window = DedupWindow(sim, window_ms=60_000)
    window.seen("evt-1")
    advance(sim, 60_001)
    assert window.seen("evt-1") is False


def test_the_window_is_the_memory(sim):
    window = DedupWindow(sim, window_ms=10_000)
    for i in range(100):
        window.seen(f"evt-{i}")
    assert len(window) == 100

    advance(sim, 10_001)
    assert len(window) == 0


def test_the_replay_depth_decides_the_window_size():
    """Deliberate replay is the duplicate source people forget, and it is the one
    that sets the number. 500,000 events a second over 24 hours is 43 billion ids
    and 690 GB — which is where week 6's membership filter comes back.
    """
    an_hour = window_bytes(500_000, 3_600)
    a_day = window_bytes(500_000, 86_400)
    assert an_hour == pytest.approx(28.8e9, rel=0.01)
    assert a_day == pytest.approx(691e9, rel=0.01)


def test_a_modest_rate_fits_in_memory():
    assert window_bytes(1_000, 3_600) < 100e6


# -- the dual write -----------------------------------------------------------


def test_a_crash_between_two_writes_leaves_one_done():
    """The order exists and nobody was told. No email, no fulfilment, no
    analytics, and the row sits there looking perfectly fine."""
    database = Database()
    published: list = []

    dual_write(database, published, row="order-1", event="OrderCreated:1", crash_between=True)

    assert database.rows == ["order-1"]
    assert published == []


def test_without_a_crash_it_looks_fine():
    """Which is why this ships."""
    database = Database()
    published: list = []
    dual_write(database, published, "order-1", "OrderCreated:1", crash_between=False)
    assert database.rows and published


# -- the outbox ---------------------------------------------------------------


def test_both_rows_commit_together():
    database = Database()
    database.insert_with_outbox("order-1", "OrderCreated:1")
    assert database.rows == ["order-1"]
    assert database.unsent_events() == ["OrderCreated:1"]


def test_the_relay_publishes_and_marks():
    database = Database()
    published: list = []
    database.insert_with_outbox("order-1", "OrderCreated:1")

    assert relay(database, published) == 1
    assert published == ["OrderCreated:1"]
    assert database.unsent_events() == []


def test_a_relay_crash_duplicates_rather_than_loses():
    """The trade, as an assertion.

    The relay published and died before marking, so the next run publishes again.
    The outbox has converted "an event may be lost" into "an event may be
    duplicated" — and you spent the morning making duplicates free.
    """
    database = Database()
    published: list = []
    database.insert_with_outbox("order-1", "OrderCreated:1")

    relay(database, published, crash_after_publish=True)
    relay(database, published)

    assert published == ["OrderCreated:1", "OrderCreated:1"]
    assert database.unsent_events() == []


def test_and_the_consumer_absorbs_it(sim):
    """The week joining up. The outbox creates duplicates on purpose, and the
    consumer's window makes them cost nothing."""
    database = Database()
    published: list = []
    window = DedupWindow(sim, window_ms=60_000)

    database.insert_with_outbox("order-1", "OrderCreated:1")
    relay(database, published, crash_after_publish=True)
    relay(database, published)

    effects = [e for e in published if not window.seen(e)]
    assert effects == ["OrderCreated:1"]


def test_the_relay_handles_a_backlog():
    database = Database()
    published: list = []
    for i in range(5):
        database.insert_with_outbox(f"order-{i}", f"OrderCreated:{i}")
    assert relay(database, published) == 5
    assert relay(database, published) == 0
