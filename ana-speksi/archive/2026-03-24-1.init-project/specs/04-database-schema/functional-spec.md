# Functional Specification: Database Schema and Multitenant Setup

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-storify

## Story

**As a** developer deploying ana-auth,
**I want** a multitenant PostgreSQL database setup with an initial user schema and a master admin user,
**So that** I can run dev and prod on the same server with isolated schemas, and the system is usable from the first deployment.

## Detailed Description

The database layer uses PostgreSQL schema-based multitenancy. Each deployment stage (main, dev) and each test runner gets its own schema (e.g., `ana-auth-main`, `ana-auth-dev`, `ana-auth-test-abc123`). A typer CLI tool (`setup_db.py`) manages schema lifecycle (create, drop, demo data). The initial schema includes user account and user email tables. A master admin user is created idempotently during schema setup so the system has at least one usable account from day one.

## Requirements

### REQ-04-01: Schema-Based Multitenancy

**Description**: The database must support multiple isolated schemas within a single PostgreSQL database, each prefixed with `ana-auth-`.

**Acceptance Scenarios**:

- **WHEN** `uv run setup_db.py create main` is executed
  **THEN** a schema named `ana-auth-main` is created in the postgres database

- **WHEN** `uv run setup_db.py create dev` is executed
  **THEN** a schema named `ana-auth-dev` is created, isolated from `ana-auth-main`

- **WHEN** `uv run setup_db.py create test-abc123` is executed
  **THEN** a schema named `ana-auth-test-abc123` is created for test isolation

### REQ-04-02: User Account Table

**Description**: The schema must include a user_account table with fields needed for authentication and user identity.

**Acceptance Scenarios**:

- **WHEN** a schema is created
  **THEN** it contains a user_account table with at minimum: id (text, primary key), user_name (text, unique), password_hash (text), given_name (text), family_name (text), display_name (text), created_at (timestamp), updated_at (timestamp)

### REQ-04-03: User Email Table

**Description**: The schema must include a user_email table linked to user accounts.

**Acceptance Scenarios**:

- **WHEN** a schema is created
  **THEN** it contains a user_email table with at minimum: id (text, primary key), user_account_id (text, foreign key to user_account), email (text, unique), is_primary (boolean), is_verified (boolean)

### REQ-04-04: Master Admin User Creation

**Description**: Schema creation must idempotently create a master admin user so the system is usable immediately.

**Acceptance Scenarios**:

- **WHEN** a schema is created for the first time
  **THEN** a master admin user (username: stenvala) is created with a pre-set password hash
  **AND** a primary email is associated with the admin user

- **WHEN** schema creation runs again on an existing schema
  **THEN** the admin user is not duplicated (INSERT ... ON CONFLICT DO NOTHING)

### REQ-04-05: Setup CLI Commands

**Description**: The setup_db.py typer CLI must support schema lifecycle management.

**Acceptance Scenarios**:

- **WHEN** `uv run setup_db.py create <suffix>` is executed
  **THEN** the schema `ana-auth-<suffix>` is created with all tables and the admin user

- **WHEN** `uv run setup_db.py drop <suffix> --confirm` is executed
  **THEN** the schema `ana-auth-<suffix>` is dropped with CASCADE

- **WHEN** `uv run setup_db.py drop <suffix>` is executed without `--confirm`
  **THEN** the user is prompted for confirmation before dropping

- **WHEN** `uv run setup_db.py main` is executed
  **THEN** the main schema is dropped and recreated with admin user (convenience command for full reset)

- **WHEN** `uv run setup_db.py e2e` is executed
  **THEN** a convenience reset is available for manual E2E testing (drop and recreate with suffix "e2e")

### REQ-04-06: Database Migration Strategy

**Description**: The setup_db.py must support incremental schema migrations so that existing data is preserved when the schema evolves.

**Acceptance Scenarios**:

- **WHEN** `uv run setup_db.py update <suffix>` is executed
  **THEN** pending migration scripts are applied to the `ana-auth-<suffix>` schema in order
  **AND** each migration is tracked so it is not applied twice
  **AND** existing data is preserved

- **WHEN** `uv run setup_db.py update main` is executed and all migrations have already been applied
  **THEN** no changes are made
  **AND** a message indicates the schema is up to date

- **WHEN** a new migration file is added to the migrations directory
  **THEN** the next `update` command applies only the new migration(s)

## Edge Cases

- Creating a schema that already exists should not fail -- use IF NOT EXISTS.
- Dropping a schema that does not exist should not fail -- use IF EXISTS.
- The admin user password hash should be a pre-computed bcrypt hash, not generated at runtime.
- Migrations must be applied in order. If a migration fails, subsequent migrations should not run.

## UI/UX Considerations

Not applicable -- this is a database setup tool.

## Out of Scope

- User registration or sign-up logic
- Password change or reset functionality
- Role or permission management

## Constraints

- Must use PostgreSQL schemas for multitenancy (not separate databases)
- Must connect to localhost:5432 with postgres/postgres credentials locally (Docker)
- Admin user creation must be idempotent
- CLI must use typer
