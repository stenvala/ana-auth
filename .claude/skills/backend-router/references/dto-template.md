# DTO Template

## DTO Patterns

All DTOs inherit from `BaseDTO` which provides camelCase conversion for API responses.

**Important**: All fields must be defined with `Field()` for proper validation and documentation.

## Critical Naming Conventions

**These naming conventions are required for `uv run after_api_change.py` to work correctly:**

1. **All DTO classes MUST end with `DTO`** - e.g., `FeatureResponseDTO`, `FeatureCreateDTO`
2. **All Enum classes MUST end with `Enum`** - e.g., `FeatureStatusEnum`, `PriorityLevelEnum`

## Critical Return Type Rules

**NEVER return raw lists from routers.** Always wrap lists in a response DTO with an `items` property.

### ❌ WRONG - Never do this:

```python
# Router returning raw list - FORBIDDEN
@router.get("/features")
async def list_features() -> list[FeatureItemDTO]:  # WRONG!
    ...
```

### ✅ CORRECT - Always wrap lists:

```python
# Response DTO with items property
class FeatureListResponseDTO(BaseDTO):
    """Response containing list of features."""

    items: list[FeatureItemDTO] = Field(..., description="List of features")


# Router returning wrapped response
@router.get("/features")
async def list_features() -> FeatureListResponseDTO:  # CORRECT!
    features = await repo.list_features()
    return FeatureListResponseDTO(items=[...])
```

## File Location

Create DTO files at: `src/shared/dtos/<domain>/<feature>_dtos.py`

## Complete DTO Example

```python
"""DTOs for <feature>."""

from typing import Optional

from pydantic import Field

from shared.base_dto import BaseDTO


class FeatureCreateDTO(BaseDTO):
    """DTO for creating feature."""

    name: str = Field(..., min_length=1, max_length=255, description="Feature name")
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Feature description"
    )
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Priority level (1-10)"
    )


class FeatureUpdateDTO(BaseDTO):
    """DTO for updating feature. All fields optional."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Feature name"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Feature description"
    )
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Priority level (1-10)"
    )


class FeatureItemDTO(BaseDTO):
    """DTO for single feature in list. Essential fields only."""

    id: str = Field(..., description="Unique feature ID")
    name: str = Field(..., description="Feature name")
    status: str = Field(..., description="Feature status")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")


class FeatureListResponseDTO(BaseDTO):
    """DTO for list response. Uses 'items' property for the list."""

    items: list[FeatureItemDTO] = Field(
        ...,
        description="List of features"
    )
    total: int = Field(..., description="Total number of features")
    offset: int = Field(..., description="Number of items skipped")


class FeatureResponseDTO(BaseDTO):
    """DTO for complete feature response. All fields."""

    id: str = Field(..., description="Unique feature ID")
    name: str = Field(..., description="Feature name")
    description: Optional[str] = Field(default=None, description="Feature description")
    status: str = Field(..., description="Feature status")
    priority: Optional[int] = Field(default=None, description="Priority level")
    group_id: str = Field(..., description="Parent group ID")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    updated_at: str = Field(..., description="Last update timestamp (ISO format)")
    created_by_user_id: str = Field(..., description="ID of user who created this")
```

## Important DTO Rules

1. **Always inherit from `BaseDTO`** - Provides camelCase conversion automatically
2. **All fields must use `Field()`** - For validation, documentation, and OpenAPI schema
3. **Never add Config or model_config** - BaseDTO handles configuration
4. **NEVER return raw lists from routers** - Always wrap in response DTO with `items` property
5. **All DTO classes MUST end with `DTO`** - Required for `after_api_change.py`
6. **All Enum classes MUST end with `Enum`** - Required for `after_api_change.py`
7. **Use `str` for datetime/date fields** - `dump_to_dto_dict()` converts to ISO strings
8. **Required fields use `Field(...)`** - Ellipsis indicates required
9. **Optional fields use `Field(default=None)`** - Explicit default

## Enum Definitions

**All enums MUST end with `Enum`** for `after_api_change.py` to detect them.

```python
from enum import Enum


class FeatureStatusEnum(str, Enum):
    """Status values for features."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class PriorityLevelEnum(str, Enum):
    """Priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

### ❌ WRONG Enum naming:

```python
class FeatureStatus(str, Enum):  # WRONG - missing 'Enum' suffix
    DRAFT = "draft"

class Priority(str, Enum):  # WRONG - missing 'Enum' suffix
    LOW = "low"
```

### ✅ CORRECT Enum naming:

```python
class FeatureStatusEnum(str, Enum):  # CORRECT
    DRAFT = "draft"

class PriorityLevelEnum(str, Enum):  # CORRECT
    LOW = "low"
```

## Field Validation Options

```python
# String validation
name: str = Field(..., min_length=1, max_length=255)

# Number validation
age: int = Field(..., ge=0, le=150)  # greater/less than or equal
price: float = Field(..., gt=0)  # greater than (exclusive)

# Pattern validation
email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# List validation
tags: list[str] = Field(..., min_length=1, max_length=10)
```

## Converting DB Models to DTOs

`dump_to_dto_dict()` automatically converts:

| Python Type | Converted To        |
| ----------- | ------------------- |
| datetime    | ISO format string   |
| date        | YYYY-MM-DD string   |
| time        | HH:MM string        |
| UUID        | string              |
| Decimal     | float               |

## BaseDTO Reference

See `base-infrastructure.md` for the BaseDTO implementation that must be created at `src/shared/base_dto.py`.
