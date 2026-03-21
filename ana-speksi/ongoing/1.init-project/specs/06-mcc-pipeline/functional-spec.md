# Functional Specification: MCC Infrastructure, Pipeline, and Multi-Stage Deployment

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-storify

## Story

**As a** developer deploying ana-auth,
**I want** build and deploy scripts with infrastructure configuration for two stages (dev and prod) on the same server,
**So that** I can deploy the service from day one with automated database setup and the deploy is fully self-contained.

## Detailed Description

The MCC (MathCodingClub) pipeline consists of build and deploy scripts following the patterns from the sibling events.3rdb.com project. The build script (`mcc_build.py`) runs quality checks and tests, builds the frontend and backend, and packages everything for deployment. The deploy script (`mcc_deploy.py`) deploys to the target server, creates the database schema if it doesn't exist, ensures the master admin user exists, and manages cron jobs. Infrastructure configuration includes systemd services and nginx configs for two stages: auth-dev.mathcodingclub.com (dev) and auth.mathcodingclub.com (prod), both on the same physical server. Stage-specific YAML configuration files drive deployment parameters.

## Requirements

### REQ-06-01: Build Script (mcc_build.py)

**Description**: The build script must run quality checks, tests, build both frontend and backend, and package the output for deployment.

**Acceptance Scenarios**:

- **WHEN** `uv run mcc_build.py` is executed
  **THEN** quality checks run (ruff, ty, complexity)
  **AND** unit tests run with 90% coverage gate
  **AND** integration tests run
  **AND** `nvm use` is run before frontend build to ensure Node.js 20.19
  **AND** the frontend is built with `npx ng build`
  **AND** the backend source is copied to the output directory
  **AND** database scripts are copied to the output directory
  **AND** deployment scripts are copied to the output directory

- **WHEN** `uv run mcc_build.py --no-tests` is executed
  **THEN** quality checks and tests are skipped
  **AND** the build proceeds directly to building and packaging

### REQ-06-02: Deploy Script (mcc_deploy.py)

**Description**: The deploy script must deploy the application to the target server and handle database setup.

**Acceptance Scenarios**:

- **WHEN** `uv run mcc_deploy.py --stage <stage>` is executed for a deployment stage (e.g., `main`, `dev`)
  **THEN** the packaged application is deployed to the correct remote path (live/auth/ for prod, live/auth-dev/ for dev)
  **AND** the database schema is created if it doesn't exist
  **AND** pending database migrations are applied to the stage's schema
  **AND** the master admin user is ensured to exist
  **AND** schema versioning prevents redundant SQL execution (checksum-based)
  **AND** the systemd service is restarted

- **WHEN** the deploy runs on the prod stage
  **THEN** cron jobs for database backup are also deployed

- **WHEN** the deploy runs on the dev stage
  **THEN** no backup cron jobs are deployed

### REQ-06-03: Schema Versioning

**Description**: The deploy must track schema versions to prevent redundant deployments.

**Acceptance Scenarios**:

- **WHEN** the deploy runs and the schema SQL has not changed since the last deployment
  **THEN** schema SQL execution is skipped
  **AND** a log message indicates the schema is already up to date

- **WHEN** the deploy runs and the schema SQL has changed
  **THEN** the new SQL is executed
  **AND** the deployment is logged in the `_deployment_log` table with the new checksum

### REQ-06-04: Stage Configuration (YAML)

**Description**: Each stage must have its own YAML configuration file with deployment parameters.

**Acceptance Scenarios**:

- **WHEN** deploying to the prod stage
  **THEN** configuration is read from `mcc/conf-prod.yml`
  **AND** it contains: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_SCHEMA_SUFFIX (main), REMOTE_BASE (live/auth), domain (auth.mathcodingclub.com), and service port

- **WHEN** deploying to the dev stage
  **THEN** configuration is read from `mcc/conf-dev.yml`
  **AND** it contains the same keys but with dev-specific values: DB_SCHEMA_SUFFIX (dev), REMOTE_BASE (live/auth-dev), domain (auth-dev.mathcodingclub.com), and a different service port

