"""The source doctrine, as code.

A small version of `tools/check_sources.py`. Implementing the rules is the fastest
way to stop treating them as vibes.

Replace each `raise NotImplementedError` with your own code.
"""

from datetime import date

NO_SOURCES = "no-sources"
UNKNOWN_SOURCE = "unknown-source"
NOT_LOAD_BEARING = "not-load-bearing"

FOUNDATIONAL_KINDS = {"paper", "official_docs", "spec"}


def tier(source: dict) -> int:
    """Which tier a source sits in. Rules in order, first match wins — see the
    day's README. Missing keys mean "no"."""
    raise NotImplementedError


def is_load_bearing(tier_number: int) -> bool:
    """Whether a claim may rest on this tier alone."""
    raise NotImplementedError


def check_claim(claim: dict, sources_by_id: dict[str, dict]) -> list[str]:
    """Problem codes for one claim, sorted. Empty list means it is fine."""
    raise NotImplementedError


def ledger_problems(ledger: dict) -> dict[str, list[str]]:
    """`{claim_id: [codes]}` for every claim with a problem, and nothing for the
    rest. `ledger` has `sources` and `claims` lists, as in the YAML files."""
    raise NotImplementedError


def is_stale(source: dict, today: date, years: int = 3) -> bool:
    """Whether this source describes a system as it was more than `years` ago.
    `published` may be an ISO string or a date."""
    raise NotImplementedError
