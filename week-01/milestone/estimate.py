"""The link shortener, in numbers.

Use your own functions from week-01/day-3/sizing.py. They are importable from here.

Replace `raise NotImplementedError` with your own code.
"""

from sizing import (  # noqa: F401 - yours, from day 3
    daily_bytes,
    human_bytes,
    peak_qps,
    qps,
    storage_bytes,
    working_set_bytes,
)

LINKS_PER_MONTH = 100_000_000
REDIRECTS_PER_DAY = 500_000_000
BYTES_PER_RECORD = 500
REPLICAS = 3
PEAK_FACTOR = 5
STORAGE_CEILING_BYTES = 2_000_000_000_000   # 2 TB, including replicas
HOT_WINDOW_DAYS = 2                          # 90% of reads land here
DAYS_PER_MONTH = 30


def estimate() -> dict:
    """Every number the design rests on, in one dict.

    Keys: write_qps, peak_write_qps, read_qps, peak_read_qps, read_write_ratio,
    daily_storage_bytes, max_retention_days, working_set_bytes, working_set_human.

    See the milestone README for what each one means.
    """
    raise NotImplementedError


if __name__ == "__main__":
    for key, value in estimate().items():
        print(f"{key:>22}  {value}")
