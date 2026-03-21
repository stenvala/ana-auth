---
name: backend-router
description: Create FastAPI routers with DTOs, auth, and dependency injection
---

# Backend Router Creation

Create FastAPI routers for API endpoints with proper DTOs and dependency injection.

## When to Use

- Creating REST API endpoints for a feature
- Adding new endpoints to existing routers
- Defining request/response DTOs
- Setting up authentication and authorization

## Prerequisites

1. Service layer must exist for write operations (use `/backend-service`)
2. Repository layer must exist for read operations (use `/database-repository`)
3. Base infrastructure must exist (BaseDTO, common DTOs, etc.)

## File Locations

- **Base infrastructure**: BaseDTO class in the shared module
- **Router**: `private_<feature>_router.py` or `public_<feature>_router.py` in the routers directory
- **DTOs**: `<feature>_dtos.py` in the shared DTOs module, organized by domain
- **Services**: `<feature>_service.py` in the shared services module, organized by domain
- **Dependencies**: Domain-level dependency files in the API dependencies module

**Note**: Services and DTOs live in the shared module (not the API module) because both the API and worker process need access to business logic. The API directory contains only routers, middleware, and dependency injection.

## Instructions

### 1. Create Base Infrastructure (first time only)

If this is a fresh project, first create the base infrastructure following `resources/base-infrastructure.md`:
- BaseDTO class with camelCase conversion
- StatusDTO and common DTOs
- BaseDBModelMixin with dump_to_dto_dict
- Common StatusEnum
- MinimalUser for audit trails

### 2. Create DTOs

Define request and response DTOs inheriting from `BaseDTO`. **All fields must use `Field()`**.

### 3. Add Dependencies

Add service/repository dependencies in the API dependencies module.

### 4. Create Router

Implement API endpoints following REST conventions.

### 5. Register Router

Add the router to the API application entry point.

### 6. Generate Frontend Types (if applicable)

```bash
uv run after_api_change.py
```

## Key Rules

### Router Prefix Rules (CRITICAL)

1. **All routers MUST have a prefix** - Never register a router without a prefix
2. **Prefix naming convention**:
   - `/api/public/<feature>` - No authentication required
   - `/api/private/<feature>` - Authentication required
3. **Prefix uniqueness**: No two routers can have the same prefix
4. **No substring prefixes**: No prefix can be a substring of another prefix
   - ❌ BAD: `/api/private/invoice` and `/api/private/invoice-item` (first is substring of second)
   - ✅ GOOD: `/api/private/invoices` and `/api/private/invoice-items`

### Tag Rules (CRITICAL for Frontend Generation)

5. **Tags determine frontend service names**: The `tags` parameter in `include_router()` directly determines the generated Angular API service class name
   - `tags=["PrivateInvoice"]` → `PrivateInvoiceApiService`
   - `tags=["PublicHealth"]` → `PublicHealthApiService`
6. **Tag naming convention**: Use PascalCase, prefix with `Private` or `Public` to match the router type
7. **One tag per router**: Each router should have exactly one tag for clean service generation

### Implementation Rules

8. **Inject services, not databases**: Always inject domain services (e.g., `AuthService`, `InvoiceService`) via `Depends()` - NEVER inject `Session` or `get_db_session` directly into routers
   - Services are injected via dependencies like `get_<domain>_service()`
   - Services handle their own database session management
   - Routers should be unaware of database details
9. **Services return DTOs**: Services handle conversion to DTOs internally, routers just return the result
10. **All DTO fields use Field()**: For validation, documentation, and OpenAPI schema generation
11. **No session.commit()**: Middleware handles transactions automatically
12. **REST conventions**: Use proper HTTP methods (GET, POST, PUT, DELETE)
13. **Authentication**: Use `Depends(get_current_user)` for authenticated endpoints
14. **Use def not async def**: Unless actually doing async operations
15. **NEVER return raw lists**: Endpoints must ALWAYS return objects, never arrays. Wrap lists in `{ items: [...], total: N }`
16. **NEVER return dict or list[dict]**: Always return Pydantic objects (see python-coding-conventions skill)
17. **NoUIEndpoints tag**: Use `tags=["NoUIEndpoints"]` for system endpoints that should NOT generate Angular services

## When to Use Service vs Repository

| Operation      | Use     | Reason                             |
| -------------- | ------- | ---------------------------------- |
| Create         | Service | Needs audit trail, validation      |
| Update         | Service | Needs audit trail, validation      |
| Delete         | Service | Needs audit trail, validation      |
| Get by ID      | Service | Consistent DTO conversion          |
| List/Search    | Service | Filtering logic, DTO conversion    |

Note: Services use repositories internally for data access.

## Error Handling

Errors are handled centrally by `ApiMiddleware`. Do NOT catch exceptions in routers.

| Exception Type    | HTTP Status | Use Case                          |
| ----------------- | ----------- | --------------------------------- |
| `ValueError`      | 400         | Business logic validation errors  |
| `HTTPException`   | varies      | Specific HTTP errors (404, etc.)  |
| `PermissionError` | 403         | Authorization failures            |
| Other exceptions  | 500         | System errors (auto-logged)       |

## Templates

See `resources/` folder for:
- `base-infrastructure.md` - **Start here for fresh projects**: BaseDTO, common DTOs, base model mixin
- `dto-template.md` - DTO patterns with Field() validation
- `router-template.md` - Complete router implementation

