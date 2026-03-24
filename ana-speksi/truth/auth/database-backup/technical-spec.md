# Technical Specification: Database Backup

**Domain**: auth/database-backup
**Last updated**: 2026-03-24

## Overview

pg_dump-based backup script with gzip compression and Python-based retention logic, deployed as a cron job for production only.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| mcc-pipeline | Governs cron job deployment during mcc_deploy.py |

## Architecture

```
backup_db.py            # Backup and retention script
live/auth/backup/       # Production backup storage
```

## Key Implementation Patterns

1. **pg_dump with schema flag**: Uses `-n "ana-auth-main"` to dump only the relevant schema.
2. **Gzip compression**: Pipe pg_dump output through gzip for space efficiency.
3. **Month-end detection**: Uses Python's `calendar.monthrange()` to determine if a date is the last day of its month.
4. **Marker-based cron**: Entries between `MCC-AUTH-START` and `MCC-AUTH-END` markers in crontab, replaced on each deployment.
5. **Environment variables**: DB connection via DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME.
