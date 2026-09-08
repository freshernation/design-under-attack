"""Day 1 — transports and connections."""

import pytest

from transport import (
    connection_memory_bytes,
    polling_qps,
    push_qps,
    reconnect_rate,
    servers_needed,
    wasted_fraction,
)


# -- polling ------------------------------------------------------------------


def test_a_million_clients_polling_every_ten_seconds():
    assert polling_qps(1_000_000, 10) == pytest.approx(100_000)


def test_polling_load_does_not_depend_on_activity():
    """The formula has no term for how much is happening. Identical on a quiet
    Sunday and during an incident — which is the whole problem, and the whole
    appeal."""
    quiet = polling_qps(1_000_000, 10)
    busy = polling_qps(1_000_000, 10)
    assert quiet == busy


def test_push_load_does():
    assert push_qps(50_000) < polling_qps(1_000_000, 10)


def test_almost_every_poll_returns_nothing():
    """A million clients, ten-second interval, a thousand events a second. Ninety-
    nine per cent of the requests are asking a question whose answer is 'no'."""
    assert wasted_fraction(1_000_000, 10, events_per_second=1_000) == pytest.approx(0.99)


def test_polling_is_fine_when_it_is_fine():
    """Not an argument against polling. Five hundred clients on a minute's interval
    is eight requests a second, and reaching for WebSockets there is engineering for
    its own sake."""
    assert polling_qps(500, 60) < 10


def test_nothing_is_wasted_when_events_outpace_polls():
    assert wasted_fraction(100, 10, events_per_second=1_000) == 0.0


def test_polling_with_no_interval_is_an_error():
    with pytest.raises(ValueError):
        polling_qps(100, 0)


# -- what push costs ----------------------------------------------------------


def test_a_million_connections_is_gigabytes_before_any_data():
    assert connection_memory_bytes(1_000_000, 20_480) == pytest.approx(20.5e9, rel=0.01)


def test_per_connection_state_is_the_lever():
    """Halving what you keep per connection halves the memory of the whole tier,
    and the application's share is usually the largest part."""
    lean = connection_memory_bytes(1_000_000, 8_192)
    heavy = connection_memory_bytes(1_000_000, 65_536)
    assert heavy / lean == pytest.approx(8)


def test_sizing_the_connection_tier():
    assert servers_needed(1_000_000, 50_000) == 20
    assert servers_needed(1_000_000, 50_000, target_utilisation=0.75) == 27


def test_sizing_at_full_utilisation_leaves_no_room_to_lose_a_host():
    """Week 2, in a capacity plan. Twenty hosts at 100% means one failure puts the
    other nineteen at 105%."""
    tight = servers_needed(1_000_000, 50_000, target_utilisation=1.0)
    roomy = servers_needed(1_000_000, 50_000, target_utilisation=0.75)
    assert roomy > tight


@pytest.mark.parametrize("per_server, utilisation", [(0, 1.0), (100, 0), (100, 1.5)])
def test_nonsense_sizing_is_an_error(per_server, utilisation):
    with pytest.raises(ValueError):
        servers_needed(1_000, per_server, utilisation)


# -- the storm ----------------------------------------------------------------


def test_an_instant_reconnect_is_a_storm():
    """One gateway restarts. A hundred thousand of the most expensive operation
    you have, in one second."""
    assert reconnect_rate(100_000, 1) == pytest.approx(100_000)


def test_jitter_turns_it_into_a_slope():
    """Same clients, same restart, one client-side change: three orders of
    magnitude. It is the same rule as a synchronised TTL and a synchronised retry."""
    assert reconnect_rate(100_000, 60) < 1_700
    assert reconnect_rate(100_000, 1) / reconnect_rate(100_000, 60) == pytest.approx(60, rel=0.01)


def test_an_instantaneous_window_is_an_error():
    with pytest.raises(ValueError):
        reconnect_rate(100_000, 0)
