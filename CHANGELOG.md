# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-04-05

### Added

- `--min-level` threshold filter to show logs at or above a specified level
- Python 3.9-3.12 CI matrix testing
- Coverage threshold configuration (`fail_under = 70`)
- Pre-commit hooks with ruff-format
- Improved timestamp parsing supporting:
  - ISO 8601 with various timezone formats
  - Common Log Format (Apache)
  - Syslog-style timestamps
  - Unix timestamps

### Documentation

- Removed references to non-existent `--pulse` flag in documentation
- Updated issue templates to reference existing `--dashboard` functionality

## [0.3.1] - 2026-04-04

### Fixed

- **Bug fixes**:
  - Fix keyword highlight case sensitivity - `--search timeout` now highlights `TIMEOUT` case-insensitively
  - Fix line counting misalignment in `get_lines()` - empty lines no longer cause counter misalignment
  - Fix spectra theme trailing spaces - removed extra space from `CRITICAL` and `FATAL` icons

### Refactored

- Remove deprecated `_normalize_level_token` wrapper function from viewer.py
- Compile regex patterns as module constants in parser.py for better performance
- DRY filter logic consolidated into `line_passes_filters()` function
- Fix mutable global state in themes.py by creating copy before modifying

### Performance

- Regex patterns in parser.py are now compiled once at module load instead of per-line

### DevOps

- Add pytest-cov and ruff as dev dependencies
- Add [tool.pytest.ini_options] and [tool.ruff] configuration to pyproject.toml

## [0.3.0] - 2026-04-03

### Added

- Custom keyword highlighting with `--highlight` and `--highlight-color` options
- Case-insensitive search highlighting now respects `--case-sensitive` flag
- 6 beautiful themes: default, neon, ocean, forest, minimal, spectra
- Custom theme support via `.logscoperc` configuration file
- DRY level normalization consolidated in `_normalize_level()` function

### Fixed

- Version divergence between pyproject.toml and __init__.py
- `--since`/`--until` time filters now properly applied in stream_logs mode
