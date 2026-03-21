# Tasks: MCC Infrastructure, Pipeline, and Multi-Stage Deployment

**Status**: Accepted
**Generated with**: as-taskify
**Story**: 06-mcc-pipeline

## Prerequisites

- 02-backend-skeleton must be complete (backend to build/deploy)
- 03-frontend-skeleton must be complete (frontend to build/deploy)
- 04-database-schema must be complete (setup_db.py for deploy)
- 05-test-infrastructure must be complete (run_tests.py for build)

---

## Phase 1: Setup

### P01.T001 -- Create MCC directory structure

Create the `mcc/` directory for stage configs and infrastructure templates.

Files:
- Create `mcc/` directory

- [ ] P01.T001

---

## Phase 2: Implementation

### Service Changes

### P02.T001 -- Create mcc_common.py

**Mandatory to use skills: /mcc-pipeline, /python-coding-conventions**

Create `mcc_common.py` at project root with:
- `run()` function that prints and executes shell commands
- Fails on non-zero exit code
- `--frozen` flag on non-macOS for uv sync

Files:
- Create `mcc_common.py`

- [ ] P02.T001

### P02.T002 -- Create mcc_config.py

**Mandatory to use skills: /mcc-pipeline, /python-coding-conventions**

Create `mcc_config.py` at project root with:
- YAML config loader reading from `mcc/conf-{stage}.yml`
- `{{VAR}}` template variable substitution
- Cycle detection for template variables

Files:
- Create `mcc_config.py`

- [ ] P02.T002

### P02.T003 -- Create stage configuration files

**Mandatory to use skills: /mcc-pipeline**

Create YAML config files for both stages:
- `mcc/conf-prod.yml`: REMOTE_USER, REMOTE_HOST, REMOTE_BASE (/home/stenvala/live/auth), SERVICE_NAME (ana-auth.service), DOMAIN (auth.mathcodingclub.com), DB_HOST, DB_PORT, DB_SCHEMA_SUFFIX (main), API_PORT (6784), CRON_JOBS
- `mcc/conf-dev.yml`: REMOTE_BASE (/home/stenvala/live/auth-dev), SERVICE_NAME (ana-auth-dev.service), DOMAIN (auth-dev.mathcodingclub.com), DB_SCHEMA_SUFFIX (dev), API_PORT (6785), no cron jobs

Files:
- Create `mcc/conf-prod.yml`
- Create `mcc/conf-dev.yml`

- [ ] P02.T003

### P02.T004 -- Create lint.py

**Mandatory to use skills: /mcc-pipeline, /python-coding-conventions**

Create `lint.py` at project root modeled after accounts/lint.py:
- `python` command: `ruff check --fix --unsafe-fixes` + `ruff format`
- `angular` command: `prettier --write` on `src/**/*.{ts,js,html,scss,css,json}`
- `--check-only` flag for CI (no auto-fix)

Files:
- Create `lint.py`

Verify: `uv run lint.py python` runs without error.

- [ ] P02.T004

### P02.T005 -- Create start_services.py

**Mandatory to use skills: /mcc-pipeline, /python-coding-conventions**

Create `start_services.py` at project root modeled after accounts/start_services.py:
- ServiceOrchestrator class with graceful shutdown
- Kill processes on required ports (6784, 6785) before starting
- Start API: `uv run uvicorn api.main:app --port 6784 --reload` from src/
- Start UI: `nvm use && npx ng serve --port 6785 --proxy-config proxy.conf.json` from src/ui/
- Staggered startup, output streaming, health checks

Files:
- Create `start_services.py`

- [ ] P02.T005

### P02.T006 -- Create after_api_change.py placeholder

**Mandatory to use skills: /create-web-app**

Create `after_api_change.py` at project root as a placeholder for future frontend type regeneration after API changes.

Files:
- Create `after_api_change.py`

- [ ] P02.T006

### P02.T007 -- Create mcc_build.py

**Mandatory to use skills: /mcc-pipeline, /python-coding-conventions**

Create `mcc_build.py` at project root:
- Run quality checks via run_tests.py
- Run unit tests with 90% coverage gate
- Run integration tests
- Build frontend: `nvm use && npx ng build`
- Assemble output directory: API source, UI dist, DB scripts, deploy scripts, configs
- `--no-tests` flag to skip test steps
- Support pyproject.toml, uv.lock, mcc/ configs in output

