"""The tells, as a program.

You have written ten design documents. Now write the thing that reviews them — and
then run it on your own week-8 project, which is the point.

Replace each `raise NotImplementedError` with your own code.
"""

import re

SECTIONS = (
    "problem",
    "envelope",
    "sizing",
    "api",
    "paths",
    "decisions",
    "failure",
    "growth",
)

UNMEASURABLE = (
    "scalable",
    "highly available",
    "high availability",
    "real-time",
    "realtime",
    "low latency",
    "fast",
    "robust",
    "fault tolerant",
    "fault-tolerant",
)

# A sample of product names. Not exhaustive, and it does not need to be — the point
# is to catch the habit, not to maintain a registry.
PRODUCTS = (
    "redis", "memcached", "kafka", "rabbitmq", "postgres", "postgresql", "mysql",
    "cassandra", "dynamodb", "mongodb", "elasticsearch", "s3", "kubernetes",
    "nginx", "envoy", "spanner", "bigtable", "sqs", "kinesis", "clickhouse",
)

# Words that make a product name acceptable: they say what property is needed.
PROPERTIES = (
    "because", "for its", "we need", "provides", "gives us", "chosen for",
    "property", "guarantee", "supports", "so that",
)


def has_derived_numbers(text: str) -> bool:
    """Whether the document contains arithmetic rather than only assertions.

    Look for a multiplication, division or an equals sign between two numbers —
    `40,000 x 3`, `500 / 86,400`, `= 1,750`. A document whose numbers all arrived
    from nowhere has skipped pass 2, and it is the single most common failure.
    """
    raise NotImplementedError


def unmeasurable_claims(text: str) -> list[str]:
    """Phrases from `UNMEASURABLE` that appear **without a number nearby**.

    "Highly available" is a wish. "99.9% over 28 days" is a requirement. Treat a
    number within roughly 60 characters as nearby, which is crude and catches the
    cases that matter.

    Returns the offending phrases, lowercased, in order of first appearance,
    without duplicates.
    """
    raise NotImplementedError


def bare_technology_names(text: str) -> list[str]:
    """Products named in a sentence that says nothing about why.

    Split on sentence enders and **blank lines only** — markdown wraps lines, so
    splitting at every newline cuts sentences in half and flags a product whose
    justification happened to be on the line above.

    A sentence containing a product name and none of the `PROPERTIES` markers is a
    decision inherited rather than made.

    This is the week-1 fence, surviving as a lint rule.
    """
    raise NotImplementedError


def sections_present(text: str) -> dict[str, bool]:
    """Which of `SECTIONS` appear as a markdown heading.

    Match loosely — a heading containing the word is enough, so "## Sizing and
    capacity" counts for `sizing`.
    """
    raise NotImplementedError


def decisions_without_alternatives(text: str) -> int:
    """How many decision headings have no rejection near them.

    Count headings whose text starts with "Decision" (any level), then look at the
    following 600 characters for "rejected", "alternative" or "instead of". A
    decision with no rejected alternative is a preference wearing a decision's
    clothes.
    """
    raise NotImplementedError


def review(text: str) -> list[str]:
    """Every finding, as readable lines.

    A clean document returns an empty list — which no first draft ever does, and
    that is the honest use of this tool: run it before anybody else reads the
    document, not after.
    """
    raise NotImplementedError
