# Functional Specification: Database Backup

**Domain**: auth/database-backup
**Last updated**: 2026-03-24

## Story

**As a** system operator,
**I want** automated daily database backups with a retention policy,
**So that** I can recover from data loss.

## Detailed Description

Daily pg_dump backups of the production database schema, compressed with gzip, with a retention policy that keeps 30 rolling daily backups plus the last day of each month for 12 months.

## Requirements

### REQ-01: Backup Script

**Description**: `backup_db.py` creates compressed database backups.

**Acceptance Scenarios**:

- **WHEN** `backup_db.py` runs
  **THEN** a pg_dump of the target schema is piped through gzip and saved as `YYYY-MM-DD-{suffix}.gz`

- **WHEN** pg_dump fails
  **THEN** the error is logged and the script exits with a non-zero code

### REQ-02: Retention Policy

**Description**: Old backups are cleaned up according to retention rules.

**Acceptance Scenarios**:

- **WHEN** retention runs
  **THEN** daily backups older than 30 days are deleted unless they are month-end backups

- **WHEN** a backup is from the last day of a month
  **THEN** it is kept for 12 months regardless of the daily retention window

### REQ-03: Automated Cron Job

**Description**: Backups run automatically via cron on the production stage only.

**Acceptance Scenarios**:

- **WHEN** the prod stage is deployed
  **THEN** a daily cron job for backup is installed with MCC-AUTH markers

- **WHEN** the dev stage is deployed
  **THEN** no backup cron job is installed

### REQ-04: Backup Storage

**Description**: Backups are stored at the deployment's backup directory.

**Acceptance Scenarios**:

- **WHEN** a production backup runs
  **THEN** the backup file is written to `live/auth/backup/`

## Constraints

- pg_dump must be available on the production server
- Cron entries use MCC-AUTH markers for safe re-deployment
- Logs written to backup.log
