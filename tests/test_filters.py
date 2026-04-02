import re

from logscope.viewer import line_passes_level, line_passes_search, parse_level_filter


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
