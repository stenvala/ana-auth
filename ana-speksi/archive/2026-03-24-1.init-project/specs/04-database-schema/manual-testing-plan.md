# Manual Testing Plan: Database Schema and Multitenant Setup

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21

## Test Scenarios

### Scenario 1: Create main schema

**Preconditions**: Docker PostgreSQL running

**Steps**:
1. Run `uv run setup_db.py create main`
2. Connect to PostgreSQL and list schemas

**Expected Result**: Schema `"ana-auth-main"` exists with user_account and user_email tables

### Scenario 2: Master admin user exists

**Preconditions**: Main schema created

**Steps**:
1. Connect to PostgreSQL
2. Query `SELECT * FROM "ana-auth-main".user_account WHERE user_name = 'stenvala'`

**Expected Result**: One row returned with the admin user details

### Scenario 3: Idempotent creation

**Preconditions**: Main schema already exists with admin user

**Steps**:
1. Run `uv run setup_db.py create main` again

**Expected Result**: No errors, no duplicate admin user, tables remain intact

### Scenario 4: Drop schema

**Preconditions**: Main schema exists

**Steps**:
1. Run `uv run setup_db.py drop main --confirm`
2. List schemas in PostgreSQL

**Expected Result**: Schema `"ana-auth-main"` no longer exists

### Scenario 5: Schema update with migrations

**Preconditions**: Main schema exists

**Steps**:
1. Run `uv run setup_db.py update main`

**Expected Result**: Message indicates schema is up to date (no pending migrations)

## Exploratory Testing Areas

- Create multiple schemas (main, dev, e2e) simultaneously
- Verify foreign key constraints between user_account and user_email
- Test cascade delete: delete a user_account and verify associated emails are deleted
