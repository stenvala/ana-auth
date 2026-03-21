---
name: test-playwright
description: Create Playwright E2E tests using Page Object pattern for user workflows
---

# E2E Test Creation

Create Playwright E2E tests using the Page Object pattern for maintainability and reusability.

## When to Use

- Testing complete user workflows (login, CRUD operations, navigation)
- Validating UI interactions across multiple pages
- Testing form submissions and validation
- Verifying authentication and authorization flows

## Prerequisites

1. Feature fully implemented and manually tested
2. Frontend and backend running

## Directory Structure

E2E tests follow this layout inside the project test directory:

```
e2e/
├── conftest.py                    # Pytest fixtures
├── pages/                         # Page objects
│   ├── base_page.py              # Base class for all pages
│   ├── auth_utils.py             # Authentication utilities
│   └── <feature>/                # Feature-specific pages
│       └── <feature>_page.py
├── tests/                        # Test files
│   └── <feature>/
│       └── test_<scenario>.py
└── utils/                        # Utilities
    ├── test_paths.py             # URL path constants
    ├── page_utils.py             # Page utilities
    └── screenshot_on_failure.py  # Artifact capture
```

## Instructions

### 1. Create Base Infrastructure (first time only)

If this is a fresh project, create the base infrastructure following `resources/base-infrastructure.md`:
- `base_page.py` - Base class with common methods
- `conftest.py` - Pytest fixtures for browser, database
- `screenshot_on_failure.py` - Artifact capture utilities

### 2. Create Page Object

Create page object class extending `BasePage` with selectors and methods.
See `resources/page-object-template.md` for patterns.

### 3. Create Test File

Create async test using page objects with artifact capture.
See `resources/test-template.md` for patterns.

### 4. Run Tests

```bash
# Run specific test
uv run pytest <e2e-tests-dir>/tests/<feature>/test_<scenario>.py -v

# Run all e2e tests
uv run pytest <e2e-tests-dir>/ -v -m e2e

# Run with visible browser (debug)
uv run pytest <e2e-tests-dir>/ -v --headed
```

## Key Rules

1. **Page Object pattern**: One class per page/section with all selectors as instance variables
2. **Async/await**: All methods must be async (Playwright requirement)
3. **data-test-id selectors**: Primary selector strategy for decoupling from CSS
4. **Wait after actions**: Always wait for navigation/state changes after clicks
5. **Business-level methods**: Page objects expose high-level actions, not raw Playwright calls
6. **Artifact capture**: Use `run_with_screenshot_on_failure` wrapper for debugging
7. **Database fixtures**: Use repositories to set up test data, not API calls

## Resources

- `resources/base-infrastructure.md` - Base page class, conftest fixtures, utilities
- `resources/page-object-template.md` - Page object class patterns
- `resources/test-template.md` - Test file structure and patterns

