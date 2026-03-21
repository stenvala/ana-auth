# Base Infrastructure

This file contains foundational classes and utilities needed before creating routers and DTOs.

## Directory Structure

Create the following structure in a fresh project:

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app, middleware, lifespan
│   ├── routers/                       # API route handlers only
│   │   └── __init__.py
│   └── dependencies/                  # FastAPI dependency injection
│       ├── __init__.py
│       ├── database.py                # Database session dependency
│       ├── repositories.py            # Repository dependencies
│       └── services.py                # Service dependencies
├── worker/                            # Background worker (optional)
│   ├── __init__.py
│   └── main.py                        # Worker entry point
└── shared/                            # Shared by API and worker
    ├── __init__.py
    ├── base_dto.py                    # BaseDTO class
    ├── common_dto.py                  # Common DTOs (StatusDTO)
    ├── dtos/                          # Feature DTOs
    │   └── __init__.py
    ├── services/                      # Business logic services
    │   └── __init__.py
    ├── db/
    │   ├── __init__.py
    │   ├── db_context.py              # Database session management
    │   ├── models/
    │   │   ├── __init__.py
    │   │   └── base_model.py          # BaseDBModelMixin
    │   └── repositories/
    │       └── __init__.py
    ├── enums/
    │   ├── __init__.py
    │   └── status_enum.py             # Common StatusEnum
    └── models/
        ├── __init__.py
        └── minimal_user.py            # MinimalUser for audit
```

**Note**: Services, DTOs, and base_dto live in `src/shared/` (not `src/api/`) because both the API and worker process need access to business logic. The `src/api/` directory contains only routers, middleware, and dependency injection.

## 1. BaseDTO (src/shared/base_dto.py)

```python
"""Base DTO class with camelCase conversion."""

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class BaseDTO(BaseModel):
    """Base class for all DTOs.

    Provides:
    - Automatic snake_case to camelCase conversion for JSON serialization
    - Validation on assignment
    - Immutable by default (frozen=False for mutability if needed)
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
    )
```

## 2. Common DTOs (src/shared/common_dto.py)

```python
"""Common DTOs used across multiple routers."""

from pydantic import Field

from shared.base_dto import BaseDTO


class StatusDTO(BaseDTO):
    """Generic status response DTO."""

    status: str = Field(..., description="Status code (SUCCESS, ERROR, etc.)")
    message: str = Field(..., description="Human-readable message")


class PaginationDTO(BaseDTO):
    """Pagination metadata."""

    total: int = Field(..., description="Total number of items")
    offset: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")


class ErrorDTO(BaseDTO):
    """Error response DTO."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict | None = Field(default=None, description="Additional error details")
```

## 3. StatusEnum (src/shared/enums/status_enum.py)

```python
"""Common status enumeration."""

from enum import Enum


class StatusEnum(str, Enum):
    """Common status values."""

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"
```

## 4. BaseDBModelMixin (src/shared/db/models/base_model.py)

```python
"""Base model mixin for SQLModel classes."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID


class BaseDBModelMixin:
    """Mixin providing common functionality for SQLModel classes."""

    def dump_to_dto_dict(self) -> dict[str, Any]:
        """Convert model to dictionary suitable for DTO construction.

        Handles conversion of:
        - datetime -> ISO format string
        - date -> YYYY-MM-DD string
        - time -> HH:MM string
        - UUID -> string
        - Decimal -> float
        """
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            result[key] = self._convert_value(value)
        return result

    def _convert_value(self, value: Any) -> Any:
        """Convert a single value to DTO-compatible format."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, time):
            return value.strftime("%H:%M")
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, list):
            return [self._convert_value(item) for item in value]
        if isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}
        return value

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update model fields from dictionary.

        Only updates fields that exist on the model and are not None in data.
        """
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
```

## 5. MinimalUser (src/shared/models/minimal_user.py)

```python
"""Minimal user model for audit trails."""

from pydantic import BaseModel, Field


class MinimalUser(BaseModel):
    """Minimal user information for audit logging.

    Used to track who performed actions without coupling to full user model.
    """

    id: str = Field(..., description="User ID")
    full_name: str = Field(..., description="User's full name for display")
    email: str | None = Field(default=None, description="User's email (optional)")
```

## 6. Database Session (src/shared/db/session.py)

```python
"""Database session management."""

from typing import Generator

from sqlmodel import Session, create_engine

# Configure your database URL
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"

engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session
```

## 7. Database Dependency (src/api/dependencies/database.py)

```python
"""Database dependencies for FastAPI."""

from typing import Generator

from fastapi import Depends
from sqlmodel import Session

from shared.db.session import get_session


def get_db_session() -> Generator[Session, None, None]:
    """Dependency for database session injection."""
    yield from get_session()
```

## 8. Dependencies Init (src/api/dependencies/__init__.py)

```python
"""API dependencies."""

from .database import get_db_session

__all__ = ["get_db_session"]
```
