# Ana-auth - Project Overview

## Core Principles

- **Ana-speksi is the workflow** — use `/as-*` skills for all non-trivial changes. Skills encode phases, gates, and artifact rules; follow them strictly.
- **Skills produce code** — always invoke mandatory skills before writing code. They encode the boring patterns correctly.
- **Correctness over cleverness** — boring, readable solutions. Smallest change that works.
- **Prove it works** — validate with tests/build/lint. Never mark done without evidence.
- **Be explicit about uncertainty** — if you can't verify, say so and propose how to verify.
- **No defensive programming** — trust internal code and framework guarantees. Validate only at system boundaries (user input, external APIs, middleware).

---

## Technology Stack

- **Frontend**: Angular 21 with Angular Material
- **Backend**: Python 3.13+ with FastAPI
- **Database**: Postgress
- **Deployment**: Linux server with nginx and systemd

---

## Project Structure

```
src/
├── api/         # FastAPI backend (see src/api/AGENTS.md)
├── ui/          # Angular frontend (see src/ui/AGENTS.md)
├── shared/      # Database models and shared code (see src/shared/AGENTS.md)
└── tests/       # Backend tests (see src/tests/AGENTS.md)
```

---

## Workflow

- **Plan mode** for non-ana-speksi tasks that are non-trivial (3+ steps, multi-file, architectural).
- **Subagents** for repo exploration, pattern discovery, test triage, dependency research. One focused objective per subagent; synthesize before coding.
- **Thin vertical slices** — implement, test, verify, then expand.
- **Lessons loop** — after corrections, write to `ana-speksi/lessons/<phase>.md` (failure mode, detection signal, prevention rule). Review at phase start.
- **Always before you push** - Check that there are no linting errors by running `uv run lint.py python` and `uv run lint.py angular`

---

## Communication

- Lead with outcome, not process. Reference concrete artifacts.
- Ask **one** targeted question when blocked, with a recommended default.
- State inferred assumptions. Show what you ran and the result.
- No busywork narration — checkpoint only on scope changes, risks, verification failures, or decisions.

---

## Context Management

- Read before write — find the authoritative source first. Prefer targeted reads over scanning.
- Keep `memory.md` updated with key constraints, decisions, and pitfalls. Compress when context grows.
- Prefer explicit names and direct control flow. Leave code easier to read.

---

## Engineering Standards

- **Interfaces** — stable boundaries, optional params over duplication, consistent error semantics.
- **Testing** — smallest test that catches the bug. Unit > integration > E2E. No brittle tests.
- **Types** — no `any`, no ignores. Validate at boundaries only.
- **Dependencies** — no new deps unless the existing stack can't solve it cleanly.
- **Security** — no secrets in code/logs/chat. Untrusted input: validate, sanitize, constrain. Least privilege.
- **Performance** — fix N+1, unbounded loops, repeated computation. No premature optimization.
- **Minimize custom scss** — use shared scss whenever possible, find patterns from other similar components and see dom layouts and css classes that are used there. Reuse these.

---

## Running Commands

- **Always use `uv run`** to execute Python commands (e.g., `uv run pytest`, `uv run python`).
- **Always expect that services (backend and ui) are running** — do NOT attempt to start, restart, or manage them.

### Linting

```bash
uv run lint.py python
uv run lint.py angular
```

To do automatic lining.

### Testing

```bash
uv run run_tests.py all          # Quality checks + unit + integration tests
uv run run_tests.py unit         # Unit tests only (excludes integration & e2e)
uv run run_tests.py int          # Integration tests only
uv run run_tests.py e2e          # E2E browser tests (requires running services)
uv run run_tests.py python       # Unit + integration tests
uv run run_tests.py quality      # Ruff + ty checks
uv run run_tests.py ruff         # Ruff linting only
uv run run_tests.py ty           # Type checking only
uv run run_tests.py cc           # Cyclomatic complexity analysis
```

Common flags: `--file <path>` (specific test file), `-x` (stop on first failure), `-v` (verbose), `-c` (coverage).
E2E-specific: `--headed` (visible browser), `--debug` (Playwright Inspector).

All tests must pass before completing work.

### Database Update After Migrations

```bash
uv run setup_db.py local-update
```

Never remove existing data, ask user to do it manually if migrations failed.

### Quick Commands

```bash
# Regenerate frontend types after API changes
uv run after_api_change.py

# Verify backend imports
cd src && uv run python -c "from api.main import app; print('OK')"

# Build frontend
nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development
```

---

## Git Hygiene

- Atomic, describable commits. No "misc fixes" bundles.
- Don't mix formatting with behavioral changes.
- Don't rewrite history unless asked.