### REQ-06-05: Infrastructure -- systemd Services

**Description**: Each stage must have its own systemd service running the FastAPI application via gunicorn + uvicorn.

**Acceptance Scenarios**:

- **WHEN** the infrastructure is deployed for prod
  **THEN** a systemd service `ana-auth.service` is created and enabled
  **AND** it runs from the prod deployment directory on port 6784
  **AND** it sets the SCHEMA_SUFFIX environment variable to "main"

- **WHEN** the infrastructure is deployed for dev
  **THEN** a systemd service `ana-auth-dev.service` is created and enabled
  **AND** it runs from the dev deployment directory on port 6785
  **AND** it sets the SCHEMA_SUFFIX environment variable to "dev"

### REQ-06-06: Infrastructure -- nginx Configuration

**Description**: Each stage must have its own nginx server block with SSL.

**Acceptance Scenarios**:

- **WHEN** nginx is configured for prod
  **THEN** auth.mathcodingclub.com serves the Angular frontend from the prod dist directory
  **AND** /api/* requests are proxied to the prod gunicorn service on port 6784
  **AND** SSL is configured via certbot/Let's Encrypt

- **WHEN** nginx is configured for dev
  **THEN** auth-dev.mathcodingclub.com serves from the dev dist directory
  **AND** /api/* requests are proxied to the dev gunicorn service on port 6785
  **AND** SSL is configured via certbot/Let's Encrypt

### REQ-06-07: Supporting Scripts

**Description**: The pipeline must include supporting scripts following events.3rdb.com patterns.

**Acceptance Scenarios**:

- **WHEN** the project is set up
  **THEN** the following scripts exist: mcc_common.py (shared utilities), mcc_config.py (configuration loading with YAML template variable resolution), lint.py (ruff wrapper), start_services.py (local dev server startup), mcc/deploy_server.py (server infrastructure setup via Fabric/SSH)

### REQ-06-08: Clone-Prod-to-Dev Stage

**Description**: A non-deployment stage must exist that copies the production database schema to the dev schema, allowing dev to mirror prod data.

**Acceptance Scenarios**:

- **WHEN** `uv run mcc_deploy.py --stage clone-prod-to-dev` is executed
  **THEN** the `ana-auth-main` schema data is copied to the `ana-auth-dev` schema on the remote database
  **AND** the dev schema is dropped and recreated before copying
  **AND** all tables, data, and sequences are copied
  **AND** no application deployment or service restart occurs

- **WHEN** the clone completes
  **THEN** the dev environment has an exact copy of the prod database

### REQ-06-09: Remote Database Connection

**Description**: The deploy script must connect to the production PostgreSQL directly on the LAN.

**Acceptance Scenarios**:

- **WHEN** the deploy script needs to set up the database
  **THEN** it connects to the PostgreSQL server at the configured DB_HOST on the LAN (192.168.0.x:5432)
  **AND** no SSH tunnel is needed

## Edge Cases

- If the remote database is unreachable, the deploy should fail with a clear error message.
- If the systemd service fails to start after deployment, the deploy should report the failure.
- Template variable resolution in YAML configs must handle recursive references with cycle detection.

## UI/UX Considerations

Not applicable -- these are deployment scripts.

## Out of Scope

- CI/CD pipeline setup in the pipeline service (user will do this separately)
- Blue-green deployments or zero-downtime deployments
- Container-based deployments (Docker/Kubernetes)
- Monitoring or alerting setup

## Constraints

- Must follow patterns from events.3rdb.com sibling project
- All Python scripts must use `uv run`, all Angular CLI commands must use `npx ng`
- Backend (gunicorn/uvicorn) listens on port 6784 (prod) and 6785 (dev)
- Prod deploys to `live/auth/`, dev deploys to `live/auth-dev/`
- Both stages share the same physical server
- Database connection is direct LAN, no SSH tunnel
