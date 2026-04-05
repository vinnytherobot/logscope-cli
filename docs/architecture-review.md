# LogScope Architecture Review and Improvement Plan

## Phase 1 - Project read and context

### Current repository structure (up to 4 levels)

```text
logscope/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── dependency-update.yml
│   │   ├── pr-check.yml
│   │   └── release.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── api.md
│   └── architecture-review.md
├── examples/
│   ├── api.log
│   ├── docker.log
│   ├── kubernetes.log
│   ├── sample.log
│   ├── test_complex.log
│   └── test_time.log
├── logscope/
│   ├── __init__.py
│   ├── cli.py
│   ├── parser.py
│   ├── themes.py
│   └── viewer.py
├── tests/
│   ├── test_filters.py
│   ├── test_parser.py
│   └── test_time.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── pyproject.toml
```

### Stack identification

- Main language: Python (`3.9+`)
- Package/build manager: Poetry (`pyproject.toml`)
- CLI framework: Typer
- Terminal UI/highlighting: Rich
- Test framework: pytest
- Build backend: `poetry-core`
- Critical dependencies: `rich`, `typer`, `typing-extensions`
- Dev dependencies: `pytest`, `pytest-cov`, `ruff`

### Existing documentation and workflows read

- Docs: `README.md`, `docs/api.md`, `docs/architecture-review.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- GitHub automation: `.github/workflows/ci.yml`, `release.yml`, `pr-check.yml`, `dependency-update.yml`
- Commit convention in history: Conventional Commits (examples: `feat(...)`, `fix(...)`, `docs(...)`, `chore(...)`)

## Phase 2 - Diagnostic and gaps

### Current strengths

- Clear package boundary in `logscope/` with focused modules (`cli`, `parser`, `viewer`, `themes`).
- Tests already split by concern (`parser`, `filters`, `time`).
- CLI has practical user features (streaming, dashboard, filtering, gzip, export).
- Commit history already follows a recognizable convention.

### Critical gaps addressed

- [HIGH] Missing standardized contributor workflow docs (`CONTRIBUTING`, PR checklist, issue templates).
- [HIGH] Missing release pipeline and quality gates in GitHub Actions.
- [MEDIUM] Missing explicit API reference for contributors.
- [MEDIUM] Documentation did not clearly separate user quickstart from maintainer guidance.
- [LOW] Repository lacked a dedicated architecture note to onboard new maintainers faster.

### Prioritization rationale

1. Unblock contributions (templates + contributing guide + PR checks)
2. Guarantee quality and repeatability (CI, coverage, release process)
3. Improve long-term clarity (docs structure and architecture notes)

## Phase 3 - Proposed folder structure

### Target structure (incremental)

```text
logscope/
├── src/
│   └── logscope/
│       ├── core/          -> parsing and filtering business logic
│       ├── adapters/      -> input/output channels (stdin/file/html/follow)
│       ├── ui/            -> rich rendering, dashboard widgets
│       ├── types/         -> stable public dataclasses/protocols
│       └── cli/           -> Typer command wiring and argument handling
├── tests/
│   ├── unit/              -> parser/filter isolated behavior
│   └── integration/       -> CLI flows and stream behavior
├── docs/                  -> contributor and architecture docs
├── examples/              -> runnable sample logs and usage demos
├── scripts/               -> release and maintenance helper scripts
├── .github/               -> workflows and templates
└── pyproject.toml
```

### Folder-by-folder rules

- `src/`: only production code; no fixtures, no ad-hoc scripts.
- `src/logscope/core/`: parse/filter/time logic; avoid terminal output code.
- `src/logscope/adapters/`: file/stdin/html boundaries; avoid business rules.
- `src/logscope/ui/`: Rich rendering and live layouts only.
- `src/logscope/types/`: public dataclasses/interfaces (best place for stable `LogEntry`-like contracts).
- `src/logscope/cli/`: command declaration and argument validation only.
- `tests/unit/`: deterministic small tests; no long-running streams.
- `tests/integration/`: end-to-end command behavior and IO interactions.
- `docs/`: architecture, API, contributor docs; no implementation code.
- `examples/`: minimal sample logs intended for docs and smoke validation.
- `scripts/`: maintainers' automation; avoid logic that should be in package code.

## Phase 6 - Prioritized implementation plan

### Week 1 (unblock contributions)

- [ ] Add PR/Issue templates and `CONTRIBUTING.md` (4h, maintainer, no breaking change, no dependency)
- [ ] Enforce PR title and docs/tests checks in `pr-check.yml` (3h, maintainer, no breaking change, depends on templates)
- [ ] Improve `README.md` quickstart and contributor links (3h, any contributor, no breaking change, no dependency)

### Week 2 (guarantee quality)

- [ ] Activate CI with lint/build/tests/coverage artifact (4h, maintainer, no breaking change, depends on dev dependency setup)
- [ ] Add release workflow with tag-version validation and GitHub Release notes (4h, maintainer, no breaking change, depends on CI)
- [ ] Configure weekly dependency update workflow (2h, maintainer, no breaking change, depends on CI)

### Week 3+ (scale architecture)

- [ ] Migrate package to `src/` layout incrementally (8h, maintainer, potential breaking change for imports if not carefully mapped, depends on CI)
- [ ] Split `viewer.py` into `ui/` + `adapters/` modules (10h, maintainer, no breaking change if CLI contract remains, depends on src migration)
- [ ] Expand integration test coverage for follow/export flows (6h, any contributor, no breaking change, depends on module split)
