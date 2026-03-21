# Test Automation Plan: Backend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21

## Test Categories

### Unit Tests

| Test | Description | Priority |
|------|-------------|----------|
| test_health_returns_ok | Health endpoint returns 200 with {"status": "ok"} | High |
| test_db_context_init | DBContext initializes with correct schema name | Medium |
| test_config_defaults | Config class provides correct defaults for SCHEMA_SUFFIX, ports | Medium |

### Integration Tests

| Test | Description | Priority |
|------|-------------|----------|
| test_health_endpoint_via_client | Health check via TestClient returns 200 | High |
| test_middleware_creates_session | ApiMiddleware creates db_session in request.state | Medium |

### End-to-End Tests

None for this story -- E2E tests are covered in story 05.

## Test Data Requirements

- No database data required (health check is DB-independent)
- Mock DBContext for unit tests

## Coverage Goals

- 90% unit test coverage for all backend skeleton code
