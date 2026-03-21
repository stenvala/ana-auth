# Functional Specification: Frontend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-storify

## Story

**As a** frontend developer,
**I want** a working Angular 21 application skeleton with Angular Material v3 theming, a custom sci-fi design system, and a landing page,
**So that** I have a visually consistent foundation to build the admin UI and SSO sign-in form on top of.

## Detailed Description

The frontend skeleton is an Angular 21 application scaffolded with the Angular CLI (`npx ng`). It includes Angular Material with a custom Material Design 3 (M3) theme using a sci-fi color palette -- deep space blues, electric cyans, and neon accents. The theming uses Angular Material's Sass APIs (`mat.theme` mixin) with custom color palettes generated via `npx ng generate @angular/material:theme-color`. The design system defines a consistent visual language (colors, typography, spacing, component overrides) that all future UI components will follow. Light and dark mode are supported via CSS `color-scheme`, defaulting to dark for the sci-fi aesthetic. The application runs on port 6785 in development and proxies API requests to the backend on port 6784.

## Requirements

### REQ-03-01: Angular 21 Project Scaffold

**Description**: The frontend must be a properly scaffolded Angular 21 project using the Angular CLI.

**Acceptance Scenarios**:

- **WHEN** a developer runs `npx ng build`
  **THEN** the build completes successfully
  **AND** production-ready assets are output to the dist directory

- **WHEN** a developer runs `npx ng serve --port 6785`
  **THEN** the application is served on localhost:6785 and displays a landing page

### REQ-03-02: Angular Material v3 with Custom Sci-Fi Theme

**Description**: The application must use Angular Material with a custom Material Design 3 theme featuring a sci-fi color palette.

**Acceptance Scenarios**:

- **WHEN** the application loads
  **THEN** Angular Material components render with the custom sci-fi theme
  **AND** the primary color is a deep space blue/violet tone
  **AND** the tertiary color is an electric cyan/neon accent
  **AND** the secondary color complements the primary with a muted cool tone

- **WHEN** the custom theme is generated
  **THEN** it uses the Angular Material Sass API (`mat.theme` mixin) with custom color palettes
  **AND** all Material Design 3 color tokens (primary, secondary, tertiary, error, surface, on-surface, etc.) are defined

### REQ-03-03: Dark Mode Default with Light Mode Support

**Description**: The application must default to dark mode for the sci-fi aesthetic but support light mode via CSS color-scheme.

**Acceptance Scenarios**:

- **WHEN** the application loads without user preference
  **THEN** dark mode is active
  **AND** surfaces use dark backgrounds with light text

- **WHEN** the system preference is set to light mode or a light mode toggle is activated
  **THEN** the theme switches to light mode using CSS `light-dark()` color function
  **AND** all Angular Material components respect the mode switch

### REQ-03-04: Design System Foundation

**Description**: A design system must be established defining the visual language for the entire application.

**Acceptance Scenarios**:

- **WHEN** a developer creates a new component
  **THEN** they can use the defined CSS custom variables for colors (e.g., `--mat-sys-primary`, `--mat-sys-tertiary`, `--mat-sys-surface`)
  **AND** they can use the established typography scale (via Angular Material's typography system)
  **AND** consistent spacing and layout patterns are documented or demonstrated in the skeleton

### REQ-03-05: Landing Page

**Description**: The application must display a landing page identifying this as the ana-auth service, styled with the sci-fi theme.

**Acceptance Scenarios**:

- **WHEN** a user navigates to the root URL
  **THEN** they see a page identifying this as the ana-auth authentication service
  **AND** the page is styled with the custom sci-fi theme (dark background, neon accents)

### REQ-03-06: Routing Setup

**Description**: The application must have Angular routing configured for future feature development.

**Acceptance Scenarios**:

- **WHEN** the application loads
  **THEN** the Angular router is configured
  **AND** unknown routes redirect to the landing page

### REQ-03-07: API Proxy Configuration

**Description**: The development server must proxy API requests to the backend on port 6784.

**Acceptance Scenarios**:

- **WHEN** the frontend makes a request to `/api/*` in development mode
  **THEN** the request is proxied to localhost:6784

## Edge Cases

- The frontend should build without errors even when the backend is not running.
- The theme must be accessible -- sufficient contrast ratios between text and backgrounds in both dark and light modes.
- If the browser does not support CSS `light-dark()`, the dark theme should still render correctly as the default.

## UI/UX Considerations

- Sci-fi aesthetic: think deep space, cyberpunk terminals, holographic interfaces. Dark backgrounds with glowing accents.
- Primary palette: deep violet/indigo (space depth)
- Tertiary palette: electric cyan/teal (neon glow)
- Secondary palette: cool grey-blue (muted complement)
- Error color: warm neon red/orange
- Typography: clean, modern sans-serif (Roboto via Angular Material default is fine)
- The landing page should feel like a futuristic authentication portal

## Out of Scope

- Admin user management UI
- SSO sign-in form
- Any functional pages beyond the landing page
- Complex animations or particle effects
- Custom icon set

## Constraints

- Must use Angular 21
- Must use Node.js 20.19 via nvm (`.nvmrc` in project root); Angular 21 does not compile with lower versions
- Must use Angular Material with M3 theming (not legacy M2)
- All Angular CLI commands must use `npx ng`
- Dev server runs on port 6785
- API proxy targets localhost:6784
- Must produce a production build that can be served by nginx
