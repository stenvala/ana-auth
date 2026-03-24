# Technical Research: 1.init-project

**Created**: 2026-03-21

## Research Objectives

- What project structure and tooling patterns do the sibling projects use?
- How should schema-based multitenancy work with PostgreSQL?
- What MCC build/deploy patterns must be followed?
- How should test infrastructure be set up for parallel execution with isolated schemas?
- What Angular 21 and Material Design 3 patterns apply to the frontend skeleton?
- How should the backup and retention system work?

## Codebase Analysis

### Existing Patterns

This is a greenfield project. The `ana-speksi/truth/` directory is empty -- no existing data models, enums, or documentation. The entire codebase will be created from scratch during the codify phase.

### Sibling Projects Reference

Four sibling projects provide reference patterns. Each has different strengths:

| Project | Database | Multitenancy | Test Maturity | MCC Maturity |
|---------|----------|-------------|---------------|-------------|
| **events.3rdb.com** | PostgreSQL | Schema-based (search_path) | Moderate | Good (original patterns) |
| **accounts** | SQLite | Per-domain files | Most mature (run_tests.py, conftest.py) | Most mature (multi-domain deploy) |
| **content-management-system** | SQLite | Per-domain files | Moderate | Moderate |
| **mcc-ci-cd** | SQLite | Single DB | Basic | Includes worker service |

**Best-of-breed selection for ana-auth:**

- **run_tests.py**: From **accounts** -- most sophisticated TestRunner class with parallel execution, JUnit XML output, E2E retries, per-worker DB setup, separate commands for quality/ruff/ty/cc/unit/int/e2e/python/all
- **conftest.py**: From **accounts** -- worker-scoped database isolation, test client with header injection, seeded fixtures, session rollback for unit tests
- **lint.py**: From **accounts** -- two commands (`python` and `angular`), ruff check --fix + ruff format for Python, prettier for Angular
- **start_services.py**: From **accounts** -- starts API (uvicorn) and UI (ng serve) simultaneously, port conflict resolution (kills processes on ports), graceful shutdown with signal handlers, health checks
- **mcc_build.py**: Composite of **accounts** (E2E orchestration, JUnit output) and **events.3rdb.com** (PostgreSQL-specific patterns)
- **mcc_deploy.py**: From **accounts** -- versioned directories with symlinks, multi-step: copy API/UI, sync venv, update symlinks, refresh DB, run migrations, seed admin, deploy backup/cron, set permissions, restart service, smoke test
- **mcc_common.py**: Shared across all projects -- simple `run()` function with `--frozen` flag on non-macOS
- **mcc_config.py / config_loader.py**: From **events.3rdb.com** -- YAML with `{{VAR}}` template substitution, cycle detection
- **setup_db.py**: Hybrid -- accounts has most mature migration tracking (id, name, applied_at), events.3rdb.com has PostgreSQL schema patterns
- **Middleware**: From **accounts** -- ApiMiddleware resolves schema from `X-Schema` header (test) or env var (prod), creates DBContext, opens session, injects into request.state
- **Type checking**: Use **ty** (not mypy) -- per CLAUDE.md, mypy is not allowed

Key patterns from **accounts** project:
- **Root scripts**: `mcc_build.py`, `mcc_deploy.py`, `mcc_common.py`, `lint.py`, `run_tests.py`, `start_services.py`, `setup_db.py` all at project root
- **MCC directory**: `mcc/` contains stage configs, infrastructure templates, deploy_server.py, SQL scripts
- **Source layout**: `src/api/` (FastAPI), `src/shared/` (DB context, models, DTOs), `src/tests/` (unit, integration, e2e)
- **App factory**: `create_app()` with lifespan, CORS, middleware, router registration
- **Health check**: `GET /api/public/health/health` (public prefix pattern)
- **Versioned deploy**: `vrs-{timestamp}` directories with `current-api`/`current-ui` symlinks
- **Backup scripts**: Deployed via cron with marker-based crontab management

Key patterns from **events.3rdb.com** project:
- **PostgreSQL-specific**: Schema-based multitenancy via `search_path`, deployment log with checksums
- **DBContext**: Engine pooling (pool_size=50, max_overflow=30, pool_recycle=3600)
- **Nginx**: Rate limiting, WebSocket support, security headers, cache control
- **Systemd**: gunicorn + uvicorn worker, www-data user, environment variables

### Integration Points

Since this is a greenfield project, integration points are external:

