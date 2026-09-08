"""Day 4 — filters, and the cache key.

`test_there_is_never_a_false_negative` is the guarantee, checked rather than
asserted in prose.
"""

import pytest

from bloom import BloomFilter, cache_key, distinct_entries, is_fresh


@pytest.fixture(scope="module")
def filled():
    """20,000 keys at a 1% target. Small enough to build quickly, large enough
    for the measured rate to mean something."""
    bloom = BloomFilter(expected_keys=20_000, false_positive_rate=0.01)
    for i in range(20_000):
        bloom.add(f"key-{i}")
    return bloom


# -- sizing -------------------------------------------------------------------


def test_ten_bits_per_key_for_one_percent():
    bloom = BloomFilter(expected_keys=1_000_000, false_positive_rate=0.01)
    assert bloom.bits_per_key == pytest.approx(9.6, abs=0.2)


def test_a_million_keys_costs_about_a_megabyte():
    """Small enough to change a design, which is why this structure keeps
    appearing."""
    bloom = BloomFilter(expected_keys=1_000_000, false_positive_rate=0.01)
    assert bloom.bytes_used == pytest.approx(1.2e6, rel=0.1)


def test_accuracy_is_cheap_up_to_a_point():
    """Ten times fewer false positives costs about five more bits per key, not
    double the memory. That is unusual enough to be worth remembering."""
    loose = BloomFilter(expected_keys=100_000, false_positive_rate=0.01)
    tight = BloomFilter(expected_keys=100_000, false_positive_rate=0.001)
    assert tight.bits_per_key - loose.bits_per_key == pytest.approx(4.8, abs=0.5)
    assert tight.bytes_used < 2 * loose.bytes_used


@pytest.mark.parametrize("keys, rate", [(0, 0.01), (-1, 0.01), (100, 0), (100, 1), (100, 1.5)])
def test_nonsense_sizing_is_an_error(keys, rate):
    with pytest.raises(ValueError):
        BloomFilter(expected_keys=keys, false_positive_rate=rate)


# -- the guarantee ------------------------------------------------------------


def test_there_is_never_a_false_negative(filled):
    """Every key that was added is found. Always, for every filter, for ever.

    This is the only guarantee a bloom filter makes, and it is the only one you
    need: a "no" is trustworthy, so a "no" may safely skip the expensive lookup.
    """
    assert all(f"key-{i}" in filled for i in range(20_000))


def test_a_definite_no_is_common(filled):
    """The win. Most keys that were never added are rejected outright, and each
    rejection is an origin lookup that never happens."""
    absent = [f"missing-{i}" for i in range(2_000)]
    rejected = sum(1 for key in absent if key not in filled)
    assert rejected > 1_900


def test_the_measured_rate_matches_the_target(filled):
    probes = 20_000
    positives = sum(1 for i in range(20_000, 20_000 + probes) if f"key-{i}" in filled)
    measured = positives / probes
    assert 0.005 < measured < 0.02


def test_it_can_estimate_its_own_rate(filled):
    """From how full the array is. This is the number that tells you a filter has
    been overfilled, without needing a test corpus."""
    assert filled.estimated_false_positive_rate() == pytest.approx(0.01, abs=0.005)


def test_an_empty_filter_rejects_everything():
    bloom = BloomFilter(expected_keys=1_000)
    assert "anything" not in bloom
    assert bloom.estimated_false_positive_rate() == 0.0


# -- the failure mode people do not plan for ----------------------------------


def test_an_overfilled_filter_says_maybe_to_everything():
    """Five times its design capacity. Every bit is set, so nothing is ever
    rejected — the filter now consumes memory and provides nothing, silently.

    A filter needs a rebuild policy. A design with one and no policy is carrying a
    component that fails slowly and never says so.
    """
    bloom = BloomFilter(expected_keys=1_000, false_positive_rate=0.01)
    for i in range(5_000):
        bloom.add(f"k{i}")

    assert bloom.estimated_false_positive_rate() > 0.5
    absent = [f"never-added-{i}" for i in range(200)]
    assert sum(1 for key in absent if key in bloom) > 100


# -- the cache key ------------------------------------------------------------


def test_the_key_is_the_url_by_default():
    assert cache_key("/product/42", [], {}) == "/product/42"


def test_varying_adds_to_the_key():
    headers = {"Accept-Encoding": "gzip"}
    assert cache_key("/p/42", ["Accept-Encoding"], headers) == "/p/42|Accept-Encoding=gzip"


def test_a_missing_header_still_makes_a_stable_key():
    assert cache_key("/p/42", ["Accept-Encoding"], {}) == "/p/42|Accept-Encoding="


def test_varying_on_encoding_is_harmless():
    """Three encodings, three copies of each page. Fine."""
    assert distinct_entries(100_000, [3]) == 300_000


def test_varying_on_cookie_destroys_the_hit_rate():
    """One entry per page per user. A shared cache has become a per-user cache
    with a hit rate near zero — and every dashboard still says the CDN is working.

    One header does this, and it is usually added by accident.
    """
    with_encoding = distinct_entries(100_000, [3])
    with_cookie = distinct_entries(100_000, [2_000_000])
    assert with_cookie / with_encoding > 100_000


# -- freshness ----------------------------------------------------------------


def test_a_private_cache_uses_max_age():
    assert is_fresh(0, 200_000, max_age_s=300, s_maxage_s=3_600, shared=False) is True
    assert is_fresh(0, 400_000, max_age_s=300, s_maxage_s=3_600, shared=False) is False


def test_a_shared_cache_prefers_s_maxage():
    """The asymmetry that is the whole reason the directive exists: a long TTL
    where you can purge, a short one where you cannot."""
    assert is_fresh(0, 400_000, max_age_s=300, s_maxage_s=3_600, shared=True) is True


def test_a_shared_cache_falls_back_to_max_age():
    assert is_fresh(0, 400_000, max_age_s=300, s_maxage_s=None, shared=True) is False


def test_the_boundary_is_exclusive():
    assert is_fresh(0, 300_000, max_age_s=300, s_maxage_s=None, shared=False) is False
