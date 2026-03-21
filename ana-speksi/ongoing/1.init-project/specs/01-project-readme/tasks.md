# Tasks: Project README

**Status**: Accepted
**Generated with**: as-taskify
**Story**: 01-project-readme

## Prerequisites

- 02-backend-skeleton must be complete (project structure to document)
- 03-frontend-skeleton must be complete (frontend setup to document)
- 04-database-schema must be complete (database setup to document)

---

## Phase 1: Setup

No setup tasks.

---

## Phase 2: Implementation

### P02.T001 -- Create README.md

**Mandatory to use skills: /create-web-app**

Create `README.md` at the repository root with sections:
1. Project title and one-line description
2. What is ana-auth: private SSO/OAuth service, comparison to Cognito/Entra ID
3. Planned features: user management, SSO sign-in, JWT tokens, token refresh, user info endpoint, consent flow
4. Technology stack: Python 3.13/FastAPI, Angular 21, PostgreSQL, uv
5. Deployment domains: auth.mathcodingclub.com (prod), auth-dev.mathcodingclub.com (dev)
6. Development setup: Docker for PostgreSQL, uv sync, running backend, building frontend, running tests
7. Project structure overview (src/api, src/ui, src/shared, src/tests)
8. Clearly distinguish current state (skeleton) from planned features

Files:
- Create `README.md`

- [ ] P02.T001

---

## Phase 3: Test Automation

No automated tests -- this is a documentation file.

---

## Phase 4: Manual Verification

- Verify README.md renders correctly in GitHub markdown preview
- Verify all sections are present and accurate
- Verify development setup instructions match actual commands
