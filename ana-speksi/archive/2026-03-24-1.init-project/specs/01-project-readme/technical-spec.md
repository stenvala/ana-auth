# Technical Specification: Project README

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-techify

## Overview

Create a comprehensive README.md at the repository root documenting the ana-auth service -- its purpose, planned features, technology stack, deployment domains, and development setup instructions. This is a documentation-only story with no code changes beyond the README file.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| create-web-app | Provides context for the project structure that the README will describe |

## Architecture

Not applicable -- this is a documentation artifact. The README describes the architecture established by other stories.

## Data Model Changes

None.

## API Changes

None.

## Implementation Approach

1. Create `README.md` at the repository root
2. Write sections in this order:
   - Project title and one-line description
   - What is ana-auth (private SSO/OAuth service, comparison to Cognito/Entra ID)
   - Planned features (user management, SSO sign-in, JWT tokens, token refresh, user info endpoint, consent flow)
   - Technology stack (Python 3.13/FastAPI, Angular 21, PostgreSQL, uv)
   - Deployment domains (auth.mathcodingclub.com, auth-dev.mathcodingclub.com) and stage setup
   - Development setup (Docker for PostgreSQL, uv sync, running backend, building frontend, running tests)
   - Project structure overview
3. Clearly distinguish between current state (skeleton) and planned features

## Testing Strategy

### Automated Tests

None -- this is a documentation file.

### Manual Testing

Verify the README renders correctly in GitHub and contains all required sections.

## Out of Scope

- Detailed API documentation
- Architecture diagrams
- Contribution guidelines beyond basic setup

## Migration / Deployment Notes

None -- the README is committed to the repository and requires no deployment steps.

## Security Considerations

None.