- **PostgreSQL**: Docker locally (localhost:5432), LAN server in production (192.168.0.x:5432)
- **MCC pipeline service**: Will be configured separately by the user for CI/CD
- **DNS**: auth.mathcodingclub.com and auth-dev.mathcodingclub.com
- **SSL**: Certbot/Let's Encrypt on the deployment server

## External Research

### PostgreSQL Schema-Based Multitenancy

The events.3rdb.com project uses `search_path` for schema isolation:

```python
# Connection URL pattern
f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?options=-c%20search_path%3D{schema_name}"
```

Schema naming convention: `ana-auth-{suffix}` where suffix is `main`, `dev`, `e2e`, or `test-{uuid}`.

### SQLModel with PostgreSQL

SQLModel 0.0.22+ integrates with SQLAlchemy 2.x. Key pattern from events.3rdb.com:

```python
engine = create_engine(
    connection_url,
    pool_size=50,
    max_overflow=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

### MCC Deploy Versioning Pattern

The deploy script uses timestamp-based versioning with symlinks:

```
live/auth/
  vrs-2026-03-21T120000/   # versioned deployment
  current-api -> vrs-.../   # symlink
  current-ui -> vrs-.../    # symlink
  .venv/                    # shared virtual environment
  backup/                   # backup directory (prod only)
  logs/                     # application logs
