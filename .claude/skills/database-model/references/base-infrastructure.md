# Base Infrastructure for Database Models

This file contains foundational classes needed before creating SQLModel classes in a fresh project.

## Directory Structure

```
src/shared/db/models/
├── __init__.py
├── base_model.py                    # BaseDBModelMixin
└── <domain>_models/
    ├── __init__.py
    ├── <domain>_enums.py            # Domain enums
    ├── <domain>_types.py            # JSONB types (optional)
    └── <table_name>.py              # SQLModel classes
```

## 1. BaseDBModelMixin (src/shared/db/models/base_model.py)

```python
"""Base model mixin for SQLModel classes."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID


class BaseDBModelMixin:
    """Mixin providing common functionality for SQLModel classes.

    All SQLModel classes should inherit from this mixin to get:
    - dump_to_dto_dict() for converting to DTOs
    - update_from_dict() for updating from DTOs
    """

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

## 2. Domain Package Init (src/shared/db/models/<domain>_models/__init__.py)

```python
"""<Domain> models package."""

from .<table_name> import TableName
from .<domain>_enums import StatusEnum, TypeEnum

__all__ = ["TableName", "StatusEnum", "TypeEnum"]
```

## 3. Basic Enum Pattern (src/shared/db/models/<domain>_models/<domain>_enums.py)

```python
"""<Domain> enumerations for type-safe database fields."""

from enum import Enum


class StatusEnum(str, Enum):
    """Status values for <domain> entities."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class TypeEnum(str, Enum):
    """Type values for <domain> entities."""

    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    CUSTOM = "CUSTOM"
```

## Usage Example

```python
"""Feature SQLModel."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from ..base_model import BaseDBModelMixin
from .feature_enums import StatusEnum


class Feature(SQLModel, BaseDBModelMixin, table=True):
    """Feature entity."""

    __tablename__ = "feature"

    id: str = Field(primary_key=True, default=None)
    name: str
    status: StatusEnum
    description: Optional[str] = Field(default=None)
    group_id: str = Field(foreign_key="group.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```
