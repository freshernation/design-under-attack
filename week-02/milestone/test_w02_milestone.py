"""The milestone's mechanism.

Green means the limiter behaves. Whether your design survives twelve servers and a
two-millisecond budget is Friday's question, and no test here touches it.
"""

import pytest

from limiter import Decision, MultiTenantLimiter, divided_limit_floor, local_limit_worst_case
from simlib import Simulation
from token_bucket import advance


@pytest.fixture
def sim():
    return Simulation()


# -- tiers --------------------------------------------------------------------


def test_a_free_tenant_gets_its_burst_and_no_more(sim):
    limiter = MultiTenantLimiter(sim)
    results = [limiter.check("someone", tier="free") for _ in range(10)]
    assert sum(r.allowed for r in results) == 5
    assert results[-1].reason == "tenant"


def test_a_pro_tenant_gets_more(sim):
    limiter = MultiTenantLimiter(sim)
    assert sum(limiter.check("acme", tier="pro").allowed for _ in range(200)) == 100


def test_an_unknown_tenant_gets_the_default_tier(sim):
    limiter = MultiTenantLimiter(sim)
    assert sum(limiter.check("stranger").allowed for _ in range(10)) == 5


def test_an_unknown_tier_is_an_error(sim):
    limiter = MultiTenantLimiter(sim)
    with pytest.raises(ValueError):
        limiter.check("acme", tier="platinum")


# -- isolation ----------------------------------------------------------------


def test_one_tenant_cannot_spend_anothers_quota(sim):
    """Fairness, which is most of why this thing exists."""
    limiter = MultiTenantLimiter(sim)
    for _ in range(500):
        limiter.check("noisy", tier="pro")
    assert limiter.check("quiet", tier="pro").allowed is True


def test_quotas_refill_independently(sim):
    limiter = MultiTenantLimiter(sim)
    for _ in range(200):
        limiter.check("acme", tier="pro")
    assert limiter.check("acme", tier="pro").allowed is False
    advance(sim, 1_000)
    assert limiter.check("acme", tier="pro").allowed is True


def test_retry_after_is_useful(sim):
    limiter = MultiTenantLimiter(sim)
    for _ in range(10):
        limiter.check("someone", tier="free")
    decision = limiter.check("someone", tier="free")
    assert decision.allowed is False
    assert decision.retry_after_ms == 1_000, "one a second means a second"


def test_an_allowed_request_says_retry_now(sim):
    limiter = MultiTenantLimiter(sim)
    assert limiter.check("acme", tier="pro") == Decision(True, "ok", 0)


# -- protection ---------------------------------------------------------------


def test_the_global_limit_binds_even_inside_quota(sim):
    """The point of the whole milestone.

    Ten enterprise tenants, every one of them inside the quota they paid for, and
    together they exceed what the platform can serve. Fairness alone would let
    this through; protection is a separate limit and it has to exist.
    """
    limiter = MultiTenantLimiter(sim, global_rate_per_second=1_000, global_burst=1_000)
    allowed = 0
    for tenant in range(10):
        for _ in range(500):
            allowed += limiter.check(f"big-{tenant}", tier="enterprise").allowed

    assert allowed == 1_000, "the global burst, not the sum of the tenant bursts"
    assert limiter.rejected_global > 0
    assert limiter.rejected_tenant == 0, "nobody exceeded their own quota"


def test_a_globally_rejected_request_does_not_charge_the_tenant(sim):
    """Look before spending. Otherwise sustained global pressure burns every
    tenant's quota without serving anybody."""
    limiter = MultiTenantLimiter(sim, global_rate_per_second=1, global_burst=1)
    assert limiter.check("acme", tier="pro").allowed is True     # spends the global token

    refused = limiter.check("acme", tier="pro")
    assert refused.allowed is False
    assert refused.reason == "global"

    # The tenant's own bucket should be untouched by that refusal: 100 burst,
    # one spent, so 99 remain once the global limit is out of the way.
    limiter.global_bucket = None
    assert sum(limiter.check("acme", tier="pro").allowed for _ in range(200)) == 99


def test_the_tenant_limit_is_checked_first(sim):
    """A tenant over its own quota is told so, not blamed on the platform."""
    limiter = MultiTenantLimiter(sim, global_rate_per_second=10_000, global_burst=10_000)
    for _ in range(10):
        limiter.check("small", tier="free")
    assert limiter.check("small", tier="free").reason == "tenant"


def test_without_a_global_limit_only_quotas_apply(sim):
    limiter = MultiTenantLimiter(sim)
    allowed = sum(limiter.check(f"t{i}", tier="enterprise").allowed
                  for i in range(50) for _ in range(1))
    assert allowed == 50
    assert limiter.rejected_global == 0


# -- doing this on twelve servers ---------------------------------------------


def test_independent_limiters_multiply_the_limit():
    """Twelve edge servers, each allowing an enterprise tenant its full 500/s."""
    assert local_limit_worst_case(12, 500) == 6_000


def test_dividing_the_limit_starves_a_pinned_tenant():
    """The same tenant, whose connections all landed on one server, gets 42/s of
    the 500/s they are paying for."""
    assert divided_limit_floor(12, 500) == pytest.approx(41.7, abs=0.1)


def test_the_two_ways_of_being_wrong_are_far_apart():
    """A factor of 144 between them. This is why the brief tells you which
    direction to err in, and why 'just divide it' is not an answer."""
    assert local_limit_worst_case(12, 500) / divided_limit_floor(12, 500) == pytest.approx(144)
