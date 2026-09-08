"""Day 2 — the design linter.

Run the finished thing on your own week-8 project. It will find something.
"""

import pytest

from design_lint import (
    bare_technology_names,
    decisions_without_alternatives,
    has_derived_numbers,
    review,
    sections_present,
    unmeasurable_claims,
)

WEAK = """# Design

We will build a scalable, highly available file sharing system with low latency.
It uses Redis and Kafka.

## Decision: partition by tenant

We partition by tenant id.
"""

STRONG = """# File sharing

## Problem and non-goals
Not building: editing, versioning, search, virus scanning.

## Envelope
99.9% of shares succeed over a 28-day window; p99 under 200 ms.

## Sizing
8,000,000 users x 3 shares/day = 24,000,000/day, / 86,400 = 280/s average.

## API and data model
POST /shares, GET /files/{id}

## Request paths
1. edge, 2. app, 3. metadata store, 4. blob store

## Decisions

### Decision: cache the read path
Rejected: read replicas, because replication lag breaks read-your-writes for the
uploader. An in-memory store with per-key TTLs and atomic counters, chosen for the
counters — Redis, or Memcached if we drop them.

## Failure modes
Metadata store dead, slow, or returning stale rows.

## Growth
At 10x the fan-out on share breaks first; watch queue age.
"""


# -- arithmetic ---------------------------------------------------------------


def test_it_finds_arithmetic():
    assert has_derived_numbers("24,000,000 / 86,400 = 280/s") is True
    assert has_derived_numbers("10,000 x 3") is True


def test_a_document_of_assertions_has_none():
    """Every number arrived from nowhere. The most common failure there is."""
    assert has_derived_numbers("We expect around 300 requests per second.") is False


def test_the_weak_document_has_no_arithmetic():
    assert has_derived_numbers(WEAK) is False


# -- unmeasurable claims ------------------------------------------------------


def test_it_catches_a_wish():
    assert "highly available" in unmeasurable_claims("The system is highly available.")


def test_a_number_nearby_makes_it_a_requirement():
    """"Highly available" is a wish. "Highly available: 99.9% over 28 days" is a
    thing somebody can check."""
    assert unmeasurable_claims("Highly available: 99.9% over 28 days.") == []


def test_it_reports_each_phrase_once():
    text = "It is fast. Very fast. Extremely fast."
    assert unmeasurable_claims(text).count("fast") == 1


def test_the_weak_document_is_full_of_them():
    found = unmeasurable_claims(WEAK)
    assert "scalable" in found
    assert "highly available" in found


# -- bare technology names ----------------------------------------------------


def test_a_product_with_no_reason_is_flagged():
    """The week-1 fence, surviving as a lint rule."""
    assert bare_technology_names("We use Kafka for the events.") == ["kafka"]


def test_a_product_with_a_property_is_fine():
    """The rule that replaced the ban: a named product comes with the property you
    need from it."""
    text = "An append-only log with per-partition ordering, chosen for the ordering — Kafka."
    assert bare_technology_names(text) == []


def test_the_marker_has_to_be_in_the_same_sentence():
    """Otherwise every document passes by having the word 'because' somewhere."""
    text = "We use Redis. We chose it because of a long story elsewhere in this document."
    assert "redis" in bare_technology_names(text)


def test_the_strong_document_names_a_product_acceptably():
    assert bare_technology_names(STRONG) == []


# -- structure ----------------------------------------------------------------


def test_it_finds_the_sections():
    present = sections_present(STRONG)
    assert all(present.values()), f"missing: {[k for k, v in present.items() if not v]}"


def test_a_heading_matches_loosely():
    assert sections_present("## Sizing and capacity")["sizing"] is True


def test_the_weak_document_has_almost_none():
    present = sections_present(WEAK)
    assert sum(present.values()) <= 1


# -- decisions ----------------------------------------------------------------


def test_a_decision_with_no_rejection_is_counted():
    assert decisions_without_alternatives(WEAK) == 1


def test_a_decision_with_a_rejection_is_not():
    assert decisions_without_alternatives(STRONG) == 0


def test_a_document_with_no_decision_headings_has_none_missing():
    assert decisions_without_alternatives("# Just a title\n\nSome prose.") == 0


# -- the whole thing ----------------------------------------------------------


def test_a_weak_document_produces_a_long_list():
    findings = review(WEAK)
    assert len(findings) > 8


def test_a_strong_document_is_clean():
    """Which no first draft ever is. The honest use of this tool is before anybody
    else reads the document, not after."""
    assert review(STRONG) == []


def test_the_findings_are_readable():
    """A linter whose output needs decoding does not get used."""
    findings = review(WEAK)
    assert all(isinstance(f, str) and len(f) > 10 for f in findings)


def test_an_empty_document_is_not_clean():
    assert review("") != []
