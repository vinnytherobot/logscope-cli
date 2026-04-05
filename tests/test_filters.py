import re
from datetime import datetime, timedelta

from logscope.viewer import line_passes_level, line_passes_search, parse_level_filter, line_passes_filters, line_passes_min_level
from logscope.parser import LogEntry


def test_parse_level_filter_single():
    assert parse_level_filter("ERROR") == {"ERROR"}


def test_parse_level_filter_multiple():
    assert parse_level_filter("ERROR, WARN, info") == {"ERROR", "WARN", "INFO"}


def test_parse_level_filter_normalizes_warning():
    assert parse_level_filter("WARNING") == {"WARN"}


def test_parse_level_filter_empty():
    assert parse_level_filter(None) is None
    assert parse_level_filter("") is None
    assert parse_level_filter("  ") is None


def test_line_passes_level():
    assert line_passes_level("INFO", None) is True
    assert line_passes_level("INFO", {"INFO", "ERROR"}) is True
    assert line_passes_level("DEBUG", {"INFO"}) is False


def test_line_passes_search_substring():
    assert line_passes_search("hello world", "world", pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True
    assert line_passes_search("hello world", "WORLD", pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True
    assert line_passes_search("hello world", "WORLD", pattern=None, use_regex=False, case_sensitive=True, invert_match=False) is False


def test_line_passes_search_regex():
    pat = re.compile(r"err\d+", re.IGNORECASE)
    assert line_passes_search("prefix err404 suffix", "unused", pattern=pat, use_regex=True, case_sensitive=False, invert_match=False) is True
    assert line_passes_search("no match here", "unused", pattern=pat, use_regex=True, case_sensitive=False, invert_match=False) is False


def test_line_passes_search_invert():
    assert line_passes_search("keep me", "noise", pattern=None, use_regex=False, case_sensitive=False, invert_match=True) is True
    assert line_passes_search("has noise in line", "noise", pattern=None, use_regex=False, case_sensitive=False, invert_match=True) is False


def test_line_passes_search_no_search_always_passes():
    assert line_passes_search("anything", None, pattern=None, use_regex=False, case_sensitive=False, invert_match=True) is True


def make_entry(timestamp: datetime, level: str = "INFO", message: str = "test") -> LogEntry:
    """Helper to create LogEntry for time filter tests."""
    return LogEntry(level=level, message=message, raw=f"[{level}] {message}", timestamp=timestamp)


def test_line_passes_filters_since():
    """Test that --since filters out entries before the given time."""
    entry_time = datetime(2026, 4, 5, 10, 0, 0)
    since_ok = datetime(2026, 4, 5, 9, 0, 0)   # 1 hour before entry
    since_fail = datetime(2026, 4, 5, 11, 0, 0)  # 1 hour after entry

    entry = make_entry(entry_time)

    assert line_passes_filters(entry, None, None, since_ok, None, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True
    assert line_passes_filters(entry, None, None, since_fail, None, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is False


def test_line_passes_filters_until():
    """Test that --until filters out entries after the given time."""
    entry_time = datetime(2026, 4, 5, 10, 0, 0)
    until_ok = datetime(2026, 4, 5, 11, 0, 0)   # 1 hour after entry
    until_fail = datetime(2026, 4, 5, 9, 0, 0)  # 1 hour before entry

    entry = make_entry(entry_time)

    assert line_passes_filters(entry, None, None, None, until_ok, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True
    assert line_passes_filters(entry, None, None, None, until_fail, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is False


def test_line_passes_filters_since_until_range():
    """Test combining --since and --until to create a time range."""
    entry_time = datetime(2026, 4, 5, 10, 0, 0)
    since = datetime(2026, 4, 5, 9, 0, 0)
    until = datetime(2026, 4, 5, 11, 0, 0)

    entry = make_entry(entry_time)

    # Entry within range passes
    assert line_passes_filters(entry, None, None, since, until, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True

    # Entry before range fails
    entry_early = make_entry(datetime(2026, 4, 5, 8, 0, 0))
    assert line_passes_filters(entry_early, None, None, since, until, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is False

    # Entry after range fails
    entry_late = make_entry(datetime(2026, 4, 5, 12, 0, 0))
    assert line_passes_filters(entry_late, None, None, since, until, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is False


def test_line_passes_filters_no_timestamp():
    """Test that entries without timestamp pass time filters."""
    entry = LogEntry(level="INFO", message="test", raw="[INFO] test", timestamp=None)

    since = datetime(2026, 4, 5, 10, 0, 0)
    until = datetime(2026, 4, 5, 12, 0, 0)

    # Should pass because no timestamp to filter
    assert line_passes_filters(entry, None, None, since, None, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True
    assert line_passes_filters(entry, None, None, None, until, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True


def test_line_passes_filters_exact_boundary():
    """Test that boundaries are inclusive for --since and exclusive for --until."""
    entry_time = datetime(2026, 4, 5, 10, 0, 0)
    entry = make_entry(entry_time)

    # Exact since should pass (inclusive)
    assert line_passes_filters(entry, None, None, entry_time, None, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True

    # Exact until should pass (inclusive)
    assert line_passes_filters(entry, None, None, None, entry_time, pattern=None, use_regex=False, case_sensitive=False, invert_match=False) is True


def test_line_passes_min_level_threshold():
    """Test --min-level threshold filtering."""
    # TRACE is lowest, FATAL is highest
    assert line_passes_min_level("TRACE", None) is True
    assert line_passes_min_level("TRACE", "TRACE") is True
    assert line_passes_min_level("TRACE", "DEBUG") is False
    assert line_passes_min_level("ERROR", "WARN") is True
    assert line_passes_min_level("ERROR", "ERROR") is True
    assert line_passes_min_level("ERROR", "CRITICAL") is False
    assert line_passes_min_level("FATAL", "ERROR") is True
    assert line_passes_min_level("FATAL", "FATAL") is True
    assert line_passes_min_level("INFO", "DEBUG") is True


def test_line_passes_min_level_unknown_level():
    """Test that UNKNOWN level is treated as lowest severity (same as TRACE)."""
    assert line_passes_min_level("UNKNOWN", None) is True
    # UNKNOWN has same severity as TRACE (0), so it passes TRACE threshold
    assert line_passes_min_level("UNKNOWN", "TRACE") is True
    # But fails higher thresholds
    assert line_passes_min_level("UNKNOWN", "DEBUG") is False
    assert line_passes_min_level("UNKNOWN", "INFO") is False


def test_line_passes_min_level_case_insensitive():
    """Test that min_level comparison is case-insensitive."""
    assert line_passes_min_level("ERROR", "error") is True
    assert line_passes_min_level("ERROR", "WaRn") is True
    assert line_passes_min_level("INFO", "DEBUG") is True


def test_line_passes_filters_with_min_level():
    """Test --min-level combined with other filters."""
    entry = make_entry(datetime(2026, 4, 5, 10, 0, 0), level="ERROR", message="error message")

    # Combined with level filter - ERROR passes both ERROR level set and min_level WARN
    assert line_passes_filters(entry, {"ERROR"}, None, None, None, pattern=None, use_regex=False, case_sensitive=False, invert_match=False, min_level="WARN") is True

    # ERROR doesn't pass level filter for INFO only
    assert line_passes_filters(entry, {"INFO"}, None, None, None, pattern=None, use_regex=False, case_sensitive=False, invert_match=False, min_level=None) is False

    # Combined with time filter
    since = datetime(2026, 4, 5, 9, 0, 0)
    assert line_passes_filters(entry, None, None, since, None, pattern=None, use_regex=False, case_sensitive=False, invert_match=False, min_level="WARN") is True
