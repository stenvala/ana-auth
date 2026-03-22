# ana-auth

Private SSO/OAuth authentication service for centralized identity management across multiple private services.

## What is ana-auth?

ana-auth is a self-hosted identity provider -- similar to AWS Cognito or Microsoft Entra ID -- that provides Single Sign-On (SSO) authentication for private services. Instead of each service managing its own users and authentication, ana-auth acts as the central authority for user identity, JWT token issuance, and session management.

## Planned Features

ana-auth is under active development. The following capabilities are planned:

- **User management** -- admin UI for creating and managing user accounts
- **SSO sign-in form** -- centralized login page that authenticates users across services
- **JWT token issuance** -- signed tokens issued upon successful authentication
- **Token refresh** -- backend services can exchange refresh tokens for new auth tokens
- **User info endpoint** -- authenticated services can retrieve user details (givenName, familyName, displayName, userId, email)
- **User consent flow** -- users approve sharing their profile data with requesting services

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.13 with FastAPI |
| Frontend | Angular 21 with Angular Material |
| Database | PostgreSQL |
| Package management | uv (Python), npm (Angular) |
| Deployment | Linux server with nginx and systemd |

## Deployment

ana-auth runs on two stages, both on the same physical server:

| Stage | Domain |
|-------|--------|
| Production | auth.mathcodingclub.com |
| Development | auth-dev.mathcodingclub.com |

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 20.19 (via nvm)
- Docker (for local PostgreSQL)
- uv package manager

### Getting Started

1. **Start PostgreSQL** via Docker:

   ```bash
   docker compose up -d
   ```

2. **Install Python dependencies**:

   ```bash
   uv sync
   ```

3. **Set up the database**:

   ```bash
   uv run setup_db.py local-update
   ```

4. **Run the backend**:

   ```bash
   uv run start_services.py api
   ```

5. **Build and serve the frontend**:

   ```bash
   nvm use 20.19.2
   cd src/ui
   npm install
   npx ng serve
   ```

### Running Tests

```bash
uv run run_tests.py all          # Quality checks + unit + integration tests
uv run run_tests.py unit         # Unit tests only
uv run run_tests.py int          # Integration tests only
uv run run_tests.py e2e          # E2E browser tests (requires running services)
uv run run_tests.py quality      # Ruff + ty checks
```

### Linting

```bash
uv run lint.py python
uv run lint.py angular
```

## Project Structure

```
src/
  api/         # FastAPI backend
  ui/          # Angular frontend
  shared/      # Database models and shared code
  tests/       # Backend tests (unit, integration, E2E)
```

## Current State

This project is in its initial skeleton phase. The application structure, build pipeline, test infrastructure, and database schema are being established. Authentication logic, admin UI, and OAuth flows will be implemented in subsequent iterations.
