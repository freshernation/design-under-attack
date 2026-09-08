"""Finding the hot key, and the four things you can do about it.

Replace each `raise NotImplementedError` with your own code.
"""


class TopK:
    """Heavy hitters in fixed memory, by the Space-Saving algorithm.

        top = TopK(k=10)
        top.observe("channel-42")
        top.heavy_hitters()   -> [("channel-42", 1), ...]  busiest first

    Counting every key needs memory proportional to the number of keys, which is
    the thing you have too many of. This keeps `k` counters and no more.

    The rule, on each observation:

    * the key is already tracked — add to its count
    * fewer than `k` keys are tracked — start tracking it at `count`
    * otherwise — take the *smallest* tracked entry, replace its key with this one,
      and set the count to that minimum plus `count`

    That last line is the trick: the new arrival inherits the evicted count, so a
    genuinely hot key climbs quickly and a rare one is evicted before it matters.
    Counts are therefore over-estimates, which is the price of fixed memory.

    Break ties on the minimum by taking the smallest key, so the result is
    deterministic and a test can assert it.
    """

    def __init__(self, k: int) -> None:
        """Raises ValueError for k below 1."""
        raise NotImplementedError

    def observe(self, key: str, count: int = 1) -> None:
        raise NotImplementedError

    def heavy_hitters(self) -> list[tuple[str, int]]:
        """Tracked keys, busiest first. Ties broken by key, for determinism."""
        raise NotImplementedError


def share(counts: dict[str, float], key: str) -> float:
    """A key's fraction of the total, to four decimals. 0.0 if unseen."""
    raise NotImplementedError


def is_hot(counts: dict[str, float], key: str, threshold: float = 0.05) -> bool:
    """Whether a key is over the threshold share of total load."""
    raise NotImplementedError


def split_key(key: str, ways: int, which: int) -> str:
    """One write target for a split key: `"key#3"`.

    Raises ValueError when `which` is outside `range(ways)`.
    """
    raise NotImplementedError


def split_targets(key: str, ways: int) -> list[str]:
    """Every target a reader has to visit. Write to one, read all of them —
    which is why splitting a key moves the cost to the read path."""
    raise NotImplementedError


def utilisation_of_hot_partition(
    hot_share: float, partitions: int, fleet_utilisation: float
) -> float:
    """What the partition holding the hot key is running at, to three decimals.

    The model: the hot key is `hot_share` of all load and its partition carries
    essentially only that key, so it runs at `partitions x hot_share` times the
    average. Crude, and close enough to end an argument.

    May exceed 1.0. When it does, that partition is not slow, it is failing — and
    the fleet dashboard says everything is fine.
    """
    raise NotImplementedError
