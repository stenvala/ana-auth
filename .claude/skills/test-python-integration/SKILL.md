---
name: test-python-integration
description: Create pytest integration tests for complete API workflow validation
---

# Integration Test Creation

Create pytest integration tests that test complete user workflows via FastAPI TestClient.

## When to Use

- **Only when explicitly requested by the user**
- Testing end-to-end API flows that span multiple endpoints
- Verifying complete user workflows work correctly
- Testing features that require multiple services to coordinate

## What Integration Tests Are

Integration tests exercise the **complete stack** through API endpoints:

1. **Use TestClient** - make real HTTP requests to endpoints
2. **Use real database** - no mocking, actual data persistence
3. **Test happy-day flows** - no error case testing (that's for unit tests)
4. **Use `accounting_prerequisites`** fixture for common setup
5. **Session-scoped fixtures** - reuse setup across tests in same worker

## File Structure

Tests live in the integration test directory:

```
integration/
├── conftest.py                           # Shared fixtures (auth_headers, accounting_prerequisites)
├── <feature_name>/
│   ├── conftest.py                       # Feature-specific fixtures
│   └── test_<workflow_description>.py    # One file per workflow
```

## Key Fixtures

- **`test_client`** - FastAPI TestClient with test domain header set
- **`auth_headers`** - Login as admin and return authorization headers (session-scoped)
- **`accounting_prerequisites`** - Create workflow stage, dimension type, fiscal year, bank account (session-scoped)

## Key Rules

1. **Only happy-day scenarios** - error testing belongs in unit tests
2. **Test via endpoints** - never call services directly
3. **Use auth_headers** - all private endpoints need authentication
4. **Session-scoped prerequisites** - reuse accounting_prerequisites across tests
5. **Descriptive test names** - describe the workflow being tested
6. **Document setup and test steps** - clear docstrings explaining the flow
7. **One workflow per file** - keep tests focused

## What NOT to Test

Integration tests verify the **system works correctly end-to-end**. Do NOT test:
- Invalid input handling, authentication/authorization failures, database constraint violations, edge cases (all unit tests)

## Running Tests

```bash
# Run all integration tests
uv run pytest <integration-tests-dir>/ -v -m integration

# Run specific integration test
uv run pytest <integration-tests-dir>/feature/test_workflow.py -v
```

## Resources

- `resources/integration-test-example.py` - Complete integration test example with test pattern, fixture usage, and assertions

