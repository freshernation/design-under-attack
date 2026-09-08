"""A write-ahead log that survives a real crash.

Records are framed so a partial write at the end of the file is detectable:

    4 bytes   payload length, big-endian unsigned
    4 bytes   crc32 of the payload, big-endian unsigned
    n bytes   the payload

Replace each `raise NotImplementedError` with your own code.
"""

import os
import struct
import zlib
from pathlib import Path

HEADER = struct.Struct(">II")   # length, crc32


def encode(payload: bytes) -> bytes:
    """One framed record."""
    raise NotImplementedError


def decode(data: bytes) -> tuple[list[bytes], bool]:
    """Every record up to the first one that does not check out.

    Returns `(records, clean)`. `clean` is False when decoding stopped early —
    a torn write, a bad checksum, or a truncated header.

    **Stop at the first bad record**, and discard everything after it even if it
    looks intact. A gap in the middle means you cannot know what was lost, and
    replaying record 4 without record 3 applies changes out of order. Stopping is
    what makes the log a prefix of the truth, and a prefix is a state the system
    could actually have been in.
    """
    raise NotImplementedError


class WriteAheadLog:
    """An append-only log in a real file.

        log = WriteAheadLog(path)
        log.append(b"set a 1")
        log.recover()      -> [b"set a 1"]
        log.checkpoint()   -> the log is now empty
    """

    def __init__(self, path: str | Path) -> None:
        raise NotImplementedError

    def append(self, payload: bytes) -> None:
        """Write one record and make it durable before returning.

        Flush the file object, then `os.fsync(handle.fileno())`. The flush moves
        bytes from Python to the operating system; the fsync moves them from the
        operating system to the device. Only the second one is durability, and
        skipping it is the difference between "saved" and "probably saved".
        """
        raise NotImplementedError

    def recover(self) -> list[bytes]:
        """Every trustworthy record, in order. An absent or empty file gives []."""
        raise NotImplementedError

    def checkpoint(self) -> None:
        """Everything in the log has been applied to the real structure, so the
        log can start again. Truncate it.

        In a real engine this is the expensive part: the checkpoint must be durable
        before the log may be discarded, or a crash loses both.
        """
        raise NotImplementedError

    def size_bytes(self) -> int:
        raise NotImplementedError
