# LogScope v0.3.0 Release Notes

## Overview

LogScope v0.3.0 introduces **custom keyword highlighting**, a powerful new feature that allows users to visually emphasize specific terms in log messages. This release enhances log analysis workflows by making important keywords immediately stand out in terminal output.

---

## New Features

### 🔍 Custom Keyword Highlighting (`--highlight`, `-H`)

Highlight specific keywords in log messages with customizable colors and styles.

**Usage:**
```bash
# Basic highlight (default: bold magenta)
logscope app.log --highlight "payment"

# Custom color/style
logscope app.log --highlight "timeout" --highlight-color "bold red"

# Combined with filters
logscope app.log --level ERROR --highlight "database" --highlight-color "yellow"

# Multiple filters with highlight
logscope production.log --level ERROR,WARN --since 1h --highlight "failed" --highlight-color "bold red"
```

**Supported styles:** Any valid Rich style string (e.g., `bold magenta`, `red`, `underline yellow`, `italic cyan`)

---

## CLI Changes

### New Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--highlight` | `-H` | `None` | Keyword to highlight in log messages |
| `--highlight-color` | - | `bold magenta` | Rich style for highlighted keywords |

### Updated Commands

The highlight feature works in both standard and dashboard modes:

```bash
# Standard streaming output
logscope app.log --highlight "error"

# Dashboard mode
logscope app.log --dashboard --highlight "critical" --highlight-color "bold red"
```

---

## API Changes

### `LogScopeManager.format_log()`

Updated signature to support custom highlighting:

```python
def format_log(
    self,
    entry: LogEntry,
    line_number: Optional[int] = None,
    highlight: Optional[str] = None,
    highlight_color: str = "bold magenta"
) -> Text:
```

### `stream_logs()` and `run_dashboard()`

Both functions now accept `highlight` and `highlight_color` parameters.

---

## Bug Fixes

### Code Quality
- Fixed E701 lint violations in `parse_relative_time()` (multiple statements on one line)
- Removed unused `re` import from `viewer.py`
- Removed unnecessary f-string prefix from tailing message
- Removed unused `pytest` import from test file

## Testing

### New Test Suite: `tests/test_highlight.py`

Comprehensive test coverage for the highlight feature:

- `test_format_log_without_highlight` - Ensures normal formatting works
- `test_format_log_with_highlight` - Verifies keyword highlighting
- `test_format_log_with_line_numbers_and_highlight` - Combined line numbers + highlight
- `test_format_log_highlight_case_sensitive` - Case sensitivity behavior
- `test_format_log_highlight_empty_keyword` - Edge case handling
- `test_format_log_highlight_not_in_message` - Non-matching keyword handling
- `test_format_log_multiple_occurrences` - Multiple keyword matches

**Total test count:** 28 (7 new + 21 existing)

## Example Workflows

### DevOps: Monitoring Payment Failures
```bash
logscope payment-service.log --level ERROR --highlight "payment" --highlight-color "bold red"
```

### Debugging: Database Issues
```bash
logscope app.log --search "timeout" --highlight "database" --highlight-color "yellow"
```

### Security: Authentication Events
```bash
logscope auth.log --highlight "failed" --highlight-color "bold red" --dashboard
```

---

## Version Information

- **Version:** 0.3.0
- **Previous Version:** 0.2.0
- **Release Date:** 2026-04-02
- **Commits:** 2