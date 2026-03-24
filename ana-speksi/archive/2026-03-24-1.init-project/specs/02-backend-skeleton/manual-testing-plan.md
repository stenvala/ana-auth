# Manual Testing Plan: Backend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21

## Test Scenarios

### Scenario 1: Backend starts and health check responds

**Preconditions**: Docker PostgreSQL running, uv dependencies installed

**Steps**:
1. Run `uv run uvicorn api.main:app --port 6784` from `src/` directory
2. Open browser or run `curl http://localhost:6784/api/health`

**Expected Result**: Response is `{"status": "ok"}` with HTTP 200

### Scenario 2: Backend starts without database

**Preconditions**: Docker PostgreSQL NOT running

**Steps**:
1. Run `uv run uvicorn api.main:app --port 6784` from `src/` directory
2. Run `curl http://localhost:6784/api/health`

**Expected Result**: Health check still returns 200 (no DB dependency in health check)

### Scenario 3: Docker Compose database

**Preconditions**: Docker installed

**Steps**:
1. Run `docker compose up -d`
2. Connect to `localhost:5432` with user `postgres`, password `postgres`
3. Verify connection succeeds

**Expected Result**: PostgreSQL accepts connections on localhost:5432

## Exploratory Testing Areas

- Verify CORS headers allow requests from localhost:6785
- Verify X-Schema header is respected in dev mode