```

### SQL Deployment Log Tracking

Schema versioning uses a deployment log table with file checksums:

```sql
CREATE TABLE IF NOT EXISTS _deployment_log (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    checksum TEXT NOT NULL,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This prevents redundant SQL execution on re-deploy.

### Angular 21 with Material Design 3

Angular 21 uses the signals API for reactivity. Material Design 3 theming uses:

```scss
@use '@angular/material' as mat;

$theme: mat.theme(
  (
    color: (
      primary: mat.$violet-palette,
      tertiary: mat.$cyan-palette,
    ),
    typography: Roboto,
    density: 0,
  )
);

html {
  @include mat.all-component-themes($theme);
  color-scheme: dark;
}
```

Custom palettes can be generated with `npx ng generate @angular/material:theme-color`.

### Backup with pg_dump and Retention

```bash
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -n "ana-auth-main" $DB_NAME | gzip > "$BACKUP_DIR/$(date +%Y-%m-%d)-main.gz"
```

Retention logic: keep files where `age <= 30 days` OR `day == last_day_of_month AND age <= 365 days`.

### Bcrypt Password Hashing

For the master admin user, use a pre-computed bcrypt hash (cost factor 12). The hash is embedded in the SQL script -- never computed at runtime during deployment.

## Third-Party Dependencies

| Dependency | Purpose | License | Acceptable? | Alternatives |
|------------|---------|---------|-------------|--------------|
| fastapi | Web framework | MIT | Yes | None needed |
| uvicorn | ASGI server | BSD-3-Clause | Yes | None needed |
| gunicorn | Production WSGI/ASGI | MIT | Yes | None needed |
| sqlmodel | ORM (SQLAlchemy wrapper) | MIT | Yes | None needed |
| psycopg2-binary | PostgreSQL adapter | LGPL-2.1 | Yes (binary distribution) | psycopg[binary] (BSD) |
| typer | CLI framework | MIT | Yes | None needed |
| structlog | Structured logging | MIT/Apache-2.0 | Yes | None needed |
| bcrypt | Password hashing | Apache-2.0 | Yes | None needed |
| pydantic | Data validation | MIT | Yes | None needed |
| ruff | Linting/formatting | MIT | Yes | None needed |
| ty | Type checking | MIT | Yes | None needed |
| pytest | Testing | MIT | Yes | None needed |
| pytest-xdist | Parallel test execution | MIT | Yes | None needed |
| pytest-cov | Coverage reporting | MIT | Yes | None needed |
| playwright | E2E browser testing | Apache-2.0 | Yes | None needed |
| pyyaml | YAML config parsing | MIT | Yes | None needed |
| @angular/core | Frontend framework | MIT | Yes | None needed |
| @angular/material | UI components | MIT | Yes | None needed |

### Dependency Alternatives Analysis

#### PostgreSQL Adapter

| Criteria | psycopg2-binary | psycopg[binary] |
|----------|----------------|-----------------|
| License | LGPL-2.1 | BSD-3-Clause |
| Maintenance | Stable, widely used | Newer psycopg3, active |
| API | SQLAlchemy well-tested | SQLAlchemy supported |
| Performance | Good | Better (async native) |

**Recommendation**: Use psycopg2-binary for consistency with events.3rdb.com. The LGPL license is acceptable for binary distribution usage (no modifications to the library itself).

## Relevant Skills

| Skill | Relevance |
|-------|-----------|
| create-web-app | Full-stack scaffold -- defines project structure, scripts, shared modules |
| backend-router | FastAPI router patterns -- health check endpoint |
| backend-service | Service layer patterns -- will be needed for future stories but establishes conventions |
| backend-logger | Logging patterns -- StructuredLogger, file-only logging |
| database-setup-postgres | PostgreSQL setup script (setup_db.py) with schema multitenancy |
| database-schema-edit-postgres | SQL schema conventions -- table definitions, migrations |
| database-model | SQLModel class definitions -- BaseDBModelMixin patterns |
| database-repository | Repository pattern -- data access layer conventions |
| database-design | Data model documentation structure |
| frontend-component | Angular component patterns -- OnPush, standalone, data-test-id |
| frontend-store | Signal-based state management |
| mcc-pipeline | Build and deploy scripts (mcc_build.py, mcc_deploy.py) |
| mcc-infra | Server infrastructure (systemd, nginx, SSL) |
| test-python-unit | Unit test patterns with mocking |
| test-python-integration | Integration test patterns with real DB |
| test-playwright | E2E test patterns with Page Objects |
| python-coding-conventions | Return DTOs not dicts, explicit types |

## Technical Constraints

1. **Port allocation**: Backend on 6784 (prod) and 6785 (dev); frontend dev server on 6785 (needs separate port from prod backend). Local dev: API on 6784, UI on 6785 with proxy to 6784.
2. **Node.js version**: Angular 21 requires Node.js 20.19 via nvm; `.nvmrc` must be in project root.
3. **Python version**: 3.13+ required; all commands via `uv run`.
4. **Same physical server**: Both prod and dev stages share one server -- different ports, paths, and systemd services.
5. **Database on LAN**: Production PostgreSQL at 192.168.0.x:5432, not localhost. Deploy script connects directly.
6. **No `src/ui/` in Python path**: Frontend is a separate Angular project under `src/ui/`; Python source is under `src/api/` and `src/shared/`.

## Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Best-of-breed from all sibling projects | Each project excels at different things; pick the best patterns from each | Following only one project -- misses improvements from newer projects |
| run_tests.py from accounts | Most mature: JUnit XML, E2E retries, per-worker DB, comprehensive commands | events.3rdb.com version -- less sophisticated |
| lint.py from accounts | Clean two-command design (python + angular), ruff fix + format | CMS version -- uses mypy (not allowed per CLAUDE.md) |
| ty for type checking (not mypy) | Per CLAUDE.md: mypy not allowed. ty is fast and sufficient | mypy -- explicitly prohibited |
| PostgreSQL schema-based multitenancy | Matches functional spec, proven in events.3rdb.com, supports test isolation | Per-domain files (accounts pattern) -- not applicable to PostgreSQL |
| Pre-computed bcrypt hash for admin user | Avoids runtime dependency on bcrypt during deploy, idempotent SQL | Runtime hash -- adds dependency, slower deploy |
| Timestamp-based versioning with symlinks | Proven across all sibling projects, easy rollback, atomic switch | Git-based versioning -- more complex |
| Two config files (conf-dev.yml, conf-prod.yml) | Clear separation, template variables for DRY | Single config with env overrides -- less explicit |
| Gunicorn + uvicorn workers for production | Standard FastAPI production setup, proven in events.3rdb.com | Bare uvicorn -- no worker management |
| Ruff for linting + formatting, ty for type checking | Fast, comprehensive. Ruff across all projects, ty per CLAUDE.md | Flake8 + mypy -- slower, mypy not allowed |
| start_services.py from accounts | Port conflict resolution, graceful shutdown, health checks | CMS version -- async-based, more complex |

## Risks

1. **Angular 21 availability**: The spec assumes Angular 21 is published. If not yet available, the frontend skeleton may need to target Angular 20 and upgrade later.
2. **Port conflicts on shared server**: Both stages on one server require careful port allocation to avoid conflicts. Mitigated by explicit port configuration in stage YAML files.
3. **PostgreSQL schema name with hyphens**: Schema names containing hyphens must be quoted in SQL (`"ana-auth-main"`). The sibling project handles this correctly -- follow the same pattern.
4. **E2E test complexity**: Each E2E worker needs its own schema AND a running FastAPI instance. This adds startup overhead and port management complexity.
5. **psycopg2-binary on production**: The binary package may not work on all Linux distributions. If issues arise, switch to psycopg2 with libpq-dev installed.
