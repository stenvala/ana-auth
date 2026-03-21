# Proposal: 1.init-project

**Ticket**: 1
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-new

## Original Prompt

Source: GitHub Issue #1

I want to create new service ana-auth. This is like cognito or entra id, but just my private oauth service that allows other of my private services to authenticate via this in sso method. I don't at least yet want to manage any permissions in this service, just the authentication and jwt signing. I'm not expert in this area so you need to help me a bit. I need some admin user interface that allows me to manage users. Then I need to have SSO sign in form and how I pass the token to other service and how that other service get the user details givenName, familyName, displayName, userId, email to the other service. (so when user signs in, user must accept that these are given to the other user). Then I want to have token refresh possibilities etc. Other backends can with refresh token get new auth token and with valid auth token get the named fields.

In this first item, just write README.md that tells what the project is about and create application skeleton. We want to use Python 3.13, Angular 21 and PostgreSQL. Project skeleton also includes mcc infrastructure and pipeline. I want to use domain https://auth.mathcodingclub.com so set all these up. I'll then set up the ci-cd pipeline in the pipeline service.

## Problem Statement

The developer needs a private SSO/OAuth authentication service (ana-auth) to provide centralized authentication for multiple private services. Currently there is no shared authentication mechanism, meaning each service would need its own user management. ana-auth will act as a single identity provider -- similar to Cognito or Entra ID but privately owned and controlled -- handling user authentication, JWT signing, and token management. This first ticket focuses on establishing the project foundation: a README describing the service vision, a working application skeleton with build/deploy infrastructure, test infrastructure, an initial user database schema, and a master admin user.

## User Stories (High Level)

### US1: Project README

**Why**: A clear README gives anyone looking at the repository an immediate understanding of what ana-auth is, what it does, and what technology stack it uses, setting the foundation for all future development.

### US2: Backend Application Skeleton

**Why**: A working FastAPI skeleton with project structure, database connection setup, and health check endpoint provides the starting point for implementing authentication endpoints. Uses uv for package management.

### US3: Frontend Application Skeleton

**Why**: A working Angular 21 skeleton provides the starting point for building the admin UI and SSO sign-in form.

### US4: Database Schema and Multitenant Setup

**Why**: A PostgreSQL database setup using schema-per-tenant isolation (e.g., `ana-auth-main`, `ana-auth-dev`, `ana-auth-e2e`) enables running dev and prod on the same server and gives each integration test runner its own isolated schema. The initial user schema defines the tables needed for user management (user accounts, emails). A master admin user is created idempotently so the system is usable from first deployment.

### US5: Test Infrastructure

**Why**: A complete test setup with unit tests, integration tests, and E2E tests -- orchestrated by run_tests.py and executed during builds -- ensures quality from the start. Unit/integration tests run in parallel with isolated PostgreSQL schemas per test worker. Quality gates (ruff linting, ty type checking, complexity checks, 90% coverage) prevent regressions.

### US6: MCC Infrastructure, Pipeline, and Multi-Stage Deployment

**Why**: Having build and deploy scripts (mcc_build.py, mcc_deploy.py, mcc_common.py, mcc_config.py, lint.py, run_tests.py, start_services.py, mcc/deploy_server.py) and infrastructure configuration (systemd, nginx) for two stages -- auth-dev.mathcodingclub.com (dev) and auth.mathcodingclub.com (prod) -- on the same physical server means the service can be deployed from day one. The deploy script handles database schema creation and master user setup if they don't exist.

### US7: Database Backup with Automated Retention

**Why**: Automated daily database backups with retention policy (30 rolling days + last day of each month for a year) protect against data loss. Backups run via cron on the production stage only, stored at the deployment's backup folder.

## Functional Requirements (High Level)

- FR1: README.md documents the project purpose (private SSO/OAuth service), planned features (user management, SSO sign-in, JWT tokens, token refresh, user info endpoint), technology stack (Python 3.13, Angular 21, PostgreSQL), and domains (auth.mathcodingclub.com, auth-dev.mathcodingclub.com)
- FR2: Backend skeleton runs with a health check endpoint responding successfully; all commands use `uv run`
- FR3: Frontend skeleton builds and serves a landing page
- FR4: Database setup script (typer CLI) supports multitenant schemas via suffix: create, drop, and related commands -- each creating/managing a PostgreSQL schema like `ana-auth-{suffix}`
- FR5: Initial user schema SQL defines tables for user accounts (id, user_name, password_hash, given_name, family_name, display_name, email, created_at, updated_at)
- FR6: Master admin user creation via idempotent SQL script (INSERT ... ON CONFLICT DO NOTHING pattern), run as part of schema setup and during deployment
- FR7: `run_tests.py` orchestrates three test levels via typer CLI:
  - `quality`: ruff linting, ruff import sorting, ty type checking, ruff cyclomatic complexity check (C901 limit 10, fails build if exceeded)
  - `python`: unit and integration tests with pytest, parallel execution (`-n auto`, each worker gets its own schema), coverage reporting (90% minimum threshold, fails build if not reached)
  - `e2e`: E2E tests with a fixed `ana-auth-e2e` schema, reset before run
  - `all`: runs all of the above
