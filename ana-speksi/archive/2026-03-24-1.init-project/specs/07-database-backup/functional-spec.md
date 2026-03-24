# Functional Specification: Database Backup with Automated Retention

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-storify

## Story

**As a** system administrator,
**I want** automated daily database backups with a retention policy,
**So that** data is protected against loss and I can restore from any of the last 30 days or from monthly snapshots for the past year.

## Detailed Description

A backup script uses pg_dump to export the production database schema, compresses it with gzip, and stores it in the deployment's backup folder (`live/auth/backup/`). A cron job runs the backup daily on the production stage only. The retention policy keeps the last 30 daily backups and the last day of each month for 12 months. A cleanup step runs after each backup to enforce retention. The backup cron job is deployed as part of the prod deployment using marker-based crontab management.

## Requirements

### REQ-07-01: Backup Script

**Description**: A backup script must export the production schema using pg_dump and compress it with gzip.

**Acceptance Scenarios**:

- **WHEN** `uv run backup_db.py main` is executed
  **THEN** the `ana-auth-main` schema is exported using pg_dump
  **AND** the output is compressed with gzip
  **AND** the backup file is saved as `YYYY-MM-DD-main.gz` in the backup directory

- **WHEN** the backup script runs and the schema does not exist
  **THEN** the script exits with a clear error message

### REQ-07-02: Retention Policy -- Daily Backups

**Description**: The last 30 daily backups must be retained.

**Acceptance Scenarios**:

- **WHEN** the retention cleanup runs
  **THEN** daily backup files older than 30 days are deleted
  **AND** daily backup files within the last 30 days are kept

### REQ-07-03: Retention Policy -- Monthly Backups

**Description**: The backup from the last day of each month must be retained for 12 months.

**Acceptance Scenarios**:

- **WHEN** the retention cleanup runs
  **THEN** backup files from the last day of each month within the past 12 months are preserved even if they are older than 30 days

- **WHEN** a monthly backup is older than 12 months
  **THEN** it is deleted

### REQ-07-04: Automated Cron Job (Prod Only)

**Description**: A cron job must run the backup daily on the production stage only.

**Acceptance Scenarios**:

- **WHEN** the prod stage is deployed
  **THEN** a cron job is installed that runs the backup script daily
  **AND** the cron entry uses the MCC-AUTH marker prefix for safe re-deployment
  **AND** backup output is logged to a log file

- **WHEN** the dev stage is deployed
  **THEN** no backup cron job is installed

### REQ-07-05: Backup Storage Location

**Description**: Backups must be stored in the deployment's backup directory.

**Acceptance Scenarios**:

- **WHEN** the backup runs for prod
  **THEN** backups are stored at `live/auth/backup/`

- **WHEN** the backup directory does not exist
  **THEN** it is created automatically

### REQ-07-06: Cron Job Management

**Description**: Cron jobs must use marker-based entries so re-deployments cleanly replace old entries.

**Acceptance Scenarios**:

- **WHEN** the deploy installs cron jobs
  **THEN** existing entries with the MCC-AUTH marker are removed first
  **AND** new entries are added with the MCC-AUTH marker

- **WHEN** the deploy runs again
  **THEN** cron entries are replaced, not duplicated

## Edge Cases

- If pg_dump is not available on the server, the backup script should fail with a clear error.
- If the backup directory disk is full, the script should report the error.
- If both the daily and monthly retention rules apply to the same file, the file is kept (monthly takes precedence).
- The "last day of month" determination must handle months with different lengths (28, 29, 30, 31 days).

## UI/UX Considerations

Not applicable -- this is an automated system administration task.

## Out of Scope

- Backup restore tooling or procedures
- Backup verification (checking that the backup is valid)
- Off-site backup replication
- Backup of the dev stage
- Backup encryption

## Constraints

- Must use pg_dump for schema-level backups
- Must use gzip compression
- Cron job runs on the prod stage only
- Must use marker-based crontab management (MCC-AUTH prefix)
- Backup directory is `live/auth/backup/` for prod
