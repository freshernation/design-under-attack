"""Proximity search without scanning: square cells, because the arithmetic is visible.

Real systems use hexagons (H3) or a space-filling curve (S2). The mechanism is the
same and the edges are the same; the shape only changes the neighbour maths.

Replace each `raise NotImplementedError` with your own code.
"""

import math

EARTH_RADIUS_M = 6_371_000


def cell_of(lat: float, lng: float, resolution: int) -> tuple[int, int]:
    """The cell a point falls in. `resolution` is cells per degree, so 1,000 gives
    cells roughly 111 m across at the equator.

    Use `math.floor`, not `int` — `int(-0.5)` is 0 and `floor(-0.5)` is -1, and
    getting that wrong puts the entire southern and western hemispheres in the
    wrong cells in a way that looks fine in testing.
    """
    raise NotImplementedError


def neighbours(cell: tuple[int, int]) -> list[tuple[int, int]]:
    """The eight cells around this one. Not including the cell itself."""
    raise NotImplementedError


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance in metres, to one decimal.

    The exact filter that runs over the small candidate set the cells produced.
    """
    raise NotImplementedError


class CellIndex:
    """Objects bucketed by cell.

        index = CellIndex(resolution=1_000)
        index.insert("driver-1", 51.5074, -0.1278)
        index.search(51.5074, -0.1278, ring=1)
    """

    def __init__(self, resolution: int) -> None:
        """Raises ValueError for a resolution below 1."""
        raise NotImplementedError

    def insert(self, key: str, lat: float, lng: float) -> None:
        raise NotImplementedError

    def move(self, key: str, lat: float, lng: float) -> bool:
        """Reposition. Returns whether the object changed cell — which is the
        write that a moving population generates, and the reason live-location
        systems keep positions in memory."""
        raise NotImplementedError

    def search(self, lat: float, lng: float, ring: int = 1) -> list[str]:
        """Keys in this cell and, with `ring=1`, the eight around it. Sorted.

        **Searching only your own cell silently misses neighbours across a
        boundary**, and one test exists to demonstrate exactly that.
        """
        raise NotImplementedError

    def within(self, lat: float, lng: float, radius_m: float, ring: int = 1) -> list[str]:
        """Search, then filter by true distance. Cheap check over a small set,
        rather than an expensive one over everything."""
        raise NotImplementedError

    def occupants(self, cell: tuple[int, int]) -> int:
        raise NotImplementedError


def cell_side_metres(resolution: int) -> float:
    """Roughly how wide a cell is at the equator, to one decimal.

    One degree of latitude is about 111 km. Divide.
    """
    raise NotImplementedError


def candidates_at_resolution(density_per_km2: float, resolution: int, ring: int = 1) -> float:
    """Expected candidates from a search, to one decimal.

    The number that chooses a resolution: too many and you filter thousands, too
    few and you read a large ring. Include the ring — a `ring=1` search covers nine
    cells, not one.
    """
    raise NotImplementedError


def churn_writes_per_second(objects: int, report_interval_s: float) -> float:
    """Position updates per second from a moving population.

    Run it on 400,000 drivers reporting every 4 seconds, then ask whether those
    writes need to be durable.
    """
    raise NotImplementedError
