# Functional Specification: Test Infrastructure

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-storify

## Story

**As a** developer working on ana-auth,
**I want** a complete test infrastructure with unit tests, integration tests, E2E tests, quality gates, and a test runner script,
**So that** code quality is enforced from the start and regressions are caught automatically during builds.

## Detailed Description

The test infrastructure has two main components: (1) `run_tests.py`, a typer CLI that orchestrates quality checks and test execution across three separate test levels, and (2) pytest conftest.py fixtures that provide isolated database schemas for integration and E2E test workers. Quality gates include ruff linting and import sorting, ty type checking, and ruff cyclomatic complexity checking (C901 limit 10). Unit tests use mocks and run without a database; they enforce 90% coverage. Integration tests use real PostgreSQL schemas (one per worker) and run in parallel with pytest-xdist. E2E tests use Playwright (Python) with each worker getting its own schema and application instance.

## Requirements

### REQ-05-01: Test Runner CLI (run_tests.py)

**Description**: A typer CLI script that orchestrates all quality checks and test execution.

**Acceptance Scenarios**:

- **WHEN** `uv run run_tests.py quality` is executed
  **THEN** ruff linting runs (and fails the build on violations)
  **AND** ruff import sorting check runs (and fails the build on violations)
  **AND** ty type checking runs (and fails the build on errors)
  **AND** ruff cyclomatic complexity check runs with C901 limit 10 (and fails the build if any function exceeds the limit)

- **WHEN** `uv run run_tests.py unit` is executed
  **THEN** unit tests run with pytest in parallel (`-n auto`)
  **AND** only tests under `tests/unit/` are executed

- **WHEN** `uv run run_tests.py unit --coverage` is executed
  **THEN** unit test coverage is measured and reported
  **AND** the build fails if coverage is below 90%

- **WHEN** `uv run run_tests.py integration` is executed
  **THEN** integration tests run with pytest in parallel (`-n auto`, each worker gets its own schema)
  **AND** only tests under `tests/integration/` are executed

- **WHEN** `uv run run_tests.py integration --coverage` is executed
  **THEN** integration test coverage is measured and reported (no minimum threshold enforced, informational only)

- **WHEN** `uv run run_tests.py e2e` is executed
  **THEN** E2E tests run with the `e2e` pytest marker using Playwright (Python)
  **AND** each E2E test worker creates its own isolated schema (same pattern as unit/integration)

- **WHEN** `uv run run_tests.py all` is executed
  **THEN** quality checks, unit tests, integration tests, and E2E tests all run in sequence

### REQ-05-02: Session-Scoped Test Schema Fixtures

**Description**: Pytest fixtures must create an isolated PostgreSQL schema per test session (per worker in parallel mode) and tear it down afterwards.

**Acceptance Scenarios**:

- **WHEN** a test session starts
  **THEN** a new schema `ana-auth-test-<uuid>` is created with all tables
  **AND** the schema is available for the duration of the session

- **WHEN** the test session ends
  **THEN** the schema is dropped with CASCADE

### REQ-05-03: Function-Scoped Database Sessions

**Description**: Each test function gets its own database session for transaction isolation.

**Acceptance Scenarios**:

- **WHEN** a test function uses the `db_session` fixture
  **THEN** it gets a fresh SQLModel Session connected to the test schema
  **AND** the session is committed on success or rolled back on failure

### REQ-05-04: Integration Test Client

**Description**: An integration test client fixture must inject the X-Schema header so the API middleware routes to the correct test schema.

**Acceptance Scenarios**:

- **WHEN** a test uses the `integration_client` fixture
  **THEN** all requests made through that client include the X-Schema header with the test schema suffix
  **AND** the API processes requests against the isolated test schema

### REQ-05-05: Test Password Hash Constant

**Description**: A pre-computed bcrypt password hash must be available as a test constant for fast test execution.

**Acceptance Scenarios**:

- **WHEN** tests need to create user accounts
  **THEN** they use the shared `TEST_PASSWORD_HASH` constant instead of computing bcrypt at runtime
  **AND** the corresponding `TEST_PASSWORD` constant is available for login tests

### REQ-05-06: E2E Tests with Playwright (Python)

**Description**: E2E tests use Playwright for Python to test the full application through a browser. Each E2E test worker gets its own isolated schema, following the same pattern as unit/integration tests.

**Acceptance Scenarios**:

- **WHEN** E2E tests run
  **THEN** each test worker creates its own `ana-auth-test-<uuid>` schema
  **AND** the schema is populated with tables and a master admin user
  **AND** the schema is dropped after the worker finishes

- **WHEN** the skeleton is set up
  **THEN** one initial Playwright test exists that navigates to the landing page and verifies it loads successfully

### REQ-05-07: E2E Test Application Instance

**Description**: E2E tests must start the backend application with the test schema and serve the frontend so Playwright can interact with it.

**Acceptance Scenarios**:

- **WHEN** an E2E test starts
  **THEN** a FastAPI test server is started with the worker's schema suffix
  **AND** Playwright navigates to the served application

## Edge Cases

- If PostgreSQL is not running, tests should fail with a clear error message rather than hanging.
- If a test worker crashes, its schema should still be cleaned up (session-scoped fixture teardown handles this).
- Parallel test workers must not interfere with each other's schemas.

## UI/UX Considerations

Not applicable -- this is developer tooling.

## Out of Scope

- Performance testing
- Security testing
- Test data generators beyond basic fixtures

## Constraints

- Must use pytest with pytest-xdist for parallel execution
- Must use Playwright for Python for E2E tests
- Must use ruff for linting and complexity, ty for type checking
- Coverage threshold must be 90% (configurable but defaulting to 90%)
- C901 complexity limit must be 10
- All test commands must use `uv run`
