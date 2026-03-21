---
name: database-repository
description: Create repository classes for database operations using repository pattern
---

# Database Repository Creation

Create repository classes that handle database operations using the repository pattern.

## When to Use

- Creating data access layer after SQLModel classes exist
- Adding new query methods to existing repositories
- Implementing complex database queries
- Separating database operations from business logic

## Prerequisites

1. Database design exists in the data model documentation directory
2. Schema exists in the database scripts directory
3. SQLModel class exists in the models directory

## File Location

Create repository in the domain's repository directory, one file per table.

## Instructions

### 1. Create Repository Class

Implement the repository with session injection and standard CRUD methods.

### 2. Add Domain-Specific Queries

Add methods for common query patterns needed by services.

### 3. Verify Import

Verify the repository can be imported successfully from the repositories module.

## Key Rules

1. **Session injection**: Accept `Session` in `__init__`, never create sessions
2. **No commits**: Use `session.flush()` not `session.commit()` - transaction managed by service layer
3. **Refresh after write**: Always call `session.refresh(entity)` after `add()` + `flush()`
4. **Return types**: Use `Optional[T]` for single results, `List[T]` for multiple
5. **Query patterns**:
   - Simple ID lookup: `session.get(Model, id)`
   - Complex queries: `select(Model).where(...)` with `session.exec(...)`
6. **List conversion**: Always wrap `session.exec(...).all()` in `list()` for proper typing

## Templates

See `resources/` folder for:
- `repository-template.md` - Basic repository structure
- `query-patterns.md` - Common query patterns

