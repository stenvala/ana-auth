# Technical Specification: MCC Infrastructure, Pipeline, and Multi-Stage Deployment

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-techify

## Overview

Create the complete MCC build/deploy pipeline and server infrastructure using best-of-breed patterns from sibling projects. Primary references: **accounts** (most mature deploy with versioned directories, symlinks, multi-step pipeline, smoke tests) and **events.3rdb.com** (PostgreSQL-specific: schema setup, deployment log with checksums, nginx/systemd patterns). Includes mcc_build.py, mcc_deploy.py, mcc_common.py, mcc_config.py, lint.py, start_services.py, stage configuration (YAML), systemd services, nginx configs. Two stages on one server: auth.mathcodingclub.com (prod) and auth-dev.mathcodingclub.com (dev).

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| mcc-pipeline | Build and deploy script patterns (mcc_build.py, mcc_deploy.py, mcc_common.py) |
| mcc-infra | Server infrastructure -- systemd, nginx, SSL, deploy_server.py |
| database-setup-postgres | DB setup integration -- schema creation during deploy |
| python-coding-conventions | Script code quality |

## Architecture

```
project root/
  mcc_build.py                    # Build orchestration (runs on CI)
  mcc_deploy.py                   # Deploy script (runs on remote server)
  mcc_common.py                   # Shared utilities (run command helper)
  mcc_config.py                   # Configuration loader with template resolution
  lint.py                         # Ruff/Prettier wrapper
  start_services.py               # Local dev service orchestrator
  after_api_change.py             # Frontend type regeneration (placeholder)
  mcc/
    conf-prod.yml                 # Production stage config
    conf-dev.yml                  # Development stage config
    deploy_server.py              # Server infrastructure setup (Fabric/SSH)
    daemon.template               # Single systemd service template (rendered per stage)
    nginx.template                # Single nginx config template (rendered per stage)
    ensure_admin.sql              # Master admin user SQL (idempotent)
```

### Stage Configuration

**Production (conf-prod.yml)**:
- REMOTE_USER: stenvala
- REMOTE_HOST: mathcodingclub.com
- REMOTE_BASE: /home/stenvala/live/auth
- SERVICE_NAME: ana-auth.service
- DOMAIN: auth.mathcodingclub.com
- DB_HOST: 192.168.0.x (LAN)
- DB_PORT: 5432
- DB_SCHEMA_SUFFIX: main
- API_PORT: 6784
- CRON_JOBS: daily backup

**Development (conf-dev.yml)**:
- REMOTE_BASE: /home/stenvala/live/auth-dev
- SERVICE_NAME: ana-auth-dev.service
- DOMAIN: auth-dev.mathcodingclub.com
- DB_SCHEMA_SUFFIX: dev
- API_PORT: 6785
- No cron jobs

### Build Pipeline (mcc_build.py)

1. Run quality checks (`uv run run_tests.py quality`)
2. Run unit tests with 90% coverage gate (`uv run run_tests.py unit --coverage`)
3. Run integration tests (`uv run run_tests.py integration`)
4. Build frontend (`nvm use && npx ng build`)
5. Copy backend source to output/
6. Copy database scripts to output/
7. Copy deployment scripts to output/
8. Copy pyproject.toml, uv.lock, config files to output/
9. Support `--no-tests` flag to skip steps 1-3

### Deploy Pipeline (mcc_deploy.py)

1. Read stage config from `mcc/conf-{stage}.yml`
2. Create versioned directory (`vrs-{timestamp}`)
3. Deploy API and UI files
4. Sync virtual environment (`uv sync`)
5. Create database schema if not exists
6. Apply pending migrations (checksum-tracked)
7. Ensure master admin user
8. Update symlinks (current-api, current-ui)
9. Deploy cron jobs (prod only)
10. Set permissions for www-data
11. Restart systemd service
12. Run smoke test (health check)
13. Clean up old versions

### Clone-Prod-to-Dev Stage

Non-deployment stage: copies ana-auth-main schema data to ana-auth-dev schema on the remote database. Drops and recreates dev schema, copies all tables and sequences.

### Infrastructure

### Template-Based Infrastructure (accounts pattern)

A single `daemon.template` and single `nginx.template` with `{{PLACEHOLDER}}` syntax. `deploy_server.py` renders them with values from the stage's YAML config. This avoids duplicating config files per stage.

**daemon.template** (systemd, rendered per stage):
```ini
[Service]
User=www-data
WorkingDirectory={{API_SYMLINK}}
ExecStart={{REMOTE_BASE}}/.venv/bin/gunicorn api.main:app \
    --workers {{WORKERS}} \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:{{API_PORT}} \
    --access-logfile {{REMOTE_BASE}}/logs/access.log \
    --error-logfile {{REMOTE_BASE}}/logs/error.log
Environment="SCHEMA_SUFFIX={{DB_SCHEMA_SUFFIX}};LOG_ROOT={{REMOTE_BASE}}/logs;ENV_TYPE=PROD;STAGE={{STAGE}}"
```

