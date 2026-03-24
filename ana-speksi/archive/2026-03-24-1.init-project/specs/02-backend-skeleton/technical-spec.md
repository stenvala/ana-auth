# Technical Specification: Backend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-techify

## Overview

Set up the FastAPI backend application with uv package management, SQLModel database integration with schema-based multitenancy, request-scoped database sessions via middleware, a health check endpoint, and Docker Compose for local PostgreSQL. Follows the events.3rdb.com sibling project patterns.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| create-web-app | Defines project scaffold structure, pyproject.toml, shared modules |
| backend-router | FastAPI router patterns -- health check endpoint at /api/health |
| backend-logger | Logging setup -- StructuredLogger, file-only logging |
| database-setup-postgres | DBContext pattern with schema-based multitenancy |
| database-model | SQLModel BaseDBModelMixin for ORM models |
| python-coding-conventions | Return DTOs not dicts, explicit types |

## Architecture

```
project root/
  pyproject.toml          # uv project definition with all dependencies
  uv.lock                 # locked dependencies
  docker-compose.yml      # PostgreSQL for local dev
  .nvmrc                  # Node.js 20.19 for Angular
  src/
    api/
      __init__.py
      main.py             # create_app() factory, lifespan, CORS, middleware
      middleware.py        # ApiMiddleware -- request-scoped DB session, schema routing
      routers/
        health.py         # GET /api/health
    shared/
      __init__.py
      db/
        __init__.py
        db_context.py     # DBContext class -- engine pool, schema multitenancy
        models/
          __init__.py
          base_model.py   # BaseDBModelMixin
      config.py           # Environment configuration (SCHEMA_SUFFIX, DB_*, ENV_TYPE, LOG_ROOT, STAGE)
```

### Key Patterns (from events.3rdb.com)

- **create_app() factory**: Returns FastAPI app with lifespan, CORS, middleware, routers
- **ApiMiddleware**: Creates DBContext per request, injects session into request.state, commits on success, rolls back on exception
- **DBContext**: Manages SQLAlchemy engine with connection pooling; schema via PostgreSQL `search_path` option in connection URL
- **Schema routing**: Default schema from `SCHEMA_SUFFIX` env var (defaults to "main"); overridden by `X-Schema` header in test/dev mode
- **Health check**: Simple GET /api/health returning `{"status": "ok"}`; no database dependency

## Data Model Changes

This story establishes the database connection infrastructure but does not create tables. Table creation is handled by story 04-database-schema.

## API Changes

### GET /api/health

- **Response 200**: `{"status": "ok"}`
- No authentication required
- No database dependency

## Implementation Approach

1. **Initialize uv project**: Create `pyproject.toml` with Python 3.13 requirement, all dependencies (fastapi, uvicorn, gunicorn, sqlmodel, psycopg2-binary, structlog, typer, bcrypt, pyyaml, pydantic), dev dependencies (pytest, pytest-xdist, pytest-cov, ruff, playwright)
2. **Create docker-compose.yml**: PostgreSQL 15 on localhost:5432, postgres/postgres credentials, persistent volume
3. **Create .nvmrc**: Contains `20.19.2`
4. **Create src/shared/config.py**: Environment configuration class reading from env vars with defaults
5. **Create src/shared/db/db_context.py**: DBContext with engine pooling, schema multitenancy via search_path
6. **Create src/shared/db/models/base_model.py**: BaseDBModelMixin with type conversion utilities
7. **Create src/api/main.py**: create_app() factory with lifespan, CORS (localhost:6785), router registration
8. **Create src/api/middleware.py**: ApiMiddleware for request-scoped sessions with auto commit/rollback
9. **Create src/api/routers/health.py**: Health check router at /api/health
10. **Run `uv sync`** to verify dependency resolution

## Testing Strategy

### Automated Tests

- Unit test for health check endpoint (mock client, verify 200 and response body)
- Unit test for DBContext initialization
- Integration test for health check via TestClient

### Manual Testing

- Start the backend with `uv run uvicorn api.main:app --port 6784`
- Verify `curl localhost:6784/api/health` returns `{"status": "ok"}`

## Out of Scope

- Authentication endpoints
- User management endpoints
- JWT signing logic
- Any business logic beyond health check

## Migration / Deployment Notes

- Backend runs on port 6784 locally and in production
- Production uses gunicorn with uvicorn workers
- SCHEMA_SUFFIX defaults to "main" if not set

## Security Considerations

- Database credentials for local dev are hardcoded (postgres/postgres) -- this is expected for Docker-based dev
- Production credentials come from environment variables, never committed to code
- X-Schema header override should only be active in non-production environments