- FR8: Test conftest.py fixtures provide:
  - Session-scoped schema creation with UUID suffix and automatic teardown for unit/integration tests
  - Function-scoped database sessions for transaction isolation
  - Integration test client with X-Schema header injection
  - Pre-computed bcrypt test password hash for fast test execution
- FR9: `mcc_build.py` runs quality checks and unit/integration tests (with `--no-tests` escape hatch), then builds frontend and backend, packages for deployment
- FR10: `mcc_deploy.py` deploys the application, creates the database schema if it doesn't exist, ensures master admin user exists, and deploys cron jobs for prod stage. Connects to remote PostgreSQL directly on LAN (192.168.0.x:5432)
- FR11: Schema versioning via SQL file checksum and deployment log table to prevent redundant deployments
- FR12: Infrastructure configuration supports two stages on the same server: auth-dev.mathcodingclub.com (dev) and auth.mathcodingclub.com (prod) with separate systemd services, nginx configs, and SSL certificates
  - Prod deploys to `live/auth/`, dev deploys to `live/auth-dev/`
- FR13: MCC scripts follow the patterns from the sibling events.3rdb.com project (mcc_build.py, mcc_deploy.py, mcc_common.py, mcc_config.py, lint.py, run_tests.py, start_services.py, mcc/deploy_server.py)
- FR14: Local development uses Docker for PostgreSQL (docker-compose.yml with postgres service on localhost:5432) -- no special local initialization script needed
- FR15: Stage-specific configuration via YAML files (conf-dev.yml, conf-main.yml) with database host, port, schema suffix, and other deployment parameters
- FR16: Database backup script using pg_dump piped through gzip, producing daily compressed backups
- FR17: Backup retention policy: keep last 30 daily backups + last day of each month for 12 months
- FR18: Backup cron job deployed only for prod stage, runs daily, stores backups at `live/auth/backup/`
- FR19: Cron job management uses marker-based crontab entries (MCC-AUTH prefix) for safe re-deployment

## Success Criteria

- SC1: `uv run pytest` passes on the backend skeleton
- SC2: `ng build` succeeds on the frontend skeleton
- SC3: `uv run mcc_build.py` completes successfully (quality + tests + build)
- SC4: README.md clearly describes the project vision, stack, and planned features
- SC5: Database setup script can create and drop schemas with `uv run db_setup.py create main` and `uv run db_setup.py drop main --confirm`
- SC6: Schema creation includes user account tables and master admin user
- SC7: `uv run run_tests.py quality` passes ruff, ty, and complexity checks (C901 limit 10)
- SC8: `uv run run_tests.py python --coverage` passes with 90% minimum coverage
- SC9: The application can be deployed to both auth-dev.mathcodingclub.com and auth.mathcodingclub.com from the same server
- SC10: Prod deployment installs backup cron job; backup script produces compressed schema dump

## Out of Scope

- User authentication logic (sign-in, sign-up, password management)
- JWT signing and token management
- Admin user interface functionality
- SSO sign-in form
- OAuth/OIDC protocol implementation
- Permission or authorization management
- User consent flow
- CI/CD pipeline setup in the pipeline service (user will do this separately)
- Database copy/migration tooling between environments

## Assumptions

- Python 3.13 and uv are available in the development environment
- Angular 21 CLI is available (user confirms it has been published)
- PostgreSQL runs in Docker locally for development (localhost:5432, postgres/postgres) and is always available
- Production PostgreSQL is on the same LAN as the deployment server (192.168.0.x:5432, direct connection)
- pg_dump is available on the production server for backup scripts
- The domains auth.mathcodingclub.com and auth-dev.mathcodingclub.com DNS will be configured by the user
- The target deployment server is a Linux machine accessible via the MCC pipeline; both stages run on the same physical server
- SSL certificates will be managed via certbot/Let's Encrypt
- The sibling events.3rdb.com project is available as a reference for MCC script patterns

## Dependencies

- PostgreSQL database server (Docker locally, LAN server in production)
- Node.js and Angular CLI for frontend development
- Python 3.13 and uv for backend and script management
- Target Linux server for deployment (shared between dev and prod stages)
- DNS configuration for auth.mathcodingclub.com and auth-dev.mathcodingclub.com
- pg_dump on production server for backups
