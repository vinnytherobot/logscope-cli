# Contributing to LogScope

Thanks for helping improve LogScope.

## Development prerequisites

- Python `3.9+`
- [Poetry](https://python-poetry.org/) `1.7+`
- Git

Optional but recommended:

- `pipx` for installing Poetry
- `pre-commit` for local hooks

## Run project locally

```bash
git clone https://github.com/vinnytherobot/logscope.git
cd logscope
poetry install
poetry run logscope --help
```

Run tests:

```bash
poetry run pytest
```

## Branch naming convention

Use prefixes:

- `feat/<short-topic>` for features
- `fix/<short-topic>` for bug fixes
- `docs/<short-topic>` for documentation-only changes
- `chore/<short-topic>` for maintenance and tooling

Examples:

- `feat/dashboard-improvements`
- `fix/windows-stdin-encoding`
- `docs/release-process`

## Commit convention

LogScope uses Conventional Commits:

- `feat(cli): add --min-level support`
- `fix(parser): normalize EMERGENCY to FATAL`
- `docs(readme): add min-level examples`
- `chore(ci): pin GitHub Actions versions`

Recommended format:

```text
<type>(<scope>): <imperative summary>
```

## Testing and how to read results

Primary suite:

```bash
poetry run pytest -q
```

Coverage run (used by CI):

```bash
poetry run pytest --cov=logscope --cov-report=term-missing --cov-report=xml
```

Interpretation:

- Failing test in `tests/test_parser.py`: parser behavior regression.
- Failing test in `tests/test_filters.py`: filtering/search semantics regression.
- Failing test in `tests/test_time.py`: date parsing or time filter regression.

## Pull request process

Use this checklist before opening a PR:

- [ ] Branch name follows convention.
- [ ] Commit messages follow Conventional Commits.
- [ ] Tests were added/updated for behavior changes.
- [ ] `poetry run pytest` passes locally.
- [ ] `README.md`/docs updated if behavior changed.
- [ ] Breaking changes explicitly documented.

PR template is defined in `.github/PULL_REQUEST_TEMPLATE.md`.

## Review and merge

- At least one maintainer review is required.
- CI must be green (`ci.yml` and `pr-check.yml`).
- Squash merge is recommended to keep history focused.
- Maintainer ensures changelog notes are captured before release tagging.

## Reporting bugs

Open an issue using the bug template:

- `.github/ISSUE_TEMPLATE/bug_report.yml`

Include a minimal reproducible log sample whenever possible.

## Code of conduct (short version)

- Be respectful and constructive.
- Assume good intent; discuss code, not people.
- Provide clear reproduction steps when reporting issues.
- Maintainers may moderate discussions to keep collaboration healthy.
