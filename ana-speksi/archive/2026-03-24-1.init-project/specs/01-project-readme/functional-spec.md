# Functional Specification: Project README

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-storify

## Story

**As a** developer or contributor,
**I want** a comprehensive README.md at the repository root,
**So that** I can immediately understand what ana-auth is, what it does, what technologies it uses, and how to get started.

## Detailed Description

The README serves as the entry point for anyone encountering the ana-auth project. It should clearly communicate that ana-auth is a private SSO/OAuth authentication service -- similar to Cognito or Entra ID but self-hosted -- providing centralized authentication for multiple private services. The README should cover the project vision, planned features, technology stack, domain information, and basic development setup instructions.

## Requirements

### REQ-01-01: Project Description

**Description**: The README must clearly describe ana-auth as a private SSO/OAuth authentication service for centralized identity management across multiple private services.

**Acceptance Scenarios**:

- **WHEN** a developer reads the README
  **THEN** they understand that ana-auth is a self-hosted identity provider
  **AND** they understand it provides SSO authentication, JWT signing, and token management

### REQ-01-02: Planned Features Overview

**Description**: The README must list the planned features so readers understand the project roadmap.

**Acceptance Scenarios**:

- **WHEN** a developer reads the features section
  **THEN** they see the following planned capabilities listed: user management (admin UI), SSO sign-in form, JWT token issuance, token refresh, user info endpoint (givenName, familyName, displayName, userId, email), and user consent flow

### REQ-01-03: Technology Stack

**Description**: The README must document the technology stack used by the project.

**Acceptance Scenarios**:

- **WHEN** a developer reads the tech stack section
  **THEN** they see Python 3.13 with FastAPI for the backend, Angular 21 for the frontend, PostgreSQL for the database, and uv for package management

### REQ-01-04: Domain and Deployment Information

**Description**: The README must document the deployment domains and stage setup.

**Acceptance Scenarios**:

- **WHEN** a developer reads the deployment section
  **THEN** they see auth.mathcodingclub.com as the production domain
  **AND** they see auth-dev.mathcodingclub.com as the development domain
  **AND** they understand both stages run on the same physical server

### REQ-01-05: Development Setup Instructions

**Description**: The README must include instructions for setting up the local development environment.

**Acceptance Scenarios**:

- **WHEN** a developer wants to start working on the project
  **THEN** they find instructions for starting PostgreSQL via Docker, installing dependencies with uv, running the backend, building the frontend, and running tests

## Edge Cases

- The README should be useful even before all planned features are implemented, clearly distinguishing between current state and planned features.

## UI/UX Considerations

Not applicable -- this is a documentation artifact.

## Out of Scope

- Detailed API documentation (will come with implementation)
- Architecture diagrams (will come with technical specs)
- Contribution guidelines beyond basic setup

## Constraints

- Must be a single README.md file at the repository root
- Must use standard Markdown formatting
