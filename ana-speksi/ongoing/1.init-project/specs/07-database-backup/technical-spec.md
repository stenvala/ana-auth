# Technical Specification: Database Backup with Automated Retention

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-techify

## Overview

Create a database backup script using pg_dump with gzip compression, a retention policy (30 daily + monthly for 12 months), and cron job integration deployed via the MCC pipeline for prod stage only. Uses marker-based crontab management for safe re-deployment.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| mcc-pipeline | Cron job deployment pattern from deploy script |
| mcc-infra | Server infrastructure patterns |
| python-coding-conventions | Script code quality |

## Architecture

```
project root/
  backup_db.py                    # Backup script with retention cleanup

Production filesystem:
  live/auth/
    backup/
      2026-03-21-main.gz         # Daily backup files
      2026-03-20-main.gz
      ...
    logs/
      backup.log                  # Backup script output log
```

### Backup Flow

1. Cron triggers `backup_db.py main` daily (e.g., 02:00)
2. Script reads DB connection from environment or config
3. Runs `pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -n "ana-auth-main" $DB_NAME`
4. Pipes output through gzip to `$BACKUP_DIR/YYYY-MM-DD-main.gz`
5. Runs retention cleanup
6. Logs result to backup.log

### Retention Policy

- **Daily**: Keep last 30 backups
- **Monthly**: Keep backup from last day of each month for 12 months
- **Overlap**: If a file qualifies for both daily and monthly retention, it is kept (monthly takes precedence)

### Last Day of Month Determination

Use Python's `calendar.monthrange()` to determine the last day of each month, handling varying month lengths (28, 29, 30, 31).

### Cron Job Management

Cron entries use the `MCC-AUTH` marker prefix for safe re-deployment:

```crontab
# MCC-AUTH-START
0 2 * * * cd /home/stenvala/live/auth && .venv/bin/python backup_db.py main >> logs/backup.log 2>&1
# MCC-AUTH-END
```

On each deployment, existing MCC-AUTH entries are removed before new ones are added, preventing duplicates.

## Data Model Changes

None.

## API Changes

None.

## Implementation Approach

1. **Create backup_db.py** (typer CLI or simple script):
   - `main` command: backup the ana-auth-main schema
   - Accept suffix argument for flexibility
   - Read DB connection from environment (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
   - Run pg_dump with schema flag, pipe through gzip
   - Save to `$BACKUP_DIR/YYYY-MM-DD-{suffix}.gz`
   - Run retention cleanup after backup
   - Error handling: fail with clear message if pg_dump fails or schema doesn't exist

2. **Implement retention cleanup**:
   - List all `.gz` files in backup directory
   - Parse date from filename (YYYY-MM-DD pattern)
   - Keep files where: `age <= 30 days` OR (`day == last_day_of_month(year, month)` AND `age <= 365 days`)
   - Delete files that match neither rule
   - Log deleted files

3. **Integrate with MCC deploy**:
   - Add cron job configuration to `mcc/conf-prod.yml`
   - Deploy script reads CRON_JOBS from config
   - Uses marker-based crontab management (MCC-AUTH-START/END)
   - Only deployed for prod stage

4. **Create backup directory**:
   - Backup script creates `$BACKUP_DIR` if it doesn't exist (`os.makedirs(exist_ok=True)`)

## Testing Strategy

### Automated Tests

- Unit test: Retention policy logic -- given a list of backup files and today's date, verify correct files are kept/deleted
- Unit test: Last-day-of-month determination for all 12 months including leap year February
- Unit test: Filename parsing (date extraction from YYYY-MM-DD-suffix.gz)

### Manual Testing

- Run backup_db.py against local Docker PostgreSQL
- Verify .gz file is created and can be extracted with gunzip
- Create test files with various dates and run retention cleanup

## Out of Scope

- Backup restore tooling
- Backup verification (integrity checking)
- Off-site replication
- Backup encryption
- Dev stage backups

## Migration / Deployment Notes

- Cron job only deployed for prod stage
- Backup directory is `live/auth/backup/` on the production server
- pg_dump must be available on the production server
- The backup script runs in the deployment's virtual environment

## Security Considerations

- Backup files contain database data -- ensure backup directory permissions are restrictive (750)
- pg_dump credentials come from environment, not hardcoded
- Backup log file should not contain credentials
