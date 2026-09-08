"""The rubric as code, so ten mocks can be compared rather than remembered.

Replace each `raise NotImplementedError` with your own code.
"""

PASSES = ("interrogate", "size", "contract", "path", "decide", "break", "evolve")

# Minutes by which each pass should have started, in a 45-minute interview.
SCHEDULE = {
    "interrogate": 0,
    "size": 6,
    "contract": 11,
    "path": 15,
    "decide": 20,
    "break": 33,
    "evolve": 42,
}


def score_mock(scores: dict[str, int]) -> dict:
    """One mock's result.

    `scores` is a 1–5 score per pass. Returns `total`, `mean` (two decimals),
    `weakest` (the lowest-scoring pass, ties broken by the order in `PASSES`), and
    `verdict`.

    Raises ValueError for a missing pass or a score outside 1–5. A mock with a pass
    left unscored is a mock the interviewer did not reach, and recording it as a
    zero would hide that.
    """
    raise NotImplementedError


def verdict(scores: dict[str, int]) -> str:
    """`"hire"`, `"borderline"` or `"no hire"`.

    * **no hire** — any pass below 3. One collapsed pass sinks it, which is how
      real interviews work: a design with no failure analysis is not rescued by
      excellent sizing
    * **hire** — nothing below 3 **and** a mean of 4 or above
    * **borderline** — everything else
    """
    raise NotImplementedError


def weakest_pass(scores: dict[str, int]) -> str:
    """The lowest-scoring pass. Ties break by `PASSES` order, so the answer is
    deterministic and the earlier pass wins — an early collapse usually caused the
    later one."""
    raise NotImplementedError


def on_schedule(pass_name: str, minutes_elapsed: float) -> bool:
    """Whether reaching this pass at this time is on track for 45 minutes.

    Raises ValueError for an unknown pass name.
    """
    raise NotImplementedError


def progress(mocks: list[dict]) -> dict[str, float]:
    """Improvement per pass across a series of mocks, to two decimals.

    The mean of the last three minus the mean of the first three. Positive is
    improvement; a pass that is not moving is where the next evening goes.

    Raises ValueError for fewer than four mocks — a trend needs something to be a
    trend across.
    """
    raise NotImplementedError


def readiness(mocks: list[dict]) -> bool:
    """Whether the last three mocks were all a pass — nothing below 3 in any of
    them.

    Three consecutive, not a best-of. One good mock is a good day; three in a row is
    a skill, and the difference matters when the real one is on a Tuesday morning.
    """
    raise NotImplementedError
