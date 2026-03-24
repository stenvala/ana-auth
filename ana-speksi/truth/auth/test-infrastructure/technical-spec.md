# Technical Specification: Test Infrastructure

**Domain**: auth/test-infrastructure
**Last updated**: 2026-03-24

## Overview

pytest-based test infrastructure with xdist parallelism, schema-per-worker isolation, and a typer CLI orchestrator.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| test-python-unit | Governs unit test patterns for services, repositories, routers |
| test-python-integration | Governs integration test patterns for API workflows |
| test-playwright | Governs E2E test patterns with Page Object model |

## Architecture

```
src/tests/
  conftest.py         # Shared fixtures (schema creation, sessions, clients)
  unit/               # Unit tests (mocked deps, no DB)
  integration/        # Integration tests (real PostgreSQL)
  e2e/                # Playwright E2E tests
run_tests.py          # Typer CLI orchestrator
```

## Key Implementation Patterns

1. **Schema-per-worker**: Session-scoped fixture creates `ana-auth-test-{uuid}` schema, yields the suffix, drops on teardown.
2. **Function-scoped sessions**: Each test function gets a fresh DB session wrapped in a transaction for isolation.
3. **X-Schema injection**: Integration test client automatically includes `X-Schema` header pointing to the worker's schema.
4. **Pre-computed bcrypt hash**: `TEST_PASSWORD` and `TEST_PASSWORD_HASH` constants avoid expensive bcrypt computation during tests.
5. **Coverage enforcement**: Unit tests require 90% coverage; integration tests report coverage but do not enforce a threshold.
