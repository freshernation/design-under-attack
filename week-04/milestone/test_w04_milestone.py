"""The milestone's mechanism.

Two tests are the brief: `test_the_whale_cannot_be_split` and
`test_fifo_starves_the_small_tenant`. Neither is a bug to fix.
"""

import pytest

from jobqueue import (
    effective_ways,
    fair_schedule,
    fifo_schedule,
    plan_splits,
    position_of,
    projected_loads,
    shard_key,
    split_ways,
)

# One whale at 25%, ten large tenants, four hundred small ones.
LOADS = {
    "whale": 250.0,
    **{f"big-{i}": 35.0 for i in range(10)},
    **{f"small-{i}": 1.0 for i in range(400)},
}
PARTITIONS = 16


def skew(loads):
    return round(max(loads) / (sum(loads) / len(loads)), 2)


# -- planning -----------------------------------------------------------------


def test_a_quarter_of_the_platform_needs_four_shards():
    """A quarter of a quarter is one sixteenth, which is an even share."""
    assert split_ways(0.25, 16) == 4


def test_a_small_tenant_needs_one():
    assert split_ways(0.001, 16) == 1
    assert split_ways(0.0, 16) == 1


def test_only_the_big_tenants_are_split():
    plan = plan_splits(LOADS, PARTITIONS, threshold=0.05)
    assert plan["whale"] == 4
    assert plan["big-0"] == 1
    assert plan["small-0"] == 1


def test_hot_is_relative_to_how_many_partitions_you_have():
    """A tenant at 3.5% is comfortably under an even share of 16 partitions, so it
    needs no split. Across 64 partitions an even share is 1.6%, and the same
    tenant is now more than twice that.

    The same tenant, the same load, hot in one design and not in the other.
    """
    at_16 = plan_splits(LOADS, 16, threshold=0.01)
    at_64 = plan_splits(LOADS, 64, threshold=0.01)
    assert at_16["big-0"] == 1
    assert at_64["big-0"] == 3


def test_the_plan_halves_the_skew():
    """Two numbers, and they are the argument for the plan. Put both in your
    document, not just the second one."""
    unsplit = {tenant: 1 for tenant in LOADS}
    plan = plan_splits(LOADS, PARTITIONS, threshold=0.05)

    before = skew(projected_loads(LOADS, unsplit, PARTITIONS))
    after = skew(projected_loads(LOADS, plan, PARTITIONS))

    assert before > 4
    assert after < before / 2


def test_planning_for_no_load_is_an_error():
    with pytest.raises(ValueError):
        plan_splits({}, PARTITIONS)


# -- splitting without losing ordering ----------------------------------------


def test_the_same_queue_always_lands_on_the_same_shard():
    """The property the whole ordering guarantee rests on. If this is ever false,
    two jobs from one queue can run out of order and no amount of care downstream
    puts them back."""
    for _ in range(100):
        assert shard_key("acme", "emails", 8) == shard_key("acme", "emails", 8)


def test_different_queues_can_land_on_different_shards():
    queues = [f"queue-{i}" for i in range(20)]
    shards = {shard_key("acme", q, 8) for q in queues}
    assert len(shards) > 1


def test_a_shard_key_names_its_tenant():
    assert shard_key("acme", "emails", 4).startswith("acme#")


def test_one_way_means_one_shard():
    queues = [f"queue-{i}" for i in range(50)]
    assert len({shard_key("acme", q, 1) for q in queues}) == 1


def test_zero_ways_is_an_error():
    with pytest.raises(ValueError):
        shard_key("acme", "emails", 0)


def test_the_whale_cannot_be_split():
    """The brief, as an assertion.

    The plan says split the whale four ways. The whale has one queue, and every
    job in a queue must stay in order, so all four shards would be the same shard.
    `effective_ways` returns 1.

    Nothing here is broken. The code is telling you that ordering and fairness are
    in conflict for this tenant, and your document has to choose which one gives.
    """
    plan = plan_splits(LOADS, PARTITIONS, threshold=0.05)
    assert plan["whale"] == 4
    assert effective_ways(queue_count=1, ways=plan["whale"]) == 1


def test_a_tenant_with_enough_queues_can_be_split():
    assert effective_ways(queue_count=10, ways=4) == 4


def test_a_tenant_with_some_queues_is_split_as_far_as_it_goes():
    assert effective_ways(queue_count=3, ways=16) == 3


# -- fairness -----------------------------------------------------------------

PENDING = {
    "whale": [f"w{i}" for i in range(10_000)],
    "small": ["s0"],
}


def test_fifo_starves_the_small_tenant():
    """One job, behind ten thousand. At a thousand jobs a second that is a ten
    second wait for a customer who sent one request — and the envelope allows
    thirty seconds, so this scales to a breach as soon as the whale grows."""
    schedule = fifo_schedule(PENDING, limit=5_000)
    assert position_of(schedule, "small") is None


def test_fair_scheduling_serves_it_almost_immediately():
    schedule = fair_schedule(PENDING, limit=5_000)
    assert position_of(schedule, "small") < 5


def test_fairness_does_not_reorder_a_tenants_own_jobs():
    """The guarantee that is not negotiable. Interleaving between tenants is a
    choice; reordering within one is a bug."""
    schedule = fair_schedule(PENDING, limit=1_000)
    whale_jobs = [job for tenant, job in schedule if tenant == "whale"]
    assert whale_jobs == [f"w{i}" for i in range(len(whale_jobs))]


def test_the_whale_still_gets_most_of_the_capacity():
    """Fairness is not equal shares. The small tenant has one job; once it is
    served, everything else goes to whoever has work."""
    schedule = fair_schedule(PENDING, limit=1_000)
    whale_share = sum(1 for tenant, _ in schedule if tenant == "whale")
    assert whale_share == 999


def test_round_robin_across_many_tenants():
    pending = {f"t{i}": [f"{i}-a", f"{i}-b"] for i in range(5)}
    schedule = fair_schedule(pending, limit=5)
    assert [tenant for tenant, _ in schedule] == ["t0", "t1", "t2", "t3", "t4"]


def test_a_scheduler_respects_its_limit():
    assert len(fair_schedule(PENDING, limit=7)) == 7
    assert len(fifo_schedule(PENDING, limit=7)) == 7


def test_scheduling_an_empty_queue_gives_nothing():
    assert fair_schedule({}, limit=10) == []
    assert fifo_schedule({"a": []}, limit=10) == []


def test_a_scheduler_stops_when_the_work_runs_out():
    assert len(fair_schedule({"a": ["j1", "j2"]}, limit=100)) == 2


def test_position_of_an_absent_tenant():
    assert position_of(fair_schedule(PENDING, limit=10), "nobody") is None
