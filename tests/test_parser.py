import pytest
from logscope.parser import parse_line, LogEntry

def test_parse_info_brackets():
    entry = parse_line("[INFO] System up and running.")
    assert entry.level == "INFO"
    assert entry.message == "System up and running."

def test_parse_error_no_brackets():
    entry = parse_line("ERROR: Disk space is low.")
    assert entry.level == "ERROR"
    assert entry.message == "Disk space is low."

def test_parse_warning_normalize():
    entry = parse_line("[WARN] Deprecated feature used.")
    assert entry.level == "WARNING"
    assert entry.message == "Deprecated feature used."

def test_parse_json_log():
    log_line = '{"timestamp": "2026-03-14T15:30:00", "level": "fatal", "message": "Kernel panic"}'
    entry = parse_line(log_line)
    assert entry.level == "CRITICAL"
    assert entry.message == "Kernel panic"

def test_parse_json_log_alternative_keys():
    log_line = '{"log.level": "debug", "msg": "Entering function A"}'
    entry = parse_line(log_line)
    assert entry.level == "DEBUG"
    assert entry.message == "Entering function A"

def test_parse_unknown():
    entry = parse_line("Just some random text without a level")
    assert entry.level == "UNKNOWN"
    assert entry.message == "Just some random text without a level"
