"""The harness has to be trustworthy before anything can be graded with it."""

import pytest

from simlib import Network, Node, Simulation


class Echo(Node):
    """Replies once to whatever it is sent, and remembers what it saw."""

    def __init__(self, name, sim, reply_to=None):
        super().__init__(name, sim)
        self.seen = []
        self.reply_to = reply_to

    def receive(self, src, message):
        self.seen.append((self.sim.now, src, message))
        if self.reply_to:
            self.send(src, f"ack:{message}")


def two_nodes(seed=0, **network_kwargs):
    sim = Simulation(seed=seed)
    net = Network(sim, **network_kwargs)
    a = net.add(Echo("a", sim))
    b = net.add(Echo("b", sim))
    return sim, net, a, b


# -- the clock ----------------------------------------------------------------


def test_time_starts_at_zero_and_only_moves_forward():
    sim = Simulation()
    assert sim.now == 0
    sim.schedule(50, lambda: None)
    sim.run()
    assert sim.now == 50


def test_events_fire_in_time_order_not_insertion_order():
    sim = Simulation()
    fired = []
    sim.schedule(30, lambda: fired.append("late"))
    sim.schedule(10, lambda: fired.append("early"))
    sim.schedule(20, lambda: fired.append("middle"))
    sim.run()
    assert fired == ["early", "middle", "late"]


def test_events_at_the_same_time_fire_in_insertion_order():
    sim = Simulation()
    fired = []
    for i in range(5):
        sim.schedule(10, lambda i=i: fired.append(i))
    sim.run()
    assert fired == [0, 1, 2, 3, 4], "ties must break deterministically"


def test_run_until_leaves_later_events_queued():
    sim = Simulation()
    fired = []
    sim.schedule(10, lambda: fired.append("before"))
    sim.schedule(100, lambda: fired.append("after"))

    sim.run(until_ms=50)
    assert fired == ["before"]
    assert sim.now == 50

    sim.run()
    assert fired == ["before", "after"]
    assert sim.now == 100


def test_scheduling_into_the_past_is_an_error():
    sim = Simulation()
    with pytest.raises(ValueError):
        sim.schedule(-1, lambda: None)


# -- determinism --------------------------------------------------------------


def _trace_for(seed):
    sim, net, a, b = two_nodes(seed=seed, latency_ms=(5, 200), loss=0.3)
    for i in range(40):
        a.send("b", f"m{i}")
    sim.run()
    return sim.trace


def test_same_seed_gives_an_identical_trace():
    assert _trace_for(7) == _trace_for(7)


def test_different_seeds_give_different_traces():
    assert _trace_for(1) != _trace_for(2), "a harness that ignores its seed is not random"


# -- the network --------------------------------------------------------------


def test_a_message_takes_time_to_arrive():
    sim, net, a, b = two_nodes(latency_ms=25)
    a.send("b", "hello")
    sim.run()
    assert b.seen == [(25, "a", "hello")]


def test_jitter_reorders_messages():
    """The point of the harness. Sent in order, arriving in some other order."""
    sim, net, a, b = two_nodes(seed=3, latency_ms=(1, 500))
    for i in range(20):
        a.send("b", i)
    sim.run()

    arrived = [message for _, _, message in b.seen]
    assert sorted(arrived) == list(range(20)), "nothing was lost"
    assert arrived != list(range(20)), "but order was not preserved"


def test_loss_drops_messages_silently():
    sim, net, a, b = two_nodes(seed=1, loss=0.5)
    for i in range(200):
        a.send("b", i)
    sim.run()

    assert net.dropped > 0
    assert net.delivered > 0
    assert net.delivered + net.dropped == 200
    assert len(b.seen) == net.delivered


def test_loss_of_zero_delivers_everything():
    sim, net, a, b = two_nodes(loss=0.0)
    for i in range(100):
        a.send("b", i)
    sim.run()
    assert len(b.seen) == 100
    assert net.dropped == 0


def test_sending_to_an_unknown_node_is_an_error():
    sim, net, a, b = two_nodes()
    with pytest.raises(KeyError):
        a.send("nobody", "hello")


# -- partitions ---------------------------------------------------------------


def test_a_partition_blocks_traffic_across_it_but_not_within():
    sim = Simulation()
    net = Network(sim, latency_ms=10)
    a = net.add(Echo("a", sim))
    b = net.add(Echo("b", sim))
    c = net.add(Echo("c", sim))

    net.partition({"a", "b"}, {"c"})

    a.send("b", "inside")
    a.send("c", "across")
    sim.run()

    assert [m for _, _, m in b.seen] == ["inside"]
    assert c.seen == []


def test_healing_does_not_redeliver_what_was_dropped():
    sim, net, a, b = two_nodes(latency_ms=10)
    net.partition({"a"}, {"b"})
    a.send("b", "lost forever")
    sim.run()

    net.heal()
    sim.run()
    assert b.seen == [], "a healed partition is not a replay log"

    a.send("b", "this one arrives")
    sim.run()
    assert [m for _, _, m in b.seen] == ["this one arrives"]


# -- crashes ------------------------------------------------------------------


def test_a_crashed_node_receives_nothing():
    sim, net, a, b = two_nodes(latency_ms=10)
    b.crash()
    a.send("b", "hello")
    sim.run()
    assert b.seen == []


def test_a_message_in_flight_when_the_node_dies_is_lost():
    """The message left before the crash and arrives after it. This is the case
    people forget, and it is why acknowledgements exist."""
    sim, net, a, b = two_nodes(latency_ms=100)
    a.send("b", "in flight")
    sim.schedule(50, b.crash)
    sim.run()
    assert b.seen == []
    assert net.dropped == 1


def test_a_restarted_node_receives_again():
    sim, net, a, b = two_nodes(latency_ms=10)
    b.crash()
    sim.schedule(50, b.restart)
    sim.schedule(60, lambda: a.send("b", "after restart"))
    sim.run()
    assert [m for _, _, m in b.seen] == ["after restart"]


def test_a_crashed_node_fires_no_timers():
    sim, net, a, b = two_nodes()
    fired = []
    b.set_timer(100, lambda: fired.append("tick"))
    b.crash()
    sim.run()
    assert fired == []


def test_a_crashed_node_sends_nothing():
    sim, net, a, b = two_nodes(latency_ms=10)
    b.crash()
    b.send("a", "ghost")
    sim.run()
    assert a.seen == []


# -- a request/reply round trip, which is most of week 1 ----------------------


def test_round_trip_costs_two_hops():
    sim = Simulation()
    net = Network(sim, latency_ms=20)
    client = net.add(Echo("client", sim))
    server = net.add(Echo("server", sim, reply_to=True))

    client.send("server", "ping")
    sim.run()

    assert [m for _, _, m in client.seen] == ["ack:ping"]
    assert sim.now == 40, "one hop out, one hop back"
