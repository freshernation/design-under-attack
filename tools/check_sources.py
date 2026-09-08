#!/usr/bin/env python3
"""Enforce the source doctrine in SOURCES.md.

Every file in content/sources/*.yml is checked. Failures are printed and the
script exits 1, so it can sit in a pre-commit hook or CI.

    python3 tools/check_sources.py              # structure only
    python3 tools/check_sources.py --check-urls # also resolve every URL (slow)
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a data problem
    sys.exit("PyYAML is not installed. Run: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "content" / "sources"

TIERS = {1, 2, 3, 4}
LOAD_BEARING_TIERS = {1, 2}
KINDS = {"known", "inferred", "derived", "unknown"}
REQUIRED_SOURCE_FIELDS = ("id", "title", "url", "publisher", "tier", "retrieved")


class Problems(list):
    """Accumulated failures, each tagged with the file it came from."""

    def add(self, path: Path, message: str) -> None:
        self.append(f"{path.relative_to(ROOT)}: {message}")


def _is_date(value: object) -> bool:
    """A date, a year-month, or a bare year.

    Plenty of real sources are only dated to the year, and a schema that demands a
    day either gets a fabricated one or gets ignored. Precision you do not have is
    worse than a coarse date you do.
    """
    if isinstance(value, dt.date):
        return True
    if isinstance(value, int):
        return 1900 <= value <= 2200
    if not isinstance(value, str):
        return False
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            dt.datetime.strptime(value, fmt)
        except ValueError:
            continue
        return True
    return False


def check_sources(doc: dict, path: Path, problems: Problems) -> dict[str, dict]:
    """Validate the `sources:` block. Returns the sources keyed by id."""
    by_id: dict[str, dict] = {}
    sources = doc.get("sources")

    if not sources:
        # A topic can honestly have no sources — week 12's interview material is
        # the case that forced this. Saying so explicitly is allowed; saying
        # nothing is not, because an empty list is indistinguishable from an
        # unfinished file.
        if not doc.get("no_sources_reason"):
            problems.add(path, "no sources listed, and no 'no_sources_reason' given")
        return by_id

    for index, source in enumerate(sources):
        label = source.get("id") or f"sources[{index}]"

        for field in REQUIRED_SOURCE_FIELDS:
            if field not in source:
                problems.add(path, f"{label}: missing '{field}'")

        if source.get("tier") not in TIERS:
            problems.add(path, f"{label}: tier must be one of {sorted(TIERS)}")

        # A source with no findable publication date is a real and common thing.
        # Recording that is honest; inventing a date is not. `undated: true` says so
        # out loud and is reported in the summary.
        if "published" not in source and not source.get("undated"):
            problems.add(path, f"{label}: no 'published' date, and not marked 'undated: true'")

        for field in ("published", "retrieved"):
            if field in source and not _is_date(source[field]):
                problems.add(path, f"{label}: {field} is not a date (YYYY, YYYY-MM or YYYY-MM-DD)")

        url = source.get("url", "")
        if url and not url.startswith(("http://", "https://")):
            problems.add(path, f"{label}: url is not absolute")

        if "id" in source:
            if source["id"] in by_id:
                problems.add(path, f"{label}: duplicate source id")
            by_id[source["id"]] = source

    return by_id


def check_claims(doc: dict, path: Path, by_id: dict[str, dict], problems: Problems) -> None:
    """Validate the `claims:` block against the sources it cites."""
    claims = doc.get("claims")

    if not claims:
        problems.add(path, "no claims listed — a source file with no claims proves nothing")
        return

    seen: set[str] = set()

    for index, claim in enumerate(claims):
        label = claim.get("id") or f"claims[{index}]"

        if "id" not in claim:
            problems.add(path, f"{label}: missing 'id'")
        elif claim["id"] in seen:
            problems.add(path, f"{label}: duplicate claim id")
        else:
            seen.add(claim["id"])

        if not claim.get("text"):
            problems.add(path, f"{label}: missing 'text'")

        kind = claim.get("kind")
        if kind not in KINDS:
            problems.add(path, f"{label}: kind must be one of {sorted(KINDS)}")

        cited = claim.get("sources") or []

        # Two kinds are allowed to cite nothing: an `unknown` is a question the
        # sources do not answer, and a `derived` claim follows from arithmetic,
        # which is a basis but not a citation. In a file with no sources at all,
        # those are the only two kinds available — you cannot infer from nothing.
        if not cited and kind not in ("unknown", "derived"):
            problems.add(path, f"{label}: no sources — rule 1")
            continue

        tiers = set()
        for source_id in cited:
            if source_id not in by_id:
                problems.add(path, f"{label}: cites unknown source '{source_id}'")
            else:
                tiers.add(by_id[source_id].get("tier"))

        if kind == "known" and tiers and not (tiers & LOAD_BEARING_TIERS):
            problems.add(
                path,
                f"{label}: stated as known but supported only by tier "
                f"{sorted(t for t in tiers if t)} — rule 1",
            )


def check_urls(by_id: dict[str, dict], path: Path, problems: Problems) -> None:
    """Resolve every URL. Manual-retrieval sources are skipped by design."""
    import urllib.error
    import urllib.request

    for source in by_id.values():
        if source.get("manual"):
            continue
        url = source.get("url")
        if not url:
            continue
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "curl/8"})
        try:
            urllib.request.urlopen(request, timeout=15)
        except urllib.error.HTTPError as error:
            # Some publishers refuse HEAD but serve GET perfectly well.
            if error.code in (403, 405, 501):
                continue
            problems.add(path, f"{source['id']}: {url} returned {error.code}")
        except Exception as error:  # noqa: BLE001 - any failure to resolve is a failure
            problems.add(path, f"{source['id']}: {url} did not resolve ({error})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-urls", action="store_true", help="resolve every URL too")
    args = parser.parse_args()

    files = sorted(SOURCE_DIR.glob("*.yml"))
    if not files:
        print(f"No source files in {SOURCE_DIR.relative_to(ROOT)}")
        return 1

    problems = Problems()

    for path in files:
        doc = yaml.safe_load(path.read_text()) or {}
        if not doc.get("system"):
            problems.add(path, "missing 'system'")
        by_id = check_sources(doc, path, problems)
        check_claims(doc, path, by_id, problems)
        if args.check_urls:
            check_urls(by_id, path, problems)

    if problems:
        print(f"{len(problems)} problem(s) across {len(files)} file(s):\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    docs = [yaml.safe_load(p.read_text()) for p in files]
    claims = sum(len(doc.get("claims", [])) for doc in docs)
    undated = sum(1 for doc in docs for s in doc.get("sources", []) if s.get("undated"))
    manual = sum(1 for doc in docs for s in doc.get("sources", []) if s.get("manual"))

    print(f"OK — {len(files)} source file(s), {claims} claim(s), every claim sourced.")
    if undated:
        print(f"     {undated} source(s) with no findable publication date.")
    if manual:
        print(f"     {manual} source(s) retrieved by hand (publisher blocks automated fetching).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
