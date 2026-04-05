# LogScope v0.4.1 Release Notes

## Overview

LogScope v0.4.1 introduces the **`--min-level` threshold filter**, expanded CI testing across Python versions, improved timestamp parsing, and new development tooling. This release enhances log analysis flexibility with better level filtering and broader platform support.

---

## New Features

### 📊 Minimum Level Threshold Filter (`--min-level`, `-m`)

Filter logs to show only entries at or above a specified severity level.

**Usage:**
```bash
# Show WARN and above (WARN, ERROR, CRITICAL, ALERT, FATAL)
logscope app.log --min-level WARN

# Combined with other filters
logscope production.log --min-level ERROR --search "database"

# Dashboard mode with threshold
logscope app.log --dashboard --follow --min-level ERROR
```

**Level hierarchy:** TRACE < DEBUG < INFO < NOTICE < WARN < ERROR < CRITICAL < ALERT < FATAL

---

## CLI Changes

### New Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--min-level` | `-m` | `None` | Show logs at or above this level threshold |

### Updated Commands

The min-level filter works in both standard and dashboard modes:

```bash
# Standard streaming output
logscope app.log --min-level WARN

# Dashboard mode
logscope app.log --dashboard --follow --min-level ERROR
```

---

## Improved Timestamp Parsing

LogScope now recognizes additional timestamp formats:

- **ISO 8601**: `2026-03-21T10:00:00Z`, `2026-03-21T10:00:00.123+02:00`
- **Common Log Format**: `21/Mar/2026:10:00:00 +0000`
- **Syslog-style**: `Mar 21 10:00:00`
- **Unix timestamp**: `1711054800`

---

## CI/CD Improvements

### Python Version Matrix

Tests now run across Python 3.9, 3.10, 3.11, and 3.12:

```yaml
python-version: ['3.9', '3.10', '3.11', '3.12']
```

### Development Tooling

- Added coverage threshold (`fail_under = 70`) to prevent regression
- Added ruff-format pre-commit hook for consistent code style

---

## Bug Fixes / Documentation

### Documentation Fixes

- Removed references to non-existent `--pulse` flag from:
  - `docs/architecture-review.md`
  - `CONTRIBUTING.md`
  - Issue templates

---

## Version Information

- **Version:** 0.4.1
- **Previous Version:** 0.3.1
- **Release Date:** 2026-04-05
