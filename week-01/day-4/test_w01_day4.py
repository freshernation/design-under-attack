"""Day 4 — source triage.

These check the rules. They cannot check the thing that matters, which is whether
you actually read the Slack post before writing your ledger.
"""

from datetime import date

import pytest

from triage import (
    NOT_LOAD_BEARING,
    NO_SOURCES,
    UNKNOWN_SOURCE,
    check_claim,
    is_load_bearing,
    is_stale,
    ledger_problems,
    tier,
)


# -- tiers --------------------------------------------------------------------


def test_the_team_that_runs_it_is_tier_one():
    assert tier({"publisher": "Slack Engineering", "runs_the_system": True}) == 1


def test_a_paper_by_the_team_that_runs_it_is_still_tier_one():
    """Proximity beats format. This is why the rules are ordered."""
    source = {"kind": "paper", "publisher": "Uber", "runs_the_system": True}
    assert tier(source) == 1


def test_a_paper_by_someone_else_is_tier_two():
    assert tier({"kind": "paper", "publisher": "USENIX"}) == 2


def test_official_docs_are_tier_two():
    assert tier({"kind": "official_docs", "publisher": "Apache Kafka"}) == 2


def test_a_protocol_spec_is_tier_two():
    assert tier({"kind": "spec", "publisher": "IETF"}) == 2


def test_a_named_author_with_no_other_claim_is_tier_three():
    assert tier({"author": "Someone", "kind": "blog"}) == 3


def test_a_publisher_alone_is_tier_three():
    assert tier({"publisher": "A Newsletter"}) == 3


@pytest.mark.parametrize(
    "source",
    [
        {},
        {"kind": "blog"},
        {"author": "", "publisher": ""},
        {"url": "https://example.com/how-x-works"},
    ],
)
def test_no_author_and_no_publisher_is_folklore(source):
    assert tier(source) == 4


@pytest.mark.parametrize("n, expected", [(1, True), (2, True), (3, False), (4, False)])
def test_load_bearing(n, expected):
    assert is_load_bearing(n) is expected


# -- claims -------------------------------------------------------------------

SOURCES = {
    "slack-2023": {"publisher": "Slack Engineering", "runs_the_system": True},
    "raft-2014": {"kind": "paper", "publisher": "USENIX ATC"},
    "newsletter": {"publisher": "A Newsletter"},
    "anon": {},
}


def test_a_known_claim_on_a_tier_one_source_is_fine():
    claim = {"id": "c1", "kind": "known", "sources": ["slack-2023"]}
    assert check_claim(claim, SOURCES) == []


def test_a_known_claim_on_a_tier_two_source_is_fine():
    claim = {"id": "c2", "kind": "known", "sources": ["raft-2014"]}
    assert check_claim(claim, SOURCES) == []


def test_a_known_claim_on_a_newsletter_alone_is_not():
    """Rule 1 of the doctrine, and the reason the doctrine exists."""
    claim = {"id": "c3", "kind": "known", "sources": ["newsletter"]}
    assert check_claim(claim, SOURCES) == [NOT_LOAD_BEARING]


def test_a_newsletter_alongside_a_primary_source_is_fine():
    claim = {"id": "c4", "kind": "known", "sources": ["newsletter", "slack-2023"]}
    assert check_claim(claim, SOURCES) == []


def test_an_inferred_claim_may_rest_on_anything():
    """Inference is yours. It only has to be labelled, not sourced to tier 1."""
    claim = {"id": "c5", "kind": "inferred", "sources": ["newsletter"]}
    assert check_claim(claim, SOURCES) == []


def test_a_claim_citing_nothing_is_a_problem():
    claim = {"id": "c6", "kind": "known", "sources": []}
    assert check_claim(claim, SOURCES) == [NO_SOURCES]


def test_an_unknown_claim_may_cite_nothing():
    """The third column. A question the sources do not answer has nothing to cite,
    and that is exactly the point of recording it."""
    claim = {"id": "c7", "kind": "unknown"}
    assert check_claim(claim, SOURCES) == []


def test_citing_a_source_that_does_not_exist():
    claim = {"id": "c8", "kind": "known", "sources": ["ghost"]}
    assert check_claim(claim, SOURCES) == [UNKNOWN_SOURCE]


def test_problems_come_back_sorted_and_deduplicated():
    claim = {"id": "c9", "kind": "known", "sources": ["ghost", "newsletter"]}
    assert check_claim(claim, SOURCES) == sorted([NOT_LOAD_BEARING, UNKNOWN_SOURCE])


# -- whole ledgers ------------------------------------------------------------

LEDGER = {
    "system": "Example",
    "sources": [
        {"id": "slack-2023", "publisher": "Slack Engineering", "runs_the_system": True},
        {"id": "newsletter", "publisher": "A Newsletter"},
    ],
    "claims": [
        {"id": "good", "kind": "known", "sources": ["slack-2023"]},
        {"id": "weak", "kind": "known", "sources": ["newsletter"]},
        {"id": "mine", "kind": "inferred", "sources": ["slack-2023"]},
        {"id": "open", "kind": "unknown"},
    ],
}


def test_ledger_problems_reports_only_the_broken_ones():
    assert ledger_problems(LEDGER) == {"weak": [NOT_LOAD_BEARING]}


def test_a_clean_ledger_has_no_problems():
    clean = {"sources": LEDGER["sources"], "claims": [LEDGER["claims"][0]]}
    assert ledger_problems(clean) == {}


def test_an_empty_ledger_has_no_problems():
    assert ledger_problems({"sources": [], "claims": []}) == {}


# -- dates --------------------------------------------------------------------

TODAY = date(2026, 9, 2)


def test_a_recent_source_is_not_stale():
    assert is_stale({"published": "2024-06-01"}, TODAY) is False


def test_an_old_source_is_stale():
    assert is_stale({"published": "2016-03-01"}, TODAY) is True


def test_the_threshold_is_configurable():
    source = {"published": "2023-04-11"}
    assert is_stale(source, TODAY, years=3) is True
    assert is_stale(source, TODAY, years=10) is False


def test_a_date_object_works_too():
    assert is_stale({"published": date(2016, 3, 1)}, TODAY) is True


def test_stale_does_not_mean_wrong():
    """Nothing here says a stale source is untrue. It says it describes a
    different year, which is a fact about the source, not a judgement of it."""
    assert is_stale({"published": "2012-01-01"}, TODAY) is True
