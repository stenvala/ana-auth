# Functional Specification: Backend Skeleton

**Domain**: auth/backend-skeleton
**Last updated**: 2026-03-24

## Story

**As a** developer,
**I want** a working FastAPI backend skeleton with database connectivity and health check,
**So that** I have a foundation for implementing authentication endpoints.

## Detailed Description

The backend is a FastAPI application that provides RESTful API endpoints. It connects to PostgreSQL using schema-based multitenancy and runs on port 6784 in production. All Python commands use `uv run`.

## Requirements

### REQ-01: Health Check Endpoint

**Description**: A GET endpoint at `/api/health` that confirms the service is running.

**Acceptance Scenarios**:

- **WHEN** a GET request is sent to `/api/health`
  **THEN** the response is HTTP 200 with body `{"status": "ok"}`

### REQ-02: Database Connection with Schema Multitenancy

**Description**: The backend connects to PostgreSQL and selects the appropriate schema based on environment configuration.

**Acceptance Scenarios**:

- **WHEN** the application starts with `SCHEMA_SUFFIX=main`
  **THEN** all database queries operate within the `ana-auth-main` schema

- **WHEN** a request includes the `X-Schema` header (test mode only)
  **THEN** the database session uses the specified schema instead of the default

### REQ-03: Request-Scoped Database Sessions

**Description**: Each HTTP request gets its own database session with automatic commit/rollback.

**Acceptance Scenarios**:

- **WHEN** a request completes successfully
  **THEN** the database session is committed

- **WHEN** a request raises an exception
  **THEN** the database session is rolled back

### REQ-04: Application Factory

**Description**: The app is created via a `create_app()` factory function with lifespan management, middleware, and router registration.

### REQ-05: Docker Compose for Local Development

**Description**: A docker-compose.yml provides PostgreSQL at localhost:5432 for local development.

**Acceptance Scenarios**:

- **WHEN** `docker compose up` is run
  **THEN** PostgreSQL is available at localhost:5432 with postgres/postgres credentials

## Constraints

- Backend runs on port 6784 (not default uvicorn port)
- All commands use `uv run`
- Python 3.13 required
