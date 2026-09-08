"""Guards against two mistakes that only show up as baffling import errors.

Neither is about the course material. Both cost an afternoon the first time.
"""

import sys
from collections import defaultdict

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEKS = sorted(ROOT.glob("week-*"))


def _lab_modules():
    """Every module a student writes, by basename."""
    by_name = defaultdict(list)
    for week in WEEKS:
        for path in week.rglob("*.py"):
            if path.name == "conftest.py" or path.name.startswith("test_"):
                continue
            by_name[path.name].append(path.relative_to(ROOT))
    return by_name


def test_lab_module_names_are_unique_across_the_course():
    """Each day's conftest puts its own folder on sys.path, so two labs sharing a
    filename would shadow each other — and which one wins depends on collection
    order, which is not something anybody should have to debug.

    If this fails, rename one of them.
    """
    clashes = {name: paths for name, paths in _lab_modules().items() if len(paths) > 1}
    assert not clashes, f"lab modules sharing a name: {clashes}"


def test_test_file_names_are_unique_across_the_course():
    """pytest imports test modules by basename unless they are in packages, so
    two `test_day2.py` files in different weeks are a collection error rather
    than two sets of tests. Hence `test_wNN_dayN.py`.
    """
    by_name = defaultdict(list)
    for week in WEEKS:
        for path in week.rglob("test_*.py"):
            by_name[path.name].append(path.relative_to(ROOT))
    clashes = {name: paths for name, paths in by_name.items() if len(paths) > 1}
    assert not clashes, f"test files sharing a name: {clashes}"


def test_no_lab_module_shadows_the_standard_library():
    """Each day's conftest puts its folder at the *front* of sys.path, so a lab
    called `queue.py` or `types.py` shadows the standard library for the whole
    test session — including for code that has nothing to do with that lab.

    The failure is spectacular and the cause is invisible. Name labs so it cannot
    happen: `jobqueue.py`, not `queue.py`.
    """
    stdlib = set(sys.stdlib_module_names)
    clashes = {
        name: paths
        for name, paths in _lab_modules().items()
        if name[:-3] in stdlib
    }
    assert not clashes, f"lab modules shadowing the standard library: {clashes}"


def test_every_lab_module_has_a_reference_solution():
    """A lab with no solution cannot be verified, which means its tests have
    never been shown to be satisfiable.

    Skipped in a student clone: `instructor/` is a separate private repository and
    is not there. The check still runs for whoever has it, which is the only person
    who can act on it.
    """
    solutions = ROOT / "instructor" / "solutions"
    if not solutions.is_dir():
        pytest.skip("instructor/ is a separate private repository and is not present")

    missing = []
    for name, paths in _lab_modules().items():
        for path in paths:
            if not (solutions / path).exists():
                missing.append(str(path))
    assert not missing, f"no reference solution for: {sorted(missing)}"
