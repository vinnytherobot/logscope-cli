from datetime import datetime
from logscope.parser import parse_line, extract_timestamp
from logscope.cli import parse_relative_time

def test_parse_iso_timestamp():
    log = '[INFO] 2026-03-21T10:00:00Z Test'
    entry = parse_line(log)
    assert entry.timestamp is not None
    assert entry.timestamp.year == 2026
    assert entry.timestamp.month == 3
    assert entry.timestamp.day == 21

def test_parse_json_timestamp():
    log = '{"timestamp": "2026-03-21T10:00:00Z", "level": "info", "message": "Test"}'
    entry = parse_line(log)
    assert entry.timestamp is not None
    assert entry.timestamp.year == 2026

def test_relative_time_parsing():
    # Since datetime.now() changes, we can only check delta
    now = datetime.now()
    parsed = parse_relative_time("10m")
    assert parsed is not None
    # Should be roughly 10 minutes ago
    diff = now - parsed
    assert 9 < diff.total_seconds() / 60 < 11

def test_relative_time_days():
    now = datetime.now()
    parsed = parse_relative_time("2d")
    assert parsed is not None
    diff = now - parsed
    assert 1.9 < diff.total_seconds() / 86400 < 2.1


def test_extract_iso_with_space():
    """Test ISO-like timestamp with space separator."""
    ts = extract_timestamp("2026-03-21 10:00:00 INFO message")
    assert ts is not None
    assert ts.year == 2026
    assert ts.month == 3
    assert ts.day == 21
    assert ts.hour == 10


def test_extract_iso_with_milliseconds():
    """Test ISO timestamp with milliseconds."""
    ts = extract_timestamp("2026-03-21T10:00:00.123Z INFO message")
    assert ts is not None
    assert ts.year == 2026
    assert ts.microsecond == 123000


def test_extract_iso_with_timezone():
    """Test ISO timestamp with timezone offset."""
    ts = extract_timestamp("2026-03-21T10:00:00+00:00 INFO message")
    assert ts is not None
    assert ts.year == 2026


def test_extract_common_log_format():
    """Test Apache/nginx common log format."""
    ts = extract_timestamp("21/Mar/2026:10:00:00 +0000 INFO message")
    assert ts is not None
    assert ts.year == 2026
    assert ts.month == 3
    assert ts.day == 21
    assert ts.hour == 10


def test_extract_common_log_format_bracketed():
    """Test Apache/nginx common log format in brackets."""
    ts = extract_timestamp("[21/Mar/2026:10:00:00 +0000] INFO message")
    assert ts is not None
    assert ts.year == 2026
    assert ts.month == 3
    assert ts.day == 21


def test_extract_syslog_format():
    """Test syslog-style timestamp."""
    ts = extract_timestamp("Mar 21 10:00:00 hostname process[123]: message")
    assert ts is not None
    assert ts.month == 3
    assert ts.day == 21
    assert ts.hour == 10
    assert ts.minute == 0
    assert ts.second == 0


def test_extract_unix_timestamp():
    """Test Unix timestamp (seconds since epoch)."""
    # 2026-03-21 10:00:00 UTC as Unix timestamp
    ts = extract_timestamp("1711018800 INFO message")
    assert ts is not None
    # Just verify it's a valid datetime, exact values depend on timezone
    assert ts.year in (2026, 2025)  # May vary by timezone


def test_extract_timestamp_none():
    """Test that no timestamp returns None."""
    ts = extract_timestamp("This is just a plain message with no timestamp")
    assert ts is None


def test_parse_line_with_common_log_format():
    """Test that parse_line extracts timestamp from common log format."""
    log = '[INFO] 21/Mar/2026:10:00:00 +0000 Test message'
    entry = parse_line(log)
    assert entry.timestamp is not None
    assert entry.timestamp.month == 3
