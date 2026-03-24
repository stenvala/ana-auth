# Functional Specification: Frontend Skeleton

**Domain**: auth/frontend-skeleton
**Last updated**: 2026-03-24

## Story

**As a** developer,
**I want** a working Angular 21 frontend skeleton with Material Design theming,
**So that** I have a foundation for building the admin UI and SSO sign-in form.

## Detailed Description

The frontend is an Angular 21 application with Angular Material v3 using a custom sci-fi theme. It serves as the shell for the admin interface and SSO sign-in form.

## Requirements

### REQ-01: Angular Material Sci-Fi Theme

**Description**: A custom Material Design 3 theme with dark mode default and sci-fi aesthetics.

**Acceptance Scenarios**:

- **WHEN** the application loads
  **THEN** it renders in dark mode with deep violet primary and electric cyan tertiary colors

- **WHEN** the user's system prefers light mode
  **THEN** light mode is available via CSS `light-dark()` function

### REQ-02: Landing Page

**Description**: A landing page that identifies the service as ana-auth.

**Acceptance Scenarios**:

- **WHEN** a user navigates to the root URL
  **THEN** they see a landing page identifying the ana-auth service

### REQ-03: Router Configuration

**Description**: Angular router with wildcard redirect to landing page.

**Acceptance Scenarios**:

- **WHEN** a user navigates to an unknown route
  **THEN** they are redirected to the landing page

### REQ-04: API Proxy

**Description**: Development proxy forwards `/api/*` requests to the backend.

**Acceptance Scenarios**:

- **WHEN** the frontend makes a request to `/api/health` in development
  **THEN** the request is proxied to localhost:6784

### REQ-05: Build

**Description**: The frontend builds successfully with the Angular CLI.

**Acceptance Scenarios**:

- **WHEN** `npx ng build` is run
  **THEN** the build completes successfully and outputs to `src/ui/dist/`

## Constraints

- Development server runs on port 6785
- Requires Node.js 20.19.2 (managed via nvm, `.nvmrc` at project root)
- Theme generated via `npx ng generate @angular/material:theme-color` with source color #4A0E78
