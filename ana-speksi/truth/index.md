# Ground Truth Index

**Last updated**: 2026-03-24

## Platform

- [Architecture](platform/architecture.md) -- Overall system architecture, technology stack, deployment topology, cross-cutting concerns

## Features

- **auth** -- Authentication service domain
  - [Backend Skeleton](auth/backend-skeleton/) -- FastAPI backend with health check, schema multitenancy, request-scoped sessions
  - [Frontend Skeleton](auth/frontend-skeleton/) -- Angular 21 with Material v3 sci-fi theme, dark mode default
  - [Database Schema](auth/database-schema/) -- PostgreSQL schema-based multitenancy, user tables, migration tracking, master admin
  - [Test Infrastructure](auth/test-infrastructure/) -- pytest/Playwright test runner with schema-per-worker isolation, quality gates
  - [Deployment](auth/deployment/) -- MCC build/deploy pipeline, multi-stage infrastructure (prod + dev), systemd/nginx
  - [Database Backup](auth/database-backup/) -- Automated daily pg_dump backups with 30-day rolling + monthly retention

## Data Models

- [auth](data-models/auth.md) -- User accounts and emails for the authentication service

## Enums

(none yet)
