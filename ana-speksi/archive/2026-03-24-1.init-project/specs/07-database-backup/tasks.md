# Tasks: Database Backup with Automated Retention

**Status**: Accepted
**Generated with**: as-taskify
**Story**: 07-database-backup

## Prerequisites

- 04-database-schema must be complete (schema naming conventions)
- 06-mcc-pipeline must be complete (cron job deployment integration in mcc_deploy.py)

---

## Phase 1: Setup

No setup tasks -- all files are new.

---

## Phase 2: Implementation

### Service Changes

### P02.T001 -- Create backup_db.py script

**Mandatory to use skills: /mcc-pipeline, /python-coding-conventions**

Create `backup_db.py` at project root:
- Typer CLI accepting suffix argument (e.g., `main`)
- Read DB connection from environment (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
- Run `pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -n "ana-auth-{suffix}" $DB_NAME` piped through gzip
- Save to `$BACKUP_DIR/YYYY-MM-DD-{suffix}.gz`
- Create backup directory if it doesn't exist (`os.makedirs(exist_ok=True)`)
- Error handling: fail with clear message if pg_dump fails

Files:
- Create `backup_db.py`

- [x] P02.T001

### P02.T002 -- Implement retention cleanup in backup_db.py

**Mandatory to use skills: /python-coding-conventions**

Add retention cleanup logic to backup_db.py:
- List all `.gz` files in backup directory
- Parse date from filename (YYYY-MM-DD pattern)
- Keep files where: `age <= 30 days` OR (`day == last_day_of_month(year, month)` AND `age <= 365 days`)
- Use `calendar.monthrange()` for last-day-of-month determination
- Delete files that match neither rule
- Log deleted files

Files:
- Modify `backup_db.py`

- [x] P02.T002

### P02.T003 -- Add cron job config to prod stage YAML

**Mandatory to use skills: /mcc-pipeline**

Add CRON_JOBS configuration to `mcc/conf-prod.yml`:
- Daily backup at 02:00: `0 2 * * * cd {{REMOTE_BASE}} && .venv/bin/python backup_db.py main >> logs/backup.log 2>&1`
- MCC-AUTH marker prefix for safe re-deployment

Files:
- Modify `mcc/conf-prod.yml`

- [x] P02.T003

---

## Phase 3: Test Automation

### Backend Tests

### P03.T001 -- Create retention policy unit tests

**Mandatory to use skills: /test-python-unit**

Test retention logic:
- Given list of backup files and today's date, verify correct files kept/deleted
- Last-day-of-month determination for all 12 months including leap year February
- Filename date parsing (YYYY-MM-DD-suffix.gz)
- Edge case: file exactly 30 days old (kept), 31 days old non-monthly (deleted)

Files:
- Create `src/tests/unit/test_backup_db.py`

Verify: `uv run pytest src/tests/unit/test_backup_db.py -v` passes.

- [x] P03.T001

---

## Phase 4: Manual Verification

- Run `uv run backup_db.py main` against local Docker PostgreSQL
- Verify `.gz` file is created in backup directory
- Verify file can be extracted with `gunzip`
- Create test files with various dates and run retention cleanup manually
- Verify monthly snapshots are preserved correctly
