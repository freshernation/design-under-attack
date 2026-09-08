"""The milestone's mechanism.

`test_a_paused_holder_cannot_corrupt_fenced_storage` is the brief. The test after
it shows the same sequence without fencing, so you can see what you bought.
"""

import pytest

from lease import (
    FencedStore,
    Lease,
    LeaseService,
    UnfencedStore,
    renewals_per_second,
)
from simlib import Simulation


def advance(sim, ms):
    sim.schedule(ms, lambda: None)
    sim.run(until_ms=sim.now + ms)


@pytest.fixture
def sim():
    return Simulation()


# -- exclusivity --------------------------------------------------------------


def test_one_holder_at_a_time(sim):
    service = LeaseService(sim, lease_ms=10_000)
    assert service.acquire("db-migration", "worker-a") is not None
    assert service.acquire("db-migration", "worker-b") is None
    assert service.holder_of("db-migration") == "worker-a"


def test_different_resources_do_not_conflict(sim):
    service = LeaseService(sim, lease_ms=10_000)
    assert service.acquire("job-1", "a") is not None
    assert service.acquire("job-2", "b") is not None


def test_nobody_holds_an_untouched_resource(sim):
    assert LeaseService(sim).holder_of("nothing") is None


def test_a_lease_with_no_duration_is_an_error(sim):
    with pytest.raises(ValueError):
        LeaseService(sim, lease_ms=0)


# -- expiry -------------------------------------------------------------------


def test_a_lease_expires(sim):
    service = LeaseService(sim, lease_ms=10_000)
    service.acquire("job", "a")

    advance(sim, 9_999)
    assert service.holder_of("job") == "a"

    advance(sim, 2)
    assert service.holder_of("job") is None
    assert service.acquire("job", "b") is not None


def test_renewing_extends_it(sim):
    service = LeaseService(sim, lease_ms=10_000)
    lease = service.acquire("job", "a")

    advance(sim, 6_000)
    renewed = service.renew(lease)
    assert renewed is not None

    advance(sim, 6_000)
    assert service.holder_of("job") == "a", "12 seconds in, and still held"


def test_a_renewal_keeps_the_same_token(sim):
    """It is the same period of leadership continuing. A new token would fence the
    holder out of storage it had already written to."""
    service = LeaseService(sim, lease_ms=10_000)
    lease = service.acquire("job", "a")
    advance(sim, 1_000)
    assert service.renew(lease).token == lease.token


def test_renewing_after_it_has_gone_fails(sim):
    service = LeaseService(sim, lease_ms=1_000)
    lease = service.acquire("job", "a")

    advance(sim, 2_000)
    service.acquire("job", "b")
    assert service.renew(lease) is None


def test_releasing_frees_it(sim):
    service = LeaseService(sim, lease_ms=10_000)
    lease = service.acquire("job", "a")
    assert service.release(lease) is True
    assert service.acquire("job", "b") is not None


def test_you_cannot_release_someone_elses(sim):
    service = LeaseService(sim, lease_ms=1_000)
    stale = service.acquire("job", "a")
    advance(sim, 2_000)
    service.acquire("job", "b")
    assert service.release(stale) is False
    assert service.holder_of("job") == "b"


# -- tokens -------------------------------------------------------------------


def test_tokens_only_increase(sim):
    service = LeaseService(sim, lease_ms=1_000)
    tokens = []
    for holder in ("a", "b", "c"):
        lease = service.acquire("job", holder)
        tokens.append(lease.token)
        service.release(lease)
    assert tokens == sorted(set(tokens))


def test_a_clean_release_and_reacquire_still_takes_a_new_token(sim):
    """Even the same holder. If tokens can repeat, they order nothing."""
    service = LeaseService(sim, lease_ms=10_000)
    first = service.acquire("job", "a")
    service.release(first)
    second = service.acquire("job", "a")
    assert second.token > first.token


# -- the scenario the brief exists for ----------------------------------------


