# Tasks: Backend Application Skeleton

**Status**: Accepted
**Generated with**: as-taskify
**Story**: 02-backend-skeleton

## Prerequisites

- None (first story to implement)

---

## Phase 1: Setup

### P01.T001 -- Initialize uv project with pyproject.toml

**Mandatory to use skills: /create-web-app**

Create `pyproject.toml` at the project root with:
- Python 3.13 requirement
- Dependencies: fastapi, uvicorn, gunicorn, sqlmodel, psycopg2-binary, structlog, typer, bcrypt, pyyaml, pydantic
- Dev dependencies: pytest, pytest-xdist, pytest-cov, ruff, playwright
- Project metadata (name: ana-auth)

Files:
- Create `pyproject.toml`

Verify: `uv sync` completes without errors.

- [ ] P01.T001

### P01.T002 -- Create Docker Compose for local PostgreSQL

**Mandatory to use skills: /create-web-app**

Create `docker-compose.yml` with PostgreSQL 15 service:
- Port: localhost:5432
- Credentials: postgres/postgres
- Persistent volume for data

Files:
- Create `docker-compose.yml`

Verify: `docker compose up -d` starts PostgreSQL.

- [ ] P01.T002

### P01.T003 -- Create .nvmrc for Node.js version

Create `.nvmrc` at project root containing `20.19.2`.

Files:
- Create `.nvmrc`

- [ ] P01.T003

---

## Phase 2: Implementation

### Service Layer

### P02.T001 -- Create shared config module

**Mandatory to use skills: /create-web-app, /python-coding-conventions**

Create `src/shared/config.py` reading environment variables with defaults:
- SCHEMA_SUFFIX (default: "main")
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME (defaults for local Docker)
- ENV_TYPE (default: "LOCAL")
- LOG_ROOT (default: "logs")
- STAGE (default: "local")
- API_PORT (default: 6784)

Files:
- Create `src/shared/__init__.py`
- Create `src/shared/config.py`

- [ ] P02.T001

### P02.T002 -- Create DBContext with schema-based multitenancy

**Mandatory to use skills: /database-setup-postgres, /python-coding-conventions**

Create `src/shared/db/db_context.py` following events.3rdb.com patterns:
- SQLAlchemy engine with connection pooling (pool_size=50, max_overflow=30, pool_recycle=3600, pool_pre_ping=True)
- Schema via PostgreSQL `search_path` option in connection URL
- Connection URL format: `postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?options=-c%20search_path%3D{schema_name}`
- Schema name format: `"ana-auth-{suffix}"`

Files:
- Create `src/shared/db/__init__.py`
- Create `src/shared/db/db_context.py`

- [ ] P02.T002

### P02.T003 -- Create BaseDBModelMixin

**Mandatory to use skills: /database-model**

Create `src/shared/db/models/base_model.py` with BaseDBModelMixin providing common fields and type conversion utilities for SQLModel classes.

Files:
- Create `src/shared/db/models/__init__.py`
- Create `src/shared/db/models/base_model.py`

- [ ] P02.T003

### API Layer

### P02.T004 -- Create ApiMiddleware for request-scoped DB sessions

**Mandatory to use skills: /create-web-app, /python-coding-conventions**

Create `src/api/middleware.py` following events.3rdb.com patterns:
- Creates DBContext per request
- Injects session into `request.state`
- Default schema from SCHEMA_SUFFIX env var
- Override via `X-Schema` header in non-production environments
- Commits on success, rolls back on exception

Files:
- Create `src/api/__init__.py`
- Create `src/api/middleware.py`

- [ ] P02.T004

### P02.T005 -- Create FastAPI application factory

**Mandatory to use skills: /create-web-app, /backend-logger**

Create `src/api/main.py` with `create_app()` factory:
- Lifespan context manager
- CORS configuration (allow localhost:6785 for dev)
- ApiMiddleware registration
- Router registration
- Structured logging setup

Files:
- Create `src/api/main.py`

- [ ] P02.T005

### P02.T006 -- Create health check router

**Mandatory to use skills: /backend-router**

Create `src/api/routers/health.py`:
- GET /api/health returning `{"status": "ok"}`
- No authentication required
- No database dependency

Files:
- Create `src/api/routers/__init__.py`
- Create `src/api/routers/health.py`

Verify: `cd src && uv run python -c "from api.main import app; print('OK')"` succeeds.

- [ ] P02.T006

---

## Phase 3: Test Automation

### Backend Tests

### P03.T001 -- Create health check unit test

**Mandatory to use skills: /test-python-unit**

Test health endpoint returns 200 with `{"status": "ok"}` using mocked client.

Files:
- Create `src/tests/__init__.py`
- Create `src/tests/unit/__init__.py`
- Create `src/tests/unit/api/__init__.py`
- Create `src/tests/unit/api/routers/__init__.py`
- Create `src/tests/unit/api/routers/test_health.py`

Verify: `uv run pytest src/tests/unit/api/routers/test_health.py -v` passes.

- [ ] P03.T001

### P03.T002 -- Create DBContext and config unit tests

**Mandatory to use skills: /test-python-unit**

- Test DBContext initializes with correct schema name
- Test Config class provides correct defaults for SCHEMA_SUFFIX, ports

Files:
- Create `src/tests/unit/shared/__init__.py`
- Create `src/tests/unit/shared/test_config.py`
- Create `src/tests/unit/shared/db/__init__.py`
- Create `src/tests/unit/shared/db/test_db_context.py`

Verify: `uv run pytest src/tests/unit/shared/ -v` passes.

- [ ] P03.T002

---

## Phase 4: Manual Verification

- Start the backend with `uv run uvicorn api.main:app --port 6784` from `src/`
- Verify `curl localhost:6784/api/health` returns `{"status": "ok"}`
- Verify Docker PostgreSQL is running with `docker compose up -d`
- Verify CORS headers are present in health check response
