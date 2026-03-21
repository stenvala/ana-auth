# Manual Testing Plan: Frontend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21

## Test Scenarios

### Scenario 1: Landing page loads with dark theme

**Preconditions**: Node.js 20.19 via nvm, npm dependencies installed

**Steps**:
1. Run `nvm use 20.19.2 && cd src/ui && npx ng serve --port 6785`
2. Open browser to `http://localhost:6785`

**Expected Result**: Landing page displays with dark background, violet/cyan color scheme, and ana-auth branding

### Scenario 2: Light mode switch

**Preconditions**: Dev server running

**Steps**:
1. Open browser developer tools
2. Toggle system color scheme to light mode (or use emulated CSS media)

**Expected Result**: Theme switches to light mode with appropriate color adjustments

### Scenario 3: Production build

**Preconditions**: Node.js 20.19 via nvm

**Steps**:
1. Run `nvm use 20.19.2 && cd src/ui && npx ng build`
2. Check `src/ui/dist/` directory

**Expected Result**: Build succeeds, dist/ contains production-ready assets

### Scenario 4: Unknown routes redirect

**Preconditions**: Dev server running

**Steps**:
1. Navigate to `http://localhost:6785/nonexistent-page`

**Expected Result**: Redirects to the landing page

## Exploratory Testing Areas

- Verify Angular Material components render correctly with custom theme
- Check accessibility (contrast ratios) in both dark and light modes
- Verify proxy configuration: requests to /api/* reach the backend
