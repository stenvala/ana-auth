# Functional Specification: MCC Pipeline and Deployment

**Domain**: auth/deployment
**Last updated**: 2026-03-24

## Story

**As a** developer,
**I want** automated build and deploy scripts with multi-stage infrastructure,
**So that** I can deploy the service to production and development from day one.

## Detailed Description

The MCC pipeline provides build (`mcc_build.py`) and deploy (`mcc_deploy.py`) scripts that handle quality checks, testing, packaging, deployment, database management, and infrastructure setup for two stages on the same physical server.

## Requirements

### REQ-01: Build Pipeline

**Description**: `mcc_build.py` runs quality checks, tests, and packages the application.

**Acceptance Scenarios**:

- **WHEN** `uv run mcc_build.py` is run
  **THEN** quality checks, unit tests (90% coverage gate), and integration tests execute, then frontend and backend are built and packaged

- **WHEN** `uv run mcc_build.py --no-tests` is run
  **THEN** tests are skipped and only packaging occurs

### REQ-02: Deploy Pipeline

**Description**: `mcc_deploy.py` deploys the application to a target stage.

**Acceptance Scenarios**:

- **WHEN** `mcc_deploy.py --stage main` is run
  **THEN** the application deploys to auth.mathcodingclub.com with database schema creation/migration and admin user ensuring

- **WHEN** `mcc_deploy.py --stage dev` is run
  **THEN** the application deploys to auth-dev.mathcodingclub.com

- **WHEN** deployment completes
  **THEN** the systemd service is restarted and a health check smoke test passes

### REQ-03: Multi-Stage Infrastructure

**Description**: Two stages (prod and dev) run on the same physical server with separate configurations.

**Acceptance Scenarios**:

- **WHEN** prod is deployed
  **THEN** it uses auth.mathcodingclub.com, port 6784, schema ana-auth-main, deploy path live/auth/

- **WHEN** dev is deployed
  **THEN** it uses auth-dev.mathcodingclub.com, port 6785, schema ana-auth-dev, deploy path live/auth-dev/

### REQ-04: Database Management During Deploy

**Description**: Deploy creates schemas and runs migrations automatically.

**Acceptance Scenarios**:

- **WHEN** deploying to a fresh server
  **THEN** the database schema is created and the master admin user is ensured

- **WHEN** deploying with pending migrations
  **THEN** migrations are applied in order with checksum tracking

### REQ-05: Clone-Prod-to-Dev

**Description**: A non-deployment stage that copies the production database to dev.

**Acceptance Scenarios**:

- **WHEN** `mcc_deploy.py --stage clone-prod-to-dev` is run
  **THEN** the production schema is copied to the dev schema

### REQ-06: Infrastructure Configuration

**Description**: Systemd services and nginx configs are managed via templates.

**Acceptance Scenarios**:

- **WHEN** infrastructure is deployed
  **THEN** systemd service files are installed and enabled, nginx configs with SSL are set up

### REQ-07: Stage Configuration

**Description**: Stage-specific settings via YAML files.

**Acceptance Scenarios**:

- **WHEN** deploying to a stage
  **THEN** the corresponding YAML config (`mcc/conf-prod.yml` or `mcc/conf-dev.yml`) provides database host, port, schema suffix, and other parameters

## Constraints

- Production PostgreSQL at 192.168.0.x:5432 (direct LAN connection, no SSH tunnel)
- Template variable substitution with `{{PLACEHOLDER}}` syntax
- Marker-based cron management (MCC-AUTH prefix) for safe re-deployment
- Follows patterns from sibling events.3rdb.com project
