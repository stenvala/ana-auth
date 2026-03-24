# Technical Specification: Test Infrastructure

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-techify

## Overview

Create the complete test infrastructure: `run_tests.py` CLI orchestrating quality checks (ruff, ty, complexity) and three test levels (unit, integration, E2E), pytest conftest.py fixtures for isolated database schemas per worker, and Playwright E2E setup. Primary reference: **accounts** project (most mature run_tests.py and conftest.py), adapted for PostgreSQL schema-based multitenancy from **events.3rdb.com**. Uses pytest-xdist for parallel execution.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| test-python-unit | Unit test patterns -- mocking, db_session fixture, one-test-per-method |
| test-python-integration | Integration test patterns -- TestClient, real DB, happy-day flows |
| test-playwright | E2E patterns -- Page Objects, data-test-id, conftest fixtures |
| python-coding-conventions | Test code follows same conventions (explicit types, no any) |

## Architecture

```
project root/
  run_tests.py                    # Typer CLI test runner
  src/
    tests/
      __init__.py
      conftest.py                 # Root conftest -- schema fixtures, session fixtures
      unit/
        __init__.py
        conftest.py               # Unit-specific fixtures (mocks)
        api/
          routers/
            test_health.py        # Health check unit test
      integration/
        __init__.py
        conftest.py               # Integration-specific fixtures (TestClient, X-Schema)
        api/
          routers/
            test_health.py        # Health check integration test
      e2e/
        __init__.py
        conftest.py               # E2E fixtures (Playwright, schema, app server)
        pages/
          base_page.py            # Base page object
          landing_page.py         # Landing page object
        test_landing.py           # Landing page E2E test
```

### Test Runner Commands

| Command | What It Does |
|---------|-------------|
| `uv run run_tests.py quality` | ruff check + ruff import sort + ty check + ruff C901 (limit 10) |
| `uv run run_tests.py ruff` | ruff linting only |
| `uv run run_tests.py ty` | ty type checking only |
| `uv run run_tests.py cc` | Cyclomatic complexity check (C901 limit 10) |
| `uv run run_tests.py unit` | Unit tests with pytest -n auto |
| `uv run run_tests.py unit --coverage` | Unit tests with 90% coverage gate |
| `uv run run_tests.py integration` | Integration tests with pytest -n auto, isolated schemas |
| `uv run run_tests.py integration --coverage` | Integration tests with coverage (no threshold) |
| `uv run run_tests.py e2e` | E2E tests with Playwright, isolated schemas |
| `uv run run_tests.py python` | Unit + integration tests |
| `uv run run_tests.py all` | Quality + unit + integration + e2e |

### Fixture Architecture

**Session-scoped schema fixture** (shared by all tests in a worker):
1. Generate UUID suffix: `test-{uuid4_short}`
2. Create schema `"ana-auth-test-{uuid}"` with all tables + admin user
3. Yield the suffix for use in tests
4. Teardown: DROP SCHEMA CASCADE

**Function-scoped db_session fixture**:
1. Create SQLModel Session connected to the worker's test schema
2. Yield session
3. Commit on success, rollback on failure

**Integration test client fixture**:
1. Create FastAPI TestClient
2. Inject `X-Schema` header with the worker's schema suffix
3. All requests route to the isolated test schema

**E2E test fixtures**:
1. Session-scoped schema (same as above)
2. Start FastAPI test server with the worker's schema on a free port
3. Provide Playwright browser/page fixtures
4. Navigate to the test server URL

### Pre-computed Test Constants

```python
TEST_PASSWORD = "TestPassword123!"
TEST_PASSWORD_HASH = "$2b$12$..."  # Pre-computed at development time
```

This avoids expensive bcrypt computation during test execution.

## Data Model Changes

None -- test infrastructure uses the schema created by story 04.

## API Changes

None.

## Implementation Approach

1. **Create run_tests.py** (typer CLI, modeled after accounts/run_tests.py):
   - TestRunner class with `run_command()` method
   - `quality` command: run ruff check, ruff import sort check, ty, ruff C901
   - `ruff` command: ruff linting only
   - `ty` command: ty type checking only
   - `cc` command: cyclomatic complexity check (C901 limit 10)
   - `unit` command: `pytest src/tests/unit/ -n auto` with optional `--cov --cov-fail-under=90`
   - `integration` command: `pytest src/tests/integration/ -n auto` with optional `--cov`
   - `e2e` command: `pytest src/tests/e2e/ -n auto` with Playwright options (--headed, --debug), `--reruns 2` for flaky tests
   - `python` command: unit + integration
   - `all` command: quality + unit + integration + e2e
   - Support `--file`, `-x`, `-v`, `-c` (coverage) passthrough flags
   - JUnit XML output support for CI/CD integration
   - Per-worker DB setup via setup_db.py subprocess (accounts pattern)

2. **Create root conftest.py** (`src/tests/conftest.py`):
   - Session-scoped `test_schema_suffix` fixture: create schema, yield suffix, drop schema
   - Function-scoped `db_session` fixture: create Session with test schema, yield, cleanup
   - `TEST_PASSWORD` and `TEST_PASSWORD_HASH` constants

3. **Create unit conftest.py** (`src/tests/unit/conftest.py`):
   - Mock-oriented fixtures (mock_session, mock_service, etc.)

4. **Create integration conftest.py** (`src/tests/integration/conftest.py`):
   - `test_client` fixture: FastAPI TestClient with X-Schema header injection
   - Reuses session-scoped schema from root conftest

5. **Create E2E conftest.py** (`src/tests/e2e/conftest.py`):
   - Session-scoped fixture to start FastAPI test server on a free port
   - Playwright browser and page fixtures
   - Schema creation/teardown per worker

6. **Create initial test files**:
   - `tests/unit/api/routers/test_health.py`: Test health endpoint returns 200 with mock
   - `tests/integration/api/routers/test_health.py`: Test health endpoint via TestClient
   - `tests/e2e/test_landing.py`: Playwright test navigating to landing page

7. **Configure pytest** in `pyproject.toml`:
   - Test paths, markers (integration, e2e), asyncio mode, coverage settings

## Testing Strategy

### Automated Tests

This IS the test infrastructure. Verification:
- `uv run run_tests.py quality` passes
- `uv run run_tests.py unit` passes
- `uv run run_tests.py integration` passes
- `uv run run_tests.py e2e` passes (requires running frontend build)

### Manual Testing

- Verify parallel execution: run with `-n 4` and confirm isolated schemas
- Verify schema cleanup: check no `ana-auth-test-*` schemas remain after test run

## Out of Scope

- Performance testing
- Security testing
- Load testing

## Migration / Deployment Notes

- Tests run during the build phase (mcc_build.py)
- E2E tests require a built frontend and running backend
- Playwright browsers must be installed: `uv run playwright install chromium`

## Security Considerations

- Test database credentials are for local Docker only (postgres/postgres)
- Test schemas are automatically cleaned up to prevent data leakage
- Pre-computed test password hash avoids bcrypt timing side-channels in tests
