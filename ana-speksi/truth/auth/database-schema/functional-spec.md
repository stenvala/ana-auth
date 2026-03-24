# Functional Specification: Database Schema and Multitenancy

**Domain**: auth/database-schema
**Last updated**: 2026-03-24

## Story

**As a** developer,
**I want** a PostgreSQL schema-based multitenant database setup with user tables and a master admin,
**So that** I can run multiple environments (prod, dev, test) on the same database server with full isolation.

## Detailed Description

The database uses PostgreSQL schema-based isolation where each environment gets its own schema prefixed with `ana-auth-`. A typer CLI tool (`setup_db.py`) manages schema lifecycle. The initial schema includes user account and email tables, plus an idempotently-created master admin user.

## Requirements

### REQ-01: Schema-Based Multitenancy

**Description**: Each environment operates in its own PostgreSQL schema.

**Acceptance Scenarios**:

- **WHEN** `uv run setup_db.py create main` is run
  **THEN** a schema `ana-auth-main` is created with all tables and the master admin user

- **WHEN** `uv run setup_db.py create dev` is run
  **THEN** a schema `ana-auth-dev` is created independently

- **WHEN** tests run in parallel
  **THEN** each test worker gets its own `ana-auth-test-{uuid}` schema

### REQ-02: Schema Management CLI

**Description**: `setup_db.py` provides commands for schema lifecycle management.

**Acceptance Scenarios**:

- **WHEN** `uv run setup_db.py create <suffix>` is run
  **THEN** the schema is created with tables and admin user

- **WHEN** `uv run setup_db.py drop <suffix> --confirm` is run
  **THEN** the schema is dropped with CASCADE

- **WHEN** `uv run setup_db.py update <suffix>` is run
  **THEN** pending migrations are applied

- **WHEN** `uv run setup_db.py local-update` is run
  **THEN** the main schema is updated with pending migrations

### REQ-03: Initial User Tables

**Description**: The schema includes user_account and user_email tables.

See [auth data model](../../data-models/auth.md) for full table definitions.

### REQ-04: Master Admin User

**Description**: A master admin user is created idempotently during schema creation and deployment.

**Acceptance Scenarios**:

- **WHEN** the schema is created for the first time
  **THEN** the master admin user (stenvala) is created with a pre-computed bcrypt hash

- **WHEN** schema creation runs again
  **THEN** the admin user INSERT is skipped via ON CONFLICT DO NOTHING

### REQ-05: Migration Tracking

**Description**: Migrations are tracked via a `_deployment_log` table to prevent redundant execution.

**Acceptance Scenarios**:

- **WHEN** a migration has already been applied (matching filename and checksum)
  **THEN** it is skipped

- **WHEN** a migration file's checksum changes after it was applied
  **THEN** the system detects the mismatch

## Constraints

- SQL files stored in `src/shared/db/schema/` and `src/shared/db/migrations/`
- Idempotent schema creation using `IF NOT EXISTS`
- Docker Compose provides PostgreSQL locally; production uses LAN server (192.168.0.x:5432)
