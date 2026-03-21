---
name: test-python-unit
description: Create pytest unit tests for backend services, repositories, and routers
---

# Backend Unit Test Creation

Create pytest unit tests for backend functionality following project testing patterns.

## When to Use

- Writing tests after implementing services, repositories, or routers
- Adding test coverage to existing backend code
- Testing error scenarios, edge cases, and validation logic

## File Structure

Tests mirror source structure with one folder per source file and one test file per method:

```
tests/
├── api/
│   └── services/
│       └── <service_name>/           # Unit tests (with mocking)
│           ├── test_<method>.py
│           └── conftest.py
├── shared/
│   └── db/repositories/
│       └── <domain>_repository/
│           └── <table>_repository/
│               ├── test_<method>.py
│               └── conftest.py
└── conftest.py                  # Global fixtures
```

## Test Types

### Service/Router Unit Tests
- **Use mocking** for dependencies (MagicMock, patch)
- **Test all scenarios**: happy path, edge cases, error handling
- **Use `db_session` fixture** which auto-rollbacks changes

### Repository Tests
- **Use real database** via `db_session` fixture
- **Test CRUD operations** and query methods
- **Auto-rollback** ensures isolation between tests

## Instructions

### 1. Create Test File
Create ONE test file at a time, following the naming pattern.

### 2. Run Test Immediately
```bash
uv run pytest <path/to/test_file.py> -v
```

### 3. Verify Zero Warnings
Fix any warnings before proceeding to next test.

### 4. Repeat
Only then create the next test file.

## Key Rules

1. **One folder per source file**: Each source file gets its own test folder
2. **One test file per method**: Each method gets its own test file
3. **Module-level functions only**: No class wrappers - use pytest functions
4. **Mirror structure**: Test folders mirror source structure exactly
5. **Test immediately**: Create ONE file, run, validate, then proceed
6. **Zero warnings**: All tests must pass with zero warnings
7. **AAA pattern**: Arrange, Act, Assert structure

## Database Lifecycle

- Database created **ONCE per pytest-xdist worker**
- Unit tests: rollback changes at end (via `db_session` fixture)
- Never recreate DB per test - too slow

## Running Tests

```bash
uv run pytest <path/to/test_file.py> -v     # Single file
uv run run_tests.py python                    # All Python tests
uv run run_tests.py python -cv                # With coverage
uv run run_tests.py quality                   # Quality checks
```

## Resources

- `resources/unit-test-patterns.md` - Complete examples for router, service, and repository unit tests, plus shared fixture (conftest.py) patterns

