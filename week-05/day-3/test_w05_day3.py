"""Day 3 — leader election.

`test_no_term_ever_has_two_leaders` is the safety property. When it passes, you
have implemented the thing that provides it.
"""

import pytest

from election import (
    RaftNode,
    build_cluster,
    current_leaders,
    leader_terms,
    split_brain_terms,
)
from simlib import Simulation


# -- getting started ----------------------------------------------------------


def test_a_leader_is_elected():
    sim = Simulation(seed=1)
    _net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=2_000)
    assert len(current_leaders(nodes)) == 1


def test_everyone_agrees_who_it_is():
    sim = Simulation(seed=1)
    _net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=2_000)

    leader = current_leaders(nodes)[0]
    assert {n.leader for n in nodes} == {leader.name}
    assert {n.term for n in nodes} == {leader.term}


def test_it_happens_quickly():
    """A few hundred milliseconds, not seconds. This is the availability cost of
    a leader failure, and it is a number your envelope should contain."""
    sim = Simulation(seed=1)
    _net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=600)
    assert len(current_leaders(nodes)) == 1


def test_a_majority_is_more_than_half():
    sim = Simulation(seed=1)
    _net, nodes = build_cluster(sim, n=5)
    assert nodes[0].majority == 3

    _net6, nodes6 = build_cluster(Simulation(seed=1), n=6)
    assert nodes6[0].majority == 4, "the sixth machine costs money and buys nothing"


def test_a_stable_leader_is_not_replaced():
    """Heartbeats keep the followers quiet. A cluster that re-elects while healthy
    has its timeouts wrong."""
    sim = Simulation(seed=1)
    _net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=5_000)
    assert len(leader_terms(nodes)) == 1


# -- failure ------------------------------------------------------------------


def test_a_new_leader_takes_over_when_the_old_one_dies():
    sim = Simulation(seed=1)
    _net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=1_000)

    old = current_leaders(nodes)[0]
    old.crash()
    sim.run(until_ms=4_000)

    new = current_leaders(nodes)
    assert len(new) == 1
    assert new[0].name != old.name
    assert new[0].term > old.term


def test_two_failures_out_of_five_are_survivable():
    sim = Simulation(seed=4)
    _net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=1_000)

    for node in nodes[:2]:
        node.crash()
    sim.run(until_ms=5_000)
    assert len(current_leaders(nodes)) == 1


def test_three_failures_out_of_five_are_not():
    """No majority is reachable, so no leader can be elected. The cluster is
    unavailable, and that is the guarantee being kept rather than a bug."""
    sim = Simulation(seed=4)
    _net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=1_000)

    for node in nodes[:3]:
        node.crash()
    sim.run(until_ms=5_000)
    assert current_leaders(nodes) == []


# -- partitions ---------------------------------------------------------------


def test_only_the_majority_side_elects():
    sim = Simulation(seed=2)
    net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=1_000)

    net.partition({"n0", "n1", "n2"}, {"n3", "n4"})
    sim.run(until_ms=4_000)

    by_name = {n.name: n for n in nodes}
    majority = [n for n in ("n0", "n1", "n2") if by_name[n].state == "leader"]
    minority = [n for n in ("n3", "n4") if by_name[n].state == "leader"]

    assert len(majority) == 1
    assert minority == [], "two nodes cannot make a majority of five"


def test_a_leader_stranded_in_the_minority_steps_down():
    """Without this, the old leader keeps accepting writes on the wrong side of
    the partition — which is split brain, and how data is lost."""
    sim = Simulation(seed=2)
    net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=1_000)

    leader = current_leaders(nodes)[0]
    others = [n.name for n in nodes if n.name != leader.name]
    net.partition({leader.name, others[0]}, set(others[1:]))
    sim.run(until_ms=4_000)

    assert leader.state != "leader"


def test_healing_leaves_exactly_one_leader():
    sim = Simulation(seed=2)
    net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=1_000)
    net.partition({"n0", "n1", "n2"}, {"n3", "n4"})
    sim.run(until_ms=4_000)

    net.heal()
    sim.run(until_ms=10_000)
    assert len(current_leaders(nodes)) == 1


def test_the_higher_term_wins_after_a_heal():
    """A node stranded in the minority kept standing for election and failing, so
    its term climbed. When the partition heals it has the highest term, and a
    higher term always wins — even though it was the one that could do nothing."""
    sim = Simulation(seed=2)
    net, nodes = build_cluster(sim, n=5)
    sim.run(until_ms=1_000)
    first_term = current_leaders(nodes)[0].term      # the value, not the node —
                                                     # the node's term keeps moving
    net.partition({"n0", "n1", "n2"}, {"n3", "n4"})
    sim.run(until_ms=4_000)
    net.heal()
    sim.run(until_ms=10_000)

    assert current_leaders(nodes)[0].term > first_term


# -- the guarantee ------------------------------------------------------------


@pytest.mark.parametrize("seed", range(10))
def test_no_term_ever_has_two_leaders(seed):
    """The safety property, under sustained abuse.

    Ten seconds of message loss, random crashes and restarts, and partitions that
    move. Leaders come and go and the cluster is often unavailable — none of that
    is a violation.

    The violation would be two nodes leading the *same term*, and it cannot
    happen: any two majorities share a node, and that node votes once per term.
    """
    sim = Simulation(seed=seed)
    net, nodes = build_cluster(sim, n=5, latency_ms=(5, 60), loss=0.05)
    rng = sim.random

    for step in range(40):
        sim.run(until_ms=(step + 1) * 250)

        victim = rng.choice(nodes)
        if victim.crashed:
            victim.restart()
        elif rng.random() < 0.35:
            victim.crash()

        if rng.random() < 0.2:
            names = [n.name for n in nodes]
            rng.shuffle(names)
            net.partition(set(names[:2]), set(names[2:]))
        elif rng.random() < 0.4:
            net.heal()

    assert split_brain_terms(nodes) == {}


def test_a_leader_is_eventually_elected_despite_message_loss():
    sim = Simulation(seed=9)
    _net, nodes = build_cluster(sim, n=5, latency_ms=(5, 60), loss=0.05)
    sim.run(until_ms=3_000)
    assert len(current_leaders(nodes)) >= 1
