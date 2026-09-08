"""Day 4 — the write-ahead log.

These tests damage a real file in the ways a real crash damages one.
"""

import pytest

from wal import HEADER, WriteAheadLog, decode, encode


@pytest.fixture
def log(tmp_path):
    return WriteAheadLog(tmp_path / "wal.log")


# -- framing ------------------------------------------------------------------


def test_a_record_round_trips():
    records, clean = decode(encode(b"hello"))
    assert records == [b"hello"]
    assert clean is True


def test_several_records_round_trip():
    data = encode(b"one") + encode(b"two") + encode(b"three")
    assert decode(data) == ([b"one", b"two", b"three"], True)


def test_an_empty_payload_is_a_valid_record():
    assert decode(encode(b"")) == ([b""], True)


def test_nothing_decodes_to_nothing():
    assert decode(b"") == ([], True)


def test_a_record_carries_its_own_length_and_checksum():
    assert len(encode(b"hello")) == HEADER.size + 5


# -- damage -------------------------------------------------------------------


def test_a_torn_final_record_is_discarded():
    """The power went while the third record was being written."""
    data = encode(b"one") + encode(b"two") + encode(b"three")
    torn = data[:-2]
    records, clean = decode(torn)
    assert records == [b"one", b"two"]
    assert clean is False


def test_a_truncated_header_is_discarded():
    data = encode(b"one") + encode(b"two")[:3]
    assert decode(data) == ([b"one"], False)


def test_a_flipped_byte_fails_its_checksum():
    data = bytearray(encode(b"one") + encode(b"two"))
    data[-1] ^= 0xFF
    records, clean = decode(bytes(data))
    assert records == [b"one"]
    assert clean is False


def test_a_record_after_a_corrupt_one_is_discarded_even_though_it_is_intact():
    """The rule people argue with before they think about it.

    Record 3 is perfectly readable. It is thrown away anyway, because applying it
    without record 2 produces a state the system was never in. A log is only useful
    if replaying it gives you a prefix of what happened.
    """
    data = bytearray(encode(b"one") + encode(b"two") + encode(b"three"))
    corrupt_at = HEADER.size + 3 + HEADER.size      # inside record two's payload
    data[corrupt_at] ^= 0xFF

    records, clean = decode(bytes(data))
    assert records == [b"one"]
    assert clean is False
    assert b"three" not in b"".join(records)


# -- the log ------------------------------------------------------------------


def test_appended_records_come_back(log):
    log.append(b"set a 1")
    log.append(b"set b 2")
    assert log.recover() == [b"set a 1", b"set b 2"]


def test_a_missing_file_recovers_to_nothing(log):
    assert log.recover() == []
    assert log.size_bytes() == 0


def test_recovery_survives_the_file_being_truncated(log, tmp_path):
    for payload in (b"one", b"two", b"three"):
        log.append(payload)

    path = tmp_path / "wal.log"
    with open(path, "r+b") as handle:
        handle.truncate(path.stat().st_size - 3)

    assert log.recover() == [b"one", b"two"]


def test_recovery_survives_a_flipped_byte(log, tmp_path):
    for payload in (b"one", b"two"):
        log.append(payload)

    path = tmp_path / "wal.log"
    data = bytearray(path.read_bytes())
    data[-1] ^= 0xFF
    path.write_bytes(bytes(data))

    assert log.recover() == [b"one"]


def test_the_log_can_be_appended_to_after_recovery(log):
    """Recovery is a read. It does not consume the log, and a crash during
    recovery must leave you able to try again."""
    log.append(b"one")
    assert log.recover() == [b"one"]
    log.append(b"two")
    assert log.recover() == [b"one", b"two"]


def test_a_checkpoint_empties_the_log(log):
    log.append(b"one")
    log.append(b"two")
    assert log.size_bytes() > 0

    log.checkpoint()
    assert log.recover() == []
    assert log.size_bytes() == 0


def test_the_log_grows_without_checkpoints(log):
    """Which is why checkpoints exist, and why 'how long may recovery take?' is a
    requirement rather than an implementation detail."""
    log.append(b"x" * 100)
    first = log.size_bytes()
    log.append(b"x" * 100)
    assert log.size_bytes() > first