def test_checking_the_expiry_does_not_help(sim):
    """The check-then-act race, made explicit.

    The holder checks, gets a truthful yes, and is then paused. There is no gap to
    close: the pause can happen anywhere, including between the check and the very
    next instruction.
    """
    service = LeaseService(sim, lease_ms=10_000)
    lease = service.acquire("job", "a")

    assert lease.is_valid(sim.now) is True       # truthful at the moment it is asked
    advance(sim, 40_000)                          # the process freezes
    assert lease.is_valid(sim.now) is False       # and it has been wrong for 30 seconds


def test_a_paused_holder_cannot_corrupt_fenced_storage(sim):
    """The milestone.

    A holds the lease and starts work. Its host freezes for forty seconds. The
    lease expires; B acquires it legitimately and writes. A wakes up believing
    nothing has happened, and writes.

    A's write is refused. Not because A behaved badly — it did everything right —
    but because storage will not accept a token that has been superseded.

    Fencing does not stop A being confused. It makes A's confusion harmless.
    """
    service = LeaseService(sim, lease_ms=10_000)
    store = FencedStore()

    lease_a = service.acquire("ledger", "a")
    assert store.write("balance", "written by a", lease_a.token) is True

    advance(sim, 40_000)                          # a is frozen; the lease expires

    lease_b = service.acquire("ledger", "b")
    assert lease_b is not None
    assert store.write("balance", "written by b", lease_b.token) is True

    # a wakes up, still holding its lease object, and carries on
    assert store.write("balance", "written by a, too late", lease_a.token) is False
    assert store.read("balance") == "written by b"
    assert store.rejected == 1


def test_without_fencing_the_same_sequence_corrupts_it(sim):
    """Identical events, ordinary storage. B's work is overwritten by a process
    that stopped being in charge half a minute ago, and nothing anywhere logs it."""
    service = LeaseService(sim, lease_ms=10_000)
    store = UnfencedStore()

    lease_a = service.acquire("ledger", "a")
    store.write("balance", "written by a")

    advance(sim, 40_000)
    service.acquire("ledger", "b")
    store.write("balance", "written by b")

    store.write("balance", "written by a, too late")
    assert store.read("balance") == "written by a, too late"


def test_a_holder_may_write_repeatedly_with_its_own_token(sim):
    """Fencing rejects writers that are behind, not writers that are busy."""
    service = LeaseService(sim, lease_ms=10_000)
    store = FencedStore()
    lease = service.acquire("job", "a")

    for i in range(5):
        assert store.write("progress", i, lease.token) is True
    assert store.read("progress") == 4


def test_fencing_is_per_key(sim):
    """A high token on one key must not lock a legitimate holder out of another."""
    store = FencedStore()
    assert store.write("a", 1, token=99) is True
    assert store.write("b", 1, token=2) is True


# -- sizing -------------------------------------------------------------------


def test_renewal_load_on_the_brief():
    """200,000 leases on a 10-second lease, renewed halfway: 40,000 a second, which
    is eight times the brief's stated peak. That is a number your Size section has
    to confront."""
    assert renewals_per_second(200_000, 10_000) == pytest.approx(40_000)


def test_halving_the_lease_doubles_the_renewal_traffic():
    """The trade, in one assertion. Shorter leases recover faster from a crashed
    holder and cost proportionally more traffic — and more spurious expiries when
    the network is slow, which is exactly when it is slow."""
    long_lease = renewals_per_second(200_000, 10_000)
    short_lease = renewals_per_second(200_000, 5_000)
    assert short_lease == pytest.approx(2 * long_lease)


def test_renewing_later_costs_less_and_risks_more():
    assert renewals_per_second(1_000, 10_000, renew_at=0.9) < renewals_per_second(
        1_000, 10_000, renew_at=0.5
    )


@pytest.mark.parametrize("lease_ms, renew_at", [(0, 0.5), (1_000, 0), (1_000, 1.5)])
def test_nonsense_renewal_settings_are_an_error(lease_ms, renew_at):
    with pytest.raises(ValueError):
        renewals_per_second(100, lease_ms, renew_at)
