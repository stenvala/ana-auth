# Functional Specification: Backend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-storify

## Story

**As a** backend developer,
**I want** a working FastAPI application skeleton with project structure, database connection setup, and a health check endpoint,
**So that** I have a solid foundation to build authentication endpoints on top of.

## Detailed Description

The backend skeleton establishes the Python project structure using uv for package management and FastAPI as the web framework. It includes a health check endpoint to verify the application is running, database connection configuration using SQLModel, and the middleware pattern for request-scoped database sessions with schema isolation. The project structure follows the patterns established in the sibling events.3rdb.com project.

## Requirements

### REQ-02-01: Project Structure with uv

**Description**: The backend must be set up as a uv-managed Python 3.13 project with proper dependency management.

**Acceptance Scenarios**:

- **WHEN** a developer clones the repository and runs `uv sync`
  **THEN** all Python dependencies are installed
  **AND** the project is ready to run

- **WHEN** a developer runs `uv run` commands
  **THEN** the commands execute in the correct virtual environment

### REQ-02-02: FastAPI Application with Health Check

**Description**: The application must start successfully and expose a health check endpoint.

**Acceptance Scenarios**:

- **WHEN** the application starts
  **THEN** a GET request to `/api/health` returns HTTP 200
  **AND** the response body indicates the service is healthy

- **WHEN** the application cannot connect to the database
  **THEN** the health check still responds (the skeleton health check does not require DB connectivity)

### REQ-02-03: Database Connection with Schema Isolation

**Description**: The backend must configure SQLModel/SQLAlchemy database connections with schema-based multitenancy support.

**Acceptance Scenarios**:

- **WHEN** the application starts with a `SCHEMA_SUFFIX` environment variable set
  **THEN** all database queries use the schema `ana-auth-{SCHEMA_SUFFIX}`

- **WHEN** a request includes an `X-Schema` header (for testing)
  **THEN** that request uses the schema specified by the header

### REQ-02-04: Request-Scoped Database Sessions

**Description**: The backend must provide middleware that creates a database session per request with automatic commit/rollback.

**Acceptance Scenarios**:

- **WHEN** an API request is processed successfully
  **THEN** the database session is committed automatically

- **WHEN** an API request raises an exception
  **THEN** the database session is rolled back automatically

### REQ-02-05: Docker Compose for Local Development

**Description**: A docker-compose.yml must provide PostgreSQL for local development.

**Acceptance Scenarios**:

- **WHEN** a developer runs `docker compose up -d`
  **THEN** PostgreSQL is available at localhost:5432 with user postgres/postgres

## Edge Cases

- If the SCHEMA_SUFFIX environment variable is not set, it should default to "main".
- Connection pooling configuration must handle both development (low concurrency) and production (high concurrency) scenarios.

## UI/UX Considerations

Not applicable -- this is a backend service.

## Out of Scope

- Authentication endpoints
- User management endpoints
- JWT signing logic
- Any business logic beyond health check

## Constraints

- Must use Python 3.13 and uv for package management
- Must use FastAPI as the web framework
- Must use SQLModel for ORM
- All commands must use `uv run`, never bare `python`
- Backend runs on port 6784 (not the default uvicorn port)