Files:
- Create `mcc_build.py`

Verify: `uv run mcc_build.py --no-tests` completes and creates output directory.

- [ ] P02.T007

### P02.T008 -- Create mcc_deploy.py

**Mandatory to use skills: /mcc-pipeline, /python-coding-conventions**

Create `mcc_deploy.py` at project root:
- `--stage` argument (prod, dev, clone-prod-to-dev)
- Versioned deployment: create `vrs-{timestamp}` directory
- Deploy API and UI files
- Sync virtual environment (`uv sync`)
- Create database schema if not exists (via setup_db.py)
- Apply pending migrations (checksum-tracked)
- Ensure master admin user
- Update symlinks (current-api, current-ui)
- Deploy cron jobs (prod only, MCC-AUTH marker)
- Set permissions for www-data
- Restart systemd service
- Smoke test (health check)
- Clean up old versions
- Clone-prod-to-dev stage

Files:
- Create `mcc_deploy.py`

- [ ] P02.T008

### P02.T009 -- Create systemd service template

**Mandatory to use skills: /mcc-infra**

Create `mcc/daemon.template` with `{{PLACEHOLDER}}` syntax:
- Gunicorn + uvicorn workers
- www-data user
- Environment variables (SCHEMA_SUFFIX, LOG_ROOT, ENV_TYPE, STAGE)
- Configurable API_PORT, WORKERS, REMOTE_BASE, API_SYMLINK

Files:
- Create `mcc/daemon.template`

- [ ] P02.T009

### P02.T010 -- Create nginx config template

**Mandatory to use skills: /mcc-infra**

Create `mcc/nginx.template` with `{{PLACEHOLDER}}` syntax:
- Rate limiting (10r/s with burst 20)
- Proxy /api/ to localhost:{{API_PORT}}
- Serve Angular build from {{UI_SYMLINK}}/browser/
- Cache control: 1y for assets (immutable), no-cache for index.html
- Security headers
- SSL via Certbot placeholder
- Angular SPA routing (try_files to index.html)

Files:
- Create `mcc/nginx.template`

- [ ] P02.T010

### P02.T011 -- Create deploy_server.py

**Mandatory to use skills: /mcc-infra, /python-coding-conventions**

Create `mcc/deploy_server.py` modeled after accounts:
- `render_template()` -- replaces `{{KEY}}` placeholders with config values
- `generate_service_config()` -- renders daemon.template per stage
- `generate_nginx_config()` -- renders nginx.template per stage
- `upload_configuration_files()` -- uploads both via Fabric/SSH
- `setup_backend_daemons()` -- enables/restarts systemd services
- `setup_nginx()` -- certbot SSL setup, symlinks, test, restart
- `main()` -- orchestrates setup for both prod and dev stages

Files:
- Create `mcc/deploy_server.py`

- [ ] P02.T011

### P02.T012 -- Copy ensure_admin.sql to MCC directory

**Mandatory to use skills: /mcc-pipeline**

Copy or symlink the ensure_admin.sql to `mcc/ensure_admin.sql` so the deploy script can access it from the packaged output.

Files:
- Create `mcc/ensure_admin.sql` (or symlink to `src/shared/db/schema/ensure_admin.sql`)

- [ ] P02.T012

---

## Phase 3: Test Automation

### Backend Tests

### P03.T001 -- Create mcc_config.py unit tests

**Mandatory to use skills: /test-python-unit**

Test template variable resolution:
- Simple substitution
- Nested variable substitution
- Cycle detection error

Files:
- Create `src/tests/unit/test_mcc_config.py`

Verify: `uv run pytest src/tests/unit/test_mcc_config.py -v` passes.

- [ ] P03.T001

---

## Phase 4: Manual Verification

- Run `uv run mcc_build.py --no-tests` and verify output directory structure
- Run `uv run mcc_build.py` and verify full build pipeline (quality + tests + build)
- Verify `mcc/conf-prod.yml` and `mcc/conf-dev.yml` have correct values
- Verify templates render correctly by running deploy_server.py render functions
- Run `uv run lint.py python` and verify ruff runs
- Run `uv run start_services.py` and verify both services start