**nginx.template** (rendered per stage):
- Rate limiting (10r/s with burst 20)
- Proxy /api/ to localhost:{{API_PORT}}
- Serve Angular build from {{UI_SYMLINK}}/browser/
- Cache control: 1y for assets with immutable flag, no-cache for index.html
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- SSL via Certbot
- Angular SPA routing (try_files to index.html)

**deploy_server.py** renders both templates for each stage, uploads via Fabric/SSH, and handles:
- SSL certificate setup (certbot standalone for first-time, nginx plugin for renewal)
- Systemd enable/restart
- Nginx symlink creation, test, and restart

## Data Model Changes

None directly -- this story deploys the schema created by story 04.

## API Changes

None -- the deploy script interacts with the health check endpoint for smoke testing.

## Implementation Approach

1. **Create mcc_common.py**: `run()` function that prints and executes shell commands, fails on non-zero exit
2. **Create mcc_config.py**: YAML config loader with `{{VAR}}` template variable substitution, cycle detection
3. **Create mcc_build.py**:
   - TestRunner integration for quality + unit + integration
   - Frontend build with nvm use + npx ng build
   - Output directory assembly (API source, UI dist, DB scripts, deploy scripts, configs)
   - `--no-tests` flag
4. **Create mcc_deploy.py**:
   - `--stage` argument (prod, dev, clone-prod-to-dev)
   - Versioned deployment with symlinks
   - Database setup: schema creation, migration application with checksum tracking
   - Admin user ensuring
   - Cron job deployment (prod only, MCC-AUTH marker)
   - Service restart and smoke test
   - Old version cleanup
5. **Create stage config files** (conf-prod.yml, conf-dev.yml):
   - All deployment parameters with template variables
6. **Create daemon.template**: Single systemd service template with `{{PLACEHOLDER}}` syntax (API_SYMLINK, REMOTE_BASE, API_PORT, WORKERS, DB_SCHEMA_SUFFIX, STAGE, LOG_ROOT)
7. **Create nginx.template**: Single nginx config template with `{{PLACEHOLDER}}` syntax (DOMAIN, API_PORT, UI_SYMLINK) -- rate limiting, SSL, security headers, SPA routing
8. **Create deploy_server.py** (modeled after accounts/mcc/deploy_server.py):
   - `render_template()` -- replaces `{{KEY}}` placeholders with config values
   - `generate_service_config()` -- renders daemon.template per stage
   - `generate_nginx_config()` -- renders nginx.template per stage
   - `upload_configuration_files()` -- uploads both via Fabric/SSH
   - `setup_backend_daemons()` -- enables/restarts systemd services
   - `setup_nginx()` -- certbot SSL setup (standalone first-time, nginx plugin renewal), symlinks, test, restart
   - `main()` -- orchestrates setup for both prod and dev by loading both conf-prod.yml and conf-dev.yml
9. **Create lint.py** (modeled after accounts/lint.py):
   - Two commands: `python` (ruff check --fix --unsafe-fixes + ruff format) and `angular` (prettier --write on `src/**/*.{ts,js,html,scss,css,json}`)
   - `--check-only` flag for CI (no auto-fix)
   - Explicit display of results, proper exit code propagation
10. **Create start_services.py** (modeled after accounts/start_services.py):
   - ServiceOrchestrator class with graceful shutdown
   - Kill processes on required ports (6784, 6785) before starting
   - Start API: `uv run uvicorn api.main:app --port 6784 --reload` from src/
   - Start UI: `nvm use && npx ng serve --port 6785 --proxy-config proxy.conf.json` from src/ui/
   - Staggered startup with 1s delay between services
   - Output streaming to logger, unified logging to console and file
   - Health checks before declaring "ready"
11. **Create after_api_change.py**: Placeholder for frontend type regeneration

## Testing Strategy

### Automated Tests

- Unit test: mcc_config.py template variable resolution
- Unit test: mcc_build.py output directory structure verification (with mocked commands)
- Integration test: mcc_deploy.py database setup commands (against local PostgreSQL)

### Manual Testing

- `uv run mcc_build.py --no-tests` -- verify output directory structure
- `uv run mcc_build.py` -- verify full build pipeline
- Deploy to dev stage and verify service starts, health check passes
- Deploy to prod stage and verify cron job installed

## Out of Scope

- CI/CD pipeline setup (user does this separately)
- Blue-green or zero-downtime deployments
- Container-based deployments
- Monitoring or alerting

## Migration / Deployment Notes

- Both stages share the same physical server
- Prod port: 6784, Dev port: 6785
- Database is on LAN, not localhost -- deploy script connects directly
- First deployment creates the schema and admin user automatically
- Subsequent deployments apply only new migrations

## Security Considerations

- Database credentials in YAML configs must not be committed with real passwords; use placeholder values in the repo
- SSH keys for deployment should be pre-configured on the server
- Nginx config includes security headers (X-Frame-Options DENY, X-Content-Type-Options nosniff)
- Rate limiting on API endpoints prevents brute-force attacks
- SSL/TLS via Certbot for HTTPS
