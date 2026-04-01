from datetime import datetime
from logscope.parser import parse_line
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
