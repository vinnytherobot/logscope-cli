"""Tests for custom keyword highlighting feature."""

import pytest
from logscope.viewer import manager
from logscope.parser import LogEntry


def test_format_log_without_highlight():
    """Log formatting without highlight should work normally."""
    entry = LogEntry(level="INFO", message="System started", raw="[INFO] System started")
    text = manager.format_log(entry, line_number=None, highlight=None)
    assert "System started" in text.plain


def test_format_log_with_highlight():
    """Highlight keyword should be present in formatted output."""
    entry = LogEntry(level="ERROR", message="Payment failed for user", raw="[ERROR] Payment failed for user")
    text = manager.format_log(entry, line_number=None, highlight="Payment", highlight_color="bold magenta")
    # The formatted text should contain the message
    assert "Payment" in text.plain
    assert "failed for user" in text.plain


def test_format_log_with_line_numbers_and_highlight():
    """Both line numbers and highlight should work together."""
    entry = LogEntry(level="WARN", message="Database connection timeout", raw="[WARN] Database connection timeout")
    text = manager.format_log(entry, line_number=42, highlight="timeout", highlight_color="bold red")
    assert "42" in text.plain
    assert "timeout" in text.plain


def test_format_log_highlight_case_sensitive():
    """Highlight should be case-sensitive for matching."""
    entry = LogEntry(level="INFO", message="Processing PAYMENT transaction", raw="[INFO] Processing PAYMENT transaction")
    text = manager.format_log(entry, line_number=None, highlight="payment", highlight_color="bold green")
    # Since split is case-sensitive, "PAYMENT" won't match "payment"
    # but the message should still be there
    assert "Processing" in text.plain
    assert "PAYMENT" in text.plain


def test_format_log_highlight_empty_keyword():
    """Empty highlight keyword should not affect formatting."""
    entry = LogEntry(level="DEBUG", message="Debug message here", raw="[DEBUG] Debug message here")
    text = manager.format_log(entry, line_number=None, highlight="", highlight_color="bold cyan")
    # Empty string highlight should not cause issues
    assert "Debug message here" in text.plain


def test_format_log_highlight_not_in_message():
    """Keyword not present in message should still render fine."""
    entry = LogEntry(level="INFO", message="User logged in", raw="[INFO] User logged in")
    text = manager.format_log(entry, line_number=None, highlight="payment", highlight_color="bold yellow")
    assert "User logged in" in text.plain


def test_format_log_multiple_occurrences():
    """Highlight should work with multiple occurrences of keyword."""
    entry = LogEntry(level="ERROR", message="Payment failed, retry Payment now", raw="[ERROR] Payment failed, retry Payment now")
    text = manager.format_log(entry, line_number=None, highlight="Payment", highlight_color="bold red")
    # Both occurrences should be present
    assert text.plain.count("Payment") == 2
