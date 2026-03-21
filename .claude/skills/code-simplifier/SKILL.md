---
name: code-simplifier
description: Review and simplify recently modified code preserving functionality
---

# Code Simplifier

Review recently modified code and apply simplifications that preserve functionality while improving clarity.

## Process

1. Identify files modified in this session (check git diff or recent edits)
2. Review each file for simplification opportunities
3. Apply fixes, verify build passes

## Angular Simplifications

### Signal Patterns

- Replace manual `isLoading = signal(false)` with derived `isLoading = computed(() => this.data() === null)`
- Remove `ngOnInit` data loading - services auto-load via `untracked()`
- Convert `@Input()` to `input<Type>()`, `@Output()` to `output<Type>()`
- Use `computed()` for all derived state, never `subscribe()`

### Component Structure

- Remove `standalone: true` (it's the default)
- Ensure `ChangeDetectionStrategy.OnPush` is set
- Use `inject()` not constructor injection
- Imports must be `[CoreModule, MaterialModule, SharedModule]` (or without SharedModule for shared components)
- No unused import to files

### Templates

- Replace nested ternaries with `@if/@else` or `@switch`
- Buttons must use `matButton` directive with type: `filled`, `outlined`, `tonal`, or `elevated`
- No template inside typescript file, always separate file

### SCSS

- **Use global styles only**: All styling via classes from project-wide shared stylesheets (`_layout.scss`, `_pages.scss`, `_cards.scss`, `_components.scss`, `_buttons.scss`, `_forms.scss`)
- **No custom SCSS**: Delete component `.scss` files unless explicitly requested
- **No "nice" additions**: No shadows, borders, padding tweaks, or decorative styles unless asked, no `<i>` all of a sudden for single word
- All lists tables, etc use shared scss
- No scss inside typescript file, always separate file, but rather not to have component specific scss

### Shared Components

- Use `<shared-empty-state>` for empty states (not custom markup)
- Use `<shared-loading-bar />` or `<shared-loading-spinner>` for loading
- Check the shared components directory before creating new UI patterns
- Extract repeated UI patterns into shared components

### Naming

- Route components: `route-<name>`
- Shared components: `shared-<name>`
- Presentational components: `<feature>-<name>`
- Dialog components: `<feature>-dialog-<name>`

## General Principles

### DRY (Don't Repeat Yourself)

- Extract repeated code into functions/methods
- Consolidate duplicate logic across files
- Use shared services for common operations
- Create utility functions for repeated patterns

### SOLID

- **Single Responsibility**: Each class/function does one thing
- **Open/Closed**: Extend via composition, not modification
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions (inject services)

## Python/FastAPI Simplifications

### Services

- Session and AuditTrailService in constructor
- Instantiate repositories in `__init__`
- Return DTOs not models
- Use `HTTPException` for 404, `ValueError` for validation

### General

- Remove redundant comments
- Consolidate duplicate logic
- Simplify conditionals

## Verification

```bash
# Frontend
source ~/.nvm/nvm.sh && nvm use 20.19.2 && cd <ui-dir> && npx ng build --configuration=development 2>&1 | head -20

# Backend
cd <project-src> && uv run python -c "from api.main import app; print('OK')"
```

