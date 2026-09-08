"""The three amplifications, as explicit models.

These are models with stated assumptions, not measurements. Real amplification
depends on the workload, the key distribution and a dozen config options — anyone
quoting one number for it without a workload attached is guessing, and so would you
be if you presented these as fact.

Replace each `raise NotImplementedError` with your own code.
"""

# Stipulated, illustrative figures for the two compaction families. They are here
# so the *direction* of the trade is inspectable, not because these are anyone's
# measured numbers. The tests assert the direction and never the values.
COMPACTION_MODELS = {
    "leveled": {"write": 30.0, "read": 1.1, "space": 1.1},
    "tiered": {"write": 5.0, "read": 4.0, "space": 2.0},
}


def btree_write_amplification(page_bytes: float, row_bytes: float) -> float:
    """A row update rewrites its whole page. 8 KB page, 100 B row -> 80x.

    Batching makes the real figure lower under load; sparse random updates make it
    worse. Raises ValueError for a row of zero or fewer bytes.
    """
    raise NotImplementedError


def lsm_write_amplification(levels: int, size_ratio: float) -> float:
    """Data is rewritten as it moves down each level: roughly levels x ratio."""
    raise NotImplementedError


def lsm_read_amplification(file_count: int, false_positive_rate: float = 0.01) -> float:
    """One read, plus the files whose membership filter wrongly says "maybe".

    With no filter (rate 1.0) this is the file count, which is the thing filters
    exist to remove.
    """
    raise NotImplementedError


def space_amplification(live_bytes: float, obsolete_bytes: float) -> float:
    """Total stored over live. 1.0 means nothing wasted."""
    raise NotImplementedError


def device_write_rate(
    writes_per_second: float, bytes_per_write: float, amplification: float
) -> float:
    """Bytes per second actually hitting the device.

    Do this multiplication in pass 2 whenever a design is write-heavy. It takes ten
    seconds and it occasionally changes the architecture.
    """
    raise NotImplementedError


def compare_compaction(strategy: str) -> dict:
    """The three amplifications for `"leveled"` or `"tiered"`, from the model above.

    Raises ValueError for an unknown strategy.
    """
    raise NotImplementedError
