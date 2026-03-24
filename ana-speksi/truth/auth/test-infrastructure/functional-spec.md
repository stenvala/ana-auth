# Functional Specification: Test Infrastructure

**Domain**: auth/test-infrastructure
**Last updated**: 2026-03-24

## Story

**As a** developer,
**I want** a complete test infrastructure with unit, integration, and E2E tests orchestrated by a CLI tool,
**So that** I can maintain quality with automated checks from the start.

## Detailed Description

The test infrastructure provides three test levels (unit, integration, E2E) plus quality checks, all orchestrated by `run_tests.py`. Tests run in parallel with isolated database schemas per worker.

## Requirements

### REQ-01: Test Runner CLI

**Description**: `run_tests.py` provides commands for running different test levels.

**Acceptance Scenarios**:

- **WHEN** `uv run run_tests.py quality` is run
  **THEN** ruff linting, import sorting, ty type checking, and C901 complexity checks (limit 10) execute

- **WHEN** `uv run run_tests.py unit` is run
  **THEN** unit tests run in parallel with 90% coverage threshold

- **WHEN** `uv run run_tests.py integration` is run
  **THEN** integration tests run with real PostgreSQL, each worker getting its own schema

- **WHEN** `uv run run_tests.py e2e` is run
  **THEN** Playwright E2E tests run with isolated schemas

- **WHEN** `uv run run_tests.py all` is run
  **THEN** quality + unit + integration + e2e all execute

- **WHEN** `uv run run_tests.py python` is run
  **THEN** unit + integration tests execute

### REQ-02: Test Isolation

**Description**: Each test worker gets its own database schema for full isolation.

**Acceptance Scenarios**:

- **WHEN** integration or E2E tests start
  **THEN** a `ana-auth-test-{uuid}` schema is created per worker (session-scoped)

- **WHEN** tests complete
  **THEN** the test schema is dropped automatically

### REQ-03: Quality Gates

**Description**: Automated quality checks enforce code standards.

**Acceptance Scenarios**:

- **WHEN** unit test coverage is below 90%
  **THEN** the test run fails

- **WHEN** cyclomatic complexity exceeds C901 limit of 10
  **THEN** the quality check fails

### REQ-04: Test Fixtures

**Description**: pytest fixtures provide database sessions and test utilities.

**Acceptance Scenarios**:

- **WHEN** an integration test needs a database session
  **THEN** a function-scoped session with transaction isolation is provided

- **WHEN** an integration test needs an HTTP client
  **THEN** a test client with X-Schema header injection is provided

- **WHEN** a test needs a password hash
  **THEN** pre-computed TEST_PASSWORD and TEST_PASSWORD_HASH constants are available

## Constraints

- Unit tests: mocked dependencies, no DB access
- Integration tests: real PostgreSQL with parallel execution via pytest-xdist
- E2E tests: Playwright (Python), require running services
- Common flags: `--file <path>`, `-x` (stop on first failure), `-v` (verbose), `-c` (coverage)
- E2E flags: `--headed` (visible browser), `--debug` (Playwright Inspector)
