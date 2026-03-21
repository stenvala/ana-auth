---
name: backend-service
description: Create service classes for business logic and write operations
---

# Backend Service Creation

Create service classes that implement business logic for write operations.

## When to Use

- Implementing create, update, or delete operations
- Adding audit trail logging
- Enforcing business rules and validation
- Coordinating multiple repository operations

## Prerequisites

1. Repository layer must exist (use `/database-repository` first)
2. Base infrastructure exists (use `resources/base-infrastructure.md` for fresh projects)

## File Location

Create services as `<feature>_service.py` in the shared services module, organized by domain.

**Note**: Services live in the shared module (not the API module) because both the API and worker process need access to business logic. The API directory contains only routers, middleware, and dependency injection.

## Instructions

### 1. Create Service Class

Implement the service with session in constructor and repository instantiation.

### 2. Implement Write Operations

Add create, update, and delete methods with audit logging.

### 3. Verify Import

```bash
cd src && uv run python -c "from shared.services.<domain>.<feature>_service import <Feature>Service; print('OK')"
```

## Key Rules

1. **Services return DTOs**: Services convert DB models to DTOs internally
2. **Audit trail required**: All write operations must log via `AuditTrailService`
3. **Session in constructor**: Accept `Session` in `__init__`, instantiate repositories there
4. **AuditTrailService in constructor**: Accept optional `AuditTrailService` for audit logging
5. **Business validation**: Validate data, check references exist, enforce business rules
6. **Error handling**: Raise `HTTPException` for not found (404), `ValueError` for validation (400)
7. **Internal DTO conversion**: Use `_to_dto()` helper method for consistent conversion
8. **List operations return DTOs**: All list/get methods return DTOs, not DB models

## Templates

See `resources/` folder for:
- `base-infrastructure.md` - **Start here for fresh projects**: MinimalUser, logger, audit models
- `service-template.md` - Complete service implementation pattern

