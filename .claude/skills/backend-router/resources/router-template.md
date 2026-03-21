# Router Template

## Complete Router Implementation

```python
"""Private router for <feature> endpoints."""

from fastapi import APIRouter, Depends, status

from shared.common_dto import StatusDTO
from shared.enums.status_enum import StatusEnum
from api.dependencies.<domain> import get_<feature>_service
from shared.dtos.<domain>.<feature>_dtos import (
    <Feature>CreateDTO,
    <Feature>DTO,
    <Feature>ListResponseDTO,
    <Feature>UpdateDTO,
)
from shared.services.<domain>.<feature>_service import <Feature>Service

router = APIRouter()


@router.get(
    "",
    response_model=<Feature>ListResponseDTO,
    summary="List all <feature>s",
)
def list_<feature>s(
    service: <Feature>Service = Depends(get_<feature>_service),
) -> <Feature>ListResponseDTO:
    """Get all <feature>s."""
    items = service.list_all()
    return <Feature>ListResponseDTO(items=items, total=len(items))


@router.get(
    "/{<feature>_id}",
    response_model=<Feature>DTO,
    summary="Get <feature> by ID",
)
def get_<feature>(
    <feature>_id: str,
    service: <Feature>Service = Depends(get_<feature>_service),
) -> <Feature>DTO:
    """Get a <feature> by its ID."""
    return service.get_by_id(<feature>_id)


@router.post(
    "",
    response_model=<Feature>DTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create <feature>",
)
def create_<feature>(
    dto: <Feature>CreateDTO,
    service: <Feature>Service = Depends(get_<feature>_service),
) -> <Feature>DTO:
    """Create a new <feature>."""
    return service.create(dto)


@router.put(
    "/{<feature>_id}",
    response_model=<Feature>DTO,
    summary="Update <feature>",
)
def update_<feature>(
    <feature>_id: str,
    dto: <Feature>UpdateDTO,
    service: <Feature>Service = Depends(get_<feature>_service),
) -> <Feature>DTO:
    """Update an existing <feature>."""
    return service.update(<feature>_id, dto)


@router.delete(
    "/{<feature>_id}",
    response_model=StatusDTO,
    summary="Delete <feature>",
)
def delete_<feature>(
    <feature>_id: str,
    service: <Feature>Service = Depends(get_<feature>_service),
) -> StatusDTO:
    """Delete a <feature>."""
    service.delete(<feature>_id)
    return StatusDTO(status=StatusEnum.DELETED, message="<Feature> deleted")
```

## List Response DTO Pattern (CRITICAL)

**NEVER return raw lists from endpoints.** Always wrap in an object with `items` property:

```python
# In <feature>_dtos.py:
class <Feature>ListResponseDTO(BaseDTO):
    """Response containing list of <feature>s."""

    items: list[<Feature>DTO] = Field(description="List of <feature>s")
    total: int = Field(description="Total number of items")
```

This ensures:
- Consistent API structure across all endpoints
- Room for pagination metadata (total, offset, limit)
- TypeScript can properly type the response

## Dependency Registration (CRITICAL)

**IMPORTANT**: Services must be injected in routers, NOT database sessions.

Add service dependency in `src/api/dependencies/<domain>.py`:

```python
from fastapi import Depends
from sqlmodel import Session

from shared.services.<domain>.<feature>_service import <Feature>Service
from shared.services.<domain>.audit_trail_service import AuditTrailService
from .database import get_db_session


def get_<feature>_service(
    session: Session = Depends(get_db_session),
    audit_trail: AuditTrailService = Depends(get_audit_trail_service),
) -> <Feature>Service:
    """Get <Feature>Service instance for current request."""
    return <Feature>Service(session=session, audit_trail=audit_trail)
```

Then in your router, inject the SERVICE, not the Session:

```python
def get_feature(
    feature_id: str,
    service: <Feature>Service = Depends(get_<feature>_service),  # ✅ CORRECT
) -> <Feature>DTO:
    return service.get_by_id(feature_id)

# ❌ WRONG - Never do this:
# def get_feature(session: Session = Depends(get_db_session)):
```

## Router Registration (src/api/main.py)

### CRITICAL Rules for Registration

1. **All routers MUST have a prefix** - Never register without one
2. **Prefix must start with**:
   - `/api/public/` - For unauthenticated endpoints
   - `/api/private/` - For authenticated endpoints
3. **Prefix uniqueness**: No duplicate prefixes allowed
4. **No substring prefixes**: Prefix cannot be substring of another
   - ❌ `/api/private/invoice` and `/api/private/invoice-item`
   - ✅ `/api/private/invoices` and `/api/private/invoice-items`

### Example Registration

```python
from api.routers.private_<feature>_router import router as private_<feature>_router

app.include_router(
    private_<feature>_router,
    prefix="/api/private/<feature>s",
    tags=["Private<Feature>"],
)
```

### Tag Rules (CRITICAL for Frontend Generation)

The `tags` parameter directly determines the generated Angular API service class name:

| Tag                    | Generated Service Class      |
| ---------------------- | ---------------------------- |
| `["PrivateInvoice"]`   | `PrivateInvoiceApiService`   |
| `["PublicHealth"]`     | `PublicHealthApiService`     |
| `["NoUIEndpoints"]`    | No service generated         |

**Rules**:
- Use PascalCase (no spaces)
- Prefix with `Private` or `Public` to match router type
- One tag per router for clean service generation
- Use `NoUIEndpoints` for system endpoints that don't need frontend services

## After API Changes

After creating or modifying routers, regenerate frontend types:

```bash
cd src && uv run after_api_change.py
```

This generates:
- TypeScript DTOs in `src/ui/src/api-integration/dto.ts`
- Angular API services in `src/ui/src/api-integration/`
