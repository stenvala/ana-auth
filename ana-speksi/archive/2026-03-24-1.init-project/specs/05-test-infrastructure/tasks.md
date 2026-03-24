# Tasks: Test Infrastructure

**Status**: Accepted
**Generated with**: as-taskify
**Story**: 05-test-infrastructure

## Prerequisites

- 02-backend-skeleton must be complete (backend code to test)
- 04-database-schema must be complete (schema for integration tests)
- 03-frontend-skeleton must be complete (for E2E tests)

---

## Phase 1: Setup

### P01.T001 -- Configure pytest in pyproject.toml

**Mandatory to use skills: /test-python-unit**

Add pytest configuration to `pyproject.toml`:
- Test paths: `src/tests/`
- Markers: integration, e2e
- Coverage settings (source, omit patterns)
- Default options

Files:
- Modify `pyproject.toml` (add [tool.pytest] and [tool.coverage] sections)

- [x] P01.T001

---

## Phase 2: Implementation

### Service Changes

### P02.T001 -- Create run_tests.py typer CLI

**Mandatory to use skills: /create-web-app, /python-coding-conventions**

Create `run_tests.py` at project root modeled after accounts/run_tests.py:
- TestRunner class with `run_command()` method
- Commands: quality, ruff, ty, cc, unit, integration, e2e, python, all
- `quality`: ruff check + ruff import sort check + ty + ruff C901 (limit 10)
- `unit`: `pytest src/tests/unit/ -n auto` with optional `--cov --cov-fail-under=90`
- `integration`: `pytest src/tests/integration/ -n auto` with optional `--cov`
- `e2e`: `pytest src/tests/e2e/` with Playwright options (--headed, --debug)
- Support `--file`, `-x`, `-v`, `-c` (coverage) passthrough flags
- JUnit XML output support for CI/CD integration

Files:
- Create `run_tests.py`

Verify: `uv run run_tests.py --help` shows all commands.

- [x] P02.T001

### P02.T002 -- Create root conftest.py with schema fixtures

**Mandatory to use skills: /test-python-unit, /test-python-integration**

Create `src/tests/conftest.py` with:
- Session-scoped `test_schema_suffix` fixture: create schema `"ana-auth-test-{uuid}"`, run create_schema.sql and ensure_admin.sql, yield suffix, teardown DROP SCHEMA CASCADE
- Function-scoped `db_session` fixture: create SQLModel Session with test schema, yield, cleanup
- `TEST_PASSWORD` and `TEST_PASSWORD_HASH` pre-computed constants

Files:
- Create `src/tests/conftest.py`

- [x] P02.T002

### P02.T003 -- Create unit test conftest with mock fixtures

**Mandatory to use skills: /test-python-unit**

Create `src/tests/unit/conftest.py` with mock-oriented fixtures:
- mock_session fixture (mocked SQLModel Session)
- Any shared unit test utilities

Files:
- Create `src/tests/unit/conftest.py`

- [x] P02.T003

### P02.T004 -- Create integration test conftest with TestClient

**Mandatory to use skills: /test-python-integration**

Create `src/tests/integration/conftest.py` with:
- `test_client` fixture: FastAPI TestClient with X-Schema header injection
- Reuses session-scoped schema from root conftest

Files:
- Create `src/tests/integration/conftest.py`

- [x] P02.T004

### P02.T005 -- Create E2E conftest with Playwright fixtures

**Mandatory to use skills: /test-playwright**

Create `src/tests/e2e/conftest.py` with:
- Session-scoped fixture to start FastAPI test server on a free port
- Playwright browser and page fixtures
- Schema creation/teardown per worker

Files:
- Create `src/tests/e2e/__init__.py`
- Create `src/tests/e2e/conftest.py`

- [x] P02.T005

### P02.T006 -- Create E2E page objects

**Mandatory to use skills: /test-playwright**

Create base page object and landing page object:
- BasePage with common navigation helpers
- LandingPage with selectors for landing page elements (data-test-id)

Files:
- Create `src/tests/e2e/pages/base_page.py`
- Create `src/tests/e2e/pages/landing_page.py`

- [x] P02.T006

---

## Phase 3: Test Automation

### Backend Tests

### P03.T001 -- Create health check integration test

**Mandatory to use skills: /test-python-integration**

Test health endpoint via TestClient returns 200 with `{"status": "ok"}`.

Files:
- Create `src/tests/integration/api/__init__.py`
- Create `src/tests/integration/api/routers/__init__.py`
- Create `src/tests/integration/api/routers/test_health.py`

Verify: `uv run pytest src/tests/integration/api/routers/test_health.py -v` passes.

- [x] P03.T001

### E2E Tests

### P03.T002 -- Create landing page E2E test

**Mandatory to use skills: /test-playwright**

Playwright test navigating to root URL, verifying landing page loads and displays ana-auth branding.

Files:
- Create `src/tests/e2e/test_landing.py`

Verify: `uv run run_tests.py e2e` passes (requires running services).

- [x] P03.T002

---

## Phase 4: Manual Verification

- Run `uv run run_tests.py quality` and verify it passes
- Run `uv run run_tests.py unit -v` and verify tests pass
- Run `uv run run_tests.py integration -v` and verify tests pass with isolated schemas
- After tests complete, verify no `ana-auth-test-*` schemas remain in PostgreSQL
- Run `uv run run_tests.py unit --coverage` and verify 90% threshold check works
