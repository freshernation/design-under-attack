"""Day 4 — the gateway tier."""

import pytest

from gateway import (
    GatewayTier,
    channel_owner,
    reconnect_rate,
    rolling_restart_seconds,
    storm_survivable,
)


# -- the tier -----------------------------------------------------------------


def test_connections_spread_across_hosts():
    tier = GatewayTier(["gw-0", "gw-1", "gw-2"], capacity_each=100)
    for i in range(30):
        tier.connect(f"c{i}")
    assert [tier.connections(h) for h in ("gw-0", "gw-1", "gw-2")] == [10, 10, 10]


def test_a_full_tier_rejects():
    """A rejection is better than an acceptance you cannot serve — week 2, in a
    connection tier."""
    tier = GatewayTier(["gw-0"], capacity_each=2)
    assert tier.connect("a") == "gw-0"
    assert tier.connect("b") == "gw-0"
    assert tier.connect("c") is None


def test_restarting_a_host_drops_its_clients():
    tier = GatewayTier(["gw-0", "gw-1"], capacity_each=100)
    for i in range(20):
        tier.connect(f"c{i}")

    dropped = tier.restart("gw-0")
    assert len(dropped) == 10
    assert tier.connections("gw-0") == 0
    assert tier.total_connections == 10


def test_a_restarted_host_stays_empty_until_clients_return():
    """The slow-moving load-balancing problem: connections are long-lived, so
    nothing rebalances them. A fresh host is idle until something forces
    reconnections."""
    tier = GatewayTier(["gw-0", "gw-1"], capacity_each=100)
    for i in range(20):
        tier.connect(f"c{i}")
    tier.restart("gw-0")
    assert tier.connections("gw-0") == 0
    assert tier.connections("gw-1") == 10


def test_reconnecting_clients_land_on_the_empty_host():
    tier = GatewayTier(["gw-0", "gw-1"], capacity_each=100)
    for i in range(20):
        tier.connect(f"c{i}")
    for client in tier.restart("gw-0"):
        tier.connect(client)
    assert tier.connections("gw-0") == 10


@pytest.mark.parametrize("hosts, capacity", [([], 10), (["gw-0"], 0)])
def test_a_nonsense_tier_is_an_error(hosts, capacity):
    with pytest.raises(ValueError):
        GatewayTier(hosts, capacity)


def test_restarting_an_unknown_host_is_an_error():
    with pytest.raises(KeyError):
        GatewayTier(["gw-0"], 10).restart("gw-9")


# -- channels -----------------------------------------------------------------


def test_a_channel_always_has_the_same_owner():
    hosts = ["cs-0", "cs-1", "cs-2"]
    assert len({channel_owner("#general", hosts) for _ in range(20)}) == 1


def test_channels_spread_across_servers():
    hosts = [f"cs-{i}" for i in range(4)]
    owners = {channel_owner(f"#channel-{i}", hosts) for i in range(200)}
    assert len(owners) == 4


def test_adding_a_server_moves_about_a_quarter():
    """Week 4's ring, unchanged. Adding a fourth server moves roughly 1/N of the
    channels rather than nearly all of them."""
    before = [f"cs-{i}" for i in range(3)]
    after = before + ["cs-3"]
    channels = [f"#channel-{i}" for i in range(2_000)]

    moved = sum(
        1 for c in channels if channel_owner(c, before) != channel_owner(c, after)
    )
    assert 0.15 < moved / len(channels) < 0.45


def test_no_channel_servers_is_an_error():
    with pytest.raises(ValueError):
        channel_owner("#general", [])


# -- the storm ----------------------------------------------------------------


def test_an_instant_reconnect_exceeds_capacity():
    """Forty thousand connections coming back in one second, against a tier that
    can accept six thousand a second. It does not degrade — it fails, at the moment
    the fleet is already short of a host."""
    assert storm_survivable(40_000, window_s=1, accept_capacity=6_000) is False


def test_jitter_makes_it_survivable():
    """The same clients, the same restart, one client-side change."""
    assert storm_survivable(40_000, window_s=60, accept_capacity=6_000) is True
    assert reconnect_rate(40_000, 60) < 700


def test_a_zero_window_is_an_error():
    with pytest.raises(ValueError):
        reconnect_rate(40_000, 0)


# -- the deploy ---------------------------------------------------------------


def test_a_safe_rolling_deploy_takes_a_while():
    """Twenty-six hosts, 40,000 connections each, 6,000/s accept capacity, a
    90-second settle. About forty-three minutes — which is a number a product
    manager should see before anyone promises a same-day rollback."""
    seconds = rolling_restart_seconds(26, 40_000, 6_000, settle_s=90)
    assert seconds / 60 == pytest.approx(43, rel=0.05)


def test_find_out_which_term_actually_dominates():
    """Worth doing before optimising the wrong thing.

    With a 90-second settle, making reconnections ten times cheaper improves the
    deploy by about 16% — because the settle dominates and the accept time is a
    rounding error. Drop the settle to 10 seconds and the same change nearly halves
    it.

    The lever is whichever term is larger, and you find that out by computing both
    rather than by assuming the expensive-sounding one.
    """
    long_settle_slow = rolling_restart_seconds(26, 40_000, 2_000, settle_s=90)
    long_settle_fast = rolling_restart_seconds(26, 40_000, 20_000, settle_s=90)
    assert long_settle_fast / long_settle_slow > 0.8, "barely moved"

    short_settle_slow = rolling_restart_seconds(26, 40_000, 2_000, settle_s=10)
    short_settle_fast = rolling_restart_seconds(26, 40_000, 20_000, settle_s=10)
    assert short_settle_fast / short_settle_slow < 0.6, "now it matters"


def test_a_nonsense_deploy_is_an_error():
    with pytest.raises(ValueError):
        rolling_restart_seconds(0, 1_000, 1_000, 10)
